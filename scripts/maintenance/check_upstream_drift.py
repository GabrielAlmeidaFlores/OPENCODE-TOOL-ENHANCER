#!/usr/bin/env python3
"""
Compare pinned upstream commits with the current remote HEAD.

Usage: python3 scripts/maintenance/check_upstream_drift.py [--registry FILE] [--offline] [--fail-on-drift] [--fail-on-unknown]
Options: --offline prints pins without network access; --fail-on-drift exits 1 on drift; --fail-on-unknown exits 1 on network errors.
Environment: Requires git; PyYAML is required to read the registry.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/provenance/registry.yml"


def load_sources(path: Path) -> dict[str, dict[str, str]]:
    try:
        import yaml
    except ImportError as error:
        raise SystemExit("PyYAML is required: python3 -m pip install pyyaml") from error
    with path.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    sources = document.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise SystemExit(f"{path}: missing sources")
    return sources


def remote_head(repository: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "ls-remote", repository, "HEAD"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.split()[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--fail-on-drift", action="store_true")
    parser.add_argument("--fail-on-unknown", action="store_true")
    args = parser.parse_args()
    sources = load_sources(args.registry.resolve())
    drifted = 0
    unknown = 0
    print("| Source | Pinned | Remote | Status |")
    print("| --- | --- | --- | --- |")
    for name, entry in sorted(sources.items()):
        repository = str(entry.get("repository", ""))
        pinned = str(entry.get("commit", ""))
        if not repository or not pinned:
            print(f"| {name} | missing | missing | invalid |")
            drifted += 1
            continue
        if args.offline:
            print(f"| {name} | {pinned[:12]} | skipped | offline |")
            continue
        head = remote_head(repository)
        if head is None:
            print(f"| {name} | {pinned[:12]} | unknown | network-error |")
            unknown += 1
            continue
        status = "current" if head == pinned else "drift"
        if status == "drift":
            drifted += 1
        print(f"| {name} | {pinned[:12]} | {head[:12]} | {status} |")
    print(f"\n{drifted} drifted, {unknown} unknown")
    if args.fail_on_drift and drifted:
        return 1
    if args.fail_on_unknown and unknown:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
