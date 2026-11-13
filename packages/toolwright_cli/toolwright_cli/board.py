"""
Markdown task board with optional Git worktrees.

Public API: :func:`add_task`, :func:`list_tasks`, :func:`move_task`,
:func:`summary`, and :func:`manage_worktree`.

State lives in ``.toolwright/board/tasks`` as one Markdown file per task. The board
file is generated. Worktrees live under ``.toolwright/worktrees`` and are never
committed. This module never stages, commits, or merges.
"""
from __future__ import annotations
from .constants import FALSE_VALUE
from .board_strings import (
    EMPTY_STRING,
    ENCODING_UTF8,
    FLAG_FORCE,
    FLAG_ID_TITLE_STATUS_CREATED_WORKTREE_VERIFY_APPROVED_NOTES_GO_HE,
    FLAG_TEXT,
    KEY_ADD,
    KEY_APPROVED,
    KEY_BACKLOG,
    KEY_BOARD,
    KEY_BY_STATUS,
    KEY_CREATED,
    KEY_DONE,
    KEY_GIT,
    KEY_ID,
    KEY_READY,
    KEY_REMOVE,
    KEY_REVIEW,
    KEY_STATUS,
    KEY_TASKS,
    KEY_TITLE,
    KEY_TRUE,
    KEY_VERIFY,
    KEY_WIP_LIMIT,
    KEY_WORKTREE,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    TEXT_B,
    TEXT_BOARD_MUST_BE_A_TABLE,
    TEXT_BOARD_WIP_LIMIT_MUST_BE_A_POSITIVE_INTEGER,
    TEXT_C,
    TEXT_GIT_WORKTREE_ADD_FAILED,
    TEXT_GIT_WORKTREE_REMOVE_FAILED,
    TEXT_ID_TITLE_STATUS_WORKTREE_VERIFY,
    TEXT_INVALID_TOML,
    TEXT_IN_PROGRESS,
    TEXT_MD,
    TEXT_MD_2,
    TEXT_MISSING,
    TEXT_MISSING_FRONTMATTER,
    TEXT_MOVING_A_TASK_TO_DONE_REQUIRES_APPROVED,
    TEXT_T,
    TEXT_TASK,
    TEXT_TASK_ALREADY_HAS_A_WORKTREE,
    TEXT_TASK_BOARD,
    TEXT_TASK_HAS_NO_WORKTREE,
    TEXT_TASK_TITLE_IS_REQUIRED,
    TEXT_TASK_TITLE_MUST_BE_A_SINGLE_LINE,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TEXT_4,
    TEXT_TEXT_5,
    TEXT_TEXT_6,
    TEXT_TOOLWRIGHT_BOARD_BOARD_MD,
    TEXT_TOOLWRIGHT_BOARD_TASKS,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_TOOLWRIGHT_WORKTREES,
    TEXT_T_03D,
    TEXT_UNKNOWN_STATUS,
    TEXT_UNKNOWN_STATUS_2,
    TEXT_UNKNOWN_TASK,
    TEXT_UNTERMINATED_FRONTMATTER,
    TEXT_VERIFICATION_COMMAND_MUST_BE_A_SINGLE_LINE,
    TEXT_WIP,
    TEXT_WIP_LIMIT_REACHED,
)

import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import ToolWrightError
from .process import capture_command

STATUSES = (KEY_BACKLOG, KEY_READY, TEXT_IN_PROGRESS, KEY_REVIEW, KEY_DONE)
DEFAULT_WIP_LIMIT = 3
TASK_ROOT = Path(TEXT_TOOLWRIGHT_BOARD_TASKS)
BOARD = Path(TEXT_TOOLWRIGHT_BOARD_BOARD_MD)
WORKTREES = Path(TEXT_TOOLWRIGHT_WORKTREES)


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
    values = {KEY_WIP_LIMIT: DEFAULT_WIP_LIMIT}
    config = root / TEXT_TOOLWRIGHT_CONFIG_TOML
    if not config.is_file():
        return values
    try:
        data = tomllib.loads(config.read_text(encoding=ENCODING_UTF8))
    except tomllib.TOMLDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_TOML.format(config, error)) from error
    section = data.get(KEY_BOARD, {})
    if not isinstance(section, dict):
        raise ToolWrightError(TEXT_BOARD_MUST_BE_A_TABLE.format(config))
    value = section.get(KEY_WIP_LIMIT, values[KEY_WIP_LIMIT])
    if not isinstance(value, int) or value <= 0:
        raise ToolWrightError(TEXT_BOARD_WIP_LIMIT_MUST_BE_A_POSITIVE_INTEGER.format(config))
    values[KEY_WIP_LIMIT] = value
    return values


