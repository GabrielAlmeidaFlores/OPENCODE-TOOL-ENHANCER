"""
Repository and target path resolution for the ``toolwright`` command line.

Public API: :class:`ToolWrightError`, :func:`find_repo_root`, :func:`resolve_target`,
and the path helpers for lock, state, and backup files.

Side effects: none. All functions only read directory metadata.
"""
from __future__ import annotations
from .paths_strings import (
    KEY_BACKUPS,
    STATE_DIR_NAME,
    TEXT_AGENTS_COORDINATOR_AGENT_MD,
    TEXT_CANNOT_LOCATE_THE_TOOLWRIGHT_REPOSITORY_RUN_FROM_A_CHECKOUT_,
    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
    TEXT_STATE_JSON,
    TEXT_TOOLWRIGHT_LOCK_JSON,
    TEXT_TOOLWRIGHT_REPO,
    TEXT_TOOLWRIGHT_REPO_DOES_NOT_POINT_TO_A_REPOSITORY_ROOT,
    TEXT_VERSION,
)

import os
from pathlib import Path

_MARKERS = (TEXT_VERSION, TEXT_AGENTS_COORDINATOR_AGENT_MD, TEXT_SCRIPTS_INSTALLATION_INSTALL_SH)
_BUNDLED_ROOT = Path(__file__).resolve().parents[3]


class ToolWrightError(Exception):

    def __init__(self, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def is_repository_root(path: Path) -> bool:
    return all((path / marker).exists() for marker in _MARKERS)


def find_repo_root(start: Path | None = None) -> Path:
    explicit = os.environ.get(TEXT_TOOLWRIGHT_REPO)
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if is_repository_root(candidate):
            return candidate
        raise ToolWrightError(TEXT_TOOLWRIGHT_REPO_DOES_NOT_POINT_TO_A_REPOSITORY_ROOT.format(candidate))
    origin = (start or Path.cwd()).resolve()
    for candidate in (origin, *origin.parents):
        if is_repository_root(candidate):
            return candidate
    if is_repository_root(_BUNDLED_ROOT):
        return _BUNDLED_ROOT
    raise ToolWrightError(
        TEXT_CANNOT_LOCATE_THE_TOOLWRIGHT_REPOSITORY_RUN_FROM_A_CHECKOUT_
    )


def resolve_target(explicit: str | None) -> Path:
    target = Path(explicit).expanduser() if explicit else Path.cwd()
    return target.resolve()


def lock_path(target: Path) -> Path:
    return target / TEXT_TOOLWRIGHT_LOCK_JSON


def state_path(target: Path) -> Path:
    return target / STATE_DIR_NAME / TEXT_STATE_JSON


def backup_root(target: Path) -> Path:
    return target / STATE_DIR_NAME / KEY_BACKUPS


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True
