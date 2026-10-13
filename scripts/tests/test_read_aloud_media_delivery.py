import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read_aloud_media_delivery as media


class MediaDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.nas = self.root / "nas"
        self.nas.mkdir()
        self.wav = self.root / "demo.wav"
        self.wav.write_bytes(b"RIFF-authoritative-demonstration")
        self.sha = hashlib.sha256(self.wav.read_bytes()).hexdigest()
        self.kw = dict(article_id="post-test1234", date="2026-10-11", title="活着就是基督",
                       workflow_id="w" * 64, render_sha="r" * 64, nas_root=self.nas,
                       require_mount=False)

    def tearDown(self):
        self.temp.cleanup()

    def test_append_only_archive_exact_hash_replay(self):
        first = media.archive_wav(self.wav, self.sha, **self.kw)
        self.assertTrue(first["verified"])
        second = media.archive_wav(self.wav, self.sha, **self.kw)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(Path(first["manifest_path"]).read_text())["article_id"], "post-test1234")

    def test_wrong_archive_sha_is_blocked(self):
        with self.assertRaises(media.DeliveryError):
            media.archive_wav(self.wav, "0" * 64, **self.kw)

    def test_archive_existing_different_content_blocks(self):
        first = media.archive_wav(self.wav, self.sha, **self.kw)
        Path(first["master_path"]).write_bytes(b"mismatched")
        with self.assertRaises(media.DeliveryError):
            media.archive_wav(self.wav, self.sha, **self.kw)

    def test_r2_no_permission_never_uploads(self):
        with patch.object(media, "verify_r2", return_value=False), self.assertRaises(media.DeliveryError):
            media.upload_r2(self.wav, self.sha, article_id="post-test1234", upload_allowed=False)

    def test_existing_matching_r2_is_idempotent(self):
        with patch.object(media, "verify_r2", return_value=True):
            result = media.upload_r2(self.wav, self.sha, article_id="post-test1234", upload_allowed=False)
        self.assertTrue(result["existed"])


if __name__ == "__main__":
    unittest.main()
