"""
Unit tests for the real-repository pilot runner.
"""
from __future__ import annotations
from tests.unit.test_toolwright_pilot_strings import (
    EMPTY_STRING,
    KEY_A,
    KEY_CAPTURE_COMMAND,
    KEY_CLONE,
    KEY_COMMIT,
    KEY_CONFIG,
    KEY_COST,
    KEY_CWD,
    KEY_DEMO,
    KEY_DRY_RUN,
    KEY_F6FBAF0299C48EEA9E656E03E2FFE7AC755E8823,
    KEY_FOCUS,
    KEY_GIT,
    KEY_HONO,
    KEY_INPUT,
    KEY_INSTALL,
    KEY_LOAD_PILOTS,
    KEY_LOAD_PROFILES,
    KEY_MINIMAL,
    KEY_NOPE,
    KEY_OPENCODE,
    KEY_OPENCODE_EXIT,
    KEY_OUTPUT,
    KEY_PART,
    KEY_PWD,
    KEY_REPOSITORY,
    KEY_STACK,
    KEY_STEPS,
    KEY_STEP_FINISH,
    KEY_SUCCESS,
    KEY_TEST,
    KEY_TOKENS,
    KEY_TRUE,
    KEY_TURBOREPO,
    KEY_TYPE,
    KEY_WORKSPACE,
    KEY_X,
    TEXT_ARTIFACTS_META_JSON,
    TEXT_ARTIFACTS_SESSION_JSONL,
    TEXT_ARTIFACTS_VERIFICATION_LOG,
    TEXT_CHECKOUT_DETACH,
    TEXT_CLEAN_ARCHITECTURE,
    TEXT_CONFIGS_PILOTS_PILOTS_TOML,
    TEXT_DO_THE_TASK,
    TEXT_GITHUB_COM_HONOJS_HONO,
    TEXT_HTTPS_EXAMPLE_COM_DEMO_GIT,
    TEXT_MAIN,
    TEXT_MODEL_FAILED,
    TEXT_OPENCODE_CONFIG,
    TEXT_OPENCODE_JSONC,
    TEXT_PILOTS_DEMO_REPOSITORY_HTTPS_EXAMPLE_COM_REPO,
    TEXT_PROVIDER_MODEL,
    TEXT_PWD,
    TEXT_TEXT,
    TEXT_UTF_8,
    TEXT_VERIFICATION_OK,
)

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
        self.assertEqual(sorted(pilots), [TEXT_CLEAN_ARCHITECTURE, KEY_HONO, KEY_TURBOREPO])
        self.assertEqual(pilots[KEY_HONO][KEY_COMMIT], KEY_F6FBAF0299C48EEA9E656E03E2FFE7AC755E8823)

    def test_list_includes_stack_and_focus(self) -> None:
        pilots = pilot.list_pilots(support.REPO_ROOT)
        self.assertTrue(all(item[KEY_STACK] and item[KEY_FOCUS] for item in pilots))

    def test_missing_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / TEXT_CONFIGS_PILOTS_PILOTS_TOML
            path.parent.mkdir(parents=True)
            path.write_text(TEXT_PILOTS_DEMO_REPOSITORY_HTTPS_EXAMPLE_COM_REPO, encoding=TEXT_UTF_8)
            with self.assertRaises(ToolWrightError):
                pilot.load_pilots(root)


