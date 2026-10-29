import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "content_workflow.py"
SPEC = importlib.util.spec_from_file_location("content_workflow_share_ingest", SCRIPT)
content_workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(content_workflow)


class ShareIngestSystemMetadataTests(unittest.TestCase):
    def test_share_ingest_moves_business_files_and_preserves_ds_store(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inbox = root / "inbox"
            raw = root / "raw"
            inbox.mkdir()
            pdf = inbox / "example.pdf"
            pdf.write_bytes(b"%PDF-1.4\nexample\n")
            metadata = inbox / ".DS_Store"
            metadata.write_bytes(b"finder metadata")

            with patch.dict(content_workflow.RAW_DIRS, {"share": raw}):
                content_workflow.ingest_share(inbox)

            self.assertFalse(pdf.exists())
            self.assertEqual((raw / "example.pdf").read_bytes(), b"%PDF-1.4\nexample\n")
            self.assertEqual(metadata.read_bytes(), b"finder metadata")
            self.assertFalse((raw / ".DS_Store").exists())

    def test_share_listing_ignores_ds_store_without_changing_default_listing(self):
        with tempfile.TemporaryDirectory() as directory:
            inbox = Path(directory)
            (inbox / ".DS_Store").write_bytes(b"finder metadata")
            (inbox / "article.pdf").write_bytes(b"pdf")

            self.assertEqual(
                [path.name for path in content_workflow.list_files(inbox, skip_ds_store=True)],
                ["article.pdf"],
            )
            self.assertEqual(
                [path.name for path in content_workflow.list_files(inbox)],
                [".DS_Store", "article.pdf"],
            )

    def test_only_ds_store_is_not_an_ingestable_share(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inbox = root / "inbox"
            inbox.mkdir()
            (inbox / ".DS_Store").write_bytes(b"finder metadata")
            with patch.dict(content_workflow.RAW_DIRS, {"share": root / "raw"}):
                with self.assertRaisesRegex(SystemExit, "分享收件目录没有文件"):
                    content_workflow.ingest_share(inbox)
            self.assertTrue((inbox / ".DS_Store").exists())


if __name__ == "__main__":
    unittest.main()
