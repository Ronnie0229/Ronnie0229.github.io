export const CANONICAL_ORIGIN = "https://ronniecross.com";

const CATEGORY_PATHS = new Map([
  ["教会讲道", "/posts/category/sermons/"],
  ["灵命成长", "/posts/category/spiritual-growth/"],
]);

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

  const postsRedirect = redirectLegacyPostsQuery(url);
  if (postsRedirect) return postsRedirect;

  const hostRedirect = redirectToCanonicalHost(url);
  if (hostRedirect) return hostRedirect;

  return context.next();
}
