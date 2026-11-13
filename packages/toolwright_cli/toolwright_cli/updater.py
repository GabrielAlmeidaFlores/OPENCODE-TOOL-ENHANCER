"""
Update checks for an installed target project.

Public API: :func:`check_for_updates`.

Side effects: reads the lock and local files. Network access happens only when
``remote=True`` and uses ``git ls-remote`` without modifying the repository.
"""
from __future__ import annotations
from .updater_strings import (
    DEFAULT_COMMIT,
    EMPTY_STRING,
    KEY_AVAILABLE_COMMIT,
    KEY_COMMIT,
    KEY_CURRENT,
    KEY_CURRENT_COMMIT,
    KEY_FILES_CHANGED,
    KEY_LOCK,
    KEY_LOCKED_COMMIT,
    KEY_MESSAGE,
    KEY_REMOTE_CHECKED,
    KEY_REPOSITORY,
    KEY_SOURCE,
    KEY_STATUS,
    STATUS_MODIFIED,
    TEXT_COULD_NOT_READ_THE_REMOTE_HEAD_CHECK_NETWORK_ACCESS,
    TEXT_MANAGED_FILE_S_DIFFER_FROM_THE_LOCK,
    TEXT_NO_LOCK,
    TEXT_NO_LOCK_FILE_AT_RUN_TOOLWRIGHT_INSTALL_APPLY_FIRST,
    TEXT_REMOTE_HEAD_IS_LOCK_IS,
    TEXT_SOURCE_ADVANCED_FROM_TO,
    TEXT_UPDATE_AVAILABLE,
    TEXT_UP_TO_DATE,
)

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
            KEY_STATUS: TEXT_NO_LOCK,
            KEY_MESSAGE: TEXT_NO_LOCK_FILE_AT_RUN_TOOLWRIGHT_INSTALL_APPLY_FIRST.format(path),
            KEY_LOCK: str(path),
        }

    source = lock.get(KEY_SOURCE, {})
    locked_commit = str(source.get(KEY_COMMIT, DEFAULT_COMMIT))
    current_commit = git_commit(root) or DEFAULT_COMMIT
    drift = lock_drift(lock, target)

    result: dict[str, Any] = {
        KEY_LOCK: str(path),
        KEY_LOCKED_COMMIT: locked_commit,
        KEY_CURRENT_COMMIT: current_commit,
        KEY_FILES_CHANGED: drift,
        KEY_REMOTE_CHECKED: False,
        KEY_AVAILABLE_COMMIT: None,
        KEY_STATUS: KEY_CURRENT,
    }

    if drift:
        result[KEY_STATUS] = STATUS_MODIFIED
        result[KEY_MESSAGE] = TEXT_MANAGED_FILE_S_DIFFER_FROM_THE_LOCK.format(len(drift))
        return result

    if locked_commit != current_commit:
        result[KEY_STATUS] = TEXT_UPDATE_AVAILABLE
        result[KEY_MESSAGE] = TEXT_SOURCE_ADVANCED_FROM_TO.format(locked_commit[:12], current_commit[:12])
        return result

    if remote:
        repository = str(source.get(KEY_REPOSITORY, EMPTY_STRING))
        available = git_remote_head(repository) if repository else None
        result[KEY_REMOTE_CHECKED] = True
        result[KEY_AVAILABLE_COMMIT] = available
        if available and available != locked_commit:
            result[KEY_STATUS] = TEXT_UPDATE_AVAILABLE
            result[KEY_MESSAGE] = TEXT_REMOTE_HEAD_IS_LOCK_IS.format(available[:12], locked_commit[:12])
            return result
        if available is None:
            result[KEY_STATUS] = DEFAULT_COMMIT
            result[KEY_MESSAGE] = TEXT_COULD_NOT_READ_THE_REMOTE_HEAD_CHECK_NETWORK_ACCESS
            return result

    result[KEY_MESSAGE] = TEXT_UP_TO_DATE
    return result
