"""
Unit tests for the deterministic verification engine.
"""
from __future__ import annotations
from tests.unit.test_toolwright_verify_strings import (
    KEY_FAIL,
    KEY_FAILED,
    KEY_MAX_ITERATIONS,
    KEY_MISSING,
    KEY_NOPE,
    KEY_OK,
    KEY_ONE,
    KEY_PASS,
    KEY_PASSED,
    KEY_SLOW,
    KEY_SRC,
    KEY_STATUS,
    KEY_TIMEOUT,
    KEY_TRUE,
    KEY_TWO,
    KEY_X,
    TEXT_COMMAND_FAILURE,
    TEXT_COUNTER_TXT,
    TEXT_GOVERNANCE_MAX_ITERATIONS_5,
    TEXT_INPUT_TXT,
    TEXT_MAIN,
    TEXT_MISSING_COMMAND,
    TEXT_SRC_KEEP_TXT,
    TEXT_SRC_PYCACHE,
    TEXT_SRC_PYCACHE_DROP_PYC,
    TEXT_TEXT,
    TEXT_TOOLWRIGHT_CACHE_VERIFY_CACHE_JSON,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_UTF_8,
    TEXT_VERIFY_CHECKS_BAD_NAME_COMMAND_TRUE,
    TEXT_VERIFY_CHECKS_CACHE_COMMAND_SH_C_ECHO_X_COUNTER_TXT_INPUTS_S,
    TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_GOVERNANCE_VALIDATOR_MODE_L,
    TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_INPUTS_ETC_PASSWD,
    TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_INPUTS_MISSING_TXT,
    TEXT_VERIFY_CHECKS_OK_TIMEOUT_5,
    TEXT_VERIFY_TIMEOUT_30_VERIFY_CHECKS_OK_COMMAND_TRUE_GOVERNANCE_M,
)

import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import verify
from toolwright_cli.paths import ToolWrightError


def write_config(root: Path, body: str) -> Path:
    path = root / TEXT_TOOLWRIGHT_CONFIG_TOML
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding=TEXT_UTF_8)
    return path


class ConfigTests(unittest.TestCase):

    def test_loads_checks_and_governance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                TEXT_VERIFY_TIMEOUT_30_VERIFY_CHECKS_OK_COMMAND_TRUE_GOVERNANCE_M,
            )
            checks, governance = verify.load_verification_config(root)
            self.assertEqual(checks[KEY_OK].command, KEY_TRUE)
            self.assertEqual(checks[KEY_OK].timeout, 30.0)
            self.assertEqual(governance[KEY_MAX_ITERATIONS], 5)

    def test_missing_config_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ToolWrightError):
                verify.load_verification_config(Path(directory))

    def test_missing_verify_table_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, TEXT_GOVERNANCE_MAX_ITERATIONS_5)
            with self.assertRaises(ToolWrightError):
                verify.load_verification_config(root)

    def test_missing_command_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, TEXT_VERIFY_CHECKS_OK_TIMEOUT_5)
            with self.assertRaises(ToolWrightError):
                verify.load_verification_config(root)

    def test_invalid_check_name_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, TEXT_VERIFY_CHECKS_BAD_NAME_COMMAND_TRUE)
            with self.assertRaises(ToolWrightError):
                verify.load_verification_config(root)


