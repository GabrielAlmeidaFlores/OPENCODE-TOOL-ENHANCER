"""
Unit tests for installer planning, summaries, uninstall, and backups.
"""
from __future__ import annotations
from tests.unit.test_toolwright_installer_strings import (
    KEY_ABC,
    KEY_AGENTS,
    KEY_APPLIED,
    KEY_CHANGED,
    KEY_CLEAN,
    KEY_CODEGRAPH,
    KEY_COMMIT,
    KEY_COMPONENTS,
    KEY_FILES,
    KEY_FIXTURE,
    KEY_MINIMAL,
    KEY_NEW,
    KEY_NODE_MODULES,
    KEY_OLD,
    KEY_PATH,
    KEY_PROFILE,
    KEY_REMOVABLE,
    KEY_SAME,
    KEY_SCHEMA_VERSION,
    KEY_SERENA,
    KEY_SHA256,
    KEY_SKILLS,
    KEY_SKIPPED,
    KEY_SOURCE,
    KEY_TARGET,
    KEY_UNCHANGED,
    KEY_UPDATED,
    KEY_X,
    TEXT_0,
    TEXT_20260101T000000Z,
    TEXT_20260201T000000Z,
    TEXT_ASSETS_KEEP_PY,
    TEXT_ASSETS_PYCACHE,
    TEXT_ASSETS_PYCACHE_DROP_PYC,
    TEXT_AST_GREP,
    TEXT_CHANGED_TXT,
    TEXT_DS_STORE,
    TEXT_MAIN,
    TEXT_NEW_TXT,
    TEXT_NODE_MODULES_DROP_JS,
    TEXT_OPENCODE_AGENTS,
    TEXT_OPENCODE_AGENTS_CHANGED_MD,
    TEXT_OPENCODE_AGENTS_CLEAN_MD,
    TEXT_OPENCODE_AGENTS_COORDINATOR_MD,
    TEXT_OPENCODE_COMMANDS_REVIEW_MD,
    TEXT_OPENCODE_OPENCODE_JSONC,
    TEXT_OPENCODE_SKILLS_DEMO_ASSETS_KEEP_PY,
    TEXT_OPENCODE_SKILLS_DEMO_ASSETS_PYCACHE_DROP_PYC,
    TEXT_OPENCODE_SKILLS_DEMO_DS_STORE,
    TEXT_OPENCODE_SKILLS_DEMO_NODE_MODULES_DROP_JS,
    TEXT_OPENCODE_SKILLS_TEST_DRIVEN_DEVELOPMENT_SKILL_MD,
    TEXT_PROJECT_OPENCODE_TAR_GZ,
    TEXT_RALPH_HATS_CODE_ASSIST_YML,
    TEXT_RALPH_RALPH_YML,
    TEXT_SAME_TXT,
    TEXT_SKILLS_DEMO,
    TEXT_SKILL_MD,
    TEXT_TMP_TOOLWRIGHT_PLAN,
    TEXT_TOOLWRIGHT,
    TEXT_TOOLWRIGHT_BACKUPS,
    TEXT_TOOLWRIGHT_LOCK_JSON,
    TEXT_UTF_8,
)

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
            support.REPO_ROOT / KEY_TARGET,
            list(FILE_COMPONENTS),
        )
        destinations = {item.destination.relative_to(support.REPO_ROOT / KEY_TARGET).as_posix() for item in planned}
        self.assertIn(TEXT_OPENCODE_OPENCODE_JSONC, destinations)
        self.assertIn(TEXT_OPENCODE_AGENTS_COORDINATOR_MD, destinations)
        self.assertIn(TEXT_OPENCODE_COMMANDS_REVIEW_MD, destinations)
        self.assertIn(TEXT_OPENCODE_SKILLS_TEST_DRIVEN_DEVELOPMENT_SKILL_MD, destinations)
        self.assertIn(TEXT_RALPH_RALPH_YML, destinations)
        self.assertIn(TEXT_RALPH_HATS_CODE_ASSIST_YML, destinations)
        self.assertEqual(sum(1 for item in planned if item.component == KEY_AGENTS), 12)

    def test_tool_only_components_produce_no_files(self) -> None:
        planned = installer.plan_files(
            support.REPO_ROOT,
            support.REPO_ROOT / KEY_TARGET,
            [TEXT_AST_GREP, KEY_SERENA, KEY_CODEGRAPH],
        )
        self.assertEqual(planned, [])

    def test_every_planned_source_exists(self) -> None:
        planned = installer.plan_files(support.REPO_ROOT, Path(TEXT_TMP_TOOLWRIGHT_PLAN), list(FILE_COMPONENTS))
        self.assertTrue(all(item.source.is_file() for item in planned))


