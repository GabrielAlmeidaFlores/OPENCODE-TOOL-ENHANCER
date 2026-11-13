"""
Unit tests for the ``toolwright`` command-line package.

Covers parser behaviour, version wiring, and lock file
handling. No test writes inside the repository working tree.
"""
from __future__ import annotations
from tests.unit.test_toolwright_cli_strings import (
    EMPTY_STRING,
    FLAG_APPLY,
    FLAG_DRY_RUN,
    FLAG_VERSION,
    KEY_ABC,
    KEY_ADAPTER,
    KEY_ADAPTERS,
    KEY_AGENTS,
    KEY_CATALOG,
    KEY_CHECKS,
    KEY_CLAUDE,
    KEY_COMMANDS,
    KEY_COMMIT,
    KEY_COMPONENTS,
    KEY_DEPENDENCIES,
    KEY_FAIL,
    KEY_FILES,
    KEY_FULL,
    KEY_GENERATOR,
    KEY_INSTALL,
    KEY_MINIMAL,
    KEY_MISSING,
    KEY_MODIFIED,
    KEY_NAME,
    KEY_NEW,
    KEY_ONE,
    KEY_OPENCODE,
    KEY_PATH,
    KEY_PROFILE,
    KEY_PROJECT,
    KEY_RALPH,
    KEY_RB,
    KEY_REPOSITORY,
    KEY_ROOT,
    KEY_SCHEMA_VERSION,
    KEY_SERENA,
    KEY_SHA256,
    KEY_SKILLS,
    KEY_SOURCE,
    KEY_STANDARD,
    KEY_STATUS,
    KEY_SUMMARY,
    KEY_TARGET,
    KEY_TWO,
    KEY_VERSION,
    KEY_X,
    TEXT_0,
    TEXT_1,
    TEXT_2,
    TEXT_ABSENT_JSON,
    TEXT_AGENTS_COMMANDS,
    TEXT_AGENTS_NONSENSE,
    TEXT_AST_GREP,
    TEXT_A_TXT,
    TEXT_B_TXT,
    TEXT_CLAUDE_AGENTS_A_MD,
    TEXT_COMMAND_NOT_FOUND,
    TEXT_DEFINITELY_NOT_A_REAL_COMMAND_TOOLWRIGHT,
    TEXT_FILE_TXT,
    TEXT_MAIN,
    TEXT_OPENCODE_AGENTS_A_MD,
    TEXT_OPENCODE_AGENTS_B_MD,
    TEXT_OPENCODE_COPY,
    TEXT_OPENCODE_NEW_MD,
    TEXT_OPENCODE_OLD_MD,
    TEXT_OPTIONAL_DEPENDENCIES,
    TEXT_PYPROJECT_TOML,
    TEXT_PYYAML_6_0,
    TEXT_TOOLWRIGHT_LOCK_JSON,
    TEXT_UTF_8,
    TEXT_VERSION,
)

import contextlib
import io
import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from tests import support

import toolwright_cli
from toolwright_cli import cli, installer, locking
from toolwright_cli.process import capture_command
from toolwright_cli.paths import ToolWrightError


class VersionTests(unittest.TestCase):

    def test_version_matches_version_file(self) -> None:
        expected = (support.REPO_ROOT / TEXT_VERSION).read_text(encoding=TEXT_UTF_8).strip()
        self.assertEqual(toolwright_cli.__version__, expected)

    def test_pyproject_version_matches_version_file(self) -> None:
        expected = (support.REPO_ROOT / TEXT_VERSION).read_text(encoding=TEXT_UTF_8).strip()
        with (support.CLI_PACKAGE / TEXT_PYPROJECT_TOML).open(KEY_RB) as handle:
            project = tomllib.load(handle)[KEY_PROJECT]
        self.assertEqual(project[KEY_VERSION], expected)

    def test_package_has_no_runtime_dependencies(self) -> None:
        with (support.CLI_PACKAGE / TEXT_PYPROJECT_TOML).open(KEY_RB) as handle:
            project = tomllib.load(handle)[KEY_PROJECT]
        self.assertEqual(project.get(KEY_DEPENDENCIES, []), [])
        self.assertEqual(project.get(TEXT_OPTIONAL_DEPENDENCIES, {}).get(KEY_CATALOG), [TEXT_PYYAML_6_0])


