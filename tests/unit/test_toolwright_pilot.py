"""
Unit tests for the real-repository pilot runner.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import support

from toolwright_cli import pilot
from toolwright_cli.profiles import load_profiles as real_profiles
from toolwright_cli.paths import ToolWrightError


class PilotConfigTests(unittest.TestCase):

    def test_expected_pilots_load(self) -> None:
        pilots = pilot.load_pilots(support.REPO_ROOT)
        self.assertEqual(sorted(pilots), ["clean-architecture", "hono", "turborepo"])
        self.assertEqual(pilots["hono"]["commit"], "f6fbaf0299c48eea9e656e03e2ffe7ac755e8823")

    def test_list_includes_stack_and_focus(self) -> None:
        pilots = pilot.list_pilots(support.REPO_ROOT)
        self.assertTrue(all(item["stack"] and item["focus"] for item in pilots))

    def test_missing_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "configs/pilots/pilots.toml"
            path.parent.mkdir(parents=True)
            path.write_text('[pilots.demo]\nrepository = "https://example.com/repo"\n', encoding="utf-8")
            with self.assertRaises(ToolWrightError):
                pilot.load_pilots(root)


class PilotExecutionTests(unittest.TestCase):
    def _run(self, opencode_exit: int):
        workspace_dir = tempfile.TemporaryDirectory()
        self.addCleanup(workspace_dir.cleanup)
        workspace = Path(workspace_dir.name) / "workspace"
        pilots = {
            "demo": {
                "repository": "https://example.com/demo.git",
                "commit": "a" * 40,
                "stack": "test",
                "focus": "test",
            }
        }
        session = json.dumps(
            {"type": "step_finish", "part": {"cost": 0.25, "tokens": {"input": 10, "output": 5}}}
        ) + "\n"

        captured = {}

        def fake_capture(args, cwd=None, env=None, timeout=600):
            if args[0] == "git":
                return 0, "", ""
            if args[0] == "opencode":
                captured["cwd"] = str(cwd)
                captured["pwd"] = (env or {}).get("PWD")
                captured["config"] = (env or {}).get("OPENCODE_CONFIG")
                return opencode_exit, session, "" if opencode_exit == 0 else "model failed"
            return 0, "verification ok", ""

        with mock.patch.object(pilot, "load_pilots", return_value=pilots), \
             mock.patch.object(pilot, "load_profiles", return_value=real_profiles(support.REPO_ROOT)), \
             mock.patch.object(pilot, "install"), \
             mock.patch.object(pilot, "capture_command", side_effect=fake_capture):
            result = pilot.run_pilot(
                root=support.REPO_ROOT,
                name="demo",
                workspace=workspace,
                prompt="do the task",
                verify_command="true",
                profile="minimal",
                keep=False,
                dry_run=False,
                model="provider/model",
            )
        self.assertEqual(captured["pwd"], str(workspace / "clone"))
        self.assertTrue(str(captured["config"]).endswith("opencode.jsonc"))
        return result

    def test_success_requires_both_exits(self) -> None:
        passing = self._run(0)
        self.assertTrue(passing["success"])
        self.assertTrue((Path(passing["workspace"]) / "artifacts/meta.json").is_file())
        self.assertTrue((Path(passing["workspace"]) / "artifacts/session.jsonl").is_file())
        self.assertTrue((Path(passing["workspace"]) / "artifacts/verification.log").is_file())
        self.assertAlmostEqual(passing["cost"], 0.25)

        failing = self._run(1)
        self.assertFalse(failing["success"])
        self.assertEqual(failing["opencode_exit"], 1)


class PilotRunTests(unittest.TestCase):

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            result = pilot.run_pilot(
                root=support.REPO_ROOT,
                name="hono",
                workspace=workspace,
                prompt=None,
                verify_command=None,
                profile="minimal",
                keep=False,
                dry_run=True,
                model=None,
            )
            self.assertTrue(result["dry_run"])
            self.assertFalse(workspace.exists())
            joined = "\n".join(result["steps"])
            self.assertIn("github.com/honojs/hono", joined)
            self.assertIn("f6fbaf0299c48eea9e656e03e2ffe7ac755e8823", joined)
            self.assertIn("checkout --detach", joined)

    def test_real_run_requires_prompt_and_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ToolWrightError):
                pilot.run_pilot(
                    root=support.REPO_ROOT,
                    name="hono",
                    workspace=Path(directory) / "workspace",
                    prompt=None,
                    verify_command="true",
                    profile="minimal",
                    keep=False,
                    dry_run=False,
                    model="provider/model",
                )

    def test_unknown_pilot_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            pilot.run_pilot(
                root=support.REPO_ROOT,
                name="nope",
                workspace=None,
                prompt="x",
                verify_command="true",
                profile="minimal",
                keep=False,
                dry_run=True,
                model=None,
            )


if __name__ == "__main__":
    unittest.main()
