from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import TestSession, TestResult


def load_sessions_from_json(path: str | Path) -> List[TestSession]:
    """
    Load test sessions from a JSON file.

    The JSON is expected to follow the structure given in the assignment.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    raw = json.loads(text)

    sessions: List[TestSession] = []
    for obj in raw:
        tests = []
        for t in obj.get("tests", []):
            name = str(t.get("name", "unknown"))
            status = str(t.get("status", "skipped")).lower()
            duration = float(t.get("duration", 0.0))
            tests.append(TestResult(name=name, status=status, duration=duration))

        sessions.append(
            TestSession(
                dut=str(obj.get("dut", "unknown")),
                session_id=str(obj.get("session_id", "")),
                tests=tests,
            )
        )
    return sessions