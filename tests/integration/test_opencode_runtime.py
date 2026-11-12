"""
Integration tests for OpenCode runtime discovery.

The tests skip cleanly when the OpenCode binary is unavailable. They install the
repository artifacts into a temporary target so the working tree is never
modified.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT


def _opencode() -> str | None:
    """
    Return the OpenCode executable path when available.
    """
    return shutil.which("opencode")


@unittest.skipUnless(_opencode(), "opencode binary is not installed")
class AgentDiscoveryTests(unittest.TestCase):
    """
    Tests for agent discovery through the OpenCode CLI.
    """

    def test_all_agents_are_discovered(self) -> None:
        """
        Installing the agents exposes all twelve agents to OpenCode V2.
        """
        with tempfile.TemporaryDirectory(prefix="ote-discovery-") as directory:
            target = Path(directory)
            install = subprocess.run(
                [
                    "bash",
                    "scripts/installation/install.sh",
                    "--apply",
                    "--only",
                    "agents",
                    "--target",
                    str(target),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            config = target / ".opencode" / "opencode.jsonc"
            shutil.copyfile(REPO_ROOT / "configs/opencode/minimal.jsonc", config)
            environment = dict(os.environ)
            environment["OPENCODE_CONFIG"] = str(config)
            result = subprocess.run(
                ["opencode", "--standalone", "debug", "agents"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            agents = json.loads(result.stdout)
            identifiers = {agent["id"] for agent in agents}
            self.assertEqual(sorted(identifiers & set(support.AGENT_ROLES)), sorted(support.AGENT_ROLES))

    def test_coordinator_is_primary(self) -> None:
        """
        The coordinator is exposed with primary mode.
        """
        with tempfile.TemporaryDirectory(prefix="ote-discovery-") as directory:
            target = Path(directory)
            subprocess.run(
                [
                    "bash",
                    "scripts/installation/install.sh",
                    "--apply",
                    "--only",
                    "agents",
                    "--target",
                    str(target),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )
            config = target / ".opencode" / "opencode.jsonc"
            shutil.copyfile(REPO_ROOT / "configs/opencode/minimal.jsonc", config)
            environment = dict(os.environ)
            environment["OPENCODE_CONFIG"] = str(config)
            result = subprocess.run(
                ["opencode", "--standalone", "debug", "agents"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
                env=environment,
            )
            agents = json.loads(result.stdout)
            coordinator = next(agent for agent in agents if agent["id"] == "coordinator")
            self.assertEqual(coordinator["mode"], "primary")


@unittest.skipUnless(_opencode(), "opencode binary is not installed")
class ConfigurationValidationTests(unittest.TestCase):
    """
    Tests that the shipped configurations parse in OpenCode V2.
    """

    def test_minimal_profile_parses(self) -> None:
        """
        The minimal profile is accepted by the OpenCode configuration loader.
        """
        result = subprocess.run(
            ["opencode", "--standalone", "debug", "config"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
            env={**os.environ, "OPENCODE_CONFIG": str(REPO_ROOT / "configs/opencode/minimal.jsonc")},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed, "configuration loader returned no sources")


if __name__ == "__main__":
    unittest.main()
