# Search Console 第二阶段：canonical alternate 与未收录页面优化

更新时间：2026-07-04

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

- 对旧 query 分类 URL，不需要新建页面；它们应逐步被新导航入口替代。
- 对 `/search/`，如果 Search Console 显示未收录，这是预期结果，因为页面带 `noindex,follow` 且不在 sitemap。
- 对 `/cdn-cgi/l/email-protection`，仍按 Cloudflare 功能路径处理，不在项目里创建页面。
- 后续提交部署后，可在 Search Console 里重新验证受影响 URL，并观察 canonical alternate 与未收录页面数量是否下降。
