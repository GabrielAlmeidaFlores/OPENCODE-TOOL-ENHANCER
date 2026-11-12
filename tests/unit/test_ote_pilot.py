"""
Unit tests for the real-repository pilot runner.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli import pilot
from ote_cli.paths import OteError


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
            with self.assertRaises(OteError):
                pilot.load_pilots(root)


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
            with self.assertRaises(OteError):
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
        with self.assertRaises(OteError):
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
