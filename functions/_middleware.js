export const CANONICAL_ORIGIN = "https://ronniecross.com";

const PERMANENTLY_REMOVED_POST_SLUGS = new Set([
  "2026-06-13-马太福音-2119为什么耶稣要咒诅无花果树",
]);

const CATEGORY_PATHS = new Map([
  ["教会讲道", "/posts/category/sermons/"],
  ["灵命成长", "/posts/category/spiritual-growth/"],
]);

function decodePathSegment(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

export function isPermanentlyRemovedPostSlug(value) {
  return PERMANENTLY_REMOVED_POST_SLUGS.has(decodePathSegment(value).trim());
}

export function permanentlyGoneResponse(request) {
  const body = request.method === "HEAD"
    ? null
    : `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex,follow">
    <title>内容已删除 | Ronnie</title>
  </head>
  <body>
    <main>
      <h1>内容已删除</h1>
      <p>这篇文章已不再提供。</p>
      <p><a href="/posts/">返回全部文章</a></p>
    </main>
  </body>
</html>`;

  return new Response(body, {
    status: 410,
    headers: {
      "Cache-Control": "public, max-age=3600",
      "Content-Type": "text/html; charset=utf-8",
      "X-Robots-Tag": "noindex, follow",
    },
  });
}

export function matchPermanentlyRemovedPost(url) {
  const directPostMatch = url.pathname.match(/^\/posts\/([^/]+)\/?$/);
  if (directPostMatch && isPermanentlyRemovedPostSlug(directPostMatch[1])) {
    return true;
  }

  if (url.pathname === "/posts" || url.pathname === "/posts/") {
    const focus = url.searchParams.get("focus");
    return Boolean(focus && isPermanentlyRemovedPostSlug(focus));
  }

  return false;
}

export function redirectToCanonicalHost(url) {
  if (url.hostname === "ronniecross.com" && url.protocol === "https:") {
    return null;
  }

  const target = new URL(`${url.pathname}${url.search}${url.hash}`, CANONICAL_ORIGIN);
  return Response.redirect(target.toString(), 301);
}

export function redirectLegacyPostsQuery(url) {
  if (url.pathname !== "/posts" && url.pathname !== "/posts/") {
    return null;
  }

  const focus = url.searchParams.get("focus")?.trim();
  if (focus) {
    const target = new URL(`/posts/${encodeURIComponent(focus)}/`, CANONICAL_ORIGIN);
    return Response.redirect(target.toString(), 301);
  }

  const category = url.searchParams.get("category")?.trim();
  const categoryPath = category ? CATEGORY_PATHS.get(category) : null;
  if (categoryPath) {
    return Response.redirect(new URL(categoryPath, CANONICAL_ORIGIN).toString(), 301);
  }

  return null;
}

export async function onRequest(context) {
  const url = new URL(context.request.url);

  if (matchPermanentlyRemovedPost(url)) {
    return permanentlyGoneResponse(context.request);
  }

  const postsRedirect = redirectLegacyPostsQuery(url);
  if (postsRedirect) return postsRedirect;

  const hostRedirect = redirectToCanonicalHost(url);
  if (hostRedirect) return hostRedirect;

  return context.next();
}
