#!/usr/bin/env python3
"""
Verify that the repository version and package version agree.

Usage: python3 scripts/release/check_version.py [--root DIR] [--tag TAG]
Options: --root checks another checkout; --tag also requires v<VERSION>.
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tag")
    args = parser.parse_args()
    root = args.root.resolve()
    version_file = root / "VERSION"
    project_file = root / "packages/ote_cli/pyproject.toml"
    if not version_file.is_file() or not project_file.is_file():
        print("VERSION or pyproject.toml is missing", file=sys.stderr)
        return 2
    version = version_file.read_text(encoding="utf-8").strip()
    if not SEMVER.match(version):
        print(f"VERSION is not semantic: {version}", file=sys.stderr)
        return 2
    with project_file.open("rb") as handle:
        project_version = tomllib.load(handle)["project"]["version"]
    if project_version != version:
        print(f"version mismatch: VERSION={version} pyproject={project_version}", file=sys.stderr)
        return 1
    if args.tag and args.tag != f"v{version}":
        print(f"tag mismatch: tag={args.tag} expected=v{version}", file=sys.stderr)
        return 1
    print(f"version ok: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
