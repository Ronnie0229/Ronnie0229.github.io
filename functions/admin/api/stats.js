import { requireAdmin } from "../../_lib/admin-auth.js";

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: { "Cache-Control": "no-store" }
  });
}

export async function onRequestGet({ request, env }) {
  const admin = await requireAdmin(request, env);
  if (!admin.ok) return admin.response;
  if (!env.COMMENTS_DB) return json({ error: "统计数据库尚未配置" }, 503);

  try {
    await env.COMMENTS_DB.prepare(
      `CREATE TABLE IF NOT EXISTS daily_views (
         view_date TEXT NOT NULL,
         post_slug TEXT NOT NULL,
         view_count INTEGER NOT NULL DEFAULT 0,
         PRIMARY KEY (view_date, post_slug)
       )`
    ).run();
    const [popular, trend, totals] = await env.COMMENTS_DB.batch([
      env.COMMENTS_DB.prepare(
        `SELECT post_slug AS postSlug, view_count AS viewCount
         FROM post_views ORDER BY view_count DESC LIMIT 10`
      ),
      env.COMMENTS_DB.prepare(
        `SELECT view_date AS viewDate, SUM(view_count) AS viewCount
         FROM daily_views
         WHERE view_date >= date('now', '-29 days')
         GROUP BY view_date ORDER BY view_date ASC`
      ),
      env.COMMENTS_DB.prepare(
        `SELECT
           (SELECT COALESCE(SUM(view_count), 0) FROM post_views) AS totalViews,
           (SELECT COUNT(*) FROM comments WHERE status = 'visible') AS visibleComments,
           (SELECT COUNT(*) FROM comments WHERE status = 'hidden') AS hiddenComments`
      )
    ]);

    return json({
      popular: popular.results || [],
      trend: trend.results || [],
      totals: totals.results?.[0] || {}
    });
  } catch {
    return json({ error: "暂时无法读取统计数据" }, 500);
  }
}
