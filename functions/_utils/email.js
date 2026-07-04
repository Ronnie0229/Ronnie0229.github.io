const RESEND_ENDPOINT = "https://api.resend.com/emails";

export function siteUrlFromEnv(env) {
  const raw = typeof env.SITE_URL === "string" ? env.SITE_URL.trim() : "";
  return raw ? raw.replace(/\/$/, "") : "https://ronniecross.com";
}

export function buildConfirmUrl(env, token) {
  const siteUrl = siteUrlFromEnv(env);
  const url = new URL("/api/confirm", siteUrl);
  url.searchParams.set("token", token);
  return url.toString();
}

export function buildUnsubscribeUrl(env, token) {
  const siteUrl = siteUrlFromEnv(env);
  const url = new URL("/api/unsubscribe", siteUrl);
  url.searchParams.set("token", token);
  return url.toString();
}

export async function sendConfirmEmail(env, { email, confirmToken }) {
  if (!env.RESEND_API_KEY || !env.EMAIL_FROM) {
    throw new Error("Email service is not configured.");
  }

  const confirmUrl = buildConfirmUrl(env, confirmToken);
  const payload = {
    from: env.EMAIL_FROM,
    to: [email],
    subject: "确认订阅 RonnieCross 更新提醒",
    text: [
      "你好，",
      "",
      "你正在订阅 RonnieCross 的更新提醒。",
      "",
      "请点击下面链接确认订阅：",
      "",
      confirmUrl,
      "",
      "如果这不是你本人操作，可以忽略这封邮件。"
    ].join("\n"),
    html: [
      "<p>你好，</p>",
      "<p>你正在订阅 RonnieCross 的更新提醒。</p>",
      `<p><a href=\"${escapeHtml(confirmUrl)}\">点击这里确认订阅</a></p>`,
      "<p>如果这不是你本人操作，可以忽略这封邮件。</p>"
    ].join("\n")
  };

  const response = await fetch(RESEND_ENDPOINT, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Resend request failed: ${response.status}`);
  }
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;");
}
