const MAX_NAME_LENGTH = 40;
const MAX_CONTENT_LENGTH = 2000;
const MAX_SLUG_LENGTH = 300;
const RATE_LIMIT_MINUTES = 1;
const RATE_LIMIT_COUNT = 3;

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store"
    }
  });
}

function cleanText(value) {
  return typeof value === "string" ? value.trim() : "";
}

async function hashVisitor(request) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const userAgent = request.headers.get("User-Agent") || "unknown";
  const bytes = new TextEncoder().encode(`${ip}|${userAgent}`);
  const digest = await crypto.subtle.digest("SHA-256", bytes);

  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export async function onRequestGet({ request, env }) {
  if (!env.COMMENTS_DB) {
    return json({ error: "留言数据库尚未配置" }, 503);
  }

  const postSlug = cleanText(new URL(request.url).searchParams.get("slug"));

  if (!postSlug || postSlug.length > MAX_SLUG_LENGTH) {
    return json({ error: "文章地址无效" }, 400);
  }

  try {
    const result = await env.COMMENTS_DB.prepare(
      `SELECT id, parent_id AS parentId, author_name AS authorName, content, created_at AS createdAt
       FROM comments
       WHERE post_slug = ? AND status = 'visible'
       ORDER BY created_at ASC, id ASC`
    )
      .bind(postSlug)
      .all();

    return json({ comments: result.results || [] });
  } catch {
    return json({ error: "暂时无法读取留言" }, 500);
  }
}

export async function onRequestPost({ request, env }) {
  if (!env.COMMENTS_DB) {
    return json({ error: "留言数据库尚未配置" }, 503);
  }

  let body;

  try {
    body = await request.json();
  } catch {
    return json({ error: "提交内容格式不正确" }, 400);
  }

  if (!body || typeof body !== "object") {
    return json({ error: "提交内容格式不正确" }, 400);
  }

  const postSlug = cleanText(body.postSlug);
  const authorName = cleanText(body.authorName);
  const content = cleanText(body.content);
  const website = cleanText(body.website);
  const parentId = body.parentId === null || body.parentId === undefined
    ? null
    : Number(body.parentId);

  if (website) {
    return json({ error: "提交失败" }, 400);
  }

  if (!postSlug || postSlug.length > MAX_SLUG_LENGTH) {
    return json({ error: "文章地址无效" }, 400);
  }

  if (!authorName || authorName.length > MAX_NAME_LENGTH) {
    return json({ error: `昵称需为 1-${MAX_NAME_LENGTH} 个字符` }, 400);
  }

  if (!content || content.length > MAX_CONTENT_LENGTH) {
    return json({ error: `留言需为 1-${MAX_CONTENT_LENGTH} 个字符` }, 400);
  }

  if (parentId !== null && (!Number.isInteger(parentId) || parentId < 1)) {
    return json({ error: "回复的留言无效" }, 400);
  }

  try {
    if (parentId !== null) {
      const parent = await env.COMMENTS_DB.prepare(
        `SELECT id FROM comments
         WHERE id = ? AND post_slug = ? AND status = 'visible'`
      )
        .bind(parentId, postSlug)
        .first();

      if (!parent) {
        return json({ error: "要回复的留言不存在" }, 400);
      }
    }

    const visitorHash = await hashVisitor(request);
    const recent = await env.COMMENTS_DB.prepare(
      `SELECT COUNT(*) AS count
       FROM comments
       WHERE visitor_hash = ?
         AND julianday(created_at) >= julianday('now', ?)`
    )
      .bind(visitorHash, `-${RATE_LIMIT_MINUTES} minute`)
      .first();

    if (Number(recent?.count || 0) >= RATE_LIMIT_COUNT) {
      return json({ error: "提交过于频繁，请稍后再试" }, 429);
    }

    const duplicate = await env.COMMENTS_DB.prepare(
      `SELECT id FROM comments
       WHERE post_slug = ? AND visitor_hash = ? AND content = ?
         AND julianday(created_at) >= julianday('now', '-10 minutes')
       LIMIT 1`
    )
      .bind(postSlug, visitorHash, content)
      .first();

    if (duplicate) {
      return json({ error: "请不要重复提交相同内容" }, 409);
    }

    const result = await env.COMMENTS_DB.prepare(
      `INSERT INTO comments
       (post_slug, parent_id, author_name, content, visitor_hash)
       VALUES (?, ?, ?, ?, ?)`
    )
      .bind(postSlug, parentId, authorName, content, visitorHash)
      .run();

    const comment = await env.COMMENTS_DB.prepare(
      `SELECT id, parent_id AS parentId, author_name AS authorName, content, created_at AS createdAt
       FROM comments WHERE id = ?`
    )
      .bind(result.meta.last_row_id)
      .first();

    return json({ comment }, 201);
  } catch {
    return json({ error: "暂时无法提交留言" }, 500);
  }
}
