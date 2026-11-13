"""
Integration tests for validation entry points and the benchmark harness.

These tests execute the real shell and Python entry points. They require no
network access and no model credentials.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT
PYTHON_BIN = Path(sys.executable).parent
SAFE_PATH = f"{PYTHON_BIN}:/usr/bin:/bin"


class ValidationEntryPointTests(unittest.TestCase):

    def test_validate_config_script_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/validation/validate_config.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_validate_shell_entrypoint_passes(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/validation/validate.sh"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_reports_checked_count(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/validation/validate_config.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        self.assertRegex(result.stdout, r"checked: \d+")


class BenchmarkHarnessTests(unittest.TestCase):

    def test_every_task_supports_dry_run_without_opencode(self) -> None:
        tasks = sorted((REPO_ROOT / "benchmarks/tasks").glob("*.json"))
        self.assertTrue(tasks, "no benchmark tasks found")
        for task in tasks:
            result = subprocess.run(
                ["bash", "benchmarks/harness/run.sh", "--arm", "baseline", "--task", str(task), "--dry-run"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                env={"PATH": SAFE_PATH, "HOME": str(REPO_ROOT)},
            )
            self.assertEqual(result.returncode, 0, f"{task.name}: {result.stderr}")
            self.assertIn("would run:", result.stdout, task.name)

    def test_dry_run_rejects_unknown_arm(self) -> None:
        task = next((REPO_ROOT / "benchmarks/tasks").glob("*.json"))
        result = subprocess.run(
            ["bash", "benchmarks/harness/run.sh", "--arm", "nonsense", "--task", str(task), "--dry-run"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown arm", result.stdout + result.stderr)

    def test_dry_run_rejects_missing_task(self) -> None:
        result = subprocess.run(
            ["bash", "benchmarks/harness/run.sh", "--arm", "baseline", "--task", "missing.json", "--dry-run"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("task not found", result.stdout + result.stderr)


class InstallationDryRunTests(unittest.TestCase):

    def test_default_mode_is_check_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="toolwright-install-") as directory:
            target = Path(directory) / "project"
            result = subprocess.run(
                ["bash", "scripts/installation/install.sh", "--target", str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists(), "default mode must not create the target")

    def test_dry_run_lists_planned_actions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="toolwright-install-") as directory:
            target = Path(directory) / "project"
            result = subprocess.run(
                ["bash", "scripts/installation/install.sh", "--dry-run", "--only", "agents", "--target", str(target)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("agents", result.stdout)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
