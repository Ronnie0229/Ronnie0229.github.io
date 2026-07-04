function redirectTo(path, request) {
  const target = new URL(path, request.url);
  return Response.redirect(target.toString(), 302);
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const ckey = url.searchParams.get("token")?.trim() || "";

  if (!ckey || !env.COMMENTS_DB) {
    return redirectTo("/subscribe/confirmed/?status=invalid", request);
  }

  try {
    const subscriber = await env.COMMENTS_DB.prepare(
      `SELECT id FROM email_subscribers WHERE confirm_token = ?`
    )
      .bind(ckey)
      .first();

    if (!subscriber) {
      return redirectTo("/subscribe/confirmed/?status=invalid", request);
    }

    await env.COMMENTS_DB.prepare(
      `UPDATE email_subscribers
       SET status = 'confirmed',
           confirmed_at = ?,
           unsubscribed_at = NULL
       WHERE id = ?`
    )
      .bind(new Date().toISOString(), subscriber.id)
      .run();

    return redirectTo("/subscribe/confirmed/", request);
  } catch {
    return redirectTo("/subscribe/confirmed/?status=invalid", request);
  }
}
