function redirectTo(path, request) {
  const target = new URL(path, request.url);
  return Response.redirect(target.toString(), 302);
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const ukey = url.searchParams.get("token")?.trim() || "";

  if (!ukey || !env.COMMENTS_DB) {
    return redirectTo("/subscribe/unsubscribed/?status=invalid", request);
  }

  try {
    const subscriber = await env.COMMENTS_DB.prepare(
      `SELECT id FROM email_subscribers WHERE unsubscribe_token = ?`
    )
      .bind(ukey)
      .first();

    if (!subscriber) {
      return redirectTo("/subscribe/unsubscribed/?status=invalid", request);
    }

    await env.COMMENTS_DB.prepare(
      `UPDATE email_subscribers
       SET status = 'unsubscribed',
           unsubscribed_at = ?
       WHERE id = ?`
    )
      .bind(new Date().toISOString(), subscriber.id)
      .run();

    return redirectTo("/subscribe/unsubscribed/", request);
  } catch {
    return redirectTo("/subscribe/unsubscribed/?status=invalid", request);
  }
}
