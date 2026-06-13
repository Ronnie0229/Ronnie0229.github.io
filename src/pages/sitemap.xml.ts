import { getCollection } from "astro:content";
import { getBooksForScripture } from "../data/bible";

export async function GET({ site }: { site: URL }) {
  const posts = await getCollection("posts", ({ data }) => !data.draft);
  const books = [
    ...new Set(posts.flatMap((post) => getBooksForScripture(post.data.scripture)))
  ];
  const staticPaths = ["/", "/posts/", "/bible/", "/search/", "/about/"];
  const urls = [
    ...staticPaths.map((path) => ({ path, date: "" })),
    ...books.map((book) => ({
      path: `/bible/${encodeURIComponent(book)}/`,
      date: ""
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
