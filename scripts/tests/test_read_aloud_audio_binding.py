import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from read_aloud_audio_binding import BindingError, plan_audio_binding


class AudioBindingTests(unittest.TestCase):
    def setUp(self):
        self.before = b'---\narticleId: "post-123"\ntitle: "Hi"\ndate: 2026-10-11\n---\n\nParagraph.\n'
        self.sha = hashlib.sha256(self.before).hexdigest()
        self.url = "https://audio.ronniecross.com/audio/articles/post-123/article.mp3"

    def test_binding_only_changes_frontmatter_audio_url(self):
        after = plan_audio_binding(self.before, "post-123", self.sha, self.url)
        self.assertEqual(after.replace(b'\naudioUrl: "' + self.url.encode() + b'"', b""), self.before)
        self.assertEqual(after.split(b"---\n")[-1], self.before.split(b"---\n")[-1])

    def test_stale_sha_blocks(self):
        with self.assertRaises(BindingError):
            plan_audio_binding(self.before, "post-123", "0" * 64, self.url)

    def test_unexpected_url_blocks(self):
        with self.assertRaises(BindingError):
            plan_audio_binding(self.before, "post-123", self.sha, "https://evil.example/audio.mp3")

    def test_existing_audio_blocks(self):
        changed = self.before.replace(b'title: "Hi"', b'title: "Hi"\naudioUrl: "existing"')
        with self.assertRaises(BindingError):
            plan_audio_binding(changed, "post-123", hashlib.sha256(changed).hexdigest(), self.url)


if __name__ == "__main__":
    unittest.main()
