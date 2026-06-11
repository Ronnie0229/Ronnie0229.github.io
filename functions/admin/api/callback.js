import { requireAdmin } from "../../_lib/admin-auth.js";

function getCookie(request, name) {
  const cookie = request.headers.get("Cookie") || "";
  for (const item of cookie.split(";")) {
    const [key, ...value] = item.trim().split("=");
    if (key === name) return decodeURIComponent(value.join("="));
  }
  return "";
}

function renderResult(origin, status, content) {
  const message = JSON.stringify(
    `authorization:github:${status}:${JSON.stringify(content)}`
  ).replace(/</g, "\\u003c");
  const safeOrigin = JSON.stringify(origin).replace(/</g, "\\u003c");

  return `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <title>正在完成登录</title>
  </head>
  <body>
    <p>正在完成登录，请稍候...</p>
    <script>
      const targetOrigin = ${safeOrigin};
      const message = ${message};
      const receiveMessage = (event) => {
        if (event.origin !== targetOrigin || event.source !== window.opener) return;
        window.opener.postMessage(message, targetOrigin);
        window.removeEventListener("message", receiveMessage);
      };
      window.addEventListener("message", receiveMessage);
      if (window.opener) {
        window.opener.postMessage("authorizing:github", targetOrigin);
      }
    </script>
  </body>
</html>`;
}

export async function onRequestGet({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;

  if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) {
    return new Response("GitHub OAuth 环境变量尚未配置", { status: 503 });
  }

  const url = new URL(request.url);
  const code = url.searchParams.get("code") || "";
  const state = url.searchParams.get("state") || "";
  const savedState = getCookie(request, "ronniecross_oauth_state");

  if (!code || !state || !savedState || state !== savedState) {
    return new Response(renderResult(url.origin, "error", {
      message: "登录请求已经失效，请返回后台重新登录。"
    }), {
      status: 400,
      headers: {
        "Content-Type": "text/html; charset=UTF-8",
        "Cache-Control": "no-store"
      }
    });
  }

  const response = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "User-Agent": "ronniecross-admin"
    },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: `${url.origin}/admin/api/callback`
    })
  });
  const result = await response.json();

  if (!response.ok || result.error || !result.access_token) {
    return new Response(renderResult(url.origin, "error", {
      message: result.error_description || "GitHub 登录失败，请稍后再试。"
    }), {
      status: 401,
      headers: {
        "Content-Type": "text/html; charset=UTF-8",
        "Cache-Control": "no-store"
      }
    });
  }

  return new Response(renderResult(url.origin, "success", {
    token: result.access_token,
    provider: "github"
  }), {
    headers: {
      "Content-Type": "text/html; charset=UTF-8",
      "Cache-Control": "no-store",
      "Set-Cookie": [
        "ronniecross_oauth_state=",
        "Path=/admin/api/callback",
        "HttpOnly",
        "Secure",
        "SameSite=Lax",
        "Max-Age=0"
      ].join("; ")
    }
  });
}
