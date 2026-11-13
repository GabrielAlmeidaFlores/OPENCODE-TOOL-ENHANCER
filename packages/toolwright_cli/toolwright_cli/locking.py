"""
Installation lock file handling.

Public API: :class:`PlannedFile`, :func:`sha256_file`, :func:`read_lock`,
:func:`write_json`, :func:`build_lock`, and :func:`lock_drift`.

Side effects: :func:`write_json` writes the requested path atomically.

Module constants: ``SCHEMA_VERSION`` is the supported lock schema.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class PlannedFile:

    source: Path
    destination: Path
    component: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    )
    try:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    finally:
        handle.close()
    os.replace(handle.name, path)


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def read_lock(path: Path) -> dict[str, Any] | None:
    data = read_json(path)
    if data is None:
        return None
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{path}: unsupported lock schema_version {data.get('schema_version')}")
    if not isinstance(data.get("files"), list):
        raise ValueError(f"{path}: lock file has no files list")
    return data


def build_lock(
    root: Path,
    target: Path,
    profile: str,
    components: list[str],
    planned: list[PlannedFile],
    source: dict[str, str],
) -> dict[str, Any]:
    files: list[dict[str, str]] = []
    for item in planned:
        if not item.destination.is_file():
            raise FileNotFoundError(f"planned destination missing after install: {item.destination}")
        files.append(
            {
                "path": item.destination.relative_to(target).as_posix(),
                "source": item.source.relative_to(root).as_posix(),
                "component": item.component,
                "sha256": sha256_file(item.destination),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profile": profile,
        "components": components,
        "source": source,
        "files": sorted(files, key=lambda entry: entry["path"]),
    }


def lock_drift(lock: dict[str, Any], target: Path) -> list[dict[str, str]]:
    drift: list[dict[str, str]] = []
    for entry in lock.get("files", []):
        relative = entry.get("path", "")
        expected = entry.get("sha256", "")
        path = target / relative
        if not path.is_file():
            drift.append({"path": relative, "status": "missing"})
            continue
        if sha256_file(path) != expected:
            drift.append({"path": relative, "status": "modified"})
    return drift