def _parse(path: Path) -> Task:
    text = path.read_text(encoding=ENCODING_UTF8)
    if not text.startswith(FLAG_TEXT):
        raise ToolWrightError(TEXT_MISSING_FRONTMATTER.format(path))
    end = text.find(TEXT_TEXT_2, 3)
    if end == -1:
        raise ToolWrightError(TEXT_UNTERMINATED_FRONTMATTER.format(path))
    metadata: dict[str, str] = {}
    for line in text[3:end].splitlines():
        key, separator, value = line.partition(TEXT_TEXT_3)
        if separator:
            metadata[key.strip()] = value.strip()
    required = (KEY_ID, KEY_TITLE, KEY_STATUS, KEY_CREATED)
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ToolWrightError(TEXT_MISSING.format(path, SEPARATOR_COMMA_SPACE.join(missing)))
    if metadata[KEY_STATUS] not in STATUSES:
        raise ToolWrightError(TEXT_UNKNOWN_STATUS.format(path, metadata[KEY_STATUS]))
    return Task(
        identifier=metadata[KEY_ID],
        title=metadata[KEY_TITLE],
        status=metadata[KEY_STATUS],
        created=metadata[KEY_CREATED],
        worktree=metadata.get(KEY_WORKTREE, EMPTY_STRING),
        verify=metadata.get(KEY_VERIFY, EMPTY_STRING),
        approved=metadata.get(KEY_APPROVED, FALSE_VALUE) == KEY_TRUE,
        path=path,
    )


def _tasks(root: Path) -> list[Task]:
    directory = root / TASK_ROOT
    if not directory.is_dir():
        return []
    return sorted((_parse(path) for path in directory.glob(TEXT_MD_2)), key=lambda task: task.identifier)


def _write(task: Task) -> None:
    task.path.write_text(
        FLAG_ID_TITLE_STATUS_CREATED_WORKTREE_VERIFY_APPROVED_NOTES_GO_HE.format(task.identifier, task.title, task.status, task.created, task.worktree, task.verify, KEY_TRUE if task.approved else FALSE_VALUE),
        encoding=ENCODING_UTF8,
    )


def _write_board(root: Path) -> None:
    tasks = _tasks(root)
    limit = _board_settings(root)[KEY_WIP_LIMIT]
    in_progress = sum(1 for task in tasks if task.status == TEXT_IN_PROGRESS)
    lines = [
        TEXT_TASK_BOARD,
        EMPTY_STRING,
        TEXT_WIP.format(in_progress, limit),
        EMPTY_STRING,
        TEXT_ID_TITLE_STATUS_WORKTREE_VERIFY,
        TEXT_TEXT_4,
    ]
    for task in tasks:
        lines.append(
            TEXT_TEXT.format(task.identifier, task.title, task.status, task.worktree or TEXT_TEXT_5, task.verify or TEXT_TEXT_5)
        )
    lines.append(EMPTY_STRING)
    target = root / BOARD
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(NEWLINE.join(lines), encoding=ENCODING_UTF8)


def _next_identifier(root: Path) -> str:
    numbers = []
    for task in _tasks(root):
        try:
            numbers.append(int(task.identifier.removeprefix(TEXT_T)))
        except ValueError:
            continue
    return TEXT_T_03D.format(max(numbers, default=0) + 1)


