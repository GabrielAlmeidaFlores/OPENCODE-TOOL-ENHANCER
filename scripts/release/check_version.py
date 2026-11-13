#!/usr/bin/env python3
"""
Verify that the repository version and package version agree.

Usage: python3 scripts/release/check_version.py [--root DIR] [--tag TAG]
Options: --root checks another checkout; --tag also requires v<VERSION>.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.python_strings import (
    TEXT_MAIN,
    TEXT_PACKAGES_TOOLWRIGHT_CLI_PYPROJECT_TOML,
    TEXT_UTF_8,
    TEXT_VERSION,
)

import argparse
import re
import sys
import tomllib
from pathlib import Path

FLAG_ROOT = '--root'
FLAG_TAG = '--tag'
KEY_PROJECT = 'project'
KEY_RB = 'rb'
KEY_VERSION = 'version'
TEXT_D_D_D = '^\\d+\\.\\d+\\.\\d+$'
TEXT_TAG_MISMATCH_TAG_EXPECTED_V = 'tag mismatch: tag={} expected=v{}'
TEXT_V = 'v{}'
TEXT_VERSION_IS_NOT_SEMANTIC = 'VERSION is not semantic: {}'
TEXT_VERSION_MISMATCH_VERSION_PYPROJECT = 'version mismatch: VERSION={} pyproject={}'
TEXT_VERSION_OK = 'version ok: {}'
TEXT_VERSION_OR_PYPROJECT_TOML_IS_MISSING = 'VERSION or pyproject.toml is missing'


ROOT = Path(__file__).resolve().parents[2]
SEMVER = re.compile(TEXT_D_D_D)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(FLAG_ROOT, type=Path, default=ROOT)
    parser.add_argument(FLAG_TAG)
    args = parser.parse_args()
    root = args.root.resolve()
    version_file = root / TEXT_VERSION
    project_file = root / TEXT_PACKAGES_TOOLWRIGHT_CLI_PYPROJECT_TOML
    if not version_file.is_file() or not project_file.is_file():
        print(TEXT_VERSION_OR_PYPROJECT_TOML_IS_MISSING, file=sys.stderr)
        return 2
    version = version_file.read_text(encoding=TEXT_UTF_8).strip()
    if not SEMVER.match(version):
        print(TEXT_VERSION_IS_NOT_SEMANTIC.format(version), file=sys.stderr)
        return 2
    with project_file.open(KEY_RB) as handle:
        project_version = tomllib.load(handle)[KEY_PROJECT][KEY_VERSION]
    if project_version != version:
        print(TEXT_VERSION_MISMATCH_VERSION_PYPROJECT.format(version, project_version), file=sys.stderr)
        return 1
    if args.tag and args.tag != TEXT_V.format(version):
        print(TEXT_TAG_MISMATCH_TAG_EXPECTED_V.format(args.tag, version), file=sys.stderr)
        return 1
    print(TEXT_VERSION_OK.format(version))
    return 0


if __name__ == TEXT_MAIN:
    sys.exit(main())
