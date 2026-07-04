const MAX_SLUG_LENGTH = 300;
const MAX_BATCH_SIZE = 50;

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}

function emptyNoindex(status = 204) {
  return new Response(null, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}

function cleanSlug(value) {
  return typeof value === "string" ? value.trim() : "";
}

function isValidSlug(slug) {
  return slug.length > 0 && slug.length <= MAX_SLUG_LENGTH;
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);

  if (!url.searchParams.toString()) {
    return emptyNoindex();
  }

  if (!env.COMMENTS_DB) {
    return json({ error: "阅读计数数据库尚未配置" }, 503);
  }

  const slugs = [
    ...new Set(
      url.searchParams
        .getAll("slug")
        .map(cleanSlug)
        .filter(isValidSlug)
    )
  ];

  if (!slugs.length || slugs.length > MAX_BATCH_SIZE) {
    return json({ error: `每次可查询 1-${MAX_BATCH_SIZE} 篇文章` }, 400);
  }

  try {
    const placeholders = slugs.map(() => "?").join(", ");
    const result = await env.COMMENTS_DB.prepare(
      `SELECT post_slug AS postSlug, view_count AS viewCount
       FROM post_views
       WHERE post_slug IN (${placeholders})`
    )
      .bind(...slugs)
      .all();
    const views = Object.fromEntries(slugs.map((slug) => [slug, 0]));

    for (const row of result.results || []) {
      views[row.postSlug] = Number(row.viewCount) || 0;
    }

    return json({ views });
  } catch {
    return json({ error: "暂时无法读取阅读次数" }, 500);
  }
}

export function onRequestHead() {
  return emptyNoindex();
}

export async function onRequestPost({ request, env }) {
  if (!env.COMMENTS_DB) {
    return json({ error: "阅读计数数据库尚未配置" }, 503);
  }

  let body;

  try {
    body = await request.json();
  } catch {
    return json({ error: "提交内容格式不正确" }, 400);
  }

  const postSlug = cleanSlug(body?.postSlug);

  if (!isValidSlug(postSlug)) {
    return json({ error: "文章地址无效" }, 400);
  }

  try {
    await env.COMMENTS_DB.prepare(
      `CREATE TABLE IF NOT EXISTS daily_views (
         view_date TEXT NOT NULL,
         post_slug TEXT NOT NULL,
         view_count INTEGER NOT NULL DEFAULT 0,
         PRIMARY KEY (view_date, post_slug)
       )`
    ).run();
    await env.COMMENTS_DB.batch([
      env.COMMENTS_DB.prepare(
        `INSERT INTO post_views (post_slug, view_count)
         VALUES (?, 1)
         ON CONFLICT(post_slug) DO UPDATE SET
           view_count = view_count + 1,
           updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')`
      ).bind(postSlug),
      env.COMMENTS_DB.prepare(
        `INSERT INTO daily_views (view_date, post_slug, view_count)
         VALUES (date('now'), ?, 1)
         ON CONFLICT(view_date, post_slug) DO UPDATE SET
           view_count = view_count + 1`
      ).bind(postSlug)
    ]);

    const result = await env.COMMENTS_DB.prepare(
      `SELECT view_count AS viewCount
       FROM post_views
       WHERE post_slug = ?`
    )
      .bind(postSlug)
      .first();

    return json({ postSlug, viewCount: Number(result?.viewCount) || 0 });
  } catch {
    return json({ error: "暂时无法更新阅读次数" }, 500);
  }
}
