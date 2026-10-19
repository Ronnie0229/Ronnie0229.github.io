import hashlib
import unittest
from scripts.import_sermons import bind_article_id


class SermonArticleIdTest(unittest.TestCase):
    def test_assigns_deterministic_id_and_idempotent(self):
        slug = "2026-10-18-腓立比书-2-1-5｜藉着谦卑实现合一"
        expected = "post-" + hashlib.sha256(slug.encode("utf-8")).hexdigest()[:16]
        original = "---\ntitle: \"标题\"\n---\n\n正文。\n"
        published = bind_article_id(original, slug)
        self.assertIn(f'articleId: "{expected}"', published)
        self.assertEqual(bind_article_id(published, slug), published)
        self.assertTrue(published.endswith("\n正文。\n"))

    def test_empty_id_filled_before_write(self):
        text = '---\narticleId: ""\ntitle: "标题"\n---\n正文。\n'
        result = bind_article_id(text, "one-slug")
        self.assertEqual(result.count("articleId:"), 1)
        self.assertNotIn('articleId: ""', result)

    def test_identity_collision_rejected(self):
        with self.assertRaisesRegex(SystemExit, "ARTICLE_ID_IDENTITY_MISMATCH"):
            bind_article_id('---\narticleId: "post-wrong"\n---\n正文。\n', "one-slug")

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(SystemExit, "ARTICLE_ID_DUPLICATE"):
            bind_article_id('---\narticleId: ""\narticleId: ""\n---\n正文。\n', "one-slug")


if __name__ == "__main__":
    unittest.main()
