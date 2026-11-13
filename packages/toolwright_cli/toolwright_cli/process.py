"""
Subprocess helpers used by the ``toolwright`` commands.

Public API: :func:`run_command`, :func:`capture_command`, :func:`git_commit`, :func:`git_remote`,
and :func:`git_remote_head`.

Side effects: runs external commands with the caller-provided arguments.
"""
from __future__ import annotations
from .process_strings import (
    EMPTY_STRING,
    FLAG_PORCELAIN,
    KEY_GIT,
    KEY_ORIGIN,
    KEY_REMOTE,
    KEY_STATUS,
    TEXT_C,
    TEXT_COMMAND_NOT_FOUND,
    TEXT_COMMAND_TIMED_OUT_AFTER_S,
    TEXT_GET_URL,
    TEXT_HEAD,
    TEXT_LS_REMOTE,
    TEXT_REV_PARSE,
)

import subprocess
from pathlib import Path


def run_command(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=check,
        timeout=600,
    )


def capture_command(
    args: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 600,
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
            timeout=timeout,
            env=env,
        )
    except FileNotFoundError:
        return 127, EMPTY_STRING, TEXT_COMMAND_NOT_FOUND.format(args[0])
    except subprocess.TimeoutExpired:
        return 124, EMPTY_STRING, TEXT_COMMAND_TIMED_OUT_AFTER_S.format(timeout, args[0])
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def git_commit(root: Path) -> str | None:
    code, stdout, _ = capture_command([KEY_GIT, TEXT_C, str(root), TEXT_REV_PARSE, TEXT_HEAD])
    return stdout if code == 0 and stdout else None


def git_remote(root: Path) -> str | None:
    code, stdout, _ = capture_command([KEY_GIT, TEXT_C, str(root), KEY_REMOTE, TEXT_GET_URL, KEY_ORIGIN])
    return stdout if code == 0 and stdout else None


def git_remote_head(url: str) -> str | None:
    code, stdout, _ = capture_command([KEY_GIT, TEXT_LS_REMOTE, url, TEXT_HEAD])
    if code != 0 or not stdout:
        return None
    return stdout.split()[0]


def git_dirty(root: Path) -> bool:
    code, stdout, _ = capture_command([KEY_GIT, TEXT_C, str(root), KEY_STATUS, FLAG_PORCELAIN])
    return code == 0 and bool(stdout)
