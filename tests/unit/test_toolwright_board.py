"""
Tests for the optional Markdown task board.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import board
from toolwright_cli.paths import ToolwrightError


class BoardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        config = self.root / ".toolwright/config.toml"
        config.parent.mkdir(parents=True)
        config.write_text("[board]\nwip_limit = 2\n", encoding="utf-8")


class BoardStateTests(BoardTestCase):
    def test_add_and_list(self) -> None:
        first = board.add_task(self.root, "First task", verify="npm test")
        second = board.add_task(self.root, "Second task")
        self.assertEqual(first.identifier, "T-001")
        self.assertEqual(second.identifier, "T-002")
        self.assertTrue(first.path.is_file())
        rows = board.list_tasks(self.root)
        self.assertEqual([task.title for task in rows], ["First task", "Second task"])
        board_file = (self.root / ".toolwright/board/BOARD.md").read_text(encoding="utf-8")
        self.assertIn("First task", board_file)
        self.assertIn("WIP: 0/2", board_file)

    def test_multiline_title_is_rejected(self) -> None:
        with self.assertRaises(ToolwrightError):
            board.add_task(self.root, "bad\n---\ntitle")

    def test_wip_limit_blocks(self) -> None:
        board.add_task(self.root, "One")
        board.add_task(self.root, "Two")
        board.add_task(self.root, "Three")
        board.move_task(self.root, "T-001", "in-progress")
        board.move_task(self.root, "T-002", "in-progress")
        with self.assertRaises(ToolwrightError):
            board.move_task(self.root, "T-003", "in-progress")

    def test_done_requires_approval(self) -> None:
        board.add_task(self.root, "One")
        with self.assertRaises(ToolwrightError):
            board.move_task(self.root, "T-001", "done")
        task = board.move_task(self.root, "T-001", "done", approved=True)
        self.assertEqual(task.status, "done")
        self.assertTrue(task.approved)

    def test_summary_counts(self) -> None:
        board.add_task(self.root, "One")
        board.add_task(self.root, "Two")
        board.move_task(self.root, "T-001", "review")
        result = board.summary(self.root)
        self.assertEqual(result["tasks"], 2)
        self.assertEqual(result["by_status"]["review"], 1)
        self.assertEqual(result["wip_limit"], 2)

    def test_unknown_task_and_status(self) -> None:
        with self.assertRaises(ToolwrightError):
            board.move_task(self.root, "T-999", "ready")
        board.add_task(self.root, "One")
        with self.assertRaises(ToolwrightError):
            board.move_task(self.root, "T-001", "shipped")


class WorktreeTests(BoardTestCase):
    def _git_repo(self) -> None:
        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        (self.root / "file.txt").write_text("one", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "file.txt"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "init"], check=True)

    def test_create_and_remove_worktree(self) -> None:
        self._git_repo()
        task = board.add_task(self.root, "Worktree task", worktree=True)
        path = self.root / task.worktree
        self.assertTrue(path.is_dir())
        branches = subprocess.run(
            ["git", "-C", str(self.root), "branch", "--list", "task/T-001"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertIn("task/T-001", branches)
        board.manage_worktree(self.root, task.identifier, remove=True, force=False)
        self.assertFalse(path.exists())

    def test_worktree_requires_git_repository(self) -> None:
        with self.assertRaises(ToolwrightError):
            board.add_task(self.root, "No repo", worktree=True)


if __name__ == "__main__":
    unittest.main()
