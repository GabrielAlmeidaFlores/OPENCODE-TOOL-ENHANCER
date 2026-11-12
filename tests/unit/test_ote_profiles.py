"""
Unit tests for profile manifest loading and validation.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli.paths import OteError
from ote_cli.profiles import load_profile, load_profiles, resolve_components, verify_profiles


class RepositoryProfileTests(unittest.TestCase):
    """
    Tests against the committed profile manifests.
    """

    def test_manifests_load(self) -> None:
        """
        The three committed profiles load and expose the expected components.
        """
        profiles = load_profiles(support.REPO_ROOT)
        self.assertEqual(sorted(profiles), ["full", "minimal", "standard"])
        self.assertEqual(len(profiles["minimal"].components), 5)
        self.assertIn("ast-grep", profiles["standard"].components)
        self.assertIn("codegraph", profiles["full"].components)

    def test_verify_reports_ok(self) -> None:
        """
        Every committed manifest validates.
        """
        results = verify_profiles(support.REPO_ROOT)
        self.assertTrue(results)
        self.assertTrue(all(result["status"] == "ok" for result in results))

    def test_resolve_unknown_profile_is_an_error(self) -> None:
        """
        An unknown profile name lists the available profiles.
        """
        profiles = load_profiles(support.REPO_ROOT)
        with self.assertRaises(OteError) as raised:
            resolve_components(profiles, "nope", None)
        self.assertIn("available", str(raised.exception))


class ManifestValidationTests(unittest.TestCase):
    """
    Tests for manifest rejection paths.
    """

    def _profile(self, body: str) -> Path:
        """
        Write a profile manifest in a temporary directory and return its path.
        """
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "demo.yml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_valid_manifest(self) -> None:
        """
        A complete manifest loads.
        """
        path = self._profile(
            "name: demo\ndescription: Demo profile.\ncomponents:\n  - agents\n"
        )
        profile = load_profile(path)
        self.assertEqual(profile.name, "demo")
        self.assertEqual(profile.components, ("agents",))

    def test_name_must_match_file(self) -> None:
        """
        A manifest whose name differs from its file name is rejected.
        """
        path = self._profile(
            "name: other\ndescription: Demo.\ncomponents:\n  - agents\n"
        )
        with self.assertRaises(OteError):
            load_profile(path)

    def test_unknown_component_is_rejected(self) -> None:
        """
        A component that no installer supports is rejected.
        """
        path = self._profile(
            "name: demo\ndescription: Demo.\ncomponents:\n  - agents\n  - made-up\n"
        )
        with self.assertRaises(OteError):
            load_profile(path)

    def test_duplicate_component_is_rejected(self) -> None:
        """
        A component listed twice is rejected.
        """
        path = self._profile(
            "name: demo\ndescription: Demo.\ncomponents:\n  - agents\n  - agents\n"
        )
        with self.assertRaises(OteError):
            load_profile(path)

    def test_missing_description_is_rejected(self) -> None:
        """
        A manifest without a description is rejected.
        """
        path = self._profile("name: demo\ncomponents:\n  - agents\n")
        with self.assertRaises(OteError):
            load_profile(path)

    def test_unsupported_syntax_is_rejected(self) -> None:
        """
        Nested mappings are outside the supported subset.
        """
        path = self._profile(
            "name: demo\ndescription: Demo.\ncomponents:\n  - agents\nmetadata:\n  owner: x\n"
        )
        with self.assertRaises(OteError):
            load_profile(path)


if __name__ == "__main__":
    unittest.main()