class GeneratedFileTests(unittest.TestCase):

    def test_generated_files_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / TEXT_SKILLS_DEMO
            (skill / TEXT_ASSETS_PYCACHE).mkdir(parents=True)
            (skill / KEY_NODE_MODULES).mkdir(parents=True)
            (skill / TEXT_SKILL_MD).write_text(KEY_FIXTURE, encoding=TEXT_UTF_8)
            (skill / TEXT_ASSETS_KEEP_PY).write_text(KEY_X, encoding=TEXT_UTF_8)
            (skill / TEXT_ASSETS_PYCACHE_DROP_PYC).write_text(KEY_X, encoding=TEXT_UTF_8)
            (skill / TEXT_NODE_MODULES_DROP_JS).write_text(KEY_X, encoding=TEXT_UTF_8)
            (skill / TEXT_DS_STORE).write_text(KEY_X, encoding=TEXT_UTF_8)
            planned = installer.plan_files(root, root / KEY_TARGET, [KEY_SKILLS])
            names = sorted(item.destination.relative_to(root / KEY_TARGET).as_posix() for item in planned)
            self.assertIn(TEXT_OPENCODE_SKILLS_DEMO_ASSETS_KEEP_PY, names)
            self.assertNotIn(TEXT_OPENCODE_SKILLS_DEMO_ASSETS_PYCACHE_DROP_PYC, names)
            self.assertNotIn(TEXT_OPENCODE_SKILLS_DEMO_NODE_MODULES_DROP_JS, names)
            self.assertNotIn(TEXT_OPENCODE_SKILLS_DEMO_DS_STORE, names)


class SummaryTests(unittest.TestCase):

    def test_summary_tracks_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / KEY_TARGET
            sources = []
            for name, content in ((TEXT_NEW_TXT, KEY_SAME), (TEXT_SAME_TXT, KEY_SAME), (TEXT_CHANGED_TXT, KEY_NEW)):
                source = root / KEY_SOURCE / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(content, encoding=TEXT_UTF_8)
                sources.append(source)
            target.mkdir()
            (target / TEXT_SAME_TXT).write_text(KEY_SAME, encoding=TEXT_UTF_8)
            (target / TEXT_CHANGED_TXT).write_text(KEY_OLD, encoding=TEXT_UTF_8)
            planned = [
                installer.PlannedFile(source=source, destination=target / source.name, component=KEY_AGENTS)
                for source in sources
            ]
            summary = installer.summarize_file_changes(planned, target)
            self.assertEqual(summary, {KEY_NEW: 1, KEY_UPDATED: 1, KEY_UNCHANGED: 1})


class UninstallTests(unittest.TestCase):

    def _target(self) -> tuple[Path, dict]:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        target = Path(directory.name)
        (target / TEXT_OPENCODE_AGENTS).mkdir(parents=True)
        (target / TEXT_OPENCODE_AGENTS_CLEAN_MD).write_text(KEY_CLEAN, encoding=TEXT_UTF_8)
        (target / TEXT_OPENCODE_AGENTS_CHANGED_MD).write_text(KEY_CHANGED, encoding=TEXT_UTF_8)
        lock = {
            KEY_SCHEMA_VERSION: 1,
            KEY_PROFILE: KEY_MINIMAL,
            KEY_COMPONENTS: [KEY_AGENTS],
            KEY_SOURCE: {KEY_COMMIT: KEY_ABC},
            KEY_FILES: [
                {KEY_PATH: TEXT_OPENCODE_AGENTS_CLEAN_MD, KEY_SHA256: installer.sha256_file(target / TEXT_OPENCODE_AGENTS_CLEAN_MD)},
                {KEY_PATH: TEXT_OPENCODE_AGENTS_CHANGED_MD, KEY_SHA256: TEXT_0 * 64},
            ],
        }
        write_json(target / TEXT_TOOLWRIGHT_LOCK_JSON, lock)
        return target, lock

    def test_plan_does_not_remove(self) -> None:
        target, _ = self._target()
        result = installer.uninstall(target, apply=False)
        self.assertFalse(result[KEY_APPLIED])
        self.assertTrue((target / TEXT_OPENCODE_AGENTS_CLEAN_MD).is_file())
        self.assertEqual(len(result[KEY_REMOVABLE]), 1)
        self.assertEqual(len(result[KEY_SKIPPED]), 1)

    def test_apply_removes_clean_and_keeps_modified(self) -> None:
        target, _ = self._target()
        installer.uninstall(target, apply=True)
        self.assertFalse((target / TEXT_OPENCODE_AGENTS_CLEAN_MD).exists())
        self.assertTrue((target / TEXT_OPENCODE_AGENTS_CHANGED_MD).exists())

    def test_force_removes_modified(self) -> None:
        target, _ = self._target()
        installer.uninstall(target, apply=True, force=True)
        self.assertFalse((target / TEXT_OPENCODE_AGENTS_CHANGED_MD).exists())

    def test_purge_removes_state_and_lock(self) -> None:
        target, _ = self._target()
        installer.uninstall(target, apply=True, force=True, purge=True)
        self.assertFalse((target / TEXT_TOOLWRIGHT_LOCK_JSON).exists())
        self.assertFalse((target / TEXT_TOOLWRIGHT).exists())

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
            root = target / TEXT_TOOLWRIGHT_BACKUPS
            for name in (TEXT_20260101T000000Z, TEXT_20260201T000000Z):
                (root / name).mkdir(parents=True)
                (root / name / TEXT_PROJECT_OPENCODE_TAR_GZ).write_bytes(b"x")
            backups = installer.list_backups(target)
            self.assertEqual([Path(entry[KEY_PATH]).name for entry in backups], [TEXT_20260201T000000Z, TEXT_20260101T000000Z])


if __name__ == TEXT_MAIN:
    unittest.main()
