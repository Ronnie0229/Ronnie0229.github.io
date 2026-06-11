import { requireAdmin } from "../../_lib/admin-auth.js";

function randomState() {
  const bytes = crypto.getRandomValues(new Uint8Array(24));
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function onRequestGet({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;

  if (!env.GITHUB_CLIENT_ID) {
    return new Response("GitHub OAuth Client ID 尚未配置", { status: 503 });
  }

  const requestUrl = new URL(request.url);
  const state = randomState();
  const authorizeUrl = new URL("https://github.com/login/oauth/authorize");
  authorizeUrl.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  authorizeUrl.searchParams.set("redirect_uri", `${requestUrl.origin}/admin/api/callback`);
  authorizeUrl.searchParams.set("scope", "public_repo read:user");
  authorizeUrl.searchParams.set("state", state);

  return new Response(null, {
    status: 302,
    headers: {
      Location: authorizeUrl.toString(),
      "Cache-Control": "no-store",
      "Set-Cookie": [
        `ronniecross_oauth_state=${state}`,
        "Path=/admin/api/callback",
        "HttpOnly",
        "Secure",
        "SameSite=Lax",
        "Max-Age=600"
      ].join("; ")
    }
  });
}
