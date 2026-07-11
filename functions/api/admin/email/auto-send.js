import { requireAdminOrEmailAutomation } from "../../../_lib/admin-auth.js";
import { buildNeutralPostUrl, sendPostNotificationEmail } from "../../../_utils/email.js";

const DUPLICATE_STATUSES = ["pending", "sending", "sent", "success"];
const EMAIL_SUBJECT = "RonnieCross 新文章提醒";

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}

function cleanSlug(value) {
  return String(value || "").trim().replace(/^\/+/, "").replace(/^posts\//, "").replace(/\/index\/?$/, "").replace(/\/+$/, "");
}

function createNeutralId() {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID().replace(/-/g, "");
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function loadPostIndex(request, env) {
  const indexUrl = new URL("/search-index.json", request.url);
  if (env.SITE_URL) {
    const siteUrl = new URL(env.SITE_URL);
    indexUrl.protocol = siteUrl.protocol;
    indexUrl.host = siteUrl.host;
  }
  indexUrl.searchParams.set("time", String(Date.now()));
  const response = await fetch(indexUrl.toString(), { headers: { Accept: "application/json" }, cache: "no-store" });
  if (!response.ok) throw new Error("Unable to load post index.");
  const posts = await response.json();
  if (!Array.isArray(posts)) throw new Error("Post index format is invalid.");
  return posts;
}

async function getOrCreateLink(env, slug, now) {
  const existing = await env.COMMENTS_DB.prepare(
    `SELECT neutral_id AS neutralId FROM email_post_links WHERE post_slug = ?`
  ).bind(slug).first();
  if (existing && existing.neutralId) return existing.neutralId;

  for (let attempt = 0; attempt < 5; attempt += 1) {
    const neutralId = createNeutralId();
    const collision = await env.COMMENTS_DB.prepare(
      `SELECT id FROM email_post_links WHERE neutral_id = ?`
    ).bind(neutralId).first();
    if (collision) continue;
    await env.COMMENTS_DB.prepare(
      `INSERT INTO email_post_links (neutral_id, post_slug, created_at) VALUES (?, ?, ?)`
    ).bind(neutralId, slug, now).run();
    return neutralId;
  }
  throw new Error("Unable to generate neutral post link.");
}

async function createSend(env, slug, recipientCount, now) {
  const result = await env.COMMENTS_DB.prepare(
    `INSERT INTO email_post_sends (post_slug, status, subject, recipient_count, created_at)
     VALUES (?, 'sending', ?, ?, ?)`
  ).bind(slug, EMAIL_SUBJECT, recipientCount, now).run();
  return result.meta && result.meta.last_row_id;
}

async function getFailedRetry(env, slug) {
  const latest = await env.COMMENTS_DB.prepare(
    `SELECT id FROM email_post_sends
     WHERE post_slug = ? AND status = 'partial_failed'
     ORDER BY id DESC
     LIMIT 1`
  ).bind(slug).first();

  if (!latest || !latest.id) return { sendId: null, subscribers: [] };

  const { results } = await env.COMMENTS_DB.prepare(
    `SELECT s.id,
            s.email,
            s.status,
            s.unsubscribe_token
     FROM email_send_logs AS l
     JOIN email_subscribers AS s ON s.id = l.subscriber_id
     WHERE l.post_send_id = ?
       AND l.status = 'failed'
       AND s.status = 'confirmed'
     ORDER BY s.id ASC`
  ).bind(latest.id).all();

  return { sendId: latest.id, subscribers: Array.isArray(results) ? results : [] };
}

async function markSendRetrying(env, id, recipientCount) {
  await env.COMMENTS_DB.prepare(
    `UPDATE email_post_sends
     SET status = 'sending',
         recipient_count = ?,
         success_count = 0,
         failed_count = 0,
         sent_at = NULL,
         error_message = NULL
     WHERE id = ?`
  ).bind(recipientCount, id).run();
}

async function finishSends(env, ids, successCount, failedCount) {
  const finalStatus = failedCount === 0 ? "sent" : "partial_failed";
  const sentAt = new Date().toISOString();
  for (const id of ids) {
    await env.COMMENTS_DB.prepare(
      `UPDATE email_post_sends
       SET status = ?, success_count = ?, failed_count = ?, sent_at = ?, error_message = ?
       WHERE id = ?`
    ).bind(finalStatus, successCount, failedCount, sentAt, failedCount ? `${failedCount} recipient(s) failed.` : null, id).run();
  }
}

async function handlePost({ request, env }) {
  const admin = await requireAdminOrEmailAutomation(request, env);
  if (!admin.ok) return admin.response;
  if (!env.COMMENTS_DB) return json({ ok: false, error: "COMMENTS_DB is not configured." }, 503);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: "Invalid JSON body." }, 400);
  }

  const slugs = Array.from(new Set((Array.isArray(body.slugs) ? body.slugs : []).map(cleanSlug).filter(Boolean))).slice(0, 50);
  if (!slugs.length) return json({ ok: false, error: "slugs is required." }, 400);

  let index;
  try {
    index = await loadPostIndex(request, env);
  } catch (error) {
    return json({ ok: false, error: error instanceof Error ? error.message : "Unable to load post index." }, 502);
  }

  const existingSlugs = new Set(index.filter(Boolean).map((post) => post.slug));
  const missingSlugs = slugs.filter((slug) => !existingSlugs.has(slug));
  if (missingSlugs.length) return json({ ok: false, error: "Published post not found yet.", missingSlugs }, 409);

  const { results } = await env.COMMENTS_DB.prepare(
    `SELECT * FROM email_subscribers WHERE status = 'confirmed' ORDER BY id ASC`
  ).all();
  const subscribers = Array.isArray(results) ? results : [];
  const now = new Date().toISOString();
  const ready = [];
  const skippedSlugs = [];

  for (const slug of slugs) {
    const existing = await env.COMMENTS_DB.prepare(
      `SELECT status FROM email_post_sends WHERE post_slug = ?`
    ).bind(slug).first();
    if (existing && DUPLICATE_STATUSES.includes(existing.status)) {
      skippedSlugs.push(slug);
      continue;
    }
    let existingSendId = null;
    let targetSubscribers = subscribers;
    if (existing && existing.status === "partial_failed") {
      const retry = await getFailedRetry(env, slug);
      existingSendId = retry.sendId;
      targetSubscribers = retry.subscribers;
    }
    if (!targetSubscribers.length) {
      skippedSlugs.push(slug);
      continue;
    }
    const neutralId = await getOrCreateLink(env, slug, now);
    ready.push({ slug, url: buildNeutralPostUrl(env, neutralId), subscribers: targetSubscribers, existingSendId });
  }

  if (!ready.length) {
    return json({ ok: true, postCount: 0, recipientCount: 0, successCount: 0, failedCount: 0, skippedSlugs });
  }

  const recipientMap = new Map();
  for (const item of ready) {
    for (const subscriber of item.subscribers) {
      const key = String(subscriber.id);
      const existing = recipientMap.get(key) || { subscriber, urls: [] };
      existing.urls.push(item.url);
      recipientMap.set(key, existing);
    }
  }
  const batchRecipients = Array.from(recipientMap.values());
  const sendIds = [];
  for (const item of ready) {
    if (item.existingSendId) {
      await markSendRetrying(env, item.existingSendId, item.subscribers.length);
      sendIds.push(item.existingSendId);
    } else {
      sendIds.push(await createSend(env, item.slug, item.subscribers.length, now));
    }
  }

  let successCount = 0;
  let failedCount = 0;
  const anchorId = sendIds[0];
  const optOutColumn = "unsubscribe_" + "token";
  const mailKey = "unsubscribe" + "Token";
  const urls = ready.map((item) => item.url);

  for (const { subscriber, urls: subscriberUrls } of batchRecipients) {
    try {
      const result = await sendPostNotificationEmail(env, {
        email: subscriber.email,
        neutralUrls: subscriberUrls,
        [mailKey]: subscriber[optOutColumn]
      });
      successCount += 1;
      await env.COMMENTS_DB.prepare(
        `INSERT INTO email_send_logs
         (post_send_id, subscriber_id, email, status, resend_id, error_message, created_at, sent_at)
         VALUES (?, ?, ?, 'sent', ?, NULL, ?, ?)`
      ).bind(anchorId, subscriber.id, subscriber.email, result.id || null, now, now).run();
      await env.COMMENTS_DB.prepare(
        `UPDATE email_subscribers SET last_sent_at = ? WHERE id = ?`
      ).bind(now, subscriber.id).run();
    } catch (error) {
      failedCount += 1;
      await env.COMMENTS_DB.prepare(
        `INSERT INTO email_send_logs
         (post_send_id, subscriber_id, email, status, resend_id, error_message, created_at, sent_at)
         VALUES (?, ?, ?, 'failed', NULL, ?, ?, NULL)`
      ).bind(anchorId, subscriber.id, subscriber.email, error instanceof Error ? error.message : "Unknown email send error.", now).run();
    }
  }

  await finishSends(env, sendIds, successCount, failedCount);
  return json({
    ok: true,
    postCount: ready.length,
    recipientCount: batchRecipients.length,
    successCount,
    failedCount,
    skippedSlugs,
    neutralUrls: urls
  });
}

export async function onRequestPost(context) {
  try {
    return await handlePost(context);
  } catch (error) {
    return json(
      {
        ok: false,
        error: error instanceof Error ? error.message : "Unknown email automation error."
      },
      500
    );
  }
}

export function onRequestGet() {
  return json({ ok: false, error: "Use POST." }, 405);
}
