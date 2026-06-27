import { getCollection } from "astro:content";
import { buildPostKnowledge, type PostLike } from "../lib/knowledge";

function latestDateForBook(book: string, posts: PostLike[]): string {
  const dates = posts
    .filter((post) => buildPostKnowledge(post).bibleBooks.includes(book))
    .map((post) => new Date(post.data.date ?? 0).valueOf());

  if (!dates.length) return "";
  return new Date(Math.max(...dates)).toISOString();
}

export async function GET({ site }: { site: URL }) {
  const posts = await getCollection("posts", ({ data }) => !data.draft);
  const postKnowledge = posts.map((post) => buildPostKnowledge(post));
  const books = [...new Set(postKnowledge.flatMap((knowledge) => knowledge.bibleBooks))];
  const staticPaths = ["/", "/posts/", "/bible/", "/search/", "/about/"];
  const urls = [
    ...staticPaths.map((path) => ({ path, date: "" })),
    ...books.map((book) => ({
      path: `/bible/${encodeURIComponent(book)}/`,
      date: latestDateForBook(book, posts)
    })),
    ...posts.map((post) => ({
      path: `/posts/${post.slug}/`,
      date: post.data.date.toISOString()
    }))
  ];
  const body = urls
    .map(
      ({ path, date }) =>
        `<url><loc>${new URL(path, site)}</loc>${date ? `<lastmod>${date}</lastmod>` : ""}</url>`
    )
    .join("");

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${body}</urlset>`,
    { headers: { "Content-Type": "application/xml; charset=utf-8" } }
  );
}
