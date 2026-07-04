import { sendConfirmEmail } from "../_utils/email.js";

const SUCCESS_MESSAGE = "如果邮箱地址有效，我们会发送一封确认邮件。请前往邮箱完成确认。";
const INVALID_EMAIL_MESSAGE = "请输入有效的邮箱地址。";
const SERVER_ERROR_MESSAGE = "暂时无法完成订阅，请稍后再试。";
const MAX_EMAIL_LENGTH = 254;

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}

function cleanText(value) {
  return typeof value === "string" ? value.trim() : "";
}

function normalizeEmail(value) {
  return cleanText(value).toLowerCase();
}

function isValidEmail(email) {
  if (!email || email.length > MAX_EMAIL_LENGTH || email.includes(" ")) return false;
  const at = email.indexOf("@");
  const dot = email.lastIndexOf(".");
  return at > 0 && dot > at + 1 && dot < email.length - 1;
}

function createToken() {
  if (typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function onRequestPost({ request, env }) {
  if (!env.COMMENTS_DB) {
    return json({ ok: false, message: SERVER_ERROR_MESSAGE }, 503);
  }

  let body;

  try {
    body = await request.json();
  } catch {
    return json({ ok: false, message: INVALID_EMAIL_MESSAGE }, 400);
  }

  if (!body || typeof body !== "object") {
    return json({ ok: false, message: INVALID_EMAIL_MESSAGE }, 400);
  }

  const website = cleanText(body.website);

  if (website) {
    return json({ ok: true, message: SUCCESS_MESSAGE });
  }

  const email = normalizeEmail(body.email);

  if (!isValidEmail(email)) {
    return json({ ok: false, message: INVALID_EMAIL_MESSAGE }, 400);
  }

  try {
    const now = new Date().toISOString();
    const existing = await env.COMMENTS_DB.prepare(
      `SELECT id, status, unsubscribe_token AS unsubscribeToken
       FROM email_subscribers
       WHERE email = ?`
    )
      .bind(email)
      .first();

    if (!existing) {
      const ckey = createToken();
      const ukey = createToken();

      await env.COMMENTS_DB.prepare(
        `INSERT INTO email_subscribers
         (email, status, confirm_token, unsubscribe_token, created_at)
         VALUES (?, 'pending', ?, ?, ?)`
      )
        .bind(email, ckey, ukey, now)
        .run();

      await sendConfirmEmail(env, { email, confirmToken: ckey });
      return json({ ok: true, message: SUCCESS_MESSAGE });
    }

    if (existing.status === "confirmed") {
      return json({ ok: true, message: SUCCESS_MESSAGE });
    }

    const ckey = createToken();
    const ukey = existing.unsubscribeToken || createToken();

    await env.COMMENTS_DB.prepare(
      `UPDATE email_subscribers
       SET status = 'pending',
           confirm_token = ?,
           unsubscribe_token = ?,
           unsubscribed_at = NULL
       WHERE email = ?`
    )
      .bind(ckey, ukey, email)
      .run();

    await sendConfirmEmail(env, { email, confirmToken: ckey });
    return json({ ok: true, message: SUCCESS_MESSAGE });
  } catch {
    return json({ ok: false, message: SERVER_ERROR_MESSAGE }, 500);
  }
}

export function onRequestGet() {
  return json({ ok: false, message: "请使用 POST 提交订阅。" }, 405);
}

export function onRequestHead() {
  return new Response(null, {
    status: 204,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}
