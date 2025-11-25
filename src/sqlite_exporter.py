from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List

from .models import TestSession, OverallSummary, ExtraMetrics


def export_to_sqlite(
    sessions: List[TestSession],
    summary: OverallSummary,
    extras: ExtraMetrics,
    db_path: str | Path,
) -> None:
    """
    Export data to a SQLite database.

    Tables:
      - sessions: one row per pytest session
      - tests: one row per individual test execution
      - summary: a single row with overall statistics
    """
    path = Path(db_path)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")

    _create_schema(conn)
    _write_sessions_and_tests(conn, sessions)
    _write_summary_metadata(conn, summary, extras)

    conn.commit()
    conn.close()


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dut TEXT NOT NULL,
            session_id TEXT NOT NULL,
            total_tests INTEGER NOT NULL,
            passed INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            skipped INTEGER NOT NULL,
            total_duration REAL NOT NULL
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            dut TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL NOT NULL
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS summary (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_tests INTEGER NOT NULL,
            total_passed INTEGER NOT NULL,
            total_failed INTEGER NOT NULL,
            total_skipped INTEGER NOT NULL,
            total_duration REAL NOT NULL,
            avg_duration REAL NOT NULL,
            overall_pass_rate REAL NOT NULL,
            unique_test_names INTEGER NOT NULL
        );
        """
    )


def _write_sessions_and_tests(
    conn: sqlite3.Connection,
    sessions: List[TestSession],
) -> None:
    # Clear existing rows to keep the DB in sync with the latest run
    conn.execute("DELETE FROM sessions;")
    conn.execute("DELETE FROM tests;")

    for session in sessions:
        total = len(session.tests)
        passed = sum(1 for t in session.tests if t.status == "passed")
        failed = sum(1 for t in session.tests if t.status == "failed")
        skipped = sum(1 for t in session.tests if t.status == "skipped")
        total_duration = sum(t.duration for t in session.tests)

        conn.execute(
            """
            INSERT INTO sessions (dut, session_id, total_tests, passed, failed, skipped, total_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                session.dut,
                session.session_id,
                total,
                passed,
                failed,
                skipped,
                total_duration,
            ),
        )

        for t in session.tests:
            conn.execute(
                """
                INSERT INTO tests (session_id, dut, name, status, duration)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    session.session_id,
                    session.dut,
                    t.name,
                    t.status,
                    t.duration,
                ),
            )


def _write_summary_metadata(
    conn: sqlite3.Connection,
    summary: OverallSummary,
    extras: ExtraMetrics,
) -> None:
    # We keep a single row with id=1 to store overall metadata.
    conn.execute("DELETE FROM summary;")
    conn.execute(
        """
        INSERT INTO summary (
            id,
            total_tests,
            total_passed,
            total_failed,
            total_skipped,
            total_duration,
            avg_duration,
            overall_pass_rate,
            unique_test_names
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            1,
            summary.total_tests,
            summary.total_passed,
            summary.total_failed,
            summary.total_skipped,
            summary.total_duration,
            summary.avg_duration,
            summary.overall_pass_rate,
            extras.unique_test_names,
        ),
    )