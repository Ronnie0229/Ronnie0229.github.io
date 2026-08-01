# 个人网页项目状态

最后更新：2026-08-01 +09:00

## 当前状态

- 项目：使用 Astro 构建的中文文章网站，部署目标为 Cloudflare Pages。
- 当前分支：`main`。
- 当前任务入口：`docs/tasks/current.md`。
- 当前活动任务：无。

## Search Console canonical alternate 修复（2026-08-01）

- `www` 域名与旧 `/posts/?category=...&focus=...` 的既有 301 逻辑保持不变。
- 已删除的《马太福音 21:19｜为什么耶稣要咒诅无花果树？》详情 URL 及其旧 `focus` URL 改为 HTTP 410，并输出 `X-Robots-Tag: noindex, follow`。
- 新增自定义 `404.astro`；Astro 本地预览已确认未知路径返回 HTTP 404，带 `noindex,follow`且无 canonical。
- robots.txt 已取消 `/posts/?*` 抓取屏蔽，使 Googlebot 可读取旧参数 URL 的 301/410 响应；`/admin/`、`/api/`和 `/search/?*` 仍保持屏蔽。
- 验证：`node scripts/test-search-console-middleware.mjs` 通过；`node --check functions/_middleware.js` 通过；`npm run build -- --force` 通过，327 pages built；Search Console 列出的 34 个 `focus` slug 中 33 个均存在对应生成文章，唯一缺失项为预期返回 410 的已删除无花果树文章；`git diff --check` 通过。
- 实现提交 `15b3dc957f21fb8e7bc692fc0d747fefe6e53e46` 已 push 到 `origin/main` 并由 Cloudflare Pages 自动部署；`/deployment.json` 已确认线上版本与该提交一致。
- 线上验收通过：首页与 RSS 返回 200；`www/about/` 返回 301 到正式域名；普通 `focus` URL 返回 301 到正式文章；已删除文章详情与 `focus` URL 返回 410；未知路径返回 404、`noindex,follow` 且无 canonical；robots.txt 和 sitemap 符合新规则。
- 本轮未直接操作 Google Search Console；后续按任务交接中的步骤重新提交 sitemap 并验证修复。
- 长期规则和 Search Console 操作清单已收敛到 `SEO.md`；部署后 HTTP 验收要求已同步到 `DEPLOY.md`；阶段背景与生产证据保留在 `docs/tasks/search-console-canonical-indexing-phase2.md`。

## Search Console robots.txt 屏蔽修复（2026-08-01）

- 对 Search Console 列出的 27 个 URL 完成分类：23 个 `focus` URL、2 个纯 `category` URL、1 个搜索模板 URL 和 1 个订阅 API URL。
- 23 个 `focus` 中 22 个存在正式文章并按既有规则 301；`2026-06-12-test` 是已于 2026-06-13 删除的测试文章，现登记为 410。
- 两个纯 `category` URL 已在上一轮解除 robots 屏蔽，分别 301 到稳定分类页。
- 移除 robots.txt 中 `/search/?*` 屏蔽，使 Googlebot 可读取页面既有 `noindex,follow`；同时从 `WebSite` JSON-LD 移除已停用的 `SearchAction` / `{search_term_string}`。
- `/api/subscribe` 继续受 `/api/` robots 规则保护，这是预期行为；该接口已输出 `X-Robots-Tag: noindex, nofollow`，不属于可索引网页。
- 本地验证：middleware 测试、语法检查、Knowledge Layer 285 篇 0 错误/0 警告、强制构建 327 pages 和 `git diff --check` 全部通过。
- 当前待提交、push、Cloudflare Pages 部署与线上验收。

## 当前事实源

接手项目时按以下顺序读取：

1. `README.md`
2. `AGENTS.md`
3. `STATUS.md`
4. `docs/tasks/current.md`
5. 与具体任务相关的 workflow、decision 或专项任务文档

`docs/tasks/archive/` 保存历史任务；`.ai-bridge/` 不得保存唯一长期事实。

## 当前发布与接口边界

- 正式内容位于 `src/content/posts/`，网站 raw 与 processed 镜像分别位于 `data/raw/` 和 `data/processed/`。
- 网站拥有 `website-publication-package/v1.1` 的消费和 `website-publication-result/v1.1` 的生成职责。
- v1.1 接口状态为 `contract_stable`，不等于自动发布，也不等于 `production_acceptance_passed`。
- 网站写入、构建、push、Cloudflare 部署和邮件发送必须按任务授权和发布流程执行。
- 已发布讲道正文修正不得改变 slug、articleId、日期、作者、分类、经文等锁定身份字段，除非任务明确授权。

## 最近已验证基线

最近一次完整生产验收为 2026-07-22 的 Psalm 7 分享文章：

- `npm run check:knowledge`：282 篇，0 错误，0 警告；
- Python 发布契约测试：12 tests OK；
- `npm run build -- --force`：323 pages built；
- 网站 `main` 已推送到 `e09641e79d885db971e5f569c3f2eacf43eea5d7`；
- Cloudflare deployment commit 与网站 HEAD 一致；
- 首次邮件 workflow `29927545169` 为 1 篇、3 名收件人、3 次成功、0 次失败；
- 幂等 workflow `29928285307` 为 0 篇、0 收件人，并安全 skip 已发布 slug。

该批次已通过 V2 production acceptance，正式证据位于 `workspace-control/acceptance-runs/20260722-v2-production-acceptance-thessalonica-01/`。

## 当前阻断与待办

- 当前无阻断项。
- 最近一次发布为《我们真能遵行基督的命令吗？》：网站提交 `78f569bce58e9d44efb7a6be47237c6a1f7287f8` 已 push，Cloudflare `/deployment.json` 已部署到该提交，线上正文指纹通过；GitHub Actions run `29986161978` 邮件发送成功，1 篇文章、3 名收件人、3 次成功、0 失败。
- 后续真实修改前仍应先同步 `origin/main`，确认 Admin 或其他入口没有产生远端新内容。

## 历史说明

2026-07-13 以前及其后累积在旧 `STATUS.md` 中的阶段过程、邮件 MVP、访问量修复、source 路径审计和迁移记录，应完整归档为历史状态快照，不再保留在当前 STATUS 中。正式归档后，当前状态只由本文件替换后的 `STATUS.md` 表达。

## RonnieAutomation治理接入边界（2026-07-28）

RonnieAutomation已登记为外部编排参与者，不是网站Owner。网站正式文章、raw/processed/posts、Git、build、Cloudflare和邮件事实仍由本项目拥有。

两个automation-business-operation/v1接口当前仅为`draft`，受控业务代理和网站自动化调用均未实现。未来写入仍必须通过网站正式发布契约、显式授权和本项目Gate；RonnieAutomation不得直接写网站仓库或自我声明发布成功。
