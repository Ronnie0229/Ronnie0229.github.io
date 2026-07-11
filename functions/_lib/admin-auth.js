let cachedKeys = null;
let cachedKeysAt = 0;

function jsonError(message, status) {
  return Response.json(
    { error: message },
    {
      status,
      headers: {
        "Cache-Control": "no-store"
      }
    }
  );
}

function decodeBase64Url(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function decodeJson(value) {
  return JSON.parse(new TextDecoder().decode(decodeBase64Url(value)));
}

function normalizeTeamDomain(value) {
  const domain = String(value || "").trim().replace(/\/+$/, "");
  if (!domain) return "";
  return domain.startsWith("https://") ? domain : `https://${domain}`;
}

async function getAccessKeys(teamDomain) {
  const now = Date.now();
  if (cachedKeys && now - cachedKeysAt < 60 * 60 * 1000) {
    return cachedKeys;
  }

  const response = await fetch(`${teamDomain}/cdn-cgi/access/certs`, {
    headers: { Accept: "application/json" }
  });

  if (!response.ok) {
    throw new Error("无法读取 Cloudflare Access 公钥");
  }

  const data = await response.json();
  cachedKeys = data.keys || [];
  cachedKeysAt = now;
  return cachedKeys;
}

async function verifyAccessToken(token, env) {
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("登录凭证格式无效");

  const [encodedHeader, encodedPayload, encodedSignature] = parts;
  const header = decodeJson(encodedHeader);
  const payload = decodeJson(encodedPayload);
  const teamDomain = normalizeTeamDomain(env.CF_ACCESS_TEAM_DOMAIN);

  if (!teamDomain || !env.CF_ACCESS_AUD || !env.ADMIN_EMAIL) {
    throw new Error("后台权限环境变量尚未配置");
  }

  const keys = await getAccessKeys(teamDomain);
  const jwk = keys.find((key) => key.kid === header.kid);
  if (!jwk) throw new Error("找不到登录凭证对应的公钥");

  const key = await crypto.subtle.importKey(
    "jwk",
    jwk,
    {
      name: "RSASSA-PKCS1-v1_5",
      hash: "SHA-256"
    },
    false,
    ["verify"]
  );
  const validSignature = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5",
    key,
    decodeBase64Url(encodedSignature),
    new TextEncoder().encode(`${encodedHeader}.${encodedPayload}`)
  );

  if (!validSignature) throw new Error("登录凭证签名无效");

  const now = Math.floor(Date.now() / 1000);
  if (!payload.exp || payload.exp <= now) throw new Error("登录凭证已经过期");
  if (payload.nbf && payload.nbf > now) throw new Error("登录凭证尚未生效");

  const audiences = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!audiences.includes(env.CF_ACCESS_AUD)) {
    throw new Error("登录凭证不属于本站后台");
  }

  if (String(payload.iss || "").replace(/\/+$/, "") !== teamDomain) {
    throw new Error("登录凭证来源无效");
  }

  const email = String(payload.email || "").trim().toLowerCase();
  if (!email || email !== String(env.ADMIN_EMAIL).trim().toLowerCase()) {
    throw new Error("当前账号没有后台管理权限");
  }

  return { email };
}

export async function requireAdmin(request, env) {
  const token = request.headers.get("CF-Access-Jwt-Assertion") || "";

  if (!token) {
    return {
      ok: false,
      response: jsonError("请先通过 Cloudflare Access 登录后台", 401)
    };
  }

  try {
    const identity = await verifyAccessToken(token, env);
    return { ok: true, identity };
  } catch (error) {
    return {
      ok: false,
      response: jsonError(
        error instanceof Error ? error.message : "后台权限验证失败",
        403
      )
    };
  }
}

function timingSafeEqual(left, right) {
  const a = new TextEncoder().encode(String(left || ""));
  const b = new TextEncoder().encode(String(right || ""));
  if (a.length !== b.length) return false;
  let difference = 0;
  for (let index = 0; index < a.length; index += 1) {
    difference |= a[index] ^ b[index];
  }
  return difference === 0;
}

export async function requireAdminOrEmailAutomation(request, env) {
  const suppliedSecret = request.headers.get("X-Email-Automation-Secret") || "";
  const configuredSecret = String(env.EMAIL_AUTOMATION_SECRET || "");

  if (
    configuredSecret &&
    suppliedSecret &&
    timingSafeEqual(suppliedSecret, configuredSecret)
  ) {
    return { ok: true, identity: { email: "email-automation" } };
  }

  return requireAdmin(request, env);
}
