import { requireAdmin } from "../../../_lib/admin-auth.js";

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}

export async function onRequestGet({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;

  if (!env.COMMENTS_DB) {
    return json({ ok: false, error: "COMMENTS_DB is not configured." }, 503);
  }

  const { results } = await env.COMMENTS_DB.prepare(
    `SELECT id,
            email,
            status,
            created_at AS createdAt,
            confirmed_at AS confirmedAt,
            unsubscribed_at AS unsubscribedAt,
            last_sent_at AS lastSentAt
     FROM email_subscribers
     ORDER BY created_at DESC, id DESC`
  ).all();

  const subscribers = Array.isArray(results) ? results : [];
  const counts = subscribers.reduce(
    (summary, subscriber) => {
      summary.total += 1;
      if (subscriber.status === "confirmed") summary.confirmed += 1;
      if (subscriber.status === "pending") summary.pending += 1;
      if (subscriber.status === "unsubscribed") summary.unsubscribed += 1;
      return summary;
    },
    { total: 0, confirmed: 0, pending: 0, unsubscribed: 0 }
  );

  return json({ ok: true, subscribers, counts });
}

export function onRequestPost() {
  return json({ ok: false, error: "Use GET." }, 405);
}
