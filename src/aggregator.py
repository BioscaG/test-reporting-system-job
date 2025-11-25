from __future__ import annotations

from typing import List, Dict, Tuple

from .models import (
    TestSession,
    PerDUTSummary,
    OverallSummary,
    ExtraMetrics,
    TestResult,
)


def aggregate_per_dut(sessions: List[TestSession]) -> List[PerDUTSummary]:
    """
    Aggregate results per DUT.

    Returns a list of PerDUTSummary objects, one per DUT found in the sessions.
    """
    per_dut_map: Dict[str, Dict[str, float]] = {}

    for session in sessions:
        stats = per_dut_map.setdefault(
            session.dut,
            {
                "total": 0.0,
                "passed": 0.0,
                "failed": 0.0,
                "skipped": 0.0,
                "duration": 0.0,
            },
        )
        for test in session.tests:
            stats["total"] += 1.0
            stats["duration"] += float(test.duration)

            status = test.status.lower()
            if status == "passed":
                stats["passed"] += 1.0
            elif status == "failed":
                stats["failed"] += 1.0
            else:
                stats["skipped"] += 1.0

    summaries: List[PerDUTSummary] = []
    for dut, s in per_dut_map.items():
        total = int(s["total"])
        total_duration = float(s["duration"])
        avg_duration = total_duration / total if total > 0 else 0.0
        pass_rate = (s["passed"] / total * 100.0) if total > 0 else 0.0

        summaries.append(
            PerDUTSummary(
                dut=dut,
                total=total,
                passed=int(s["passed"]),
                failed=int(s["failed"]),
                skipped=int(s["skipped"]),
                total_duration=total_duration,
                avg_duration=avg_duration,
                pass_rate=pass_rate,
            )
        )

    # Sort by DUT name for stable output
    summaries.sort(key=lambda x: x.dut)
    return summaries


def _get_slowest_tests(
    sessions: List[TestSession],
    top_n: int = 5,
) -> List[Dict[str, object]]:
    """
    Return the top N slowest tests across all sessions.

    Each entry contains: name, dut, session_id, duration, status.
    """
    all_tests: List[tuple[str, str, TestResult]] = []
    for session in sessions:
        for test in session.tests:
            all_tests.append((session.dut, session.session_id, test))

    all_tests.sort(key=lambda x: x[2].duration, reverse=True)

    result: List[Dict[str, object]] = []
    for dut, session_id, test in all_tests[:top_n]:
        result.append(
            {
                "name": test.name,
                "dut": dut,
                "session_id": session_id,
                "duration": test.duration,
                "status": test.status,
            }
        )
    return result


def aggregate_overall(sessions: List[TestSession]) -> Tuple[OverallSummary, ExtraMetrics]:
    """
    Aggregate results across all DUTs and compute extra metrics.
    """
    per_dut_summaries = aggregate_per_dut(sessions)

    total_tests = sum(d.total for d in per_dut_summaries)
    total_passed = sum(d.passed for d in per_dut_summaries)
    total_failed = sum(d.failed for d in per_dut_summaries)
    total_skipped = sum(d.skipped for d in per_dut_summaries)
    total_duration = sum(d.total_duration for d in per_dut_summaries)

    avg_duration = total_duration / total_tests if total_tests > 0 else 0.0
    overall_pass_rate = (total_passed / total_tests * 100.0) if total_tests > 0 else 0.0

    slowest_tests = _get_slowest_tests(sessions, top_n=5)
    tests_per_dut = {d.dut: d.total for d in per_dut_summaries}
    unique_test_names = len({t.name for s in sessions for t in s.tests})

    extras = ExtraMetrics(
        slowest_tests=slowest_tests,
        tests_per_dut=tests_per_dut,
        unique_test_names=unique_test_names,
    )

    overall = OverallSummary(
        total_tests=total_tests,
        total_passed=total_passed,
        total_failed=total_failed,
        total_skipped=total_skipped,
        total_duration=total_duration,
        avg_duration=avg_duration,
        overall_pass_rate=overall_pass_rate,
        per_dut=per_dut_summaries,
    )
    return overall, extras