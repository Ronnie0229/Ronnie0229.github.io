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
  const safeStatus = JSON.stringify(status).replace(/</g, "\\u003c");
  const safeContent = JSON.stringify(content).replace(/</g, "\\u003c");

  return `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>正在完成登录</title>
    <style>
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: 24px;
        box-sizing: border-box;
        color: #1d1d1f;
        background: #fff;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
          "PingFang SC", "Microsoft YaHei", sans-serif;
        text-align: center;
      }
      main { max-width: 420px; }
      p { line-height: 1.7; }
      a {
        display: inline-block;
        margin-top: 12px;
        color: #06c;
        text-decoration: none;
      }
    </style>
  </head>
  <body>
    <main>
      <p id="status">正在完成登录，请稍候...</p>
      <a id="return-link" href="/admin/editor.html" hidden>返回文章管理</a>
    </main>
    <script>
      const targetOrigin = ${safeOrigin};
      const message = ${message};
      const authStatus = ${safeStatus};
      const authContent = ${safeContent};
      const statusElement = document.getElementById("status");
      const returnLink = document.getElementById("return-link");
      let completed = false;
      let storageReady = authStatus !== "success";

      if (authStatus === "success" && authContent.token) {
        try {
          localStorage.setItem("decap-cms-user", JSON.stringify({
            token: authContent.token,
            backendName: "github"
          }));
          storageReady = true;
        } catch {
          statusElement.textContent =
            "Safari 无法保存登录状态，请关闭无痕浏览后重试。";
          returnLink.hidden = false;
        }
      }

      const returnToEditor = () => {
        if (authStatus === "success" && storageReady) {
          window.location.replace("/admin/editor.html");
          return;
        }
        statusElement.textContent =
          authContent.message || "登录没有完成，请返回文章管理后重试。";
        returnLink.hidden = false;
      };

      const sendHandshake = () => {
        if (!window.opener || window.opener.closed) return false;
        window.opener.postMessage("authorizing:github", targetOrigin);
        return true;
      };

      const sendResult = () => {
        if (completed || !window.opener || window.opener.closed) return false;
        completed = true;
        window.opener.postMessage(message, targetOrigin);
        statusElement.textContent = "登录完成，正在返回文章管理...";
        setTimeout(() => window.close(), 300);
        return true;
      };

      const receiveMessage = (event) => {
        if (
          event.origin !== targetOrigin ||
          event.data !== "authorizing:github"
        ) return;
        window.removeEventListener("message", receiveMessage);
        sendResult();
      };

      window.addEventListener("message", receiveMessage);

      if (sendHandshake()) {
        const handshakeTimer = setInterval(sendHandshake, 500);
        setTimeout(() => {
          clearInterval(handshakeTimer);
          if (!completed) returnToEditor();
        }, 5000);
      } else {
        setTimeout(returnToEditor, 300);
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
