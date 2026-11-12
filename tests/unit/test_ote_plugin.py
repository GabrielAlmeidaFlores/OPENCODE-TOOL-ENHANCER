"""
Tests for the opt-in OpenCode memory plugin.
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from tests import support

from ote_cli import installer
from ote_cli.profiles import load_profiles

PLUGIN = support.REPO_ROOT / "configs/opencode/plugins/ote-memory.js"


class PluginInstallTests(unittest.TestCase):
    def test_plugin_component_installs_the_file(self) -> None:
        target = Path("/tmp/ote-plugin-target")
        planned = installer.plan_files(support.REPO_ROOT, target, ["plugin"])
        self.assertEqual(len(planned), 1)
        self.assertEqual(planned[0].destination, target / ".opencode/plugins/ote-memory.js")

    def test_full_profile_includes_plugin(self) -> None:
        profiles = load_profiles(support.REPO_ROOT)
        self.assertIn("plugin", profiles["full"].components)
        self.assertNotIn("plugin", profiles["standard"].components)


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class PluginSyntaxTests(unittest.TestCase):
    def test_plugin_parses(self) -> None:
        result = subprocess.run(
            ["node", "--check", str(PLUGIN)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
