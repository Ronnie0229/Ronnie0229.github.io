from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validate_content_presentation.mjs"


class ContentPresentationRendererTests(unittest.TestCase):
    def run_gate(self, body: str, profile: str = "share_article") -> tuple[subprocess.CompletedProcess[str], dict]:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "article.md"
            source.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    "node", str(VALIDATOR), "--profile", profile,
                    "--source", str(source), "--candidate-id", "share-article-test",
                ],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            try:
                evidence = json.loads(result.stdout or result.stderr)
            except json.JSONDecodeError:
                evidence = {"stderr": result.stderr, "stdout": result.stdout}
            return result, evidence

    def test_share_article_keeps_native_structure_without_sermon_outline_rules(self):
        body = (
            "## 为什么要彼此相爱？\n\n"
            "第一段正文，保留作者原有的论述。\n\n"
            "### 圣经中的提醒\n\n"
            "第二段正文，解释经文与上下文。\n\n"
            "- 第一个观察\n"
            "- 第二个观察\n\n"
            "> 一段引用或对话。\n\n"
            "## 祷告\n\n"
            "求主帮助我们忠心跟随。\n\n"
            "## 思考问题\n\n"
            "今天我可以怎样回应？\n"
        )
        result, evidence = self.run_gate(body)
        self.assertEqual(result.returncode, 0, evidence)
        self.assertEqual(evidence["status"], "CONTENT_PRESENTATION_STRUCTURE_PASS")
        self.assertEqual(evidence["profile"], "share_article")
        self.assertEqual(evidence["metrics"]["source_heading_count"], 4)
        self.assertEqual(evidence["metrics"]["source_list_item_count"], 2)
        self.assertEqual(evidence["metrics"]["source_blockquote_count"], 1)

    def test_share_article_does_not_require_three_point_outline(self):
        body = "## 一段个人分享\n\n这是一篇普通分享文章，不需要讲道三点大纲。\n"
        result, evidence = self.run_gate(body)
        self.assertEqual(result.returncode, 0, evidence)

    def test_share_article_rejects_internal_workflow_notes(self):
        body = "## 分享\n\n讲员：Patrick（默认规则，待元数据最终确认）\n"
        result, evidence = self.run_gate(body)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(evidence["status"], "CONTENT_PRESENTATION_STRUCTURE_FAIL")
        self.assertTrue(any(item["kind"] == "internal_workflow_notes" for item in evidence["failures"]))

    def test_unknown_profile_fails_closed(self):
        result, evidence = self.run_gate("## 标题\n\n正文。\n", profile="unknown")
        self.assertEqual(result.returncode, 2)
        self.assertIn("profile", evidence["error"])


if __name__ == "__main__":
    unittest.main()
