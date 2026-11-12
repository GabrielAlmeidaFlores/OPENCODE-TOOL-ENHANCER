"""
Unit tests for the ``ote`` command-line package.

Covers parser behaviour, version wiring, and lock file
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
from ote_cli.process import capture_command
from ote_cli.paths import OteError


class VersionTests(unittest.TestCase):

    def test_version_matches_version_file(self) -> None:
        expected = (support.REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(ote_cli.__version__, expected)

    def test_pyproject_version_matches_version_file(self) -> None:
        expected = (support.REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        with (support.CLI_PACKAGE / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project["version"], expected)

    def test_package_has_no_runtime_dependencies(self) -> None:
        with (support.CLI_PACKAGE / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project.get("dependencies", []), [])
        self.assertEqual(project.get("optional-dependencies", {}).get("catalog"), ["pyyaml>=6.0"])


class ParserTests(unittest.TestCase):

    def test_version_flag(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
            cli.main(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn(ote_cli.__version__, stdout.getvalue())

    def test_install_rejects_apply_with_dry_run(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            cli.main(["install", "--apply", "--dry-run"])
        self.assertEqual(raised.exception.code, 2)

class LockingTests(unittest.TestCase):

    def test_sha256_file_matches_hashlib(self) -> None:
        import hashlib

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "file.txt"
            path.write_bytes(b"ote\n")
            self.assertEqual(locking.sha256_file(path), hashlib.sha256(b"ote\n").hexdigest())

    def test_write_read_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ote.lock.json"
            locking.write_json(path, {"schema_version": 1, "files": []})
            lock = locking.read_lock(path)
            self.assertIsNotNone(lock)
            self.assertEqual(lock["schema_version"], 1)

    def test_unsupported_schema_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ote.lock.json"
            path.write_text(json.dumps({"schema_version": 99, "files": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                locking.read_lock(path)

    def test_missing_file_is_not_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(locking.read_lock(Path(directory) / "absent.json"))

    def test_drift_reports_modified_and_missing(self) -> None:
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

    def test_profiles_are_loaded_from_manifests(self) -> None:
        from ote_cli.profiles import load_profiles

        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(list(profiles["minimal"].components), ["opencode", "agents", "commands", "skills", "ralph"])
        self.assertIn("ast-grep", profiles["standard"].components)
        self.assertIn("serena", profiles["full"].components)

    def test_unknown_only_component_is_rejected(self) -> None:
        from ote_cli.profiles import load_profiles, resolve_components

        profiles = load_profiles(support.REPO_ROOT)
        with self.assertRaises(OteError):
            resolve_components(profiles, "minimal", "agents,nonsense")

    def test_explicit_only_overrides_profile(self) -> None:
        from ote_cli.profiles import load_profiles, resolve_components

        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(resolve_components(profiles, "full", "agents,commands"), ["agents", "commands"])


class CaptureTests(unittest.TestCase):

    def test_missing_command_returns_127(self) -> None:
        code, stdout, stderr = capture_command(["definitely-not-a-real-command-ote"])
        self.assertEqual(code, 127)
        self.assertEqual(stdout, "")
        self.assertIn("command not found", stderr)


class DoctorFailureTests(unittest.TestCase):

    def test_missing_repository_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checks = cli.run_diagnostic_checks(root, root, mcp=False)
            summary = cli.summarize_checks(checks)
            self.assertGreater(summary["fail"], 0)
            self.assertIn("repository", {check.id for check in checks if check.status == "fail"})

    def test_json_output_has_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = cli.doctor_dict(cli.run_diagnostic_checks(root, root, mcp=False))
            self.assertIn("checks", payload)
            self.assertIn("summary", payload)


class SourceDigestTests(unittest.TestCase):

    def test_digest_changes_with_source_content(self) -> None:
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
