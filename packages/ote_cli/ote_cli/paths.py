"""
Repository and target path resolution for the ``ote`` command line.

Public API: :class:`OteError`, :func:`find_repo_root`, :func:`resolve_target`,
and the path helpers for lock, state, and backup files.

Side effects: none. All functions only read directory metadata.
"""
from __future__ import annotations

import os
from pathlib import Path

_MARKERS = ("VERSION", "agents/coordinator/AGENT.md", "scripts/installation/install.sh")
_BUNDLED_ROOT = Path(__file__).resolve().parents[3]


class OteError(Exception):
    """
    A user-facing error with a process exit code.
    """

    def __init__(self, message: str, exit_code: int = 2) -> None:
        """
        Create an error that the CLI prints without a traceback.
        """
        super().__init__(message)
        self.exit_code = exit_code


def _is_repo_root(path: Path) -> bool:
    """
    Return True when the directory contains the repository markers.
    """
    return all((path / marker).exists() for marker in _MARKERS)


def find_repo_root(start: Path | None = None) -> Path:
    """
    Locate the repository that provides the artifacts to install.
    """
    explicit = os.environ.get("OTE_REPO")
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if _is_repo_root(candidate):
            return candidate
        raise OteError(f"OTE_REPO does not point to a repository root: {candidate}")
    origin = (start or Path.cwd()).resolve()
    for candidate in (origin, *origin.parents):
        if _is_repo_root(candidate):
            return candidate
    if _is_repo_root(_BUNDLED_ROOT):
        return _BUNDLED_ROOT
    raise OteError(
        "cannot locate the OPENCODE-TOOL-ENHANCER repository; run from a checkout or set OTE_REPO"
    )


def resolve_target(explicit: str | None) -> Path:
    """
    Resolve the installation target directory without creating it.
    """
    target = Path(explicit).expanduser() if explicit else Path.cwd()
    return target.resolve()


def lock_path(target: Path) -> Path:
    """
    Return the lock file path for a target project.
    """
    return target / "ote.lock.json"


def state_path(target: Path) -> Path:
    """
    Return the CLI state file path for a target project.
    """
    return target / ".ote" / "state.json"


def backup_root(target: Path) -> Path:
    """
    Return the directory that holds CLI backups for a target project.
    """
    return target / ".ote" / "backups"


def is_within(path: Path, parent: Path) -> bool:
    """
    Return True when path resolves inside parent.
    """
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True
