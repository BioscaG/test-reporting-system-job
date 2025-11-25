from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import OverallSummary, ExtraMetrics, PerDUTSummary


def write_summary_json(
    summary: OverallSummary,
    extras: ExtraMetrics,
    path: str | Path,
) -> None:
    """
    Write the aggregated summary and extra metrics into a JSON file.
    """
    p = Path(path)
    data = {
        "overall": {
            "total_tests": summary.total_tests,
            "total_passed": summary.total_passed,
            "total_failed": summary.total_failed,
            "total_skipped": summary.total_skipped,
            "total_duration": summary.total_duration,
            "avg_duration": summary.avg_duration,
            "overall_pass_rate": summary.overall_pass_rate,
        },
        "per_dut": [
            {
                "dut": d.dut,
                "total": d.total,
                "passed": d.passed,
                "failed": d.failed,
                "skipped": d.skipped,
                "total_duration": d.total_duration,
                "avg_duration": d.avg_duration,
                "pass_rate": d.pass_rate,
            }
            for d in summary.per_dut
        ],
        "extra_metrics": {
            "slowest_tests": extras.slowest_tests,
            "tests_per_dut": extras.tests_per_dut,
            "unique_test_names": extras.unique_test_names,
        },
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_per_dut_csv(
    per_dut: Iterable[PerDUTSummary],
    path: str | Path,
) -> None:
    """
    Write a CSV file with one row per DUT summary.
    """
    p = Path(path)
    fieldnames = [
        "dut",
        "total",
        "passed",
        "failed",
        "skipped",
        "total_duration",
        "avg_duration",
        "pass_rate",
    ]
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in per_dut:
            writer.writerow(
                {
                    "dut": d.dut,
                    "total": d.total,
                    "passed": d.passed,
                    "failed": d.failed,
                    "skipped": d.skipped,
                    "total_duration": f"{d.total_duration:.3f}",
                    "avg_duration": f"{d.avg_duration:.3f}",
                    "pass_rate": f"{d.pass_rate:.2f}",
                }
            )


def _load_html_template(template_path: Path) -> str:
    """
    Load the HTML template from a file.
    """
    return template_path.read_text(encoding="utf-8")


def write_html_dashboard(
    summary: OverallSummary,
    extras: ExtraMetrics,
    path: str | Path,
    template_path: Path | None = None,
) -> None:
    """
    Generate a small static HTML dashboard for stakeholders.

    The HTML structure is stored in templates/dashboard.html and uses
    basic str.format() placeholders.
    """
    if template_path is None:
        # src/report.py -> src -> project root
        root_dir = Path(__file__).resolve().parents[1]
        template_path = root_dir / "templates" / "dashboard.html"

    template = _load_html_template(template_path)

    per_dut_rows = "".join(
        f"<tr>"
        f"<td>{d.dut}</td>"
        f"<td>{d.total}</td>"
        f"<td>{d.passed}</td>"
        f"<td>{d.failed}</td>"
        f"<td>{d.skipped}</td>"
        f"<td>{d.total_duration:.2f}</td>"
        f"<td>{d.avg_duration:.2f}</td>"
        f"<td>{d.pass_rate:.1f}%</td>"
        f"</tr>"
        for d in summary.per_dut
    )

    slowest_rows = "".join(
        f"<tr>"
        f"<td>{t['name']}</td>"
        f"<td>{t['dut']}</td>"
        f"<td>{t['session_id']}</td>"
        f"<td>{t['status']}</td>"
        f"<td>{t['duration']:.2f}</td>"
        f"</tr>"
        for t in extras.slowest_tests
    )

    html = template.format(
        total_tests=summary.total_tests,
        overall_pass_rate=summary.overall_pass_rate,
        total_duration=summary.total_duration,
        unique_test_names=extras.unique_test_names,
        per_dut_rows=per_dut_rows,
        slowest_rows=slowest_rows,
    )

    Path(path).write_text(html, encoding="utf-8")