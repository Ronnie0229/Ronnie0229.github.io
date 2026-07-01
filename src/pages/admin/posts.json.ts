import { getCollection } from "astro:content";
import { buildPostKnowledge } from "../../lib/knowledge";

export async function GET() {
  const posts = await getCollection("posts");
  const result = posts
    .map((post) => {
      const knowledge = buildPostKnowledge(post);

      return {
        id: post.id,
        articleId: post.data.articleId,
        slug: post.slug,
        title: post.data.title,
        date: post.data.date,
        category: post.data.category,
        scripture: post.data.scripture,
        draft: post.data.draft,
        readingTimeMinutes: knowledge.readingTimeMinutes
      };
    })
    .sort((a, b) => new Date(b.date).valueOf() - new Date(a.date).valueOf());

  return new Response(JSON.stringify(result), {
    headers: {
      "Content-Type": "application/json; charset=UTF-8",
      "Cache-Control": "no-store"
    }
  });
}
