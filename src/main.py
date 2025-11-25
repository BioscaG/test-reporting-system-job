from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .parser import load_sessions_from_json
from .aggregator import aggregate_overall
from .report import write_summary_json, write_per_dut_csv, write_html_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate pytest sessions for multiple DUT configurations."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input JSON file containing test sessions.",
    )
    parser.add_argument(
        "--out-dir",
        "-o",
        default="out",
        help="Directory where reports will be written (default: out).",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="If set, also generate a simple HTML dashboard.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 2

    sessions = load_sessions_from_json(input_path)
    summary, extras = aggregate_overall(sessions)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_summary_json(summary, extras, out_dir / "summary.json")
    write_per_dut_csv(summary.per_dut, out_dir / "per_dut_summary.csv")

    if args.html:
        write_html_dashboard(summary, extras, out_dir / "dashboard.html")

    print(f"Reports generated in: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())