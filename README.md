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

## Execution

From the project root, you can run:

```bash
python -m src.main --input sample_data.json --out-dir out --html --sqlite-db results.db
```


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