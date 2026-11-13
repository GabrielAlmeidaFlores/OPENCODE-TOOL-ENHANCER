"""
Tests for the optional Markdown task board.
"""
from __future__ import annotations
from tests.unit.test_toolwright_board_strings import (
    FLAG_LIST,
    KEY_ADD,
    KEY_BRANCH,
    KEY_BY_STATUS,
    KEY_COMMIT,
    KEY_CONFIG,
    KEY_DONE,
    KEY_GIT,
    KEY_INIT,
    KEY_ONE,
    KEY_READY,
    KEY_REVIEW,
    KEY_SHIPPED,
    KEY_TASKS,
    KEY_WIP_LIMIT,
    TEXT_BAD_TITLE,
    TEXT_BOARD_WIP_LIMIT_2,
    TEXT_C,
    TEXT_FILE_TXT,
    TEXT_FIRST_TASK,
    TEXT_IN_PROGRESS,
    TEXT_MAIN,
    TEXT_NO_REPO,
    TEXT_NPM_TEST,
    TEXT_ONE,
    TEXT_Q,
    TEXT_QM,
    TEXT_SECOND_TASK,
    TEXT_TASK_T_001,
    TEXT_TEST,
    TEXT_TEST_EXAMPLE_COM,
    TEXT_THREE,
    TEXT_TOOLWRIGHT_BOARD_BOARD_MD,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_TWO,
    TEXT_T_001,
    TEXT_T_002,
    TEXT_T_003,
    TEXT_T_999,
    TEXT_USER_EMAIL,
    TEXT_USER_NAME,
    TEXT_UTF_8,
    TEXT_WIP_0_2,
    TEXT_WORKTREE_TASK,
)

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import board
from toolwright_cli.paths import ToolWrightError


class BoardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        config = self.root / TEXT_TOOLWRIGHT_CONFIG_TOML
        config.parent.mkdir(parents=True)
        config.write_text(TEXT_BOARD_WIP_LIMIT_2, encoding=TEXT_UTF_8)


class BoardStateTests(BoardTestCase):
    def test_add_and_list(self) -> None:
        first = board.add_task(self.root, TEXT_FIRST_TASK, verify=TEXT_NPM_TEST)
        second = board.add_task(self.root, TEXT_SECOND_TASK)
        self.assertEqual(first.identifier, TEXT_T_001)
        self.assertEqual(second.identifier, TEXT_T_002)
        self.assertTrue(first.path.is_file())
        rows = board.list_tasks(self.root)
        self.assertEqual([task.title for task in rows], [TEXT_FIRST_TASK, TEXT_SECOND_TASK])
        board_file = (self.root / TEXT_TOOLWRIGHT_BOARD_BOARD_MD).read_text(encoding=TEXT_UTF_8)
        self.assertIn(TEXT_FIRST_TASK, board_file)
        self.assertIn(TEXT_WIP_0_2, board_file)

    def test_multiline_title_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            board.add_task(self.root, TEXT_BAD_TITLE)

    def test_wip_limit_blocks(self) -> None:
        board.add_task(self.root, TEXT_ONE)
        board.add_task(self.root, TEXT_TWO)
        board.add_task(self.root, TEXT_THREE)
        board.move_task(self.root, TEXT_T_001, TEXT_IN_PROGRESS)
        board.move_task(self.root, TEXT_T_002, TEXT_IN_PROGRESS)
        with self.assertRaises(ToolWrightError):
            board.move_task(self.root, TEXT_T_003, TEXT_IN_PROGRESS)

    def test_done_requires_approval(self) -> None:
        board.add_task(self.root, TEXT_ONE)
        with self.assertRaises(ToolWrightError):
            board.move_task(self.root, TEXT_T_001, KEY_DONE)
        task = board.move_task(self.root, TEXT_T_001, KEY_DONE, approved=True)
        self.assertEqual(task.status, KEY_DONE)
        self.assertTrue(task.approved)

    def test_summary_counts(self) -> None:
        board.add_task(self.root, TEXT_ONE)
        board.add_task(self.root, TEXT_TWO)
        board.move_task(self.root, TEXT_T_001, KEY_REVIEW)
        result = board.summary(self.root)
        self.assertEqual(result[KEY_TASKS], 2)
        self.assertEqual(result[KEY_BY_STATUS][KEY_REVIEW], 1)
        self.assertEqual(result[KEY_WIP_LIMIT], 2)

    def test_unknown_task_and_status(self) -> None:
        with self.assertRaises(ToolWrightError):
            board.move_task(self.root, TEXT_T_999, KEY_READY)
        board.add_task(self.root, TEXT_ONE)
        with self.assertRaises(ToolWrightError):
            board.move_task(self.root, TEXT_T_001, KEY_SHIPPED)


class WorktreeTests(BoardTestCase):
    def _git_repo(self) -> None:
        subprocess.run([KEY_GIT, TEXT_C, str(self.root), KEY_INIT, TEXT_Q], check=True)
        subprocess.run([KEY_GIT, TEXT_C, str(self.root), KEY_CONFIG, TEXT_USER_EMAIL, TEXT_TEST_EXAMPLE_COM], check=True)
        subprocess.run([KEY_GIT, TEXT_C, str(self.root), KEY_CONFIG, TEXT_USER_NAME, TEXT_TEST], check=True)
        (self.root / TEXT_FILE_TXT).write_text(KEY_ONE, encoding=TEXT_UTF_8)
        subprocess.run([KEY_GIT, TEXT_C, str(self.root), KEY_ADD, TEXT_FILE_TXT], check=True)
        subprocess.run([KEY_GIT, TEXT_C, str(self.root), KEY_COMMIT, TEXT_QM, KEY_INIT], check=True)

    def test_create_and_remove_worktree(self) -> None:
        self._git_repo()
        task = board.add_task(self.root, TEXT_WORKTREE_TASK, worktree=True)
        path = self.root / task.worktree
        self.assertTrue(path.is_dir())
        branches = subprocess.run(
            [KEY_GIT, TEXT_C, str(self.root), KEY_BRANCH, FLAG_LIST, TEXT_TASK_T_001],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertIn(TEXT_TASK_T_001, branches)
        board.manage_worktree(self.root, task.identifier, remove=True, force=False)
        self.assertFalse(path.exists())

    def test_worktree_requires_git_repository(self) -> None:
        with self.assertRaises(ToolWrightError):
            board.add_task(self.root, TEXT_NO_REPO, worktree=True)


if __name__ == TEXT_MAIN:
    unittest.main()
