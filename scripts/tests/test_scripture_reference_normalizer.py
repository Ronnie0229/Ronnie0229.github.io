from __future__ import annotations

import unittest

from scripts.scripture_reference_normalizer import (
    ALIAS_TO_NAME,
    BOOK_RECORDS,
    find_compact_chinese_references,
    normalize_scripture_references,
)


class ScriptureReferenceNormalizerTests(unittest.TestCase):
    def test_project_bible_inventory_has_66_books_and_unique_aliases(self) -> None:
        self.assertEqual(len(BOOK_RECORDS), 66)
        self.assertEqual(ALIAS_TO_NAME["罗"], "罗马书")
        self.assertEqual(ALIAS_TO_NAME["约"], "约翰福音")
        self.assertEqual(ALIAS_TO_NAME["来"], "希伯来书")

    def test_single_verse_uses_full_book_name(self) -> None:
        self.assertEqual(
            normalize_scripture_references("罗 1:15"),
            "罗马书1章15节",
        )

    def test_same_chapter_range_uses_tts_friendly_to(self) -> None:
        self.assertEqual(
            normalize_scripture_references("罗马书 1:15-18"),
            "罗马书1章15节到18节",
        )

    def test_cross_chapter_range(self) -> None:
        self.assertEqual(
            normalize_scripture_references("罗马书 8:38-9:2"),
            "罗马书8章38节到9章2节",
        )

    def test_full_name_and_chinese_colon(self) -> None:
        self.assertEqual(
            normalize_scripture_references("创世记 50：19-21"),
            "创世记50章19节到21节",
        )

    def test_already_spoken_reference_is_unchanged(self) -> None:
        value = "罗马书8章38节到39节"
        self.assertEqual(normalize_scripture_references(value), value)

    def test_book_title_brackets_are_normalized(self) -> None:
        self.assertEqual(
            normalize_scripture_references("《使徒行传》7:1-50"),
            "使徒行传7章1节到50节",
        )

    def test_unsupported_discontinuous_list_fails_detection_instead_of_partial_rewrite(self) -> None:
        value = "罗马书 8:28,31"
        normalized = normalize_scripture_references(value)
        self.assertEqual(normalized, value)
        self.assertEqual(find_compact_chinese_references(normalized), ["罗马书 8:28"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
