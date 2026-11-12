"""
Verified artifact catalog access and validation.

Public API: :func:`load_catalog`, :func:`search_catalog`, :func:`verify_catalog`,
:func:`build_catalog`, and :func:`check_catalog_drift`.

Side effects: reads ``catalog/registry.json`` and ``catalog/schema``. The build
and drift functions execute the generator script; the others are read-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .paths import OteError
from .process import capture_command

CATALOG = Path("catalog/registry.json")
SCHEMA = Path("catalog/schema/entry.schema.json")
BUILDER = Path("scripts/catalog/build_catalog.py")


def load_catalog(root: Path) -> dict[str, Any]:
    path = root / CATALOG
    if not path.is_file():
        raise OteError(f"catalog not found at {path}; run 'ote catalog build'")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise OteError(f"{path}: invalid JSON: {error}") from error
    if not isinstance(document, dict):
        raise OteError(f"{path}: catalog must be a JSON object")
    return document


def load_artifact_schema(root: Path) -> dict[str, Any]:
    path = root / SCHEMA
    if not path.is_file():
        raise OteError(f"catalog schema not found at {path}")
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise OteError(f"{path}: invalid JSON: {error}") from error
    return schema.get("definitions", {}).get("artifact", {})


def search_catalog(document: dict[str, Any], query: str) -> list[dict[str, Any]]:
    needle = query.strip().lower()
    if not needle:
        return []
    fields = ("id", "type", "author", "license", "source", "local")
    matches = []
    for entry in document.get("artifacts", []):
        haystack = " ".join(str(entry.get(field, "")) for field in fields).lower()
        if needle in haystack:
            matches.append(entry)
    return matches


def verify_catalog(root: Path, document: dict[str, Any] | None = None) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    def record(check: str, status: str, detail: str) -> None:
        results.append({"check": check, "status": status, "detail": detail})

    document = document if document is not None else load_catalog(root)
    if document.get("schema_version") != 1:
        record("schema_version", "fail", f"expected 1, found {document.get('schema_version')}")
        return results
    record("schema_version", "ok", "1")

    artifacts = document.get("artifacts")
    if not isinstance(artifacts, list):
        record("artifacts", "fail", "artifacts must be a list")
        return results

    schema = load_artifact_schema(root)
    required = schema.get("required", [])
    allowed_types = schema.get("properties", {}).get("type", {}).get("enum", [])
    seen: set[tuple[str, str]] = set()
    failures = 0
    counts: dict[str, int] = {}
    for entry in artifacts:
        identifier = str(entry.get("id", "?"))
        missing = [field for field in required if not str(entry.get(field, "")).strip()]
        if missing:
            record(f"artifact:{identifier}", "fail", f"missing {', '.join(missing)}")
            failures += 1
            continue
        entry_type = str(entry.get("type"))
        if allowed_types and entry_type not in allowed_types:
            record(f"artifact:{identifier}", "fail", f"unknown type {entry_type}")
            failures += 1
            continue
        key = (entry_type, identifier)
        if key in seen:
            record(f"artifact:{identifier}", "fail", "duplicate id for type")
            failures += 1
            continue
        seen.add(key)
        if not (root / str(entry["local"])).exists():
            record(f"artifact:{identifier}", "fail", f"local path missing: {entry['local']}")
            failures += 1
            continue
        counts[entry_type] = counts.get(entry_type, 0) + 1

    declared = document.get("counts", {})
    if declared != dict(sorted(counts.items())):
        record("counts", "fail", f"declared {declared}, actual {dict(sorted(counts.items()))}")
        failures += 1
    else:
        record("counts", "ok", f"{len(artifacts)} artifact(s)")

    if failures == 0:
        record("artifacts", "ok", f"{len(artifacts)} artifact(s) validated")
    return results


def run_catalog_builder(root: Path, check: bool) -> tuple[int, str]:
    command = [sys.executable, str(root / BUILDER)]
    if check:
        command.append("--check")
    code, stdout, stderr = capture_command(command, cwd=root)
    return code, "\n".join(part for part in (stdout, stderr) if part)


def build_catalog(root: Path, check: bool = False) -> dict[str, Any]:
    if not (root / BUILDER).is_file():
        raise OteError(f"catalog builder not found at {root / BUILDER}")
    code, output = run_catalog_builder(root, check)
    return {"status": "ok" if code == 0 else "fail", "exit_code": code, "output": output}


def check_catalog_drift(root: Path) -> dict[str, Any]:
    return build_catalog(root, check=True)
