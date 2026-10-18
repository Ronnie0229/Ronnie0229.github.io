"""Regression for mandatory sermon source/rendered structure gate before website import."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from consume_publication_package import enforce_sermon_prepublication_structure


class SermonPrepublicationStructureGateTest(unittest.TestCase):
    def check(self, body: str, mismatch: bool = False):
        with tempfile.TemporaryDirectory(prefix="ronnie-structure-gate-") as temp:
            candidate = Path(temp) / "candidate.md"
            candidate.write_text(body, encoding="utf-8")
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            package = {
                "content_type": "sermon",
                "metadata": {"batch_id": "sermon-structure-20261018"},
                "prepublish": {"path": str(candidate),
                               "sha256": "0" * 64 if mismatch else digest},
            }
            return enforce_sermon_prepublication_structure(package)

    def test_valid_source_renders_and_passes(self):
        result = self.check("## 第一部分\n\n第一段正文。\n\n## 第二部分\n\n第二段正文。\n")
        self.assertEqual(result["status"], "SERMON_PRESENTATION_STRUCTURE_PASS")
        self.assertEqual(result["completion_ceiling"], "publication_structure_ready")

    def test_sha_drift_fails_closed(self):
        with self.assertRaisesRegex(SystemExit, "SHA mismatch"):
            self.check("## 标题\n\n正文\n", mismatch=True)

    def test_pseudo_ordered_list_fails_closed(self):
        with self.assertRaisesRegex(SystemExit, "STRUCTURE_BLOCKED"):
            self.check("## 三个要点\n\n1）第一要点\n2）第二要点\n3）第三要点\n")


if __name__ == "__main__":
    unittest.main()
