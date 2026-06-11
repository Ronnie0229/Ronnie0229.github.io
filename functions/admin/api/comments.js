import { requireAdmin } from "../../_lib/admin-auth.js";

const MAX_LIMIT = 100;

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store"
    }
  });
}

function parseId(value) {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
}

function requireSameOrigin(request) {
  const origin = request.headers.get("Origin");
  return origin && origin === new URL(request.url).origin;
}

async function updateThreadStatus(db, id, status) {
  return db.prepare(
    `WITH RECURSIVE thread(id) AS (
       SELECT id FROM comments WHERE id = ?
       UNION ALL
       SELECT comments.id
       FROM comments
       INNER JOIN thread ON comments.parent_id = thread.id
     )
     UPDATE comments
     SET status = ?
     WHERE id IN (SELECT id FROM thread)`
  )
    .bind(id, status)
    .run();
}

export async function onRequestGet({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;
  if (!env.COMMENTS_DB) return json({ error: "留言数据库尚未配置" }, 503);

  const url = new URL(request.url);
  const requestedStatus = url.searchParams.get("status") || "all";
  const status = ["all", "visible", "hidden"].includes(requestedStatus)
    ? requestedStatus
    : "all";
  const query = (url.searchParams.get("q") || "").trim().slice(0, 100);
  const postSlug = (url.searchParams.get("slug") || "").trim().slice(0, 300);
  const limit = Math.min(
    Math.max(Number(url.searchParams.get("limit")) || 50, 1),
    MAX_LIMIT
  );
  const offset = Math.max(Number(url.searchParams.get("offset")) || 0, 0);
  const conditions = [];
  const bindings = [];

  if (status !== "all") {
    conditions.push("status = ?");
    bindings.push(status);
  }
  if (query) {
    conditions.push("(author_name LIKE ? OR content LIKE ? OR post_slug LIKE ?)");
    const pattern = `%${query}%`;
    bindings.push(pattern, pattern, pattern);
  }
  if (postSlug) {
    conditions.push("post_slug = ?");
    bindings.push(postSlug);
  }

  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";

  try {
    const result = await env.COMMENTS_DB.prepare(
      `SELECT id,
              post_slug AS postSlug,
              parent_id AS parentId,
              author_name AS authorName,
              content,
              status,
              created_at AS createdAt
       FROM comments
       ${where}
       ORDER BY created_at DESC, id DESC
       LIMIT ? OFFSET ?`
    )
      .bind(...bindings, limit, offset)
      .all();
    const count = await env.COMMENTS_DB.prepare(
      `SELECT COUNT(*) AS total FROM comments ${where}`
    )
      .bind(...bindings)
      .first();

    return json({
      comments: result.results || [],
      total: Number(count?.total) || 0,
      limit,
      offset
    });
  } catch {
    return json({ error: "暂时无法读取留言管理数据" }, 500);
  }
}

export async function onRequestPatch({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;
  if (!env.COMMENTS_DB) return json({ error: "留言数据库尚未配置" }, 503);
  if (!requireSameOrigin(request)) return json({ error: "请求来源无效" }, 403);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "提交内容格式不正确" }, 400);
  }

  const id = parseId(body?.id);
  const action = body?.action;
  const status = action === "hide" ? "hidden" : action === "restore" ? "visible" : "";

  if (!id || !status) {
    return json({ error: "留言编号或操作无效" }, 400);
  }

  try {
    const existing = await env.COMMENTS_DB.prepare(
      "SELECT id FROM comments WHERE id = ?"
    )
      .bind(id)
      .first();
    if (!existing) return json({ error: "留言不存在" }, 404);

    await updateThreadStatus(env.COMMENTS_DB, id, status);
    return json({ ok: true, id, status });
  } catch {
    return json({ error: "暂时无法更新留言状态" }, 500);
  }
}

export async function onRequestDelete({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;
  if (!env.COMMENTS_DB) return json({ error: "留言数据库尚未配置" }, 503);
  if (!requireSameOrigin(request)) return json({ error: "请求来源无效" }, 403);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "提交内容格式不正确" }, 400);
  }

  const id = parseId(body?.id);
  if (!id || body?.confirmation !== "删除") {
    return json({ error: "永久删除需要输入确认文字" }, 400);
  }

  try {
    const existing = await env.COMMENTS_DB.prepare(
      "SELECT id FROM comments WHERE id = ?"
    )
      .bind(id)
      .first();
    if (!existing) return json({ error: "留言不存在" }, 404);

    await env.COMMENTS_DB.prepare(
      `WITH RECURSIVE thread(id) AS (
         SELECT id FROM comments WHERE id = ?
         UNION ALL
         SELECT comments.id
         FROM comments
         INNER JOIN thread ON comments.parent_id = thread.id
       )
       DELETE FROM comments
       WHERE id IN (SELECT id FROM thread)`
    )
      .bind(id)
      .run();

    return json({ ok: true, id });
  } catch {
    return json({ error: "暂时无法永久删除留言" }, 500);
  }
}
