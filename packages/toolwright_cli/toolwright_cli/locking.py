"""
Installation lock file handling.

Public API: :class:`PlannedFile`, :func:`sha256_file`, :func:`read_lock`,
:func:`write_json`, :func:`build_lock`, and :func:`lock_drift`.

Side effects: :func:`write_json` writes the requested path atomically.

Module constants: ``SCHEMA_VERSION`` is the supported lock schema.
"""
from __future__ import annotations
from .constants import GENERATOR_COPY as DEFAULT_GENERATOR
from .constants import TEXT_TEXT_3_3 as TEMPFILE_PREFIX
from .constants import ISO_TIMESPEC

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .constants import (
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    NEWLINE,
    STATUS_FAIL,
    STATUS_MISSING,
    STATUS_MODIFIED,
    STATUS_NEW,
    STATUS_OK,
    STATUS_UNCHANGED,
    STATUS_UPDATED,
    OPERATION_INSTALL,
    OPERATION_UNINSTALL,
    FLAG_APPLY,
    FLAG_CLEAN,
    FLAG_DRY_RUN,
    FLAG_FORCE,
    FLAG_ONLY,
    FLAG_PROFILE,
    FLAG_TARGET,
    FLAG_TYPE,
    FLAG_YES,
    KEY_ADAPTER,
    KEY_ADAPTERS,
    KEY_APPLIED,
    KEY_ARCHIVES,
    KEY_ARTIFACTS,
    KEY_BACKUP,
    KEY_COMMIT,
    KEY_COMPONENT,
    KEY_COMPONENTS,
    KEY_CREATED,
    KEY_CURRENT,
    KEY_DETAIL,
    KEY_DIGEST,
    KEY_DIRTY,
    KEY_FAILURES,
    KEY_FEATURE,
    KEY_FILES,
    KEY_GENERATOR,
    KEY_ID,
    KEY_LAST_OPERATION,
    KEY_LOCK,
    KEY_MESSAGE,
    KEY_NAME,
    KEY_OUTPUT,
    KEY_PATH,
    KEY_PLANNED,
    KEY_PROFILE,
    KEY_PURGED,
    KEY_REMOVABLE,
    KEY_REPOSITORY,
    KEY_RESULTS,
    KEY_SCHEMA_VERSION,
    KEY_SHA256,
    KEY_SKIPPED,
    KEY_SOURCE,
    KEY_STATUS,
    KEY_SUMMARY,
    KEY_TARGET,
    KEY_TITLE,
    KEY_TYPE,
    KEY_UPDATED,
    KEY_VERSION,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
)

SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1
DEFAULT_ADAPTERS = (DEFAULT_ADAPTER,)
DEFAULT_COMPONENTS: list[str] = []

READ_MODE_BINARY = "rb"
WRITE_MODE = "w"



MESSAGE_JSON_OBJECT = " must contain a JSON object"
MESSAGE_NO_ADAPTERS = ": lock file has no adapters list"
MESSAGE_INVALID_ADAPTER = ": adapter entry must be an object"
MESSAGE_ADAPTER_NAME = ": adapter entry has no string name"
MESSAGE_ADAPTER_COMPONENTS = ": adapter components must be a list of strings"
MESSAGE_INVALID_FILE = ": file entry must be an object"
MESSAGE_FILE_PATH = ": file entry has no string path"
MESSAGE_NO_FILES = ": lock file has no files list"
MESSAGE_UNSUPPORTED_SCHEMA = ": unsupported lock schema_version "
MESSAGE_MISSING_DESTINATION = "planned destination missing after install: "


@dataclass(frozen=True)
class PlannedFile:

    source: Path
    destination: Path
    component: str
    adapter: str = DEFAULT_ADAPTER
    generator: str = DEFAULT_GENERATOR
    content: str | None = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open(READ_MODE_BINARY) as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode(ENCODING_UTF8)).hexdigest()


def planned_sha256(item: PlannedFile) -> str:
    return sha256_text(item.content) if item.content is not None else sha256_file(item.source)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        WRITE_MODE,
        encoding=ENCODING_UTF8,
        dir=path.parent,
        prefix=f"{TEMPFILE_PREFIX}{path.name}{TEMPFILE_PREFIX}",
        delete=False,
    )
    try:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write(NEWLINE)
        handle.flush()
        os.fsync(handle.fileno())
    finally:
        handle.close()
    os.replace(handle.name, path)


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open(encoding=ENCODING_UTF8) as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}{MESSAGE_JSON_OBJECT}")
    return data


