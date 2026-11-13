"""
Tests for release version checks and offline upstream-drift reporting.
"""
from __future__ import annotations
from tests.unit.test_release_strings import (
    FLAG_FAIL_ON_DRIFT,
    FLAG_OFFLINE,
    FLAG_REGISTRY,
    FLAG_ROOT,
    FLAG_TAG,
    KEY_ADD,
    KEY_COMMIT,
    KEY_CONFIG,
    KEY_DEMO,
    KEY_DRIFT,
    KEY_GIT,
    KEY_INIT,
    KEY_MISMATCH,
    KEY_OFFLINE,
    KEY_ONE,
    KEY_REMOTE,
    KEY_TWO,
    KEY_YAML,
    TEXT_1_2,
    TEXT_1_2_3,
    TEXT_1_2_4,
    TEXT_C,
    TEXT_FILE_TXT,
    TEXT_HEAD,
    TEXT_MAIN,
    TEXT_PACKAGES_TOOLWRIGHT_CLI_PYPROJECT_TOML,
    TEXT_PYYAML_IS_NOT_INSTALLED,
    TEXT_Q,
    TEXT_QAM,
    TEXT_QM,
    TEXT_REGISTRY_YML,
    TEXT_REV_PARSE,
    TEXT_SCRIPTS_MAINTENANCE_CHECK_UPSTREAM_DRIFT_PY,
    TEXT_SCRIPTS_RELEASE_CHECK_VERSION_PY,
    TEXT_TEST,
    TEXT_TEST_EXAMPLE_COM,
    TEXT_TEXT,
    TEXT_USER_EMAIL,
    TEXT_USER_NAME,
    TEXT_UTF_8,
    TEXT_V1_2_3,
    TEXT_V9_9_9,
    TEXT_VERSION,
    TEXT_VERSION_1,
    TEXT_VERSION_OK,
)

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

CHECK_VERSION = support.REPO_ROOT / TEXT_SCRIPTS_RELEASE_CHECK_VERSION_PY
DRIFT = support.REPO_ROOT / TEXT_SCRIPTS_MAINTENANCE_CHECK_UPSTREAM_DRIFT_PY


class VersionCheckTests(unittest.TestCase):
    def _root(self, version: str, package_version: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / TEXT_VERSION).write_text(version + TEXT_TEXT, encoding=TEXT_UTF_8)
        package = root / TEXT_PACKAGES_TOOLWRIGHT_CLI_PYPROJECT_TOML
        package.parent.mkdir(parents=True)
        package.write_text(f'[project]\nname = "toolwright-cli"\nversion = "{package_version}"\n', encoding=TEXT_UTF_8)
        return root

    def _run(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_VERSION), FLAG_ROOT, str(root), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def test_matching_versions_pass(self) -> None:
        result = self._run(self._root(TEXT_1_2_3, TEXT_1_2_3))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_VERSION_OK, result.stdout)

    def test_mismatch_fails(self) -> None:
        result = self._run(self._root(TEXT_1_2_3, TEXT_1_2_4))
        self.assertEqual(result.returncode, 1)
        self.assertIn(KEY_MISMATCH, result.stderr)

    def test_invalid_semver_fails(self) -> None:
        result = self._run(self._root(TEXT_1_2, TEXT_1_2))
        self.assertEqual(result.returncode, 2)

    def test_tag_must_match(self) -> None:
        root = self._root(TEXT_1_2_3, TEXT_1_2_3)
        self.assertEqual(self._run(root, FLAG_TAG, TEXT_V1_2_3).returncode, 0)
        self.assertEqual(self._run(root, FLAG_TAG, TEXT_V9_9_9).returncode, 1)


@unittest.skipUnless(importlib.util.find_spec(KEY_YAML), TEXT_PYYAML_IS_NOT_INSTALLED)
class DriftOfflineTests(unittest.TestCase):
    def test_offline_lists_pins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / TEXT_REGISTRY_YML
            registry.write_text(
                "sources:\n"
                "  demo:\n"
                '    repository: "https://example.com/demo"\n'
                '    commit: "1234567890abcdef1234567890abcdef12345678"\n',
                encoding=TEXT_UTF_8,
            )
            result = subprocess.run(
                [sys.executable, str(DRIFT), FLAG_REGISTRY, str(registry), FLAG_OFFLINE],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(KEY_DEMO, result.stdout)
            self.assertIn(KEY_OFFLINE, result.stdout)

    def test_drift_exit_codes_with_local_remote(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / KEY_REMOTE
            remote.mkdir()
            git = [KEY_GIT, TEXT_C, str(remote)]
            subprocess.run([*git, KEY_INIT, TEXT_Q], check=True)
            subprocess.run([*git, KEY_CONFIG, TEXT_USER_EMAIL, TEXT_TEST_EXAMPLE_COM], check=True)
            subprocess.run([*git, KEY_CONFIG, TEXT_USER_NAME, TEXT_TEST], check=True)
            (remote / TEXT_FILE_TXT).write_text(KEY_ONE, encoding=TEXT_UTF_8)
            subprocess.run([*git, KEY_ADD, TEXT_FILE_TXT], check=True)
            subprocess.run([*git, KEY_COMMIT, TEXT_QM, KEY_ONE], check=True)
            pinned = subprocess.run([*git, TEXT_REV_PARSE, TEXT_HEAD], capture_output=True, text=True, check=True).stdout.strip()
            (remote / TEXT_FILE_TXT).write_text(KEY_TWO, encoding=TEXT_UTF_8)
            subprocess.run([*git, KEY_COMMIT, TEXT_QAM, KEY_TWO], check=True)
            registry = root / TEXT_REGISTRY_YML
            registry.write_text(
                "sources:\n"
                "  demo:\n"
                f'    repository: "{remote}"\n'
                f'    commit: "{pinned}"\n',
                encoding=TEXT_UTF_8,
            )
            base = [sys.executable, str(DRIFT), FLAG_REGISTRY, str(registry)]
            self.assertEqual(subprocess.run(base, capture_output=True, text=True, timeout=60).returncode, 0)
            failing = subprocess.run([*base, FLAG_FAIL_ON_DRIFT], capture_output=True, text=True, timeout=60)
            self.assertEqual(failing.returncode, 1)
            self.assertIn(KEY_DRIFT, failing.stdout)

    def test_missing_sources_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / TEXT_REGISTRY_YML
            registry.write_text(TEXT_VERSION_1, encoding=TEXT_UTF_8)
            result = subprocess.run(
                [sys.executable, str(DRIFT), FLAG_REGISTRY, str(registry), FLAG_OFFLINE],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == TEXT_MAIN:
    unittest.main()