def add_task(root: Path, title: str, worktree: bool = False, verify: str = EMPTY_STRING) -> Task:
    value = title.strip()
    if not value:
        raise ToolWrightError(TEXT_TASK_TITLE_IS_REQUIRED)
    if NEWLINE in value or TEXT_TEXT_6 in value or value == FLAG_TEXT:
        raise ToolWrightError(TEXT_TASK_TITLE_MUST_BE_A_SINGLE_LINE)
    if NEWLINE in verify or TEXT_TEXT_6 in verify or verify.strip() == FLAG_TEXT:
        raise ToolWrightError(TEXT_VERIFICATION_COMMAND_MUST_BE_A_SINGLE_LINE)
    directory = root / TASK_ROOT
    directory.mkdir(parents=True, exist_ok=True)
    identifier = _next_identifier(root)
    task = Task(
        identifier=identifier,
        title=value,
        status=KEY_BACKLOG,
        created=datetime.now(timezone.utc).date().isoformat(),
        worktree=EMPTY_STRING,
        verify=verify.strip(),
        approved=False,
        path=directory / TEXT_MD.format(identifier),
    )
    _write(task)
    _write_board(root)
    if worktree:
        return manage_worktree(root, identifier, remove=False, force=False)
    return task


def list_tasks(root: Path, status: str | None = None) -> list[Task]:
    if status and status not in STATUSES:
        raise ToolWrightError(TEXT_UNKNOWN_STATUS_2.format(status))
    return [task for task in _tasks(root) if not status or task.status == status]


def move_task(root: Path, identifier: str, status: str, approved: bool = False) -> Task:
    if status not in STATUSES:
        raise ToolWrightError(TEXT_UNKNOWN_STATUS_2.format(status))
    tasks = _tasks(root)
    task = next((item for item in tasks if item.identifier == identifier), None)
    if task is None:
        raise ToolWrightError(TEXT_UNKNOWN_TASK.format(identifier))
    if status == TEXT_IN_PROGRESS:
        limit = _board_settings(root)[KEY_WIP_LIMIT]
        current = sum(1 for item in tasks if item.status == TEXT_IN_PROGRESS and item.identifier != identifier)
        if current >= limit:
            raise ToolWrightError(TEXT_WIP_LIMIT_REACHED.format(current, limit))
    if status == KEY_DONE and not approved:
        raise ToolWrightError(TEXT_MOVING_A_TASK_TO_DONE_REQUIRES_APPROVED)
    task.status = status
    if status == KEY_DONE:
        task.approved = True
    _write(task)
    _write_board(root)
    return task


def summary(root: Path) -> dict[str, Any]:
    tasks = _tasks(root)
    counts = {status: sum(1 for task in tasks if task.status == status) for status in STATUSES}
    return {
        KEY_TASKS: len(tasks),
        KEY_BY_STATUS: counts,
        KEY_WIP_LIMIT: _board_settings(root)[KEY_WIP_LIMIT],
    }


def manage_worktree(root: Path, identifier: str, remove: bool, force: bool) -> Task:
    task = next((item for item in _tasks(root) if item.identifier == identifier), None)
    if task is None:
        raise ToolWrightError(TEXT_UNKNOWN_TASK.format(identifier))
    relative = WORKTREES / identifier
    path = root / relative
    if remove:
        if not task.worktree:
            raise ToolWrightError(TEXT_TASK_HAS_NO_WORKTREE.format(identifier))
        command = [KEY_GIT, TEXT_C, str(root), KEY_WORKTREE, KEY_REMOVE]
        if force:
            command.append(FLAG_FORCE)
        command.append(str(path))
        code, stdout, stderr = capture_command(command, timeout=300)
        if code != 0:
            raise ToolWrightError(TEXT_GIT_WORKTREE_REMOVE_FAILED.format(stderr or stdout))
        task.worktree = EMPTY_STRING
        _write(task)
        _write_board(root)
        return task
    if task.worktree:
        raise ToolWrightError(TEXT_TASK_ALREADY_HAS_A_WORKTREE.format(task.worktree))
    path.parent.mkdir(parents=True, exist_ok=True)
    code, stdout, stderr = capture_command(
        [KEY_GIT, TEXT_C, str(root), KEY_WORKTREE, KEY_ADD, TEXT_B, TEXT_TASK.format(identifier), str(path)],
        timeout=300,
    )
    if code != 0:
        raise ToolWrightError(TEXT_GIT_WORKTREE_ADD_FAILED.format(stderr or stdout))
    task.worktree = relative.as_posix()
    _write(task)
    _write_board(root)
    return task
