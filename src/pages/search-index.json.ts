import { getCollection } from "astro:content";

export const prerender = true;

const cleanMarkdown = (markdown: string) =>
  markdown
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/[*_~|]/g, "")
    .replace(/\s+/g, " ")
    .trim();

export async function GET() {
  const posts = (await getCollection("posts", ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf())
    .map((post) => ({
      articleId: post.data.articleId,
      slug: post.slug,
      title: post.data.title,
      description: post.data.description,
      date: post.data.date.toISOString(),
      category: post.data.category,
      scripture: post.data.scripture,
      tags: post.data.tags,
      body: cleanMarkdown(post.body ?? "")
    }));

  return new Response(JSON.stringify(posts), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=0, must-revalidate"
    }
  });
}
