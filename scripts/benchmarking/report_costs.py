#!/usr/bin/env python3
"""
Print a Markdown cost report from benchmark result directories.

This is a compatibility wrapper around :mod:`ote_cli.stats`; the CLI offers the
same report through ``ote stats`` with Markdown, JSON, and CSV output.

Usage: python3 scripts/benchmarking/report_costs.py [--results DIR]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/ote_cli"))

from ote_cli import stats  # noqa: E402 - the package path is added above


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results",
        type=Path,
        default=ROOT / "benchmarks/results",
        help="directory containing run result directories",
    )
    args = parser.parse_args()
    runs = stats.load_runs([args.results])
    print(stats.render_markdown(runs), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
