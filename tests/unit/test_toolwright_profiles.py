"""
Unit tests for profile manifest loading and validation.
"""
from __future__ import annotations
from tests.unit.test_toolwright_profiles_strings import (
    KEY_AGENTS,
    KEY_AVAILABLE,
    KEY_CODEGRAPH,
    KEY_DEMO,
    KEY_FULL,
    KEY_MINIMAL,
    KEY_NOPE,
    KEY_OK,
    KEY_STANDARD,
    KEY_STATUS,
    TEXT_AST_GREP,
    TEXT_DEMO_YML,
    TEXT_MAIN,
    TEXT_NAME_DEMO_COMPONENTS_AGENTS,
    TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_AGENTS,
    TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_MADE_UP,
    TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_METADATA_OWNER_,
    TEXT_NAME_DEMO_DESCRIPTION_DEMO_PROFILE_COMPONENTS_AGENTS,
    TEXT_NAME_OTHER_DESCRIPTION_DEMO_COMPONENTS_AGENTS,
    TEXT_UTF_8,
)

import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli.paths import ToolWrightError
from toolwright_cli.profiles import load_profile, load_profiles, resolve_components, verify_profiles


class RepositoryProfileTests(unittest.TestCase):

    def test_manifests_load(self) -> None:
        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(sorted(profiles), [KEY_FULL, KEY_MINIMAL, KEY_STANDARD])
        self.assertEqual(len(profiles[KEY_MINIMAL].components), 5)
        self.assertIn(TEXT_AST_GREP, profiles[KEY_STANDARD].components)
        self.assertIn(KEY_CODEGRAPH, profiles[KEY_FULL].components)

    def test_verify_reports_ok(self) -> None:
        results = verify_profiles(support.REPO_ROOT)
        self.assertTrue(results)
        self.assertTrue(all(result[KEY_STATUS] == KEY_OK for result in results))

    def test_resolve_unknown_profile_is_an_error(self) -> None:
        profiles = load_profiles(support.REPO_ROOT)
        with self.assertRaises(ToolWrightError) as raised:
            resolve_components(profiles, KEY_NOPE, None)
        self.assertIn(KEY_AVAILABLE, str(raised.exception))


class ManifestValidationTests(unittest.TestCase):

    def _profile(self, body: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / TEXT_DEMO_YML
        path.write_text(body, encoding=TEXT_UTF_8)
        return path

    def test_valid_manifest(self) -> None:
        path = self._profile(
            TEXT_NAME_DEMO_DESCRIPTION_DEMO_PROFILE_COMPONENTS_AGENTS
        )
        profile = load_profile(path)
        self.assertEqual(profile.name, KEY_DEMO)
        self.assertEqual(profile.components, (KEY_AGENTS,))

    def test_name_must_match_file(self) -> None:
        path = self._profile(
            TEXT_NAME_OTHER_DESCRIPTION_DEMO_COMPONENTS_AGENTS
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_unknown_component_is_rejected(self) -> None:
        path = self._profile(
            TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_MADE_UP
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_duplicate_component_is_rejected(self) -> None:
        path = self._profile(
            TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_AGENTS
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_missing_description_is_rejected(self) -> None:
        path = self._profile(TEXT_NAME_DEMO_COMPONENTS_AGENTS)
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_unsupported_syntax_is_rejected(self) -> None:
        path = self._profile(
            TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_METADATA_OWNER_
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)


if __name__ == TEXT_MAIN:
    unittest.main()
