"""
Unit tests for the OpenCode compatibility matrix.
"""
from __future__ import annotations

import unittest

from tests import support

from toolwright_cli import compat


class CompatMatrixTests(unittest.TestCase):

    def test_rows_have_required_fields(self) -> None:
        self.assertTrue(compat.MATRIX)
        for row in compat.MATRIX:
            self.assertTrue({"feature", "v1", "v2", "note"}.issubset(row))
            self.assertTrue(row["feature"])
            self.assertTrue(row["note"])

    def test_documented_v2_only_features(self) -> None:
        rows = {row["feature"]: row for row in compat.MATRIX}
        self.assertEqual(rows["Code Mode"]["v1"], "no")
        self.assertEqual(rows["Native LSP navigation"]["v2"], "no")

    def test_as_dict_is_json_ready(self) -> None:
        payload = compat.as_compatibility_dict()
        self.assertEqual(payload["tool"], "opencode")
        self.assertEqual(payload["versions"], ["v1", "v2"])
        self.assertEqual(len(payload["features"]), len(compat.MATRIX))
        self.assertIn("not performance or benchmark", payload["disclaimer"])

    def test_render_text_contains_header_and_rows(self) -> None:
        rendered = compat.render_text()
        self.assertIn("Feature", rendered)
        self.assertIn("V1", rendered)
        self.assertIn("V2", rendered)
        self.assertIn(compat.MATRIX[0]["feature"], rendered)
        self.assertIn(compat.DISCLAIMER, rendered)


if __name__ == "__main__":
    unittest.main()
