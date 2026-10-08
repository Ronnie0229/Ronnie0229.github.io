from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ReadAloudPlayerTests(unittest.TestCase):
    def test_content_schema_has_optional_absolute_audio_url(self) -> None:
        config = (ROOT / "src/content/config.ts").read_text(encoding="utf-8")
        self.assertIn('audioUrl: z.string().url().optional()', config)

    def test_article_page_uses_native_optional_audio_player(self) -> None:
        page = (ROOT / "src/pages/posts/[slug].astro").read_text(encoding="utf-8")
        self.assertIn("post.data.audioUrl &&", page)
        self.assertIn('<audio controls preload="metadata" src={post.data.audioUrl}>', page)
        self.assertIn('aria-labelledby="article-audio-title"', page)
        self.assertLess(page.index("post.data.audioUrl &&"), page.index('<div class="article-content">'))

    def test_player_has_no_autoplay_or_custom_runtime(self) -> None:
        page = (ROOT / "src/pages/posts/[slug].astro").read_text(encoding="utf-8")
        player_block = page[page.index("post.data.audioUrl &&"):page.index('<div class="article-content">')]
        self.assertNotIn("autoplay", player_block)
        self.assertNotIn("<script", player_block)

    def test_pilot_binds_exact_production_audio_url(self) -> None:
        pilot = (ROOT / "src/content/posts/2026-10-06-does-james-4-say-not-to-make-plans.md").read_text(encoding="utf-8")
        frontmatter = pilot.split("---", 2)[1]
        self.assertIn(
            'audioUrl: "https://audio.ronniecross.com/audio/articles/post-32d30724d859c99c/article.mp3"',
            frontmatter,
        )


if __name__ == "__main__":
    unittest.main()
