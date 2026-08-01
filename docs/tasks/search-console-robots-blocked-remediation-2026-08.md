# Search Console robots.txt 屏蔽收敛

更新日期：2026-08-01

## 问题范围

Search Console 报告“已被 robots.txt 屏蔽”共 27 个 URL：

- 23 个 `/posts/?category=...&focus=...`；
- 2 个 `/posts/?category=...`；
- 1 个 `/search/?q={search_term_string}`；
- 1 个 `/api/subscribe`。

## 判定

1. 22 个 `focus` slug 存在正式文章，应允许 Googlebot 读取 301 并收敛到 `/posts/<slug>/`。
2. `2026-06-12-test` 是 2026-06-12 创建、2026-06-13 永久删除的测试文章，无正式替代内容，应返回 410。
3. 两个纯 category URL 应允许抓取并 301 到 `/posts/category/sermons/` 或 `/posts/category/spiritual-growth/`。
4. 搜索结果页不应索引，但必须允许抓取，才能让 Googlebot 读取 `noindex,follow`。
5. `{search_term_string}` 来自已停用的 sitelinks 搜索框 `SearchAction` 结构化数据，对当前 Google 搜索已无保留必要。
6. `/api/subscribe` 是 POST API，不是网页；继续由 `/api/` robots 规则屏蔽，并保留 `X-Robots-Tag: noindex, nofollow`。

## 实现

- robots.txt 移除 `/search/?*` 规则，仅保留 `/admin/` 和 `/api/`。
- `PERMANENTLY_REMOVED_POST_SLUGS` 新增 `2026-06-12-test`。
- `WebSite` JSON-LD 移除 `SearchAction`、`EntryPoint`、`urlTemplate` 和 `search_term_string`，保留站点名称、描述和发布者。
- middleware 测试增加已删除测试 slug 的 410 与 robots 可抓取断言。
- Knowledge Layer 检查增加“不得再输出已停用 SearchAction”回归门禁。
- SEO URL audit 增加搜索模板、已删除测试 URL 和订阅 API 样例。

## 验收

- `node scripts/test-search-console-middleware.mjs`：通过。
- `node --check functions/_middleware.js`：通过。
- `npm run check:knowledge`：285 篇，0 errors，0 warnings。
- `npm run build -- --force`：327 pages built。
- 生成 HTML 不含 `SearchAction` 或 `search_term_string`。
- 生成 robots.txt 只屏蔽 `/admin/` 和 `/api/`。
- 23 个 `focus` slug 中 22 个生成正式文章，唯一缺失的 `2026-06-12-test` 为预期 410。

## Search Console 后续

部署后在“编入索引 → 网页 → 已被 robots.txt 屏蔽”中启动验证。对正式文章可抽查 1–3 个目标 URL 请求编入索引；不对参数 URL、搜索结果、已删除测试 URL 或 `/api/subscribe` 请求编入索引。

Google 官方依据：

- `noindex` 只有在抓取器可访问页面时才能被读取：<https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag>
- sitelinks 搜索框自 2024-11-21 起停止展示：<https://developers.google.com/search/blog/2024/10/sitelinks-search-box>
