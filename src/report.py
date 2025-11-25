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