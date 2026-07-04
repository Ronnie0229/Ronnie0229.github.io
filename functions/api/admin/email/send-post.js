import { requireAdmin } from "../../../_lib/admin-auth.js";
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
  return String(value || "")
    .trim()
    .replace(/^\/+/, "")
    .replace(/^posts\//, "")
    .replace(/\/index\/?$/, "")
    .replace(/\/+$/, "");
}

function createNeutralId() {
  if (typeof crypto.randomUUID === "function") {
    return crypto.randomUUID().replace(/-/g, "");
  }

  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function readJson(request) {
  try {
    const data = await request.json();
    return data && typeof data === "object" ? data : null;
  } catch {
    return null;
  }
}

async function loadPost(request, env, slug) {
  const indexUrl = new URL("/search-index.json", request.url);

  if (env.SITE_URL) {
    const siteUrl = new URL(env.SITE_URL);
    indexUrl.protocol = siteUrl.protocol;
    indexUrl.host = siteUrl.host;
  }

  const response = await fetch(indexUrl.toString(), {
    headers: { Accept: "application/json" }
  });

  if (!response.ok) {
    throw new Error("Unable to load post index.");
  }

  const posts = await response.json();
  if (!Array.isArray(posts)) {
    throw new Error("Post index format is invalid.");
  }

  return posts.find((post) => post && post.slug === slug) || null;
}

async function getConfirmedSubscribers(env) {
  const { results } = await env.COMMENTS_DB.prepare(
    `SELECT id, email, unsubscribe_token AS unsubscribeToken
     FROM email_subscribers
     WHERE status = 'confirmed'
     ORDER BY id ASC`
  ).all();

  return Array.isArray(results) ? results : [];
}

async function findExistingSend(env, slug) {
  return env.COMMENTS_DB.prepare(
    `SELECT id, status
     FROM email_post_sends
     WHERE post_slug = ?`
  )
    .bind(slug)
    .first();
}

async function findExistingPostLink(env, slug) {
  return env.COMMENTS_DB.prepare(
    `SELECT neutral_id AS neutralId
     FROM email_post_links
     WHERE post_slug = ?`
  )
    .bind(slug)
    .first();
}

async function findPostLinkByNeutralId(env, neutralId) {
  return env.COMMENTS_DB.prepare(
    `SELECT id
     FROM email_post_links
     WHERE neutral_id = ?`
  )
    .bind(neutralId)
    .first();
}

async function createUniqueNeutralId(env) {
  for (let attempt = 0; attempt < 5; attempt += 1) {
    const neutralId = createNeutralId();
    const existing = await findPostLinkByNeutralId(env, neutralId);
    if (!existing) return neutralId;
  }

  throw new Error("Unable to generate neutral post link.");
}

async function getOrCreatePostLink(env, slug, now) {
  const existing = await findExistingPostLink(env, slug);
  if (existing?.neutralId) return existing.neutralId;

  const neutralId = await createUniqueNeutralId(env);
  await env.COMMENTS_DB.prepare(
    `INSERT INTO email_post_links
     (neutral_id, post_slug, created_at)
     VALUES (?, ?, ?)`
  )
    .bind(neutralId, slug, now)
    .run();

  return neutralId;
}

async function createPostSend(env, { slug, recipientCount, now }) {
  const result = await env.COMMENTS_DB.prepare(
    `INSERT INTO email_post_sends
     (post_slug, status, subject, recipient_count, created_at)
     VALUES (?, 'sending', ?, ?, ?)`
  )
    .bind(slug, EMAIL_SUBJECT, recipientCount, now)
    .run();

  return result.meta?.last_row_id;
}

async function logSendResult(env, { postSendId, subscriber, status, resendId, errorMessage, now }) {
  await env.COMMENTS_DB.prepare(
    `INSERT INTO email_send_logs
     (post_send_id, subscriber_id, email, status, resend_id, error_message, created_at, sent_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      postSendId,
      subscriber.id,
      subscriber.email,
      status,
      resendId || null,
      errorMessage || null,
      now,
      status === "sent" ? now : null
    )
    .run();
}

export async function onRequestPost({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;

  if (!env.COMMENTS_DB) {
    return json({ ok: false, error: "COMMENTS_DB is not configured." }, 503);
  }

  const body = await readJson(request);
  const slug = cleanSlug(body?.slug);
  const dryRun = body?.dryRun !== false;

  if (!slug) {
    return json({ ok: false, error: "slug is required." }, 400);
  }

  let post;
  try {
    post = await loadPost(request, env, slug);
  } catch (error) {
    return json(
      {
        ok: false,
        error: error instanceof Error ? error.message : "Unable to load post index."
      },
      502
    );
  }

  if (!post) {
    return json({ ok: false, error: "Post not found." }, 404);
  }

  const subscribers = await getConfirmedSubscribers(env);
  const existing = await findExistingSend(env, slug);
  const now = new Date().toISOString();
  const neutralId = await getOrCreatePostLink(env, slug, now);
  const neutralUrl = buildNeutralPostUrl(env, neutralId);

  if (dryRun) {
    return json({
      ok: true,
      dryRun: true,
      neutralUrl,
      recipientCount: subscribers.length
    });
  }

  if (existing && DUPLICATE_STATUSES.includes(existing.status)) {
    return json(
      {
        ok: false,
        error: "This post has already been queued or sent.",
        existingStatus: existing.status
      },
      409
    );
  }

  const postSendId = await createPostSend(env, {
    slug,
    recipientCount: subscribers.length,
    now
  });

  let successCount = 0;
  let failedCount = 0;

  for (const subscriber of subscribers) {
    try {
      const result = await sendPostNotificationEmail(env, {
        email: subscriber.email,
        neutralUrl,
        unsubscribeToken: subscriber.unsubscribeToken
      });
      successCount += 1;
      await logSendResult(env, {
        postSendId,
        subscriber,
        status: "sent",
        resendId: result.id,
        now
      });
      await env.COMMENTS_DB.prepare(
        `UPDATE email_subscribers
         SET last_sent_at = ?
         WHERE id = ?`
      )
        .bind(now, subscriber.id)
        .run();
    } catch (error) {
      failedCount += 1;
      await logSendResult(env, {
        postSendId,
        subscriber,
        status: "failed",
        errorMessage: error instanceof Error ? error.message : "Unknown email send error.",
        now
      });
    }
  }

  const finalStatus = failedCount === 0 ? "sent" : "partial_failed";
  await env.COMMENTS_DB.prepare(
    `UPDATE email_post_sends
     SET status = ?,
         success_count = ?,
         failed_count = ?,
         sent_at = ?,
         error_message = ?
     WHERE id = ?`
  )
    .bind(
      finalStatus,
      successCount,
      failedCount,
      new Date().toISOString(),
      failedCount === 0 ? null : `${failedCount} recipient(s) failed.`,
      postSendId
    )
    .run();

  return json({
    ok: true,
    dryRun: false,
    neutralUrl,
    recipientCount: subscribers.length,
    successCount,
    failedCount
  });
}

export function onRequestGet() {
  return json({ ok: false, error: "Use POST." }, 405);
}
