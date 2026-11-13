"""
Unit tests for installer planning, summaries, uninstall, and backups.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import installer
from toolwright_cli.profiles import FILE_COMPONENTS
from toolwright_cli.locking import write_json


class PlanTests(unittest.TestCase):

    def test_minimal_plan_covers_every_artifact_type(self) -> None:
        planned = installer.plan_files(
            support.REPO_ROOT,
            support.REPO_ROOT / "target",
            list(FILE_COMPONENTS),
        )
        destinations = {item.destination.relative_to(support.REPO_ROOT / "target").as_posix() for item in planned}
        self.assertIn(".opencode/opencode.jsonc", destinations)
        self.assertIn(".opencode/agents/coordinator.md", destinations)
        self.assertIn(".opencode/commands/review.md", destinations)
        self.assertIn(".opencode/skills/test-driven-development/SKILL.md", destinations)
        self.assertIn(".ralph/ralph.yml", destinations)
        self.assertIn(".ralph/hats/code-assist.yml", destinations)
        self.assertEqual(sum(1 for item in planned if item.component == "agents"), 12)

    def test_tool_only_components_produce_no_files(self) -> None:
        planned = installer.plan_files(
            support.REPO_ROOT,
            support.REPO_ROOT / "target",
            ["ast-grep", "serena", "codegraph"],
        )
        self.assertEqual(planned, [])

    def test_every_planned_source_exists(self) -> None:
        planned = installer.plan_files(support.REPO_ROOT, Path("/tmp/toolwright-plan"), list(FILE_COMPONENTS))
        self.assertTrue(all(item.source.is_file() for item in planned))


class GeneratedFileTests(unittest.TestCase):

    def test_generated_files_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills/demo"
            (skill / "assets/__pycache__").mkdir(parents=True)
            (skill / "node_modules").mkdir(parents=True)
            (skill / "SKILL.md").write_text("fixture", encoding="utf-8")
            (skill / "assets/keep.py").write_text("x", encoding="utf-8")
            (skill / "assets/__pycache__/drop.pyc").write_text("x", encoding="utf-8")
            (skill / "node_modules/drop.js").write_text("x", encoding="utf-8")
            (skill / ".DS_Store").write_text("x", encoding="utf-8")
            planned = installer.plan_files(root, root / "target", ["skills"])
            names = sorted(item.destination.relative_to(root / "target").as_posix() for item in planned)
            self.assertIn(".opencode/skills/demo/assets/keep.py", names)
            self.assertNotIn(".opencode/skills/demo/assets/__pycache__/drop.pyc", names)
            self.assertNotIn(".opencode/skills/demo/node_modules/drop.js", names)
            self.assertNotIn(".opencode/skills/demo/.DS_Store", names)


class SummaryTests(unittest.TestCase):

    def test_summary_tracks_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            sources = []
            for name, content in (("new.txt", "same"), ("same.txt", "same"), ("changed.txt", "new")):
                source = root / "source" / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(content, encoding="utf-8")
                sources.append(source)
            target.mkdir()
            (target / "same.txt").write_text("same", encoding="utf-8")
            (target / "changed.txt").write_text("old", encoding="utf-8")
            planned = [
                installer.PlannedFile(source=source, destination=target / source.name, component="agents")
                for source in sources
            ]
            summary = installer.summarize_file_changes(planned, target)
            self.assertEqual(summary, {"new": 1, "updated": 1, "unchanged": 1})


class UninstallTests(unittest.TestCase):

    def _target(self) -> tuple[Path, dict]:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        target = Path(directory.name)
        (target / ".opencode/agents").mkdir(parents=True)
        (target / ".opencode/agents/clean.md").write_text("clean", encoding="utf-8")
        (target / ".opencode/agents/changed.md").write_text("changed", encoding="utf-8")
        lock = {
            "schema_version": 1,
            "profile": "minimal",
            "components": ["agents"],
            "source": {"commit": "abc"},
            "files": [
                {"path": ".opencode/agents/clean.md", "sha256": installer.sha256_file(target / ".opencode/agents/clean.md")},
                {"path": ".opencode/agents/changed.md", "sha256": "0" * 64},
            ],
        }
        write_json(target / "toolwright.lock.json", lock)
        return target, lock

    def test_plan_does_not_remove(self) -> None:
        target, _ = self._target()
        result = installer.uninstall(target, apply=False)
        self.assertFalse(result["applied"])
        self.assertTrue((target / ".opencode/agents/clean.md").is_file())
        self.assertEqual(len(result["removable"]), 1)
        self.assertEqual(len(result["skipped"]), 1)

    def test_apply_removes_clean_and_keeps_modified(self) -> None:
        target, _ = self._target()
        installer.uninstall(target, apply=True)
        self.assertFalse((target / ".opencode/agents/clean.md").exists())
        self.assertTrue((target / ".opencode/agents/changed.md").exists())

    def test_force_removes_modified(self) -> None:
        target, _ = self._target()
        installer.uninstall(target, apply=True, force=True)
        self.assertFalse((target / ".opencode/agents/changed.md").exists())

    def test_purge_removes_state_and_lock(self) -> None:
        target, _ = self._target()
        installer.uninstall(target, apply=True, force=True, purge=True)
        self.assertFalse((target / "toolwright.lock.json").exists())
        self.assertFalse((target / ".toolwright").exists())

    def test_missing_lock_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(installer.ToolWrightError):
                installer.uninstall(Path(directory), apply=False)


class BackupTests(unittest.TestCase):

    def test_missing_backup_directory_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(installer.list_backups(Path(directory)), [])

    def test_backups_are_listed_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            root = target / ".toolwright/backups"
            for name in ("20260101T000000Z", "20260201T000000Z"):
                (root / name).mkdir(parents=True)
                (root / name / "project-opencode.tar.gz").write_bytes(b"x")
            backups = installer.list_backups(target)
            self.assertEqual([Path(entry["path"]).name for entry in backups], ["20260201T000000Z", "20260101T000000Z"])


if __name__ == "__main__":
    unittest.main()
