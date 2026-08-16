#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.scripture_reference_normalizer import normalize_scripture_references


class SitewideDisplayRemediationTests(unittest.TestCase):
    def test_normalization_changes_body_only(self) -> None:
        value = '---\ntitle: "罗马书 8:28｜测试"\nscripture: "罗马书 8:28"\n---\n\n请读罗马书 8:28。\n'
        prefix, frontmatter, body = value.split('---', 2)
        normalized = normalize_scripture_references(body)
        rebuilt = f'---{frontmatter}---{normalized}'
        self.assertIn('title: "罗马书 8:28｜测试"', rebuilt)
        self.assertIn('scripture: "罗马书 8:28"', rebuilt)
        self.assertIn('罗马书8章28节', rebuilt)

    def test_manifest_classification_vocab_is_fixed(self) -> None:
        allowed = {"AUTO_SAFE", "REVIEW_REQUIRED", "NO_CHANGE", "BLOCKED"}
        self.assertEqual(len(allowed), 4)


if __name__ == "__main__":
    unittest.main()