def _normalize_version_one(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    files = []
    for entry in data[KEY_FILES]:
        normalized = dict(entry)
        normalized.setdefault(KEY_ADAPTER, DEFAULT_ADAPTER)
        normalized.setdefault(KEY_GENERATOR, DEFAULT_GENERATOR)
        files.append(normalized)
    return {
        KEY_SCHEMA_VERSION: SCHEMA_VERSION,
        KEY_ADAPTERS: [
            {
                KEY_NAME: DEFAULT_ADAPTER,
                KEY_PROFILE: data.get(KEY_PROFILE),
                KEY_COMPONENTS: data.get(KEY_COMPONENTS, DEFAULT_COMPONENTS),
            }
        ],
        KEY_SOURCE: data.get(KEY_SOURCE, {}),
        KEY_FILES: files,
    }


def read_lock(path: Path) -> dict[str, Any] | None:
    data = read_json(path)
    if data is None:
        return None
    version = data.get(KEY_SCHEMA_VERSION)
    if version not in (LEGACY_SCHEMA_VERSION, SCHEMA_VERSION):
        raise ValueError(f"{path}{MESSAGE_UNSUPPORTED_SCHEMA}{version}")
    if not isinstance(data.get(KEY_FILES), list):
        raise ValueError(f"{path}{MESSAGE_NO_FILES}")
    if version == LEGACY_SCHEMA_VERSION:
        return _normalize_version_one(path, data)
    adapters = data.get(KEY_ADAPTERS)
    if not isinstance(adapters, list):
        raise ValueError(f"{path}{MESSAGE_NO_ADAPTERS}")
    for entry in adapters:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}{MESSAGE_INVALID_ADAPTER}")
        if not isinstance(entry.get(KEY_NAME), str) or not entry[KEY_NAME]:
            raise ValueError(f"{path}{MESSAGE_ADAPTER_NAME}")
        components = entry.get(KEY_COMPONENTS, [])
        if not isinstance(components, list) or not all(isinstance(item, str) for item in components):
            raise ValueError(f"{path}{MESSAGE_ADAPTER_COMPONENTS}")
    for entry in data[KEY_FILES]:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}{MESSAGE_INVALID_FILE}")
        if not isinstance(entry.get(KEY_PATH), str):
            raise ValueError(f"{path}{MESSAGE_FILE_PATH}")
    return data


def build_lock(
    root: Path,
    target: Path,
    profile: str,
    components: list[str],
    planned: list[PlannedFile],
    source: dict[str, str],
    adapter: str = DEFAULT_ADAPTER,
) -> dict[str, Any]:
    files: list[dict[str, str]] = []
    for item in planned:
        if not item.destination.is_file():
            raise FileNotFoundError(f"{MESSAGE_MISSING_DESTINATION}{item.destination}")
        files.append(
            {
                KEY_PATH: item.destination.relative_to(target).as_posix(),
                KEY_SOURCE: item.source.relative_to(root).as_posix(),
                KEY_COMPONENT: item.component,
                KEY_ADAPTER: item.adapter,
                KEY_GENERATOR: item.generator,
                KEY_SHA256: sha256_file(item.destination),
            }
        )
    return {
        KEY_SCHEMA_VERSION: SCHEMA_VERSION,
        KEY_CREATED: datetime.now(timezone.utc).isoformat(timespec=ISO_TIMESPEC),
        KEY_ADAPTERS: [{KEY_NAME: adapter, KEY_PROFILE: profile, KEY_COMPONENTS: components}],
        KEY_SOURCE: source,
        KEY_FILES: sorted(files, key=lambda entry: entry[KEY_PATH]),
    }


def merge_lock(existing: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    if existing is None:
        return new
    new_names = {entry[KEY_NAME] for entry in new.get(KEY_ADAPTERS, [])}
    adapters = [
        entry for entry in existing.get(KEY_ADAPTERS, [])
        if entry.get(KEY_NAME) not in new_names
    ] + list(new.get(KEY_ADAPTERS, []))
    files = [
        entry for entry in existing.get(KEY_FILES, [])
        if entry.get(KEY_ADAPTER) not in new_names
    ] + list(new.get(KEY_FILES, []))
    merged = dict(new)
    merged[KEY_ADAPTERS] = sorted(adapters, key=lambda entry: entry.get(KEY_NAME, EMPTY_STRING))
    merged[KEY_FILES] = sorted(files, key=lambda entry: entry.get(KEY_PATH, EMPTY_STRING))
    return merged


def set_adapter_digest(lock: dict[str, Any], adapter: str, digest: str) -> None:
    for entry in lock.get(KEY_ADAPTERS, []):
        if entry.get(KEY_NAME) == adapter:
            entry[KEY_DIGEST] = digest
            return


def lock_drift(lock: dict[str, Any], target: Path) -> list[dict[str, str]]:
    drift: list[dict[str, str]] = []
    for entry in lock.get(KEY_FILES, []):
        relative = entry.get(KEY_PATH, EMPTY_STRING)
        expected = entry.get(KEY_SHA256, EMPTY_STRING)
        path = target / relative
        if not path.is_file():
            drift.append({KEY_PATH: relative, KEY_STATUS: STATUS_MISSING})
            continue
        if sha256_file(path) != expected:
            drift.append({KEY_PATH: relative, KEY_STATUS: STATUS_MODIFIED})
    return drift
