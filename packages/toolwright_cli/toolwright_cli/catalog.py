"""
Verified artifact catalog access and validation.

Public API: :func:`load_catalog`, :func:`search_catalog`, :func:`verify_catalog`,
:func:`build_catalog`, and :func:`check_catalog_drift`.

Side effects: reads ``catalog/registry.json`` and ``catalog/schema``. The build
and drift functions execute the generator script; the others are read-only.
"""
from __future__ import annotations
from .constants import STATUS_FAIL
from .catalog_strings import (
    EMPTY_STRING,
    ENCODING_UTF8,
    FLAG_CHECK,
    KEY_ARTIFACT,
    KEY_ARTIFACTS,
    KEY_AUTHOR,
    KEY_CHECK,
    KEY_COUNTS,
    KEY_DEFINITIONS,
    KEY_DETAIL,
    KEY_ENUM,
    KEY_EXIT_CODE,
    KEY_ID,
    KEY_LICENSE,
    KEY_LOCAL,
    KEY_OUTPUT,
    KEY_PROPERTIES,
    KEY_REQUIRED,
    KEY_SCHEMA_VERSION,
    KEY_SOURCE,
    KEY_STATUS,
    KEY_TYPE,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
    STATUS_OK,
    TEXT_1,
    TEXT_ARTIFACT,
    TEXT_ARTIFACTS_MUST_BE_A_LIST,
    TEXT_ARTIFACT_S,
    TEXT_ARTIFACT_S_VALIDATED,
    TEXT_CATALOG_BUILDER_NOT_FOUND_AT,
    TEXT_CATALOG_MUST_BE_A_JSON_OBJECT,
    TEXT_CATALOG_NOT_FOUND_AT_RUN_TOOLWRIGHT_CATALOG_BUILD,
    TEXT_CATALOG_REGISTRY_JSON,
    TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON,
    TEXT_CATALOG_SCHEMA_NOT_FOUND_AT,
    TEXT_DECLARED_ACTUAL,
    TEXT_DUPLICATE_ID_FOR_TYPE,
    TEXT_EXPECTED_1_FOUND,
    TEXT_INVALID_JSON,
    TEXT_LOCAL_PATH_MISSING,
    TEXT_MISSING,
    TEXT_SCRIPTS_CATALOG_BUILD_CATALOG_PY,
    TEXT_TEXT,
    TEXT_UNKNOWN_TYPE,
)

import json
import sys
from pathlib import Path
from typing import Any

from .paths import ToolWrightError
from .process import capture_command

CATALOG = Path(TEXT_CATALOG_REGISTRY_JSON)
SCHEMA = Path(TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON)
BUILDER = Path(TEXT_SCRIPTS_CATALOG_BUILD_CATALOG_PY)


def load_catalog(root: Path) -> dict[str, Any]:
    path = root / CATALOG
    if not path.is_file():
        raise ToolWrightError(TEXT_CATALOG_NOT_FOUND_AT_RUN_TOOLWRIGHT_CATALOG_BUILD.format(path))
    try:
        document = json.loads(path.read_text(encoding=ENCODING_UTF8))
    except json.JSONDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_JSON.format(path, error)) from error
    if not isinstance(document, dict):
        raise ToolWrightError(TEXT_CATALOG_MUST_BE_A_JSON_OBJECT.format(path))
    return document


def load_artifact_schema(root: Path) -> dict[str, Any]:
    path = root / SCHEMA
    if not path.is_file():
        raise ToolWrightError(TEXT_CATALOG_SCHEMA_NOT_FOUND_AT.format(path))
    try:
        schema = json.loads(path.read_text(encoding=ENCODING_UTF8))
    except json.JSONDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_JSON.format(path, error)) from error
    return schema.get(KEY_DEFINITIONS, {}).get(KEY_ARTIFACT, {})


def search_catalog(document: dict[str, Any], query: str) -> list[dict[str, Any]]:
    needle = query.strip().lower()
    if not needle:
        return []
    fields = (KEY_ID, KEY_TYPE, KEY_AUTHOR, KEY_LICENSE, KEY_SOURCE, KEY_LOCAL)
    matches = []
    for entry in document.get(KEY_ARTIFACTS, []):
        haystack = SEPARATOR_SPACE.join(str(entry.get(field, EMPTY_STRING)) for field in fields).lower()
        if needle in haystack:
            matches.append(entry)
    return matches


