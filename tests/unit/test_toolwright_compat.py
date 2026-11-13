"""
Unit tests for the OpenCode compatibility matrix.
"""
from __future__ import annotations
from tests.unit.test_toolwright_compat_strings import (
    KEY_DISCLAIMER,
    KEY_FEATURE,
    KEY_FEATURES,
    KEY_NO,
    KEY_NOTE,
    KEY_OPENCODE,
    KEY_TOOL,
    KEY_V1,
    KEY_V2,
    KEY_VERSIONS,
    TEXT_CODE_MODE,
    TEXT_FEATURE,
    TEXT_MAIN,
    TEXT_NATIVE_LSP_NAVIGATION,
    TEXT_NOT_PERFORMANCE_OR_BENCHMARK,
    TEXT_V1,
    TEXT_V2,
)

import unittest

from tests import support

from toolwright_cli import compat


class CompatMatrixTests(unittest.TestCase):

    def test_rows_have_required_fields(self) -> None:
        self.assertTrue(compat.MATRIX)
        for row in compat.MATRIX:
            self.assertTrue({KEY_FEATURE, KEY_V1, KEY_V2, KEY_NOTE}.issubset(row))
            self.assertTrue(row[KEY_FEATURE])
            self.assertTrue(row[KEY_NOTE])

    def test_documented_v2_only_features(self) -> None:
        rows = {row[KEY_FEATURE]: row for row in compat.MATRIX}
        self.assertEqual(rows[TEXT_CODE_MODE][KEY_V1], KEY_NO)
        self.assertEqual(rows[TEXT_NATIVE_LSP_NAVIGATION][KEY_V2], KEY_NO)

    def test_as_dict_is_json_ready(self) -> None:
        payload = compat.as_compatibility_dict()
        self.assertEqual(payload[KEY_TOOL], KEY_OPENCODE)
        self.assertEqual(payload[KEY_VERSIONS], [KEY_V1, KEY_V2])
        self.assertEqual(len(payload[KEY_FEATURES]), len(compat.MATRIX))
        self.assertIn(TEXT_NOT_PERFORMANCE_OR_BENCHMARK, payload[KEY_DISCLAIMER])

    def test_render_text_contains_header_and_rows(self) -> None:
        rendered = compat.render_text()
        self.assertIn(TEXT_FEATURE, rendered)
        self.assertIn(TEXT_V1, rendered)
        self.assertIn(TEXT_V2, rendered)
        self.assertIn(compat.MATRIX[0][KEY_FEATURE], rendered)
        self.assertIn(compat.DISCLAIMER, rendered)


if __name__ == TEXT_MAIN:
    unittest.main()
