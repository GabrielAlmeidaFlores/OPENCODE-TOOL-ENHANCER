#!/usr/bin/env python3
"""
Compare pinned upstream commits with the current remote HEAD.

Usage: python3 scripts/maintenance/check_upstream_drift.py [--registry FILE] [--offline] [--fail-on-drift] [--fail-on-unknown]
Options: --offline prints pins without network access; --fail-on-drift exits 1 on drift; --fail-on-unknown exits 1 on network errors.
Environment: Requires git; PyYAML is required to read the registry.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.python_strings import (
    EMPTY_STRING,
    KEY_STORE_TRUE,
    TEXT_DOCS_PROVENANCE_REGISTRY_YML,
    TEXT_HEAD,
    TEXT_MAIN,
    TEXT_UTF_8,
)

import argparse
import subprocess
import sys
from pathlib import Path

FLAG_FAIL_ON_DRIFT = '--fail-on-drift'
FLAG_FAIL_ON_UNKNOWN = '--fail-on-unknown'
FLAG_OFFLINE = '--offline'
FLAG_REGISTRY = '--registry'
KEY_COMMIT = 'commit'
KEY_CURRENT = 'current'
KEY_DRIFT = 'drift'
KEY_GIT = 'git'
KEY_REPOSITORY = 'repository'
KEY_SOURCES = 'sources'
TEXT_DRIFTED_UNKNOWN = '\n{} drifted, {} unknown'
TEXT_LS_REMOTE = 'ls-remote'
TEXT_MISSING_MISSING_INVALID = '| {} | missing | missing | invalid |'
TEXT_MISSING_SOURCES = '{}: missing sources'
TEXT_PYYAML_IS_REQUIRED_PYTHON3_M_PIP_INSTALL_PYYAML = 'PyYAML is required: python3 -m pip install pyyaml'
TEXT_SKIPPED_OFFLINE = '| {} | {} | skipped | offline |'
TEXT_SOURCE_PINNED_REMOTE_STATUS = '| Source | Pinned | Remote | Status |'
TEXT_TEXT = '| {} | {} | {} | {} |'
TEXT_TEXT_2 = '| --- | --- | --- | --- |'
TEXT_UNKNOWN_NETWORK_ERROR = '| {} | {} | unknown | network-error |'


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / TEXT_DOCS_PROVENANCE_REGISTRY_YML


def load_sources(path: Path) -> dict[str, dict[str, str]]:
    try:
        import yaml
    except ImportError as error:
        raise SystemExit(TEXT_PYYAML_IS_REQUIRED_PYTHON3_M_PIP_INSTALL_PYYAML) from error
    with path.open(encoding=TEXT_UTF_8) as handle:
        document = yaml.safe_load(handle)
    sources = document.get(KEY_SOURCES)
    if not isinstance(sources, dict) or not sources:
        raise SystemExit(TEXT_MISSING_SOURCES.format(path))
    return sources


def remote_head(repository: str) -> str | None:
    try:
        result = subprocess.run(
            [KEY_GIT, TEXT_LS_REMOTE, repository, TEXT_HEAD],
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
    parser.add_argument(FLAG_REGISTRY, type=Path, default=REGISTRY)
    parser.add_argument(FLAG_OFFLINE, action=KEY_STORE_TRUE)
    parser.add_argument(FLAG_FAIL_ON_DRIFT, action=KEY_STORE_TRUE)
    parser.add_argument(FLAG_FAIL_ON_UNKNOWN, action=KEY_STORE_TRUE)
    args = parser.parse_args()
    sources = load_sources(args.registry.resolve())
    drifted = 0
    unknown = 0
    print(TEXT_SOURCE_PINNED_REMOTE_STATUS)
    print(TEXT_TEXT_2)
    for name, entry in sorted(sources.items()):
        repository = str(entry.get(KEY_REPOSITORY, EMPTY_STRING))
        pinned = str(entry.get(KEY_COMMIT, EMPTY_STRING))
        if not repository or not pinned:
            print(TEXT_MISSING_MISSING_INVALID.format(name))
            drifted += 1
            continue
        if args.offline:
            print(TEXT_SKIPPED_OFFLINE.format(name, pinned[:12]))
            continue
        head = remote_head(repository)
        if head is None:
            print(TEXT_UNKNOWN_NETWORK_ERROR.format(name, pinned[:12]))
            unknown += 1
            continue
        status = KEY_CURRENT if head == pinned else KEY_DRIFT
        if status == KEY_DRIFT:
            drifted += 1
        print(TEXT_TEXT.format(name, pinned[:12], head[:12], status))
    print(TEXT_DRIFTED_UNKNOWN.format(drifted, unknown))
    if args.fail_on_drift and drifted:
        return 1
    if args.fail_on_unknown and unknown:
        return 1
    return 0


if __name__ == TEXT_MAIN:
    sys.exit(main())
