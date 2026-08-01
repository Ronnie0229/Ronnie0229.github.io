# Search Console 第二阶段：canonical alternate 与未收录页面优化

更新时间：2026-08-01

## 2026-08-01 生产闭环补记

本阶段后续收到 Search Console 列出的 36 个“备用网页（有适当的规范标记）”样例：1 个 `www/about/`、34 个 `/posts/?category=...&focus=...` URL 和 1 个已删除文章详情 URL。

最终结论：

- `www/about/` 与 33 个有效 `focus` 目标属于预期重复/旧 URL，不应单独索引；
- 既有 middleware 已将 `www` 域名和有效 `focus` URL 以 301 收敛到正式 URL；
- 《马太福音 21:19｜为什么耶稣要咒诅无花果树？》已于 2026-06-14 永久删除，没有合理替代页；其详情 URL 与旧 `focus` URL 统一返回 410；
- 新增 `src/pages/404.astro`，其他未知路径返回真正 404、`noindex,follow` 且不输出 canonical；
- robots.txt 不再屏蔽 `/posts/?*`，使 Googlebot 能读取 301/410 响应；
- sitemap、RSS 和站内链接仍只使用正式 URL。

生产证据：

- 实现提交：`15b3dc957f21fb8e7bc692fc0d747fefe6e53e46`；
- Cloudflare Pages `builtAt=2026-08-01T13:30:57.574Z`；
- 线上首页和 RSS 返回 200；
- `www/about/` 和普通 `focus` 样例返回 301；
- 已删除文章详情与 `focus` 样例返回 410；
- 随机未知路径返回 404，HTML 带 `noindex,follow` 且无 canonical；
- 强制构建通过，327 pages built。

后续 Search Console 操作以项目根 `SEO.md` 的“部署后的 Search Console 固定操作”为唯一长期流程。本文保留本阶段的问题背景和生产证据，不重复维护操作步骤。

## 本阶段解决的问题

第一阶段已经处理搜索模板软 404、API 空请求 4xx、Cloudflare `/cdn-cgi/l/email-protection` 误报。本阶段继续减少站内主动生成的 query URL，尤其是文章分类列表：

- 旧分类入口：`/posts/?category=教会讲道`
- 旧分类入口：`/posts/?category=灵命成长`
- 旧返回定位：`/posts/?category=...&focus=...#post-...`

这些 URL 能正常显示内容，但它们本质上是同一个 `/posts/` 列表页的筛选状态，容易在 Search Console 里形成 canonical alternate 或被 robots 屏蔽的重复 URL。

## 新 URL 规则

- 教会讲道：`/posts/category/sermons/`
- 灵命成长：`/posts/category/spiritual-growth/`
- 全部文章：`/posts/`
- 搜索页：`/search/` 保持可访问，但因为它是站内工具页，输出 `noindex,follow`，不放入 sitemap。

## sitemap 规则

sitemap 只放真正希望被索引的 canonical 页面：

- 首页、全部文章、关于、圣经书卷页。
- 文章详情页。
- 圣经卷页。
- 稳定分类页：`/posts/category/sermons/`、`/posts/category/spiritual-growth/`。

sitemap 不放：

- `/search/`
- `/search/?q=...`
- `/posts/?category=...`
- `/posts/?page=...`
- `/posts/?focus=...`
- `/api/`
- `/admin/`
- `/cdn-cgi/`


## 本阶段范围说明

本阶段只处理 `/posts/` 文章分类相关的 query URL，也就是 `/posts/?category=...`、`/posts/?page=...`、`/posts/?focus=...` 这一类由文章列表产生的地址。

Bible 书卷页目前仍保留前端分页和返回定位状态逻辑，可能还会出现 `?page=` 或 `?focus=`。这部分先不在第二阶段改动，后续第三阶段再统一处理，避免一次性扩大范围影响书卷页阅读体验。
## Search Console 后续操作

- 长期操作步骤已统一转移到项目根 `SEO.md`，本文不再单独维护重复清单。
- 对旧 query、`www`、`http`、搜索结果页、Cloudflare 功能路径和已删除 URL，不应为追求“未索引计数归零”而新建重复页或请求编入索引。