def verify_catalog(root: Path, document: dict[str, Any] | None = None) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    def record(check: str, status: str, detail: str) -> None:
        results.append({KEY_CHECK: check, KEY_STATUS: status, KEY_DETAIL: detail})

    document = document if document is not None else load_catalog(root)
    if document.get(KEY_SCHEMA_VERSION) != 1:
        record(KEY_SCHEMA_VERSION, STATUS_FAIL, TEXT_EXPECTED_1_FOUND.format(document.get(KEY_SCHEMA_VERSION)))
        return results
    record(KEY_SCHEMA_VERSION, STATUS_OK, TEXT_1)

    artifacts = document.get(KEY_ARTIFACTS)
    if not isinstance(artifacts, list):
        record(KEY_ARTIFACTS, STATUS_FAIL, TEXT_ARTIFACTS_MUST_BE_A_LIST)
        return results

    schema = load_artifact_schema(root)
    required = schema.get(KEY_REQUIRED, [])
    allowed_types = schema.get(KEY_PROPERTIES, {}).get(KEY_TYPE, {}).get(KEY_ENUM, [])
    seen: set[tuple[str, str]] = set()
    failures = 0
    counts: dict[str, int] = {}
    for entry in artifacts:
        identifier = str(entry.get(KEY_ID, TEXT_TEXT))
        missing = [field for field in required if not str(entry.get(field, EMPTY_STRING)).strip()]
        if missing:
            record(TEXT_ARTIFACT.format(identifier), STATUS_FAIL, TEXT_MISSING.format(SEPARATOR_COMMA_SPACE.join(missing)))
            failures += 1
            continue
        entry_type = str(entry.get(KEY_TYPE))
        if allowed_types and entry_type not in allowed_types:
            record(TEXT_ARTIFACT.format(identifier), STATUS_FAIL, TEXT_UNKNOWN_TYPE.format(entry_type))
            failures += 1
            continue
        key = (entry_type, identifier)
        if key in seen:
            record(TEXT_ARTIFACT.format(identifier), STATUS_FAIL, TEXT_DUPLICATE_ID_FOR_TYPE)
            failures += 1
            continue
        seen.add(key)
        if not (root / str(entry[KEY_LOCAL])).exists():
            record(TEXT_ARTIFACT.format(identifier), STATUS_FAIL, TEXT_LOCAL_PATH_MISSING.format(entry[KEY_LOCAL]))
            failures += 1
            continue
        counts[entry_type] = counts.get(entry_type, 0) + 1

    declared = document.get(KEY_COUNTS, {})
    if declared != dict(sorted(counts.items())):
        record(KEY_COUNTS, STATUS_FAIL, TEXT_DECLARED_ACTUAL.format(declared, dict(sorted(counts.items()))))
        failures += 1
    else:
        record(KEY_COUNTS, STATUS_OK, TEXT_ARTIFACT_S.format(len(artifacts)))

    if failures == 0:
        record(KEY_ARTIFACTS, STATUS_OK, TEXT_ARTIFACT_S_VALIDATED.format(len(artifacts)))
    return results


def run_catalog_builder(root: Path, check: bool) -> tuple[int, str]:
    command = [sys.executable, str(root / BUILDER)]
    if check:
        command.append(FLAG_CHECK)
    code, stdout, stderr = capture_command(command, cwd=root)
    return code, NEWLINE.join(part for part in (stdout, stderr) if part)


def build_catalog(root: Path, check: bool = False) -> dict[str, Any]:
    if not (root / BUILDER).is_file():
        raise ToolWrightError(TEXT_CATALOG_BUILDER_NOT_FOUND_AT.format(root / BUILDER))
    code, output = run_catalog_builder(root, check)
    return {KEY_STATUS: STATUS_OK if code == 0 else STATUS_FAIL, KEY_EXIT_CODE: code, KEY_OUTPUT: output}


def check_catalog_drift(root: Path) -> dict[str, Any]:
    return build_catalog(root, check=True)
