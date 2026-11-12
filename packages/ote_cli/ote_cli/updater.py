"""
Update checks for an installed target project.

Public API: :func:`check_for_updates`.

Side effects: reads the lock and local files. Network access happens only when
``remote=True`` and uses ``git ls-remote`` without modifying the repository.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .locking import lock_drift, read_lock
from .paths import lock_path
from .process import git_commit, git_remote_head


def check_for_updates(root: Path, target: Path, remote: bool = False) -> dict[str, Any]:
    path = lock_path(target)
    lock = read_lock(path)
    if lock is None:
        return {
            "status": "no-lock",
            "message": f"no lock file at {path}; run 'ote install --apply' first",
            "lock": str(path),
        }

    source = lock.get("source", {})
    locked_commit = str(source.get("commit", "unknown"))
    current_commit = git_commit(root) or "unknown"
    drift = lock_drift(lock, target)

    result: dict[str, Any] = {
        "lock": str(path),
        "locked_commit": locked_commit,
        "current_commit": current_commit,
        "files_changed": drift,
        "remote_checked": False,
        "available_commit": None,
        "status": "current",
    }

    if drift:
        result["status"] = "modified"
        result["message"] = f"{len(drift)} managed file(s) differ from the lock"
        return result

    if locked_commit != current_commit:
        result["status"] = "update-available"
        result["message"] = f"source advanced from {locked_commit[:12]} to {current_commit[:12]}"
        return result

    if remote:
        repository = str(source.get("repository", ""))
        available = git_remote_head(repository) if repository else None
        result["remote_checked"] = True
        result["available_commit"] = available
        if available and available != locked_commit:
            result["status"] = "update-available"
            result["message"] = f"remote HEAD is {available[:12]}, lock is {locked_commit[:12]}"
            return result
        if available is None:
            result["status"] = "unknown"
            result["message"] = "could not read the remote HEAD; check network access"
            return result

    result["message"] = "up to date"
    return result
