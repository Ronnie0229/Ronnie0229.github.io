from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# The importer wrappers under test do not read DOCX files. Keep this focused
# unit suite independent of the optional local python-docx installation.
if "docx" not in sys.modules:
    sys.modules["docx"] = types.SimpleNamespace(Document=None)
if "pypdf" not in sys.modules:
    sys.modules["pypdf"] = types.SimpleNamespace(PdfReader=None)

from scripts.content_workflow import publish
from scripts.import_sermons import build_sermon_tags, markdown_for
from scripts.import_shares import build_share_tags
from scripts.tag_pipeline import TagPipelineError, build_tags, load_rules


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "scripts" / "tests" / "fixtures" / "tag_pipeline_cases.json"


class TagPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = load_rules()
        cls.fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))

    def test_fixed_rule_generation_and_validation_fixtures(self) -> None:
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["name"]):
                if "expected_error" in fixture:
                    with self.assertRaises(TagPipelineError) as caught:
                        build_tags(rules=self.rules, **fixture["input"])
                    self.assertEqual(fixture["expected_error"], caught.exception.code)
                else:
                    result = build_tags(rules=self.rules, **fixture["input"])
                    self.assertEqual(fixture["expected"]["tags"], result.tags)
                    self.assertTrue(all(item["source"] in {"scripture", "rule", "manual"} for item in result.evidence))

    def test_share_entry_uses_pipeline_and_preserves_manual_tags(self) -> None:
        tags = build_share_tags(
            "该隐与挪得之地：流离与救赎的盼望",
            "创世记 4:1-24",
            "Salvation, Cain",
        )
        self.assertEqual(["创世记", "该隐", "挪得之地", "盼望", "救恩"], tags)

    def test_share_entry_rejects_generic_tag(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            build_share_tags("普通标题", "罗马书 8:1", "分享")
        self.assertIn("TAG_GENERIC", str(caught.exception))

    def test_sermon_entry_does_not_default_to_type_category_or_speaker(self) -> None:
        tags = build_sermon_tags(
            "希伯来书 11:21｜信仰的殿堂：雅各",
            "希伯来书 11:21",
            None,
            "教会讲道",
            "Grayson",
        )
        self.assertEqual(["希伯来书", "雅各", "信心"], tags)
        self.assertNotIn("讲道", tags)
        self.assertNotIn("教会讲道", tags)
        self.assertNotIn("Grayson", tags)

    def test_sermon_entry_fails_closed_when_rules_are_insufficient(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            build_sermon_tags("普通标题", "罗马书 8:1", None, "教会讲道", "Patrick")
        self.assertIn("TAG_COUNT_TOO_LOW", str(caught.exception))

    def test_sermon_markdown_uses_pipeline_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "20260802希伯来书11:21信仰的殿堂雅各_Grayson"
            folder.mkdir()
            source = folder / "希伯来书11:21信仰的殿堂雅各_中文.txt"
            source.write_text("希伯来书 11:21\n\n雅各因着信心敬拜神。", encoding="utf-8")
            _date, markdown = markdown_for(
                folder,
                source,
                "Grayson 根据希伯来书十一章分享雅各晚年因信心敬拜神，并仰望神应许的生命。",
            )
        self.assertIn('tags: ["希伯来书", "雅各", "信心"]', markdown)
        tags_line = next(line for line in markdown.splitlines() if line.startswith("tags:"))
        self.assertNotIn('"讲道"', tags_line)
        self.assertNotIn('"教会讲道"', tags_line)
        self.assertNotIn('"Grayson"', tags_line)

    def test_content_workflow_forwards_manual_tags_to_sermon(self) -> None:
        with patch("scripts.content_workflow.subprocess.run") as run:
            run.return_value.returncode = 0
            publish("sermon", folder="data/raw/教会讲道/sample", tags="Faith,Jacob", dry_run=True)
        command = run.call_args.args[0]
        self.assertIn("--tags", command)
        self.assertIn("Faith,Jacob", command)

    def test_python_and_browser_runtime_results_match(self) -> None:
        completed = subprocess.run(
            ["node", "scripts/run_tag_pipeline_fixtures.mjs", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        browser_results = {item["name"]: item for item in json.loads(completed.stdout)}
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["name"]):
                browser = browser_results[fixture["name"]]
                try:
                    python_result = build_tags(rules=self.rules, **fixture["input"])
                    python_value = {"ok": True, "result": python_result.to_dict()}
                except TagPipelineError as exc:
                    python_value = {"ok": False, "error": {"code": exc.code, "message": exc.message}}
                self.assertEqual(python_value, {key: browser[key] for key in python_value})


if __name__ == "__main__":
    unittest.main()
