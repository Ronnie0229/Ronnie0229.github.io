import { getCollection } from "astro:content";
import { buildPostKnowledge, cleanMarkdown } from "../lib/knowledge";

export const prerender = true;

export async function GET() {
  const posts = (await getCollection("posts", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf())
    .map((post) => {
      const knowledge = buildPostKnowledge(post);

      return {
        articleId: post.data.articleId,
        slug: post.slug,
        title: post.data.title,
        description: post.data.description,
        date: post.data.date.toISOString(),
        category: post.data.category,
        scripture: post.data.scripture,
        tags: post.data.tags,
        body: cleanMarkdown(post.body ?? ""),
        bibleBooks: knowledge.bibleBooks,
        testament: knowledge.testament,
        topics: knowledge.topics,
        wordCount: knowledge.wordCount,
        readingTimeMinutes: knowledge.readingTimeMinutes
      };
    });

  return new Response(JSON.stringify(posts), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=0, must-revalidate"
    }
  });
}
