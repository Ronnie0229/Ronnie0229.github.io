# Search Console 4xx 与软 404 整改

更新时间：2026-07-04

## 处理规则

- `https://ronniecross.com/search/?q={search_term_string}` 是 SearchAction 的模板 URL，不是 sitemap URL。搜索参数页 canonical 到 `/search/`，并输出 `noindex,follow`。
- `/api/comments`、`/api/views`、`/api/visits` 是接口，不是内容页。直接空 GET/HEAD 访问返回 204，并带 `X-Robots-Tag: noindex, nofollow` 与 `Cache-Control: no-store`。
- `/cdn-cgi/l/email-protection` 是 Cloudflare Email Address Obfuscation 路径，不在项目中创建页面，也不写入 sitemap。
- sitemap 只放 canonical 内容页，不放 query URL、API、admin、`/cdn-cgi/`。

## 审计

- 脚本：`scripts/audit_seo_urls.mjs`
- 默认审计：`https://ronniecross.com`
- 输出：`docs/seo-url-audit.csv`
- 本地预览审计可设置 `SEO_AUDIT_BASE_URL`。
