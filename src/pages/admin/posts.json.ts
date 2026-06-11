import { getCollection } from "astro:content";

export async function GET() {
  const posts = await getCollection("posts");
  const result = posts
    .map((post) => ({
      articleId: post.data.articleId,
      slug: post.slug,
      title: post.data.title,
      draft: post.data.draft
    }))
    .sort((a, b) => a.title.localeCompare(b.title, "zh-CN"));

  return new Response(JSON.stringify(result), {
    headers: {
      "Content-Type": "application/json; charset=UTF-8",
      "Cache-Control": "no-store"
    }
  });
}
