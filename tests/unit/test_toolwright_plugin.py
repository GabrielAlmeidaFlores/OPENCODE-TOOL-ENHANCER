"""
Tests for the opt-in OpenCode memory plugin.
"""
from __future__ import annotations
from tests.unit.test_toolwright_plugin_strings import (
    FLAG_CHECK,
    KEY_FULL,
    KEY_NODE,
    KEY_PLUGIN,
    KEY_STANDARD,
    TEXT_CONFIGS_OPENCODE_PLUGINS_TOOLWRIGHT_MEMORY_JS,
    TEXT_MAIN,
    TEXT_NODE_IS_NOT_INSTALLED,
    TEXT_OPENCODE_PLUGINS_TOOLWRIGHT_MEMORY_JS,
    TEXT_TMP_TOOLWRIGHT_PLUGIN_TARGET,
)

import shutil
import subprocess
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import installer
from toolwright_cli.profiles import load_profiles

PLUGIN = support.REPO_ROOT / TEXT_CONFIGS_OPENCODE_PLUGINS_TOOLWRIGHT_MEMORY_JS


class PluginInstallTests(unittest.TestCase):
    def test_plugin_component_installs_the_file(self) -> None:
        target = Path(TEXT_TMP_TOOLWRIGHT_PLUGIN_TARGET)
        planned = installer.plan_files(support.REPO_ROOT, target, [KEY_PLUGIN])
        self.assertEqual(len(planned), 1)
        self.assertEqual(planned[0].destination, target / TEXT_OPENCODE_PLUGINS_TOOLWRIGHT_MEMORY_JS)

    def test_full_profile_includes_plugin(self) -> None:
        profiles = load_profiles(support.REPO_ROOT)
        self.assertIn(KEY_PLUGIN, profiles[KEY_FULL].components)
        self.assertNotIn(KEY_PLUGIN, profiles[KEY_STANDARD].components)


@unittest.skipUnless(shutil.which(KEY_NODE), TEXT_NODE_IS_NOT_INSTALLED)
class PluginSyntaxTests(unittest.TestCase):
    def test_plugin_parses(self) -> None:
        result = subprocess.run(
            [KEY_NODE, FLAG_CHECK, str(PLUGIN)],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == TEXT_MAIN:
    unittest.main()
