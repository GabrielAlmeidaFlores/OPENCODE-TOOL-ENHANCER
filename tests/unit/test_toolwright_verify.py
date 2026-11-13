"""
Unit tests for the deterministic verification engine.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import verify
from toolwright_cli.paths import ToolwrightError


def write_config(root: Path, body: str) -> Path:
    path = root / ".toolwright/config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class ConfigTests(unittest.TestCase):

    def test_loads_checks_and_governance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                '[verify]\ntimeout = 30\n\n[verify.checks.ok]\ncommand = "true"\n\n[governance]\nmax_iterations = 5\n',
            )
            checks, governance = verify.load_verification_config(root)
            self.assertEqual(checks["ok"].command, "true")
            self.assertEqual(checks["ok"].timeout, 30.0)
            self.assertEqual(governance["max_iterations"], 5)

    def test_missing_config_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ToolwrightError):
                verify.load_verification_config(Path(directory))

    def test_missing_verify_table_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, "[governance]\nmax_iterations = 5\n")
            with self.assertRaises(ToolwrightError):
                verify.load_verification_config(root)

    def test_missing_command_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, '[verify.checks.ok]\ntimeout = 5\n')
            with self.assertRaises(ToolwrightError):
                verify.load_verification_config(root)

    def test_invalid_check_name_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, '[verify.checks."bad name"]\ncommand = "true"\n')
            with self.assertRaises(ToolwrightError):
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
        self.assertEqual(results["ok"].status, "pass")
        self.assertEqual(results["fail"].failure_class, "command-failure")
        self.assertEqual(results["slow"].failure_class, "timeout")
        self.assertEqual(results["slow"].exit_code, 124)
        self.assertEqual(results["missing"].failure_class, "missing-command")
        self.assertEqual(results["missing"].exit_code, 127)

    def test_only_selects_checks(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        results = verify.run_verification_checks(root, checks, only=["ok"], use_cache=False)
        self.assertEqual([result.name for result in results], ["ok"])

    def test_unknown_only_check_is_an_error(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        with self.assertRaises(ToolwrightError):
            verify.run_verification_checks(root, checks, only=["nope"], use_cache=False)

    def test_summary_counts(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        results = verify.run_verification_checks(root, checks, only=["ok", "fail"], use_cache=False)
        summary = verify.summarize_results(results)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["status"], "fail")


class CacheTests(unittest.TestCase):

    def _root(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "input.txt").write_text("one", encoding="utf-8")
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
        path = root / "counter.txt"
        return len(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else 0

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
        (root / "input.txt").write_text("two", encoding="utf-8")
        second = verify.run_verification_checks(root, checks)
        self.assertEqual(self._count(root), 2)
        self.assertFalse(second[0].cached)

    def test_corrupt_cache_is_ignored(self) -> None:
        root = self._root()
        checks, _ = verify.load_verification_config(root)
        cache = root / ".toolwright/cache/verify/cache.json"
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text("[]", encoding="utf-8")
        result = verify.run_verification_checks(root, checks)
        self.assertEqual(result[0].status, "pass")
        self.assertFalse(result[0].cached)
        self.assertEqual(self._count(root), 1)

    def test_generated_files_do_not_invalidate_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/keep.txt").write_text("one", encoding="utf-8")
            write_config(
                root,
                '[verify.checks.cache]\ncommand = "sh -c \'echo x >> counter.txt\'"\ninputs = ["src"]\n',
            )
            checks, _ = verify.load_verification_config(root)
            verify.run_verification_checks(root, checks)
            (root / "src/__pycache__").mkdir()
            (root / "src/__pycache__/drop.pyc").write_text("x", encoding="utf-8")
            verify.run_verification_checks(root, checks)
            self.assertEqual(len((root / "counter.txt").read_text(encoding="utf-8").splitlines()), 1)

    def test_absolute_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, '[verify.checks.cache]\ncommand = "true"\ninputs = ["/etc/passwd"]\n')
            with self.assertRaises(ToolwrightError):
                verify.load_verification_config(root)

    def test_invalid_validator_mode_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                '[verify.checks.cache]\ncommand = "true"\n\n[governance]\nvalidator_mode = "loose"\n',
            )
            with self.assertRaises(ToolwrightError):
                verify.load_verification_config(root)

    def test_missing_input_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                '[verify.checks.cache]\ncommand = "true"\ninputs = ["missing.txt"]\n',
            )
            checks, _ = verify.load_verification_config(root)
            with self.assertRaises(ToolwrightError):
                verify.run_verification_checks(root, checks)


if __name__ == "__main__":
    unittest.main()
