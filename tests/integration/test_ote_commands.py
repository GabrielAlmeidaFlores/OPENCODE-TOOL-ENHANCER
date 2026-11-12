"""
Integration tests for the ``ote`` command line.

The tests execute the real CLI as a subprocess against temporary targets. They
require no network access and never write inside the repository.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT


def run_ote(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """
    Run the CLI module with the package on PYTHONPATH.
    """
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(support.CLI_PACKAGE)
    return subprocess.run(
        [sys.executable, "-m", "ote_cli", *args],
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        env=environment,
    )


class DoctorCommandTests(unittest.TestCase):
    """
    Tests for ``ote doctor`` against the real repository.
    """

    @unittest.skipUnless(shutil.which("opencode"), "opencode binary is not installed")
    def test_doctor_json_reports_no_failures(self) -> None:
        """
        Doctor exits zero and emits a machine-readable summary.
        """
        result = run_ote("doctor", "--json", "--no-mcp")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("checks", payload)
        self.assertEqual(payload["summary"]["fail"], 0)
        identifiers = {check["id"] for check in payload["checks"]}
        self.assertTrue({"python", "repository", "opencode", "validator"}.issubset(identifiers))

    def test_doctor_text_mode_lists_checks(self) -> None:
        """
        Text mode prints one line per check and a summary.
        """
        result = run_ote("doctor", "--no-mcp")
        self.assertIn("python", result.stdout)
        self.assertIn("summary:", result.stdout)


class InstallLifecycleTests(unittest.TestCase):
    """
    Tests for install, update, and uninstall across a temporary target.
    """

    def setUp(self) -> None:
        """
        Create a temporary target directory.
        """
        self.directory = tempfile.TemporaryDirectory(prefix="ote-cli-")
        self.addCleanup(self.directory.cleanup)
        self.target = Path(self.directory.name) / "project"

    def test_dry_run_writes_nothing(self) -> None:
        """
        The default plan lists files and leaves the target absent.
        """
        result = run_ote("install", "--profile", "minimal", "--target", str(self.target), "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("plan only", result.stdout)
        self.assertIn(".opencode/agents/coordinator.md", result.stdout)
        self.assertFalse(self.target.exists())

    def test_apply_creates_lock_and_state(self) -> None:
        """
        Apply writes artifacts, a lock with digests, and state.
        """
        result = run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.target / ".opencode/agents/coordinator.md").is_file())
        lock = json.loads((self.target / "ote.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["schema_version"], 1)
        self.assertEqual(lock["profile"], "minimal")
        self.assertTrue(lock["files"])
        for entry in lock["files"]:
            path = self.target / entry["path"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, entry["sha256"], entry["path"])
        self.assertTrue((self.target / ".ote/state.json").is_file())

    def test_reapply_is_idempotent(self) -> None:
        """
        A second apply reports no work and does not rewrite the lock.
        """
        first = run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        self.assertEqual(first.returncode, 0, first.stderr)
        lock_path = self.target / "ote.lock.json"
        before = lock_path.read_bytes()
        second = run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already up to date", second.stdout)
        self.assertEqual(lock_path.read_bytes(), before)

    def test_force_creates_backup(self) -> None:
        """
        --force re-runs the installer and archives the previous configuration.
        """
        run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        result = run_ote(
            "install", "--profile", "minimal", "--target", str(self.target), "--apply", "--force"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((self.target / ".ote/backups").iterdir())
        self.assertTrue(backups, "expected a CLI backup directory")
        archives = {archive.name for backup in backups for archive in backup.glob("*.tar.gz")}
        self.assertIn("project-opencode.tar.gz", archives)
        self.assertNotIn("global-config.tar.gz", archives)

    def test_reapply_refreshes_stale_source_commit(self) -> None:
        """
        A no-op apply updates the recorded commit so update checks stay clean.
        """
        run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        lock_path = self.target / "ote.lock.json"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["source"]["commit"] = "0" * 40
        lock_path.write_text(json.dumps(lock, indent=2), encoding="utf-8")
        applied = run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        refreshed = json.loads(lock_path.read_text(encoding="utf-8"))
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(refreshed["source"]["commit"], head)
        update = run_ote("update", "--target", str(self.target), "--check")
        self.assertEqual(update.returncode, 0, update.stdout + update.stderr)

    def test_update_detects_modified_file(self) -> None:
        """
        A tampered managed file makes update --check exit non-zero.
        """
        run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        clean = run_ote("update", "--target", str(self.target), "--check")
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        with (self.target / ".opencode/agents/coordinator.md").open("a", encoding="utf-8") as handle:
            handle.write("\ntampered\n")
        dirty = run_ote("update", "--target", str(self.target), "--check")
        self.assertEqual(dirty.returncode, 1, dirty.stdout + dirty.stderr)
        self.assertIn("modified", dirty.stdout)

    def test_uninstall_requires_confirmation(self) -> None:
        """
        --apply without --yes is refused.
        """
        run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        result = run_ote("uninstall", "--target", str(self.target), "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--yes", result.stderr)

    def test_uninstall_plan_keeps_files(self) -> None:
        """
        Planning a removal changes nothing.
        """
        run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        result = run_ote("uninstall", "--target", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("remove .opencode/agents/coordinator.md", result.stdout)
        self.assertTrue((self.target / ".opencode/agents/coordinator.md").is_file())

    def test_uninstall_apply_removes_managed_files(self) -> None:
        """
        Confirmed removal deletes unmodified managed files.
        """
        run_ote("install", "--profile", "minimal", "--target", str(self.target), "--apply")
        result = run_ote("uninstall", "--target", str(self.target), "--apply", "--yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.target / ".opencode/agents/coordinator.md").exists())
        self.assertTrue((self.target / "ote.lock.json").is_file())


class ProfileAndCatalogTests(unittest.TestCase):
    """
    Tests for the Phase 3 profile, catalog, and compatibility commands.
    """

    def test_profile_list(self) -> None:
        """
        Profile list prints every manifest.
        """
        result = run_ote("profile", "list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("minimal", "standard", "full"):
            self.assertIn(name, result.stdout)

    def test_profile_show(self) -> None:
        """
        Profile show prints components from the manifest.
        """
        result = run_ote("profile", "show", "standard")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ast-grep", result.stdout)

    def test_profile_verify(self) -> None:
        """
        Profile verify validates every manifest.
        """
        result = run_ote("profile", "verify")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_profile_use_dry_run(self) -> None:
        """
        Profile use plans an installation without writing.
        """
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            result = run_ote("profile", "use", "minimal", "--target", str(target), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("plan only", result.stdout)
            self.assertFalse(target.exists())

    def test_catalog_list_and_search(self) -> None:
        """
        Catalog list and search read the generated catalog.
        """
        listed = run_ote("catalog", "list", "--type", "agent")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("coordinator", listed.stdout)
        found = run_ote("catalog", "search", "security")
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertIn("security", found.stdout)

    def test_catalog_verify(self) -> None:
        """
        Catalog verify validates entries and local paths.
        """
        result = run_ote("catalog", "verify")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 failure(s)", result.stdout)

    def test_compat_json(self) -> None:
        """
        Compatibility output is machine-readable.
        """
        result = run_ote("compat", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["tool"], "opencode")
        self.assertTrue(payload["features"])


class VerificationCommandTests(unittest.TestCase):
    """
    Tests for ote verify and ote govern.
    """

    def _config(self, directory: str) -> Path:
        """
        Write a minimal verification configuration in a temporary directory.
        """
        path = Path(directory) / "config.toml"
        path.write_text(
            '[verify]\ntimeout = 10\n'
            '[verify.checks.ok]\ncommand = "true"\n'
            '[verify.checks.fail]\ncommand = "sh -c \'exit 3\'"\n',
            encoding="utf-8",
        )
        return path

    def test_verify_pass_and_fail(self) -> None:
        """
        Verify reports pass and exit codes for configured checks.
        """
        with tempfile.TemporaryDirectory() as directory:
            config = self._config(directory)
            passed = run_ote("verify", "--config", str(config), "--only", "ok", "--json")
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertEqual(json.loads(passed.stdout)["summary"]["status"], "pass")
            failed = run_ote("verify", "--config", str(config), "--only", "fail", "--json")
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads(failed.stdout)["summary"]["failed"], 1)

    def test_govern_contracts(self) -> None:
        """
        Contracts are derived from agent permissions.
        """
        result = run_ote("govern", "contracts")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("coordinator", result.stdout)
        self.assertIn("0 failure(s)", result.stdout)

    def test_govern_gate(self) -> None:
        """
        Risk gates are machine-readable.
        """
        result = run_ote("govern", "gate", "--risk", "high", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["required"], ["verify", "review", "security"])

    def test_govern_check(self) -> None:
        """
        A record over budget is blocked with a non-zero exit.
        """
        with tempfile.TemporaryDirectory() as directory:
            record = Path(directory) / "record.json"
            record.write_text(json.dumps({"iterations": 999}), encoding="utf-8")
            result = run_ote("govern", "check", "--record", str(record), "--json")
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["allowed"])


class MemoryAndSpecReadTests(unittest.TestCase):
    """
    Read-only checks for memory and spec commands against the repository.
    """

    def test_memory_search_and_export(self) -> None:
        """
        Searching and exporting memory do not require entries to exist.
        """
        search = run_ote("memory", "search", "decision")
        self.assertEqual(search.returncode, 0, search.stderr)
        exported = run_ote("memory", "export", "--format", "json")
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertIn("entries", json.loads(exported.stdout))

    def test_memory_preamble(self) -> None:
        """
        The preamble renders within its budget.
        """
        result = run_ote("memory", "preamble", "--budget", "100")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Project Memory", result.stdout)

    def test_spec_list(self) -> None:
        """
        Listing specs works even when only the README exists.
        """
        result = run_ote("spec", "list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("spec(s)", result.stdout)


class CommandSurfaceTests(unittest.TestCase):
    """
    Tests for command registration and safety defaults.
    """

    def test_deferred_command_exits_two(self) -> None:
        """
        A planned command reports the owning phase.
        """
        result = run_ote("stats")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Phase 6", result.stderr)

    def test_rollback_without_backups(self) -> None:
        """
        Rollback lists an empty backup set without failing.
        """
        with tempfile.TemporaryDirectory() as directory:
            result = run_ote("rollback", "--target", directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("no backups", result.stdout)

    def test_help_lists_commands(self) -> None:
        """
        The help output exposes the implemented and planned commands.
        """
        result = run_ote("--help")
        self.assertEqual(result.returncode, 0)
        for command in ("doctor", "install", "uninstall", "update", "rollback", "catalog"):
            self.assertIn(command, result.stdout)


if __name__ == "__main__":
    unittest.main()
