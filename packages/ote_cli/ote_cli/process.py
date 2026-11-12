"""
Subprocess helpers used by the ``ote`` commands.

Public API: :func:`run`, :func:`capture`, :func:`git_commit`, :func:`git_remote`,
and :func:`git_remote_head`.

Side effects: runs external commands with the caller-provided arguments.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def run(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """
    Run a command and return the completed process.
    """
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=check,
        timeout=600,
    )


def capture(
    args: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """
    Run a command and return its exit code, standard output, and standard error.

    A missing executable or a timeout is reported like a normal failure instead
    of raising, so diagnostics can continue after a missing dependency.
    """
    try:
        process = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
            env=env,
        )
    except FileNotFoundError:
        return 127, "", f"command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"command timed out after 600s: {args[0]}"
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def git_commit(root: Path) -> str | None:
    """
    Return the current commit for a repository, or None when unavailable.
    """
    code, stdout, _ = capture(["git", "-C", str(root), "rev-parse", "HEAD"])
    return stdout if code == 0 and stdout else None


def git_remote(root: Path) -> str | None:
    """
    Return the origin URL for a repository, or None when unavailable.
    """
    code, stdout, _ = capture(["git", "-C", str(root), "remote", "get-url", "origin"])
    return stdout if code == 0 and stdout else None


def git_remote_head(url: str) -> str | None:
    """
    Query the remote HEAD commit without modifying the local repository.
    """
    code, stdout, _ = capture(["git", "ls-remote", url, "HEAD"])
    if code != 0 or not stdout:
        return None
    return stdout.split()[0]


def git_dirty(root: Path) -> bool:
    """
    Return True when the repository has uncommitted changes.
    """
    code, stdout, _ = capture(["git", "-C", str(root), "status", "--porcelain"])
    return code == 0 and bool(stdout)
