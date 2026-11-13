"""
Integration tests for validation entry points and the benchmark harness.

These tests execute the real shell and Python entry points. They require no
network access and no model credentials.
"""
from __future__ import annotations
from tests.integration.test_entrypoints_strings import (
    TEXT_PATH_SUFFIX,
    TEXT_TASK_ERROR,
)
from tests.integration.test_entrypoints_strings import (
    FLAG_ARM,
    FLAG_DRY_RUN,
    FLAG_ONLY,
    FLAG_TARGET,
    FLAG_TASK,
    KEY_AGENTS,
    KEY_BASELINE,
    KEY_BASH,
    KEY_NONSENSE,
    KEY_PROJECT,
    KEY_PYTHON3,
    TEXT_BENCHMARKS_HARNESS_RUN_SH,
    TEXT_BENCHMARKS_TASKS,
    TEXT_CHECKED_D,
    TEXT_DEFAULT_MODE_MUST_NOT_CREATE_THE_TARGET,
    TEXT_HOME,
    TEXT_JSON,
    TEXT_MAIN,
    TEXT_MISSING_JSON,
    TEXT_NO_BENCHMARK_TASKS_FOUND,
    TEXT_OK,
    TEXT_PATH,
    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_SH,
    TEXT_TASK_NOT_FOUND,
    TEXT_TOOLWRIGHT_INSTALL,
    TEXT_UNKNOWN_ARM,
    TEXT_WOULD_RUN,
)

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT
PYTHON_BIN = Path(sys.executable).parent
SAFE_PATH = str(PYTHON_BIN) + TEXT_PATH_SUFFIX


class ValidationEntryPointTests(unittest.TestCase):

    def test_validate_config_script_passes(self) -> None:
        result = subprocess.run(
            [KEY_PYTHON3, TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_OK, result.stdout)

    def test_validate_shell_entrypoint_passes(self) -> None:
        result = subprocess.run(
            [KEY_BASH, TEXT_SCRIPTS_VALIDATION_VALIDATE_SH],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_reports_checked_count(self) -> None:
        result = subprocess.run(
            [KEY_PYTHON3, TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        self.assertRegex(result.stdout, TEXT_CHECKED_D)


class BenchmarkHarnessTests(unittest.TestCase):

    def test_every_task_supports_dry_run_without_opencode(self) -> None:
        tasks = sorted((REPO_ROOT / TEXT_BENCHMARKS_TASKS).glob(TEXT_JSON))
        self.assertTrue(tasks, TEXT_NO_BENCHMARK_TASKS_FOUND)
        for task in tasks:
            result = subprocess.run(
                [KEY_BASH, TEXT_BENCHMARKS_HARNESS_RUN_SH, FLAG_ARM, KEY_BASELINE, FLAG_TASK, str(task), FLAG_DRY_RUN],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                env={TEXT_PATH: SAFE_PATH, TEXT_HOME: str(REPO_ROOT)},
            )
            self.assertEqual(result.returncode, 0, TEXT_TASK_ERROR.format(task.name, result.stderr))
            self.assertIn(TEXT_WOULD_RUN, result.stdout, task.name)

    def test_dry_run_rejects_unknown_arm(self) -> None:
        task = next((REPO_ROOT / TEXT_BENCHMARKS_TASKS).glob(TEXT_JSON))
        result = subprocess.run(
            [KEY_BASH, TEXT_BENCHMARKS_HARNESS_RUN_SH, FLAG_ARM, KEY_NONSENSE, FLAG_TASK, str(task), FLAG_DRY_RUN],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(TEXT_UNKNOWN_ARM, result.stdout + result.stderr)

    def test_dry_run_rejects_missing_task(self) -> None:
        result = subprocess.run(
            [KEY_BASH, TEXT_BENCHMARKS_HARNESS_RUN_SH, FLAG_ARM, KEY_BASELINE, FLAG_TASK, TEXT_MISSING_JSON, FLAG_DRY_RUN],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(TEXT_TASK_NOT_FOUND, result.stdout + result.stderr)


class InstallationDryRunTests(unittest.TestCase):

    def test_default_mode_is_check_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_INSTALL) as directory:
            target = Path(directory) / KEY_PROJECT
            result = subprocess.run(
                [KEY_BASH, TEXT_SCRIPTS_INSTALLATION_INSTALL_SH, FLAG_TARGET, str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists(), TEXT_DEFAULT_MODE_MUST_NOT_CREATE_THE_TARGET)

    def test_dry_run_lists_planned_actions(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_INSTALL) as directory:
            target = Path(directory) / KEY_PROJECT
            result = subprocess.run(
                [KEY_BASH, TEXT_SCRIPTS_INSTALLATION_INSTALL_SH, FLAG_DRY_RUN, FLAG_ONLY, KEY_AGENTS, FLAG_TARGET, str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(KEY_AGENTS, result.stdout)
            self.assertFalse(target.exists())


if __name__ == TEXT_MAIN:
    unittest.main()
