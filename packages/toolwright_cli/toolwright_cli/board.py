"""
Markdown task board with optional Git worktrees.

Public API: :func:`add_task`, :func:`list_tasks`, :func:`move_task`,
:func:`summary`, and :func:`manage_worktree`.

State lives in ``.toolwright/board/tasks`` as one Markdown file per task. The board
file is generated. Worktrees live under ``.toolwright/worktrees`` and are never
committed. This module never stages, commits, or merges.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import ToolwrightError
from .process import capture_command

STATUSES = ("backlog", "ready", "in-progress", "review", "done")
DEFAULT_WIP_LIMIT = 3
TASK_ROOT = Path(".toolwright/board/tasks")
BOARD = Path(".toolwright/board/BOARD.md")
WORKTREES = Path(".toolwright/worktrees")


@dataclass
class Task:
    identifier: str
    title: str
    status: str
    created: str
    worktree: str
    verify: str
    approved: bool
    path: Path


def _board_settings(root: Path) -> dict[str, int]:
    values = {"wip_limit": DEFAULT_WIP_LIMIT}
    config = root / ".toolwright/config.toml"
    if not config.is_file():
        return values
    try:
        data = tomllib.loads(config.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ToolwrightError(f"{config}: invalid TOML: {error}") from error
    section = data.get("board", {})
    if not isinstance(section, dict):
        raise ToolwrightError(f"{config}: board must be a table")
    value = section.get("wip_limit", values["wip_limit"])
    if not isinstance(value, int) or value <= 0:
        raise ToolwrightError(f"{config}: board.wip_limit must be a positive integer")
    values["wip_limit"] = value
    return values


def _parse(path: Path) -> Task:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ToolwrightError(f"{path}: missing frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ToolwrightError(f"{path}: unterminated frontmatter")
    metadata: dict[str, str] = {}
    for line in text[3:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip()
    required = ("id", "title", "status", "created")
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ToolwrightError(f"{path}: missing {', '.join(missing)}")
    if metadata["status"] not in STATUSES:
        raise ToolwrightError(f"{path}: unknown status {metadata['status']}")
    return Task(
        identifier=metadata["id"],
        title=metadata["title"],
        status=metadata["status"],
        created=metadata["created"],
        worktree=metadata.get("worktree", ""),
        verify=metadata.get("verify", ""),
        approved=metadata.get("approved", "false") == "true",
        path=path,
    )


def _tasks(root: Path) -> list[Task]:
    directory = root / TASK_ROOT
    if not directory.is_dir():
        return []
    return sorted((_parse(path) for path in directory.glob("*.md")), key=lambda task: task.identifier)


def _write(task: Task) -> None:
    task.path.write_text(
        "---\n"
        f"id: {task.identifier}\n"
        f"title: {task.title}\n"
        f"status: {task.status}\n"
        f"created: {task.created}\n"
        f"worktree: {task.worktree}\n"
        f"verify: {task.verify}\n"
        f"approved: {'true' if task.approved else 'false'}\n"
        "---\n\n"
        "Notes go here. Board state is the frontmatter; prose is free form.\n",
        encoding="utf-8",
    )


def _write_board(root: Path) -> None:
    tasks = _tasks(root)
    limit = _board_settings(root)["wip_limit"]
    in_progress = sum(1 for task in tasks if task.status == "in-progress")
    lines = [
        "# Task Board",
        "",
        f"WIP: {in_progress}/{limit}",
        "",
        "| ID | Title | Status | Worktree | Verify |",
        "| --- | --- | --- | --- | --- |",
    ]
    for task in tasks:
        lines.append(
            f"| {task.identifier} | {task.title} | {task.status} | "
            f"{task.worktree or '-'} | {task.verify or '-'} |"
        )
    lines.append("")
    target = root / BOARD
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")


def _next_identifier(root: Path) -> str:
    numbers = []
    for task in _tasks(root):
        try:
            numbers.append(int(task.identifier.removeprefix("T-")))
        except ValueError:
            continue
    return f"T-{max(numbers, default=0) + 1:03d}"


def add_task(root: Path, title: str, worktree: bool = False, verify: str = "") -> Task:
    value = title.strip()
    if not value:
        raise ToolwrightError("task title is required")
    if "\n" in value or "\r" in value or value == "---":
        raise ToolwrightError("task title must be a single line")
    if "\n" in verify or "\r" in verify or verify.strip() == "---":
        raise ToolwrightError("verification command must be a single line")
    directory = root / TASK_ROOT
    directory.mkdir(parents=True, exist_ok=True)
    identifier = _next_identifier(root)
    task = Task(
        identifier=identifier,
        title=value,
        status="backlog",
        created=datetime.now(timezone.utc).date().isoformat(),
        worktree="",
        verify=verify.strip(),
        approved=False,
        path=directory / f"{identifier}.md",
    )
    _write(task)
    _write_board(root)
    if worktree:
        return manage_worktree(root, identifier, remove=False, force=False)
    return task


def list_tasks(root: Path, status: str | None = None) -> list[Task]:
    if status and status not in STATUSES:
        raise ToolwrightError(f"unknown status: {status}")
    return [task for task in _tasks(root) if not status or task.status == status]


def move_task(root: Path, identifier: str, status: str, approved: bool = False) -> Task:
    if status not in STATUSES:
        raise ToolwrightError(f"unknown status: {status}")
    tasks = _tasks(root)
    task = next((item for item in tasks if item.identifier == identifier), None)
    if task is None:
        raise ToolwrightError(f"unknown task: {identifier}")
    if status == "in-progress":
        limit = _board_settings(root)["wip_limit"]
        current = sum(1 for item in tasks if item.status == "in-progress" and item.identifier != identifier)
        if current >= limit:
            raise ToolwrightError(f"WIP limit reached: {current}/{limit}")
    if status == "done" and not approved:
        raise ToolwrightError("moving a task to done requires --approved")
    task.status = status
    if status == "done":
        task.approved = True
    _write(task)
    _write_board(root)
    return task


def summary(root: Path) -> dict[str, Any]:
    tasks = _tasks(root)
    counts = {status: sum(1 for task in tasks if task.status == status) for status in STATUSES}
    return {
        "tasks": len(tasks),
        "by_status": counts,
        "wip_limit": _board_settings(root)["wip_limit"],
    }


def manage_worktree(root: Path, identifier: str, remove: bool, force: bool) -> Task:
    task = next((item for item in _tasks(root) if item.identifier == identifier), None)
    if task is None:
        raise ToolwrightError(f"unknown task: {identifier}")
    relative = WORKTREES / identifier
    path = root / relative
    if remove:
        if not task.worktree:
            raise ToolwrightError(f"task has no worktree: {identifier}")
        command = ["git", "-C", str(root), "worktree", "remove"]
        if force:
            command.append("--force")
        command.append(str(path))
        code, stdout, stderr = capture_command(command, timeout=300)
        if code != 0:
            raise ToolwrightError(f"git worktree remove failed: {stderr or stdout}")
        task.worktree = ""
        _write(task)
        _write_board(root)
        return task
    if task.worktree:
        raise ToolwrightError(f"task already has a worktree: {task.worktree}")
    path.parent.mkdir(parents=True, exist_ok=True)
    code, stdout, stderr = capture_command(
        ["git", "-C", str(root), "worktree", "add", "-b", f"task/{identifier}", str(path)],
        timeout=300,
    )
    if code != 0:
        raise ToolwrightError(f"git worktree add failed: {stderr or stdout}")
    task.worktree = relative.as_posix()
    _write(task)
    _write_board(root)
    return task