class ExecutionTests(unittest.TestCase):

    def _root(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        write_config(
            root,
            (
                '[verify]\ntimeout = 10\n'
                '[verify.checks.ok]\ncommand = "true"\n'
                '[verify.checks.fail]\ncommand = "sh -c \'echo boom; exit 3\'"\n'
                '[verify.checks.slow]\ncommand = "sleep 2"\ntimeout = 0.2\n'
                '[verify.checks.missing]\ncommand = "definitely-not-a-command-toolwright"\n'
            ),
        )
        return root

    def test_pass_and_failure_classes(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        results = {result.name: result for result in verify.run_verification_checks(root, checks, use_cache=False)}
        self.assertEqual(results[KEY_OK].status, KEY_PASS)
        self.assertEqual(results[KEY_FAIL].failure_class, TEXT_COMMAND_FAILURE)
        self.assertEqual(results[KEY_SLOW].failure_class, KEY_TIMEOUT)
        self.assertEqual(results[KEY_SLOW].exit_code, 124)
        self.assertEqual(results[KEY_MISSING].failure_class, TEXT_MISSING_COMMAND)
        self.assertEqual(results[KEY_MISSING].exit_code, 127)

    def test_only_selects_checks(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        results = verify.run_verification_checks(root, checks, only=[KEY_OK], use_cache=False)
        self.assertEqual([result.name for result in results], [KEY_OK])

    def test_unknown_only_check_is_an_error(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        with self.assertRaises(ToolWrightError):
            verify.run_verification_checks(root, checks, only=[KEY_NOPE], use_cache=False)

    def test_summary_counts(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        results = verify.run_verification_checks(root, checks, only=[KEY_OK, KEY_FAIL], use_cache=False)
        summary = verify.summarize_results(results)
        self.assertEqual(summary[KEY_PASSED], 1)
        self.assertEqual(summary[KEY_FAILED], 1)
        self.assertEqual(summary[KEY_STATUS], KEY_FAIL)


class CacheTests(unittest.TestCase):

    def _root(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / TEXT_INPUT_TXT).write_text(KEY_ONE, encoding=TEXT_UTF_8)
        write_config(
            root,
            (
                '[verify]\ntimeout = 10\n'
                '[verify.checks.cache]\ncommand = "sh -c \'echo x >> counter.txt\'"\n'
                'inputs = ["input.txt"]\n'
            ),
        )
        return root

    def _count(self, root: Path) -> int:
        path = root / TEXT_COUNTER_TXT
        return len(path.read_text(encoding=TEXT_UTF_8).splitlines()) if path.is_file() else 0

    def test_second_run_uses_cache(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        verify.run_verification_checks(root, checks)
        second = verify.run_verification_checks(root, checks)
        self.assertEqual(self._count(root), 1)
        self.assertTrue(second[0].cached)

    def test_no_cache_forces_execution(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        verify.run_verification_checks(root, checks)
        verify.run_verification_checks(root, checks, use_cache=False)
        self.assertEqual(self._count(root), 2)

    def test_input_change_invalidates_cache(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        verify.run_verification_checks(root, checks)
        (root / TEXT_INPUT_TXT).write_text(KEY_TWO, encoding=TEXT_UTF_8)
        second = verify.run_verification_checks(root, checks)
        self.assertEqual(self._count(root), 2)
        self.assertFalse(second[0].cached)

    def test_corrupt_cache_is_ignored(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        cache = root / TEXT_TOOLWRIGHT_CACHE_VERIFY_CACHE_JSON
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(TEXT_TEXT, encoding=TEXT_UTF_8)
        result = verify.run_verification_checks(root, checks)
        self.assertEqual(result[0].status, KEY_PASS)
        self.assertFalse(result[0].cached)
        self.assertEqual(self._count(root), 1)

    def test_generated_files_do_not_invalidate_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / KEY_SRC).mkdir()
            (root / TEXT_SRC_KEEP_TXT).write_text(KEY_ONE, encoding=TEXT_UTF_8)
            write_config(
                root,
                TEXT_VERIFY_CHECKS_CACHE_COMMAND_SH_C_ECHO_X_COUNTER_TXT_INPUTS_S,
            )
            checks, _ = verify.load_verification_config(root)
            verify.run_verification_checks(root, checks)
            (root / TEXT_SRC_PYCACHE).mkdir()
            (root / TEXT_SRC_PYCACHE_DROP_PYC).write_text(KEY_X, encoding=TEXT_UTF_8)
            verify.run_verification_checks(root, checks)
            self.assertEqual(len((root / TEXT_COUNTER_TXT).read_text(encoding=TEXT_UTF_8).splitlines()), 1)

    def test_absolute_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_INPUTS_ETC_PASSWD)
            with self.assertRaises(ToolWrightError):
                verify.load_verification_config(root)

    def test_invalid_validator_mode_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_GOVERNANCE_VALIDATOR_MODE_L,
            )
            with self.assertRaises(ToolWrightError):
                verify.load_verification_config(root)

    def test_missing_input_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_INPUTS_MISSING_TXT,
            )
            checks, _ = verify.load_verification_config(root)
            with self.assertRaises(ToolWrightError):
                verify.run_verification_checks(root, checks)


if __name__ == TEXT_MAIN:
    unittest.main()
