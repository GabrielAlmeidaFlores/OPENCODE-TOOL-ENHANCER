"""
Integration tests for OpenCode runtime discovery.

The tests skip cleanly when the OpenCode binary is unavailable. They install the
repository artifacts into a temporary target so the working tree is never
modified.
"""
from __future__ import annotations
from tests.integration.test_opencode_runtime_strings import (
    FLAG_APPLY,
    FLAG_ONLY,
    FLAG_STANDALONE,
    FLAG_TARGET,
    KEY_AGENTS,
    KEY_BASH,
    KEY_CONFIG,
    KEY_COORDINATOR,
    KEY_DEBUG,
    KEY_ID,
    KEY_MODE,
    KEY_OPENCODE,
    KEY_PRIMARY,
    TEXT_CONFIGS_OPENCODE_MINIMAL_JSONC,
    TEXT_CONFIGURATION_LOADER_RETURNED_NO_SOURCES,
    TEXT_MAIN,
    TEXT_OPENCODE,
    TEXT_OPENCODE_BINARY_IS_NOT_INSTALLED,
    TEXT_OPENCODE_CONFIG,
    TEXT_OPENCODE_JSONC,
    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
    TEXT_TOOLWRIGHT_DISCOVERY,
)

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
    return shutil.which(KEY_OPENCODE)


@unittest.skipUnless(_opencode(), TEXT_OPENCODE_BINARY_IS_NOT_INSTALLED)
class AgentDiscoveryTests(unittest.TestCase):

    def test_all_agents_are_discovered(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_DISCOVERY) as directory:
            target = Path(directory)
            install = subprocess.run(
                [
                    KEY_BASH,
                    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
                    FLAG_APPLY,
                    FLAG_ONLY,
                    KEY_AGENTS,
                    FLAG_TARGET,
                    str(target),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            config = target / TEXT_OPENCODE / TEXT_OPENCODE_JSONC
            shutil.copyfile(REPO_ROOT / TEXT_CONFIGS_OPENCODE_MINIMAL_JSONC, config)
            environment = dict(os.environ)
            environment[TEXT_OPENCODE_CONFIG] = str(config)
            result = subprocess.run(
                [KEY_OPENCODE, FLAG_STANDALONE, KEY_DEBUG, KEY_AGENTS],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            agents = json.loads(result.stdout)
            identifiers = {agent[KEY_ID] for agent in agents}
            self.assertEqual(sorted(identifiers & set(support.AGENT_ROLES)), sorted(support.AGENT_ROLES))

    def test_coordinator_is_primary(self) -> None:
        with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_DISCOVERY) as directory:
            target = Path(directory)
            subprocess.run(
                [
                    KEY_BASH,
                    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
                    FLAG_APPLY,
                    FLAG_ONLY,
                    KEY_AGENTS,
                    FLAG_TARGET,
                    str(target),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )
            config = target / TEXT_OPENCODE / TEXT_OPENCODE_JSONC
            shutil.copyfile(REPO_ROOT / TEXT_CONFIGS_OPENCODE_MINIMAL_JSONC, config)
            environment = dict(os.environ)
            environment[TEXT_OPENCODE_CONFIG] = str(config)
            result = subprocess.run(
                [KEY_OPENCODE, FLAG_STANDALONE, KEY_DEBUG, KEY_AGENTS],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
                env=environment,
            )
            agents = json.loads(result.stdout)
            coordinator = next(agent for agent in agents if agent[KEY_ID] == KEY_COORDINATOR)
            self.assertEqual(coordinator[KEY_MODE], KEY_PRIMARY)


@unittest.skipUnless(_opencode(), TEXT_OPENCODE_BINARY_IS_NOT_INSTALLED)
class ConfigurationValidationTests(unittest.TestCase):

    def test_minimal_profile_parses(self) -> None:
        result = subprocess.run(
            [KEY_OPENCODE, FLAG_STANDALONE, KEY_DEBUG, KEY_CONFIG],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
            env={**os.environ, TEXT_OPENCODE_CONFIG: str(REPO_ROOT / TEXT_CONFIGS_OPENCODE_MINIMAL_JSONC)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed, TEXT_CONFIGURATION_LOADER_RETURNED_NO_SOURCES)


if __name__ == TEXT_MAIN:
    unittest.main()
