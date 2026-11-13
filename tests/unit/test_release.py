"""
Tests for release version checks and offline upstream-drift reporting.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

CHECK_VERSION = support.REPO_ROOT / "scripts/release/check_version.py"
DRIFT = support.REPO_ROOT / "scripts/maintenance/check_upstream_drift.py"


class VersionCheckTests(unittest.TestCase):
    def _root(self, version: str, package_version: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "VERSION").write_text(version + "\n", encoding="utf-8")
        package = root / "packages/toolwright_cli/pyproject.toml"
        package.parent.mkdir(parents=True)
        package.write_text(f'[project]\nname = "toolwright-cli"\nversion = "{package_version}"\n', encoding="utf-8")
        return root

    def _run(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_VERSION), "--root", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def test_matching_versions_pass(self) -> None:
        result = self._run(self._root("1.2.3", "1.2.3"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("version ok", result.stdout)

    def test_mismatch_fails(self) -> None:
        result = self._run(self._root("1.2.3", "1.2.4"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("mismatch", result.stderr)

    def test_invalid_semver_fails(self) -> None:
        result = self._run(self._root("1.2", "1.2"))
        self.assertEqual(result.returncode, 2)

    def test_tag_must_match(self) -> None:
        root = self._root("1.2.3", "1.2.3")
        self.assertEqual(self._run(root, "--tag", "v1.2.3").returncode, 0)
        self.assertEqual(self._run(root, "--tag", "v9.9.9").returncode, 1)


@unittest.skipUnless(importlib.util.find_spec("yaml"), "PyYAML is not installed")
class DriftOfflineTests(unittest.TestCase):
    def test_offline_lists_pins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry.yml"
            registry.write_text(
                "sources:\n"
                "  demo:\n"
                '    repository: "https://example.com/demo"\n'
                '    commit: "1234567890abcdef1234567890abcdef12345678"\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(DRIFT), "--registry", str(registry), "--offline"],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("demo", result.stdout)
            self.assertIn("offline", result.stdout)

    def test_drift_exit_codes_with_local_remote(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "remote"
            remote.mkdir()
            git = ["git", "-C", str(remote)]
            subprocess.run([*git, "init", "-q"], check=True)
            subprocess.run([*git, "config", "user.email", "test@example.com"], check=True)
            subprocess.run([*git, "config", "user.name", "Test"], check=True)
            (remote / "file.txt").write_text("one", encoding="utf-8")
            subprocess.run([*git, "add", "file.txt"], check=True)
            subprocess.run([*git, "commit", "-qm", "one"], check=True)
            pinned = subprocess.run([*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            (remote / "file.txt").write_text("two", encoding="utf-8")
            subprocess.run([*git, "commit", "-qam", "two"], check=True)
            registry = root / "registry.yml"
            registry.write_text(
                "sources:\n"
                "  demo:\n"
                f'    repository: "{remote}"\n'
                f'    commit: "{pinned}"\n',
                encoding="utf-8",
            )
            base = [sys.executable, str(DRIFT), "--registry", str(registry)]
            self.assertEqual(subprocess.run(base, capture_output=True, text=True, timeout=60).returncode, 0)
            failing = subprocess.run([*base, "--fail-on-drift"], capture_output=True, text=True, timeout=60)
            self.assertEqual(failing.returncode, 1)
            self.assertIn("drift", failing.stdout)

    def test_missing_sources_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "registry.yml"
            registry.write_text("version: 1\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(DRIFT), "--registry", str(registry), "--offline"],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