class ParserTests(unittest.TestCase):

    def test_version_flag(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
            cli.main([FLAG_VERSION])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn(toolwright_cli.__version__, stdout.getvalue())

    def test_install_rejects_apply_with_dry_run(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            cli.main([KEY_INSTALL, FLAG_APPLY, FLAG_DRY_RUN])
        self.assertEqual(raised.exception.code, 2)

class LockingTests(unittest.TestCase):

    def test_sha256_file_matches_hashlib(self) -> None:
        import hashlib

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_FILE_TXT
            path.write_bytes(b"toolwright\n")
            self.assertEqual(locking.sha256_file(path), hashlib.sha256(b"toolwright\n").hexdigest())

    def test_write_read_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_TOOLWRIGHT_LOCK_JSON
            locking.write_json(
                path,
                {
                    KEY_SCHEMA_VERSION: 2,
                    KEY_ADAPTERS: [{KEY_NAME: KEY_OPENCODE, KEY_PROFILE: KEY_MINIMAL, KEY_COMPONENTS: [KEY_AGENTS]}],
                    KEY_FILES: [],
                },
            )
            lock = locking.read_lock(path)
            self.assertIsNotNone(lock)
            self.assertEqual(lock[KEY_SCHEMA_VERSION], 2)
            self.assertEqual(lock[KEY_ADAPTERS][0][KEY_NAME], KEY_OPENCODE)

    def test_v1_lock_is_read_as_opencode_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_TOOLWRIGHT_LOCK_JSON
            path.write_text(
                json.dumps(
                    {
                        KEY_SCHEMA_VERSION: 1,
                        KEY_PROFILE: KEY_MINIMAL,
                        KEY_COMPONENTS: [KEY_AGENTS],
                        KEY_SOURCE: {KEY_COMMIT: KEY_ABC},
                        KEY_FILES: [{KEY_PATH: TEXT_OPENCODE_AGENTS_A_MD, KEY_SHA256: TEXT_0 * 64}],
                    }
                ),
                encoding=TEXT_UTF_8,
            )
            lock = locking.read_lock(path)
            self.assertIsNotNone(lock)
            self.assertEqual(lock[KEY_SCHEMA_VERSION], 2)
            self.assertEqual(lock[KEY_ADAPTERS][0][KEY_NAME], KEY_OPENCODE)
            self.assertEqual(lock[KEY_ADAPTERS][0][KEY_COMPONENTS], [KEY_AGENTS])
            self.assertEqual(lock[KEY_FILES][0][KEY_ADAPTER], KEY_OPENCODE)
            self.assertEqual(lock[KEY_FILES][0][KEY_GENERATOR], TEXT_OPENCODE_COPY)

    def test_v2_adapter_entry_must_be_an_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_TOOLWRIGHT_LOCK_JSON
            path.write_text(
                json.dumps({KEY_SCHEMA_VERSION: 2, KEY_ADAPTERS: [KEY_OPENCODE], KEY_FILES: []}),
                encoding=TEXT_UTF_8,
            )
            with self.assertRaises(ValueError):
                locking.read_lock(path)

    def test_merge_lock_preserves_other_adapters(self) -> None:
        existing = {
            KEY_SCHEMA_VERSION: 2,
            KEY_ADAPTERS: [{KEY_NAME: KEY_OPENCODE, KEY_PROFILE: KEY_MINIMAL, KEY_COMPONENTS: [KEY_AGENTS]}],
            KEY_FILES: [
                {KEY_PATH: TEXT_OPENCODE_AGENTS_A_MD, KEY_ADAPTER: KEY_OPENCODE, KEY_SHA256: TEXT_0 * 64},
                {KEY_PATH: TEXT_OPENCODE_AGENTS_B_MD, KEY_ADAPTER: KEY_OPENCODE, KEY_SHA256: TEXT_1 * 64},
            ],
        }
        new = {
            KEY_SCHEMA_VERSION: 2,
            KEY_ADAPTERS: [{KEY_NAME: KEY_CLAUDE, KEY_PROFILE: KEY_MINIMAL, KEY_COMPONENTS: [KEY_AGENTS]}],
            KEY_FILES: [
                {KEY_PATH: TEXT_CLAUDE_AGENTS_A_MD, KEY_ADAPTER: KEY_CLAUDE, KEY_SHA256: TEXT_2 * 64},
            ],
        }
        merged = locking.merge_lock(existing, new)
        self.assertEqual([entry[KEY_NAME] for entry in merged[KEY_ADAPTERS]], [KEY_CLAUDE, KEY_OPENCODE])
        self.assertEqual(
            sorted(entry[KEY_PATH] for entry in merged[KEY_FILES]),
            [TEXT_CLAUDE_AGENTS_A_MD, TEXT_OPENCODE_AGENTS_A_MD, TEXT_OPENCODE_AGENTS_B_MD],
        )

    def test_merge_lock_replaces_same_adapter_entries(self) -> None:
        existing = {
            KEY_SCHEMA_VERSION: 2,
            KEY_ADAPTERS: [{KEY_NAME: KEY_OPENCODE, KEY_PROFILE: KEY_MINIMAL, KEY_COMPONENTS: [KEY_AGENTS]}],
            KEY_FILES: [{KEY_PATH: TEXT_OPENCODE_OLD_MD, KEY_ADAPTER: KEY_OPENCODE}],
        }
        new = {
            KEY_SCHEMA_VERSION: 2,
            KEY_ADAPTERS: [{KEY_NAME: KEY_OPENCODE, KEY_PROFILE: KEY_FULL, KEY_COMPONENTS: [KEY_AGENTS, KEY_COMMANDS]}],
            KEY_FILES: [{KEY_PATH: TEXT_OPENCODE_NEW_MD, KEY_ADAPTER: KEY_OPENCODE}],
        }
        merged = locking.merge_lock(existing, new)
        self.assertEqual(merged[KEY_ADAPTERS][0][KEY_PROFILE], KEY_FULL)
        self.assertEqual([entry[KEY_PATH] for entry in merged[KEY_FILES]], [TEXT_OPENCODE_NEW_MD])

    def test_unsupported_schema_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_TOOLWRIGHT_LOCK_JSON
            path.write_text(json.dumps({KEY_SCHEMA_VERSION: 99, KEY_FILES: []}), encoding=TEXT_UTF_8)
            with self.assertRaises(ValueError):
                locking.read_lock(path)

    def test_missing_file_is_not_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(locking.read_lock(Path(directory) / TEXT_ABSENT_JSON))

    def test_drift_reports_modified_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / TEXT_A_TXT).write_text(KEY_NEW, encoding=TEXT_UTF_8)
            lock = {
                KEY_FILES: [
                    {KEY_PATH: TEXT_A_TXT, KEY_SHA256: TEXT_0 * 64},
                    {KEY_PATH: TEXT_B_TXT, KEY_SHA256: TEXT_0 * 64},
                ]
            }
            drift = locking.lock_drift(lock, target)
            self.assertEqual(
                sorted(entry[KEY_STATUS] for entry in drift),
                [KEY_MISSING, KEY_MODIFIED],
            )

    def test_build_lock_refuses_missing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / KEY_ROOT
            target = Path(directory) / KEY_TARGET
            source = root / TEXT_A_TXT
            source.parent.mkdir(parents=True)
            source.write_text(KEY_X, encoding=TEXT_UTF_8)
            target.mkdir()
            planned = [locking.PlannedFile(source=source, destination=target / TEXT_A_TXT, component=KEY_AGENTS)]
            with self.assertRaises(FileNotFoundError):
                locking.build_lock(root, target, KEY_MINIMAL, [KEY_AGENTS], planned, {KEY_COMMIT: KEY_ABC})


class ComponentTests(unittest.TestCase):

    def test_profiles_are_loaded_from_manifests(self) -> None:
        from toolwright_cli.profiles import load_profiles

        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(list(profiles[KEY_MINIMAL].components), [KEY_OPENCODE, KEY_AGENTS, KEY_COMMANDS, KEY_SKILLS, KEY_RALPH])
        self.assertIn(TEXT_AST_GREP, profiles[KEY_STANDARD].components)
        self.assertIn(KEY_SERENA, profiles[KEY_FULL].components)

    def test_unknown_only_component_is_rejected(self) -> None:
        from toolwright_cli.profiles import load_profiles, resolve_components

        profiles = load_profiles(support.REPO_ROOT)
        with self.assertRaises(ToolWrightError):
            resolve_components(profiles, KEY_MINIMAL, TEXT_AGENTS_NONSENSE)

    def test_explicit_only_overrides_profile(self) -> None:
        from toolwright_cli.profiles import load_profiles, resolve_components

        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(resolve_components(profiles, KEY_FULL, TEXT_AGENTS_COMMANDS), [KEY_AGENTS, KEY_COMMANDS])


class CaptureTests(unittest.TestCase):

    def test_missing_command_returns_127(self) -> None:
        code, stdout, stderr = capture_command([TEXT_DEFINITELY_NOT_A_REAL_COMMAND_TOOLWRIGHT])
        self.assertEqual(code, 127)
        self.assertEqual(stdout, EMPTY_STRING)
        self.assertIn(TEXT_COMMAND_NOT_FOUND, stderr)


class DoctorFailureTests(unittest.TestCase):

    def test_missing_repository_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checks = cli.run_diagnostic_checks(root, root, mcp=False)
            summary = cli.summarize_checks(checks)
            self.assertGreater(summary[KEY_FAIL], 0)
            self.assertIn(KEY_REPOSITORY, {check.id for check in checks if check.status == KEY_FAIL})

    def test_json_output_has_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = cli.doctor_dict(cli.run_diagnostic_checks(root, root, mcp=False))
            self.assertIn(KEY_CHECKS, payload)
            self.assertIn(KEY_SUMMARY, payload)


class SourceDigestTests(unittest.TestCase):

    def test_digest_changes_with_source_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / KEY_ROOT
            target = Path(directory) / KEY_TARGET
            source = root / TEXT_A_TXT
            source.parent.mkdir(parents=True)
            source.write_text(KEY_ONE, encoding=TEXT_UTF_8)
            target.mkdir()
            planned = [installer.PlannedFile(source=source, destination=target / TEXT_A_TXT, component=KEY_AGENTS)]
            first = installer.source_digest(planned, target)
            source.write_text(KEY_TWO, encoding=TEXT_UTF_8)
            second = installer.source_digest(planned, target)
            self.assertNotEqual(first, second)


if __name__ == TEXT_MAIN:
    unittest.main()
