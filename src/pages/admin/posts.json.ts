import { getCollection } from "astro:content";

export async function GET() {
  const posts = await getCollection("posts");
  const result = posts
    .map((post) => ({
      id: post.id,
      articleId: post.data.articleId,
      slug: post.slug,
      title: post.data.title,
      date: post.data.date,
      category: post.data.category,
      scripture: post.data.scripture,
      draft: post.data.draft
    }))
    .sort((a, b) => String(b.date).localeCompare(String(a.date)));

  return new Response(JSON.stringify(result), {
    headers: {
      "Content-Type": "application/json; charset=UTF-8",
      "Cache-Control": "no-store"
    }
  });
}