class PilotExecutionTests(unittest.TestCase):
    def _run(self, opencode_exit: int):
        workspace_dir = tempfile.TemporaryDirectory()
        self.addCleanup(workspace_dir.cleanup)
        workspace = Path(workspace_dir.name) / KEY_WORKSPACE
        pilots = {
            KEY_DEMO: {
                KEY_REPOSITORY: TEXT_HTTPS_EXAMPLE_COM_DEMO_GIT,
                KEY_COMMIT: KEY_A * 40,
                KEY_STACK: KEY_TEST,
                KEY_FOCUS: KEY_TEST,
            }
        }
        session = json.dumps(
            {KEY_TYPE: KEY_STEP_FINISH, KEY_PART: {KEY_COST: 0.25, KEY_TOKENS: {KEY_INPUT: 10, KEY_OUTPUT: 5}}}
        ) + TEXT_TEXT

        captured = {}

        def fake_capture(args, cwd=None, env=None, timeout=600):
            if args[0] == KEY_GIT:
                return 0, EMPTY_STRING, EMPTY_STRING
            if args[0] == KEY_OPENCODE:
                captured[KEY_CWD] = str(cwd)
                captured[KEY_PWD] = (env or {}).get(TEXT_PWD)
                captured[KEY_CONFIG] = (env or {}).get(TEXT_OPENCODE_CONFIG)
                return opencode_exit, session, EMPTY_STRING if opencode_exit == 0 else TEXT_MODEL_FAILED
            return 0, TEXT_VERIFICATION_OK, EMPTY_STRING

        with mock.patch.object(pilot, KEY_LOAD_PILOTS, return_value=pilots), \
             mock.patch.object(pilot, KEY_LOAD_PROFILES, return_value=real_profiles(support.REPO_ROOT)), \
             mock.patch.object(pilot, KEY_INSTALL), \
             mock.patch.object(pilot, KEY_CAPTURE_COMMAND, side_effect=fake_capture):
            result = pilot.run_pilot(
                root=support.REPO_ROOT,
                name=KEY_DEMO,
                workspace=workspace,
                prompt=TEXT_DO_THE_TASK,
                verify_command=KEY_TRUE,
                profile=KEY_MINIMAL,
                keep=False,
                dry_run=False,
                model=TEXT_PROVIDER_MODEL,
            )
        self.assertEqual(captured[KEY_PWD], str(workspace / KEY_CLONE))
        self.assertTrue(str(captured[KEY_CONFIG]).endswith(TEXT_OPENCODE_JSONC))
        return result

    def test_success_requires_both_exits(self) -> None:
        passing = self._run(0)
        self.assertTrue(passing[KEY_SUCCESS])
        self.assertTrue((Path(passing[KEY_WORKSPACE]) / TEXT_ARTIFACTS_META_JSON).is_file())
        self.assertTrue((Path(passing[KEY_WORKSPACE]) / TEXT_ARTIFACTS_SESSION_JSONL).is_file())
        self.assertTrue((Path(passing[KEY_WORKSPACE]) / TEXT_ARTIFACTS_VERIFICATION_LOG).is_file())
        self.assertAlmostEqual(passing[KEY_COST], 0.25)

        failing = self._run(1)
        self.assertFalse(failing[KEY_SUCCESS])
        self.assertEqual(failing[KEY_OPENCODE_EXIT], 1)


class PilotRunTests(unittest.TestCase):

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / KEY_WORKSPACE
            result = pilot.run_pilot(
                root=support.REPO_ROOT,
                name=KEY_HONO,
                workspace=workspace,
                prompt=None,
                verify_command=None,
                profile=KEY_MINIMAL,
                keep=False,
                dry_run=True,
                model=None,
            )
            self.assertTrue(result[KEY_DRY_RUN])
            self.assertFalse(workspace.exists())
            joined = TEXT_TEXT.join(result[KEY_STEPS])
            self.assertIn(TEXT_GITHUB_COM_HONOJS_HONO, joined)
            self.assertIn(KEY_F6FBAF0299C48EEA9E656E03E2FFE7AC755E8823, joined)
            self.assertIn(TEXT_CHECKOUT_DETACH, joined)

    def test_real_run_requires_prompt_and_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ToolWrightError):
                pilot.run_pilot(
                    root=support.REPO_ROOT,
                    name=KEY_HONO,
                    workspace=Path(directory) / KEY_WORKSPACE,
                    prompt=None,
                    verify_command=KEY_TRUE,
                    profile=KEY_MINIMAL,
                    keep=False,
                    dry_run=False,
                    model=TEXT_PROVIDER_MODEL,
                )

    def test_unknown_pilot_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            pilot.run_pilot(
                root=support.REPO_ROOT,
                name=KEY_NOPE,
                workspace=None,
                prompt=KEY_X,
                verify_command=KEY_TRUE,
                profile=KEY_MINIMAL,
                keep=False,
                dry_run=True,
                model=None,
            )


if __name__ == TEXT_MAIN:
    unittest.main()
