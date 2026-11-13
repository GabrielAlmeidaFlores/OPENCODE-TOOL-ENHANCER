"""
Task-board command handler.

Public API: :func:`_command_task`.

Side effects: delegates to the task-board module.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_12, TEMPLATE_12_2, TEMPLATE_TASKS, TEMPLATE_TASK_S, TEMPLATE_TEMPLATE_5, TEMPLATE_TEMPLATE_6, TEMPLATE_WIP_LIMIT, TEMPLATE_WORKTREE, TEMPLATE_WORKTREE_2
from ..cli_strings import (
    KEY_APPROVED,
    KEY_BY_STATUS,
    KEY_CREATED,
    KEY_MOVE,
    KEY_NONE,
    KEY_TASKS,
    KEY_WIP_LIMIT,
    TEXT_REFUSING_TO_REMOVE_A_WORKTREE_WITHOUT_YES,
)

import argparse

from ..common import emit_payload, resolve_repository_root
from ...constants import KEY_ID, KEY_STATUS, KEY_TITLE, STATUS_OK
from ...cli_constants import (
    COMMAND_ADD, COMMAND_LIST, COMMAND_VERIFY, COMMAND_WORKTREE, KEY_STATUS as CLI_KEY_STATUS,
)
from ... import board as board_module
from ...paths import ToolWrightError

def _command_task(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    action = args.task_command
    if action == COMMAND_ADD:
        task = board_module.add_task(root, args.title, worktree=args.worktree, verify=args.verify)
        if args.json:
            emit_payload({KEY_ID: task.identifier, KEY_TITLE: task.title, KEY_STATUS: task.status, COMMAND_WORKTREE: task.worktree, COMMAND_VERIFY: task.verify}, True)
            return 0
        print(TEMPLATE_TEMPLATE_5.format(task.identifier, task.status, task.title))
        if task.worktree:
            print(TEMPLATE_WORKTREE_2.format(task.worktree))
        return 0
    if action == COMMAND_LIST:
        tasks = board_module.list_tasks(root, args.status)
        if args.json:
            emit_payload(
                {
                    KEY_TASKS: [
                        {
                            KEY_ID: task.identifier,
                            KEY_TITLE: task.title,
                            KEY_STATUS: task.status,
                            KEY_CREATED: task.created,
                            COMMAND_WORKTREE: task.worktree,
                            COMMAND_VERIFY: task.verify,
                            KEY_APPROVED: task.approved,
                        }
                        for task in tasks
                    ]
                },
                True,
            )
            return 0
        for task in tasks:
            print(TEMPLATE_12.format(task.identifier, task.status, task.title))
        print(TEMPLATE_TASK_S.format(len(tasks)))
        return 0
    if action == KEY_MOVE:
        task = board_module.move_task(root, args.identifier, args.status, approved=args.approved)
        if args.json:
            emit_payload({KEY_ID: task.identifier, KEY_STATUS: task.status, KEY_APPROVED: task.approved}, True)
            return 0
        print(TEMPLATE_TEMPLATE_6.format(task.identifier, task.status))
        return 0
    if action == KEY_STATUS:
        result = board_module.summary(root)
        if args.json:
            emit_payload(result, True)
        else:
            print(TEMPLATE_TASKS.format(result[KEY_TASKS]))
            for status, count in result[KEY_BY_STATUS].items():
                print(TEMPLATE_12_2.format(status, count))
            print(TEMPLATE_WIP_LIMIT.format(result[KEY_WIP_LIMIT]))
        return 0
    if args.remove and not args.yes:
        raise ToolWrightError(TEXT_REFUSING_TO_REMOVE_A_WORKTREE_WITHOUT_YES)
    task = board_module.manage_worktree(root, args.identifier, remove=args.remove, force=args.force)
    if args.json:
        emit_payload({KEY_ID: task.identifier, COMMAND_WORKTREE: task.worktree}, True)
        return 0
    print(TEMPLATE_WORKTREE.format(task.identifier, task.worktree or KEY_NONE))
    return 0
