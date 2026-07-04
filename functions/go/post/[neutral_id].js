function redirectTo(path, request) {
  const target = new URL(path, request.url);
  return Response.redirect(target.toString(), 302);
}

export async function onRequestGet({ params, request, env }) {
  const neutralId = String(params.neutral_id || "").trim();

  if (!neutralId || !env.COMMENTS_DB) {
    return redirectTo("/posts/", request);
  }

  try {
    const row = await env.COMMENTS_DB.prepare(
      `SELECT post_slug AS postSlug
       FROM email_post_links
       WHERE neutral_id = ?`
    )
      .bind(neutralId)
      .first();

    if (!row?.postSlug) {
      return redirectTo("/posts/", request);
    }

    return redirectTo(`/posts/${row.postSlug}/`, request);
  } catch {
    return redirectTo("/posts/", request);
  }
}
