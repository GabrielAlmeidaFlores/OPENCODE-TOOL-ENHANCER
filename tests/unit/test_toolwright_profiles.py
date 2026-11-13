"""
Unit tests for profile manifest loading and validation.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli.paths import ToolWrightError
from toolwright_cli.profiles import load_profile, load_profiles, resolve_components, verify_profiles


class RepositoryProfileTests(unittest.TestCase):

    def test_manifests_load(self) -> None:
        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(sorted(profiles), ["full", "minimal", "standard"])
        self.assertEqual(len(profiles["minimal"].components), 5)
        self.assertIn("ast-grep", profiles["standard"].components)
        self.assertIn("codegraph", profiles["full"].components)

    def test_verify_reports_ok(self) -> None:
        results = verify_profiles(support.REPO_ROOT)
        self.assertTrue(results)
        self.assertTrue(all(result["status"] == "ok" for result in results))

    def test_resolve_unknown_profile_is_an_error(self) -> None:
        profiles = load_profiles(support.REPO_ROOT)
        with self.assertRaises(ToolWrightError) as raised:
            resolve_components(profiles, "nope", None)
        self.assertIn("available", str(raised.exception))


class ManifestValidationTests(unittest.TestCase):

    def _profile(self, body: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "demo.yml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_valid_manifest(self) -> None:
        path = self._profile(
            "name: demo\ndescription: Demo profile.\ncomponents:\n  - agents\n"
        )
        profile = load_profile(path)
        self.assertEqual(profile.name, "demo")
        self.assertEqual(profile.components, ("agents",))

    def test_name_must_match_file(self) -> None:
        path = self._profile(
            "name: other\ndescription: Demo.\ncomponents:\n  - agents\n"
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_unknown_component_is_rejected(self) -> None:
        path = self._profile(
            "name: demo\ndescription: Demo.\ncomponents:\n  - agents\n  - made-up\n"
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_duplicate_component_is_rejected(self) -> None:
        path = self._profile(
            "name: demo\ndescription: Demo.\ncomponents:\n  - agents\n  - agents\n"
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_missing_description_is_rejected(self) -> None:
        path = self._profile("name: demo\ncomponents:\n  - agents\n")
        with self.assertRaises(ToolWrightError):
            load_profile(path)

    def test_unsupported_syntax_is_rejected(self) -> None:
        path = self._profile(
            "name: demo\ndescription: Demo.\ncomponents:\n  - agents\nmetadata:\n  owner: x\n"
        )
        with self.assertRaises(ToolWrightError):
            load_profile(path)


if __name__ == "__main__":
    unittest.main()
