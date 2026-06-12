import { getCollection } from "astro:content";

const escapeXml = (value: string) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");

export async function GET({ site }: { site: URL }) {
  const posts = (await getCollection("posts", ({ data }) => !data.draft)).sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf()
  );
  const items = posts
    .map((post) => {
      const url = new URL(`/posts/${post.slug}/`, site);
      return `<item><title>${escapeXml(post.data.title)}</title><link>${url}</link><guid>${url}</guid><pubDate>${post.data.date.toUTCString()}</pubDate><description>${escapeXml(post.data.description)}</description></item>`;
    })
    .join("");

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Ronnie 的文章</title><link>${site}</link><description>把听到的，看到的，学到的，整理成可以安静阅读的文字。</description><language>zh-CN</language>${items}</channel></rss>`,
    { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } }
  );
}
