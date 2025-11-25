from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class TestResult:
    """Represents the result of a single test case."""
    name: str
    status: str  # "passed" | "failed" | "skipped"
    duration: float  # Execution time in seconds


@dataclass
class TestSession:
    """A pytest session run for a specific DUT configuration."""
    dut: str
    session_id: str
    tests: List[TestResult]


@dataclass
class PerDUTSummary:
    """Aggregated statistics for a single DUT."""
    dut: str
    total: int
    passed: int
    failed: int
    skipped: int
    total_duration: float
    avg_duration: float
    pass_rate: float  # Percentage 0–100


@dataclass
class OverallSummary:
    """Aggregated statistics across all DUTs."""
    total_tests: int
    total_passed: int
    total_failed: int
    total_skipped: int
    total_duration: float
    avg_duration: float
    overall_pass_rate: float  # Percentage 0–100
    per_dut: List[PerDUTSummary]


@dataclass
class ExtraMetrics:
    """
    Additional metrics that are not strictly required
    but useful for analysis (bonus).
    """
    slowest_tests: List[Dict[str, object]]
    tests_per_dut: Dict[str, int]
    unique_test_names: int