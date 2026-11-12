"""
Unit tests for the ``ote`` command-line package.

Covers parser behaviour, version wiring, deferred commands, and lock file
handling. No test writes inside the repository working tree.
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from tests import support

import ote_cli
from ote_cli import cli, installer, locking
from ote_cli.process import capture
from ote_cli.paths import OteError


class VersionTests(unittest.TestCase):
    """
    Tests that the package version follows the repository VERSION file.
    """

    def test_version_matches_version_file(self) -> None:
        """
        The imported version equals VERSION.
        """
        expected = (support.REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(ote_cli.__version__, expected)

    def test_pyproject_version_matches_version_file(self) -> None:
        """
        The distributable metadata does not drift from VERSION.
        """
        expected = (support.REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        with (support.CLI_PACKAGE / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project["version"], expected)

    def test_package_has_no_runtime_dependencies(self) -> None:
        """
        The CLI stays on the standard library.
        """
        with (support.CLI_PACKAGE / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project.get("dependencies", []), [])


class ParserTests(unittest.TestCase):
    """
    Tests for argument parsing and command registration.
    """

    def test_version_flag(self) -> None:
        """
        --version prints the package version and exits zero.
        """
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
            cli.main(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn(ote_cli.__version__, stdout.getvalue())

    def test_install_rejects_apply_with_dry_run(self) -> None:
        """
        --apply and --dry-run are mutually exclusive.
        """
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            cli.main(["install", "--apply", "--dry-run"])
        self.assertEqual(raised.exception.code, 2)

    def test_deferred_command_exits_two(self) -> None:
        """
        A planned command reports its phase and exits with code 2.
        """
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(["catalog"])
        self.assertEqual(code, 2)
        self.assertIn("Phase 3", stderr.getvalue())

    def test_every_deferred_command_is_registered(self) -> None:
        """
        Each planned command is present in the parser help.
        """
        parser = cli._build_parser()
        actions = [action for action in parser._actions if getattr(action, "choices", None)]
        names = set(actions[0].choices) if actions else set()
        self.assertTrue(set(cli.DEFERRED).issubset(names))


class LockingTests(unittest.TestCase):
    """
    Tests for lock file construction and drift detection.
    """

    def test_sha256_file_matches_hashlib(self) -> None:
        """
        The digest equals hashlib for the same bytes.
        """
        import hashlib

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "file.txt"
            path.write_bytes(b"ote\n")
            self.assertEqual(locking.sha256_file(path), hashlib.sha256(b"ote\n").hexdigest())

    def test_write_read_round_trip(self) -> None:
        """
        A written lock can be read back and keeps its schema version.
        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ote.lock.json"
            locking.write_json(path, {"schema_version": 1, "files": []})
            lock = locking.read_lock(path)
            self.assertIsNotNone(lock)
            self.assertEqual(lock["schema_version"], 1)

    def test_unsupported_schema_version_is_rejected(self) -> None:
        """
        A future schema version is refused instead of misread.
        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ote.lock.json"
            path.write_text(json.dumps({"schema_version": 99, "files": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                locking.read_lock(path)

    def test_missing_file_is_not_an_error(self) -> None:
        """
        An absent lock returns None.
        """
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(locking.read_lock(Path(directory) / "absent.json"))

    def test_drift_reports_modified_and_missing(self) -> None:
        """
        Changed and removed files are reported separately.
        """
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "a.txt").write_text("new", encoding="utf-8")
            lock = {
                "files": [
                    {"path": "a.txt", "sha256": "0" * 64},
                    {"path": "b.txt", "sha256": "0" * 64},
                ]
            }
            drift = locking.lock_drift(lock, target)
            self.assertEqual(
                sorted(entry["status"] for entry in drift),
                ["missing", "modified"],
            )

    def test_build_lock_refuses_missing_destination(self) -> None:
        """
        A lock is not written when a planned file was not created.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            target = Path(directory) / "target"
            source = root / "a.txt"
            source.parent.mkdir(parents=True)
            source.write_text("x", encoding="utf-8")
            target.mkdir()
            planned = [locking.PlannedFile(source=source, destination=target / "a.txt", component="agents")]
            with self.assertRaises(FileNotFoundError):
                locking.build_lock(root, target, "minimal", ["agents"], planned, {"commit": "abc"})


class ComponentTests(unittest.TestCase):
    """
    Tests for profile and component resolution.
    """

    def test_profiles_are_ordered_and_known(self) -> None:
        """
        Profiles expose the documented component sets.
        """
        self.assertEqual(
            cli.PROFILES["minimal"]["components"],
            ["opencode", "agents", "commands", "skills", "ralph"],
        )
        self.assertIn("ast-grep", cli.PROFILES["standard"]["components"])
        self.assertIn("serena", cli.PROFILES["full"]["components"])

    def test_unknown_only_component_is_rejected(self) -> None:
        """
        An unknown component is an error, not a silent skip.
        """
        with self.assertRaises(OteError):
            cli.resolve_components("minimal", "agents,nonsense")

    def test_explicit_only_overrides_profile(self) -> None:
        """
        --only selects exactly the requested components.
        """
        self.assertEqual(cli.resolve_components("full", "agents,commands"), ["agents", "commands"])


class CaptureTests(unittest.TestCase):
    """
    Tests for external command capture behaviour.
    """

    def test_missing_command_returns_127(self) -> None:
        """
        A missing executable is reported as a normal failure instead of raising.
        """
        code, stdout, stderr = capture(["definitely-not-a-real-command-ote"])
        self.assertEqual(code, 127)
        self.assertEqual(stdout, "")
        self.assertIn("command not found", stderr)


class DoctorFailureTests(unittest.TestCase):
    """
    Tests that doctor reports failures instead of a clean summary.
    """

    def test_missing_repository_files_fail(self) -> None:
        """
        An empty directory fails repository, artifact, and validator checks.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checks = cli.run_checks(root, root, mcp=False)
            summary = cli.summarize(checks)
            self.assertGreater(summary["fail"], 0)
            self.assertIn("repository", {check.id for check in checks if check.status == "fail"})

    def test_json_output_has_summary(self) -> None:
        """
        The JSON form carries checks and a summary.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = cli.doctor_dict(cli.run_checks(root, root, mcp=False))
            self.assertIn("checks", payload)
            self.assertIn("summary", payload)


class SourceDigestTests(unittest.TestCase):
    """
    Tests that idempotency is keyed on source contents.
    """

    def test_digest_changes_with_source_content(self) -> None:
        """
        Editing an artifact invalidates the lock digest.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            target = Path(directory) / "target"
            source = root / "a.txt"
            source.parent.mkdir(parents=True)
            source.write_text("one", encoding="utf-8")
            target.mkdir()
            planned = [installer.PlannedFile(source=source, destination=target / "a.txt", component="agents")]
            first = installer.source_digest(planned, target)
            source.write_text("two", encoding="utf-8")
            second = installer.source_digest(planned, target)
            self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
