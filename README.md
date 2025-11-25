# Test Reporting Aggregator

## Overview

This tool aggregates the results of multiple pytest sessions, each associated with
a different DUT (Device Under Test) configuration.

Typical use case:
- The same test suite is executed on different DUTs.
- Some tests pass, some fail, and some may be skipped depending on the configuration.
- You want a single high-level view of the overall software quality and per-DUT status.

The tool reads a JSON file that contains one object per pytest session, aggregates
the results, and produces:
- A JSON summary file
- A CSV file with per-DUT statistics
- Optionally, a simple static HTML dashboard for stakeholders
- Optionally, a SQLite database suitable for Grafana dashboards

## Input format

The input JSON is expected to follow this structure:

```json
[
  {
    "dut": "DUT_A",
    "session_id": "session_001",
    "tests": [
      {"name": "test_login", "status": "passed", "duration": 1.2},
      {"name": "test_signup", "status": "failed", "duration": 2.5},
      {"name": "test_logout", "status": "skipped", "duration": 0.8}
    ]
  },
  {
    "dut": "DUT_B",
    "session_id": "session_002",
    "tests": [
      {"name": "test_login", "status": "passed", "duration": 1.0},
      {"name": "test_signup", "status": "passed", "duration": 2.2}
    ]
  }
]
```

## Execution

From the project root, you can run:

```bash
python -m src.main --input sample_data.json --out-dir out --html --sqlite-db results.db
```

**Arguments:**
- `--input` → Path to the JSON file with test sessions.  
- `--out-dir` → Output directory (will be created if it does not exist).  
- `--html` → Generates a static HTML dashboard (`dashboard.html`).  
- `--sqlite-db` → Creates a SQLite database (`results.db`) that can be used as a data source in Grafana.

After running the command, the `out/` directory will contain:

- `summary.json`  
- `per_dut_summary.csv`  
- `dashboard.html` *(if `--html` is used)*  
- `results.db` *(if `--sqlite-db` is used)*

## Installation

Requirements:
- Python 3.10+
- (Optional) mypy for static type checking

Setup:

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Grafana integration (SQLite)

The tool can export results into a SQLite database, which can be used as a data
source in Grafana.

To generate the database:

```bash
python -m src.main   --input sample_data.json   --out-dir out   --sqlite-db results.db
```

This creates `out/results.db` with three tables:

- `sessions` – one row per pytest session (DUT + session_id)
- `tests` – one row per individual test
- `summary` – a single row with overall statistics (id = 1)

In Grafana:

1. Install a SQLite data source plugin (for example, a community SQLite plugin).
2. Add a new data source and point it to the `results.db` file.
3. Create panels using simple SQL queries, for example:

   - Overall pass rate (from `summary`):

     ```sql
     SELECT overall_pass_rate FROM summary WHERE id = 1;
     ```

   - Passed vs failed per DUT (from `sessions`):

     ```sql
     SELECT dut, passed, failed, skipped
     FROM sessions
     ORDER BY dut;
     ```

   - Slow tests (from `tests`):

     ```sql
     SELECT dut, name, duration
     FROM tests
     WHERE status = 'passed'
     ORDER BY duration DESC
     LIMIT 10;
     ```

This setup allows building dashboards showing pass rate over time, failures per DUT,
and performance hotspots.

## Docker Setup (optional bonus)

You can run the tool without installing Python locally using Docker.

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY templates ./templates
COPY sample_data.json ./sample_data.json

CMD ["python", "-m", "src.main", "--input", "sample_data.json", "--out-dir", "out", "--html", "--sqlite-db", "results.db"]
```

### Run it with Docker

```bash
docker build -t test-reporting .
docker run --rm -v "$(pwd)/out:/app/out" test-reporting
```

This builds the image and runs the tool inside a container, producing the same outputs
(`summary.json`, `dashboard.html`, `results.db`, etc.) inside the local `out/` directory.

## Design decisions

- **Explicit data model**  
  All entities (`TestResult`, `TestSession`, `PerDUTSummary`, `OverallSummary`,
  `ExtraMetrics`) use `dataclasses` for clarity and type safety.

- **Separation of concerns**  
  - `parser.py` → input loading  
  - `aggregator.py` → pure aggregation logic  
  - `report.py` → JSON/CSV/HTML output  
  - `sqlite_exporter.py` → database export for Grafana  
  - `main.py` → CLI interface

- **Extensible outputs**  
  The project cleanly supports multiple output formats, making it adaptable
  for dashboards, CI pipelines, or reporting tools.

- **Portable setup**  
  The Dockerfile provides a reproducible environment that works on any system
  without dependency issues.

---