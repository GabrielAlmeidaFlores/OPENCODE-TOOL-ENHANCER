"""
Unit tests for the deterministic verification engine.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli import verify
from ote_cli.paths import OteError


def write_config(root: Path, body: str) -> Path:
    """
    Write a verification configuration under a temporary root.
    """
    path = root / ".ote/config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class ConfigTests(unittest.TestCase):
    """
    Tests for loading and validating ``.ote/config.toml``.
    """

    def test_loads_checks_and_governance(self) -> None:
        """
        Checks inherit the default timeout and governance values are returned.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                '[verify]\ntimeout = 30\n\n[verify.checks.ok]\ncommand = "true"\n\n[governance]\nmax_iterations = 5\n',
            )
            checks, governance = verify.load_config(root)
            self.assertEqual(checks["ok"].command, "true")
            self.assertEqual(checks["ok"].timeout, 30.0)
            self.assertEqual(governance["max_iterations"], 5)

    def test_missing_config_is_an_error(self) -> None:
        """
        A missing file points at the expected path.
        """
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OteError):
                verify.load_config(Path(directory))

    def test_missing_verify_table_is_an_error(self) -> None:
        """
        A configuration without [verify] is rejected.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, "[governance]\nmax_iterations = 5\n")
            with self.assertRaises(OteError):
                verify.load_config(root)

    def test_missing_command_is_an_error(self) -> None:
        """
        A check without a command is rejected.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, '[verify.checks.ok]\ntimeout = 5\n')
            with self.assertRaises(OteError):
                verify.load_config(root)

    def test_invalid_check_name_is_an_error(self) -> None:
        """
        Check names must be safe identifiers.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, '[verify.checks."bad name"]\ncommand = "true"\n')
            with self.assertRaises(OteError):
                verify.load_config(root)


class ExecutionTests(unittest.TestCase):
    """
    Tests for running checks and classifying failures.
    """

    def _root(self) -> Path:
        """
        Create a temporary root with representative checks.
        """
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
                '[verify.checks.missing]\ncommand = "definitely-not-a-command-ote"\n'
            ),
        )
        return root

    def test_pass_and_failure_classes(self) -> None:
        """
        Success, command failure, timeout, and missing commands are distinguished.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        results = {result.name: result for result in verify.run_checks(root, checks, use_cache=False)}
        self.assertEqual(results["ok"].status, "pass")
        self.assertEqual(results["fail"].failure_class, "command-failure")
        self.assertEqual(results["slow"].failure_class, "timeout")
        self.assertEqual(results["slow"].exit_code, 124)
        self.assertEqual(results["missing"].failure_class, "missing-command")
        self.assertEqual(results["missing"].exit_code, 127)

    def test_only_selects_checks(self) -> None:
        """
        Only the requested checks run.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        results = verify.run_checks(root, checks, only=["ok"], use_cache=False)
        self.assertEqual([result.name for result in results], ["ok"])

    def test_unknown_only_check_is_an_error(self) -> None:
        """
        An unknown check name is rejected.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        with self.assertRaises(OteError):
            verify.run_checks(root, checks, only=["nope"], use_cache=False)

    def test_summary_counts(self) -> None:
        """
        The summary reports pass and failure counts.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        results = verify.run_checks(root, checks, only=["ok", "fail"], use_cache=False)
        summary = verify.summarize(results)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["status"], "fail")


class CacheTests(unittest.TestCase):
    """
    Tests for the input-hash execution cache.
    """

    def _root(self) -> Path:
        """
        Create a root whose check appends to a counter and declares an input.
        """
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
        """
        Return the number of recorded executions.
        """
        path = root / "counter.txt"
        return len(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else 0

    def test_second_run_uses_cache(self) -> None:
        """
        An unchanged input reuses the cached pass.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        verify.run_checks(root, checks)
        second = verify.run_checks(root, checks)
        self.assertEqual(self._count(root), 1)
        self.assertTrue(second[0].cached)

    def test_no_cache_forces_execution(self) -> None:
        """
        --no-cache ignores and does not use the cache.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        verify.run_checks(root, checks)
        verify.run_checks(root, checks, use_cache=False)
        self.assertEqual(self._count(root), 2)

    def test_input_change_invalidates_cache(self) -> None:
        """
        Editing a declared input re-runs the check.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        verify.run_checks(root, checks)
        (root / "input.txt").write_text("two", encoding="utf-8")
        second = verify.run_checks(root, checks)
        self.assertEqual(self._count(root), 2)
        self.assertFalse(second[0].cached)

    def test_corrupt_cache_is_ignored(self) -> None:
        """
        A cache file with the wrong shape is ignored and the check runs.
        """
        root = self._root()
        checks, _ = verify.load_config(root)
        cache = root / ".ote/cache/verify/cache.json"
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text("[]", encoding="utf-8")
        result = verify.run_checks(root, checks)
        self.assertEqual(result[0].status, "pass")
        self.assertFalse(result[0].cached)
        self.assertEqual(self._count(root), 1)

    def test_generated_files_do_not_invalidate_cache(self) -> None:
        """
        Creating a __pycache__ entry does not change the input digest.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/keep.txt").write_text("one", encoding="utf-8")
            write_config(
                root,
                '[verify.checks.cache]\ncommand = "sh -c \'echo x >> counter.txt\'"\ninputs = ["src"]\n',
            )
            checks, _ = verify.load_config(root)
            verify.run_checks(root, checks)
            (root / "src/__pycache__").mkdir()
            (root / "src/__pycache__/drop.pyc").write_text("x", encoding="utf-8")
            verify.run_checks(root, checks)
            self.assertEqual(len((root / "counter.txt").read_text(encoding="utf-8").splitlines()), 1)

    def test_absolute_input_is_rejected(self) -> None:
        """
        Input paths must stay inside the repository.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(root, '[verify.checks.cache]\ncommand = "true"\ninputs = ["/etc/passwd"]\n')
            with self.assertRaises(OteError):
                verify.load_config(root)

    def test_invalid_validator_mode_is_rejected(self) -> None:
        """
        Only off, advisory, and strict are accepted.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                '[verify.checks.cache]\ncommand = "true"\n\n[governance]\nvalidator_mode = "loose"\n',
            )
            with self.assertRaises(OteError):
                verify.load_config(root)

    def test_missing_input_is_an_error(self) -> None:
        """
        A declared input that does not exist is rejected instead of ignored.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_config(
                root,
                '[verify.checks.cache]\ncommand = "true"\ninputs = ["missing.txt"]\n',
            )
            checks, _ = verify.load_config(root)
            with self.assertRaises(OteError):
                verify.run_checks(root, checks)


if __name__ == "__main__":
    unittest.main()
