from __future__ import annotations

import unittest
from pathlib import Path

from scripts.import_sermons import resolve_scripture, title_parts


class ImportSermonsScriptureParserTests(unittest.TestCase):
    def test_spoken_zhi_same_chapter_range(self) -> None:
        scripture, _summary = title_parts("罗马书12章1至2节")
        self.assertEqual(scripture, "罗马书 12:1-2")

    def test_existing_spoken_dao_same_chapter_range_does_not_regress(self) -> None:
        scripture, _summary = title_parts("罗马书12章1节到2节")
        self.assertEqual(scripture, "罗马书 12:1-2")

    def test_standard_colon_range_does_not_regress(self) -> None:
        scripture, _summary = title_parts("罗马书 12:1-2")
        self.assertEqual(scripture, "罗马书 12:1-2")

    def test_exact_p5_body_no_longer_yields_chapter_only_false_conflict(self) -> None:
        body = (
            "一个小型教会团体正在反思罗马书12章1至2节。"
            "讲道者说：“将身体献上，当做活祭”，然后问更新的思维如何改变日常的工作。"
            "结论邀请会众祷告并讨论一个具体的服事行动。"
        )
        scripture, confidence = resolve_scripture(
            "20260910_罗马书12:1-2_心意更新与日常服事_Patrick",
            Path("20260910_罗马书12:1-2_心意更新与日常服事_Patrick_中文.txt"),
            body,
        )
        self.assertEqual(scripture, "罗马书 12:1-2")
        self.assertEqual(confidence, "high")

    def test_genuine_conflict_still_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            SystemExit,
            r"Scripture conflict detected; please confirm metadata manually",
        ):
            resolve_scripture(
                "罗马书 12:1-2",
                Path("罗马书 12:1-2.txt"),
                "正文引用罗马书13章1至2节。",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
