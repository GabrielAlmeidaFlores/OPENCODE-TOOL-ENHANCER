#!/usr/bin/env python3
"""
Print a Markdown cost report from benchmark result directories.

This is a compatibility wrapper around :mod:`toolwright_cli.stats`; the CLI offers the
same report through ``toolwright stats`` with Markdown, JSON, and CSV output.

Usage: python3 scripts/benchmarking/report_costs.py [--results DIR]
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.python_strings import (
    EMPTY_STRING,
    TEXT_MAIN,
)

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / TEXT_PACKAGES_TOOLWRIGHT_CLI))

from toolwright_cli import stats  # noqa: E402 - the package path is added above

FLAG_RESULTS = '--results'
TEXT_BENCHMARKS_RESULTS = 'benchmarks/results'
TEXT_DIRECTORY_CONTAINING_RUN_RESULT_DIRECTORIES = 'directory containing run result directories'
TEXT_PACKAGES_TOOLWRIGHT_CLI = 'packages/toolwright_cli'



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        FLAG_RESULTS,
        type=Path,
        default=ROOT / TEXT_BENCHMARKS_RESULTS,
        help=TEXT_DIRECTORY_CONTAINING_RUN_RESULT_DIRECTORIES,
    )
    args = parser.parse_args()
    runs = stats.load_runs([args.results])
    print(stats.render_markdown(runs), end=EMPTY_STRING)
    return 0


if __name__ == TEXT_MAIN:
    raise SystemExit(main())
