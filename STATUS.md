# 项目状态

最后更新：2026-07-07 +09:00

## 当前结论

Mac 移行后的本地项目可正常执行 CodexPro 维护任务。本轮新增 Google Search Console 域名规范化修复：`assets/_redirects` 明确将 `http://www.ronniecross.com/*`、`https://www.ronniecross.com/*`、`http://ronniecross.com/*` 统一 301 到 `https://ronniecross.com/:splat`，继续只保留不带 www 的正式网址。网站 sitemap、canonical 与 robots 仍指向 `https://ronniecross.com`。此前 Google 搜索结果网站图标修复已完成并提交：只使用专用深色背景 favicon，不牵连 apple-touch-icon 与 manifest icon。About 页访问量修复已验证、push、部署并完成复盘文档沉淀。邮件提醒 MVP 第二阶段此前已完成并验收；第三阶段已完成本地实现：Admin 发布成功后自动发送提醒，短时间连续发布多篇时合并为一封邮件，并新增只读订阅邮箱一览。当前仍不实现 Cron、打开率/点击率统计或分类订阅。

2026-07-12 追加排查：已定位《以利亚与撒勒法寡妇：信靠神的供应》邮件提醒可能漏发的原因为 GitHub Actions 等待部署时要求 `deployment.commit` 必须严格等于文章 push commit；若后续文档 commit 已包含该文章并先部署，旧逻辑会错过发送窗口。本轮已修复为“部署 commit 等于目标 commit 或包含目标 commit 均可”，并新增 `workflow_dispatch` 受控补发入口。补发范围仅限该文章 slug，不发布新文章，不在本地泄露密钥。

2026-07-12 追加修复：第一次受控补发 run 29160598088 失败，GitHub 日志中 secret 已遮蔽，返回形态显示 `/api/admin/email/auto-send` 可能被 Cloudflare Access 后台保护拦截。已新增机器触发专用路径 `/api/email/auto-send`，复用同一发送实现和 `EMAIL_AUTOMATION_SECRET` 校验；GitHub Actions 改为默认调用该路径。

2026-07-12 补发进展：第二次受控补发 run 29160786217 已对目标文章实际发送，结果为 postCount=1、recipientCount=3、successCount=2、failedCount=1。为避免重复邮件，已追加 `partial_failed` 重试逻辑：再次触发同一 slug 时仅重试上一批失败且当前仍 confirmed 的订阅者。

2026-07-12 重试修复：第三次受控补发 run 29161015280 在 failed 收件人重试分支返回 500，判断为 D1/SQLite 对 `SELECT DISTINCT s.* ... ORDER BY s.id` 的兼容问题；已改为显式列选择。

2026-07-12 重试修复续：第四次受控补发 run 29161369421 返回明确 JSON 错误 `UNIQUE constraint failed: email_post_sends.post_slug`。已确认 `email_post_sends.post_slug` 唯一，partial_failed 重试不能插入新发送任务；已改为复用原发送记录，只追加失败收件人的发送日志。

## 邮件提醒 MVP 第三阶段状态

```text
1. 新增 functions/api/admin/email/auto-send.js：接收一组已发布文章 slug，跳过已发送文章，只向 confirmed 订阅者逐个发送一封合并邮件。
2. 新增 assets/admin/auto-email.js：捕获 Admin 正式文章发布，等待 Cloudflare 部署 commit 确认成功，再以 12 秒窗口合并连续发布文章并自动调用发送 API。
3. 草稿不会加入自动邮件队列；发送失败时队列保留在 localStorage，下次打开文章管理页会重试。
4. 多篇文章邮件只列出多个中性 URL，不暴露标题、经文、摘要或真实 slug。
5. 新增 /admin/subscribers.html 与受保护 API，只读显示订阅邮箱、状态、订阅/确认/退订时间和最近发送时间。
6. 无需新增 D1 migration，继续复用 email_subscribers、email_post_sends、email_send_logs、email_post_links。
7. 第三阶段任务文档：docs/tasks/email-notification-mvp-phase3.md。
8. 本地语法检查通过；npm run build 通过，310 page(s) built。
9. 本轮不发布测试文章、不主动发送真实邮件；只提交、push 并确认 Cloudflare Pages 部署。
10. 已补充 GitHub Actions 统一自动触发：Codex、本地 Git、GitHub 网页或 Admin 只要把正式文章 push 到 main，工作流都会等待对应 Cloudflare 部署完成后自动发送。
11. 统一触发依赖 EMAIL_AUTOMATION_SECRET；必须把同一个随机值同时配置到 Cloudflare Pages 环境变量和 GitHub Actions repository secret。
12. 2026-07-12 收尾验证：git fetch origin main 后确认本地 main 与 origin/main 同步；node --check 覆盖 auto-send、subscribers API、Admin 自动邮件脚本、订阅页脚本和 GitHub Actions 通知脚本；npm run build 通过，310 page(s) built，Build Complete。
13. 本轮提交并 push：8dda26b feat: add automatic email notification flow；9a00fb5 docs: record email automation commit。
14. Cloudflare Pages 部署已确认：/deployment.json 返回 commit=9a00fb50352f9f63ff4f7fe3d3a93ee1ce653539，builtAt=2026-07-11T16:16:33.316Z。
15. 线上后台资源确认：/admin/subscribers.html、/admin/auto-email.js?v=1、/admin/subscribers.js?v=1 均被 Cloudflare Access 保护并返回 302 登录跳转；本轮未发布测试文章，未主动调用邮件发送 API。
```

```text
正式开发目录：C:\Users\caoyi\Projects\个人网页项目
当前主分支：main
当前任务状态：已新增 canonical 域名 redirects，本地构建通过；待提交、push、Cloudflare Pages 部署后在 Google Search Console 重新检查
构建状态：npm run build 通过，221 page(s) built，Build Complete
附加检查：sitemap、canonical、robots 均保持 https://ronniecross.com；新增 dist/_redirects 构建产物包含三条 canonical 301 规则
```

## 继承文档入口

未来 Codex / CodexPro / 本地模型接手时，先读 `AGENTS.md` 和本文件；网站维护读 `docs/workflows/website-maintenance-workflow.md`，设计与架构决策读 `docs/decisions/website-decisions.md`，样式结构重构读 `docs/tasks/style-structure-refactor-plan.md`。

## 本轮访问量修复复盘

新增长期复盘文档：

```text
docs/tasks/visit-counter-read-path-postmortem.md
```

已同步部署规则：

```text
DEPLOY.md：新增 API 空访问与前端读取路径规则，部署前后检查追加 sessionStorage/localStorage 与 API 成功/空访问/noindex 路径验证。
```

核心长期规则：

```text
1. 前端读取 JSON 不得复用无参数 GET，因为 API 空访问可能被 SEO 规则定义为 204 noindex。
2. 有读取和写入/自增两种语义的接口必须显式区分参数或路径。
3. 修改 Cloudflare Functions 后，部署后必须同时检查 API 行为与静态页面 HTML/JS 是否为最新构建。
4. 涉及 sessionStorage/localStorage 的前端逻辑，必须验证首次访问和已有本地标记两种状态。
```

## 邮件提醒 MVP 第一阶段状态

本轮新增：

```text
docs/tasks/email-notification-mvp-phase1.md
scripts/migrations/0004_create_email_subscribers.sql
functions/_utils/email.js
functions/api/subscribe.js
functions/api/confirm.js
functions/api/unsubscribe.js
src/components/SubscribeForm.astro
src/pages/subscribe/confirmed.astro
src/pages/subscribe/unsubscribed.astro
```

本轮修改：

```text
src/pages/about.astro
src/styles/global.css
docs/tasks/current.md
STATUS.md
```

远程 D1 migration 已执行：

```powershell
npx wrangler d1 execute ronniecross-comments --remote --file scripts/migrations/0004_create_email_subscribers.sql
```

执行结果：

```text
success: true
Total queries executed: 5
Rows read: 9
Rows written: 9
Database size (MB): 0.21
finalBookmark: 00000482-00000006-0000509e-184051cab069e7c1721ed1228cbf08cb
```

部署说明：

```text
1. Cloudflare Pages 需要重新部署后，新 Functions API 与新静态页面才会生效。
2. 远程 D1 migration 已完成；等待 Cloudflare Pages 部署完成后，可以测试线上 /api/subscribe。
3. 本轮未修改 COMMENTS_DB binding 名称，也未新增 D1 binding。
4. 本轮未触碰 RSS、文章 Markdown、导入脚本、现有评论功能、GitHub 登录/Admin 功能、SEO/sitemap 逻辑。
```

Codex 收尾复核：

```text
1. 已复核 git status 与任务范围，改动文件均属于邮件提醒 MVP 第一阶段。
2. 已搜索第二阶段关键词；相关内容只出现在任务说明/禁止清单中，没有新增第二阶段实现。
3. 已重新运行 npm.cmd run build，结果通过：212 page(s) built，Build Complete。
4. 已重新运行 npm.cmd run check:admin-save，结果通过：Errors: 0。
5. 已重新运行 npm.cmd run check:knowledge，结果通过：Posts checked: 176，Errors: 0，Warnings: 0。
6. 远程 D1 migration 已在用户确认后执行成功。
7. 已提交并 push：8a352b7 feat: add email subscription confirmation flow。
```


## 邮件提醒 MVP 第二阶段状态

本轮新增/修改：

```text
scripts/migrations/0005_create_email_post_sends.sql
scripts/migrations/0006_create_email_send_logs.sql
functions/api/admin/email/send-post.js
functions/_utils/email.js
STATUS.md
docs/tasks/current.md
```

当前实现：

```text
1. POST /api/admin/email/send-post 已完成并通过线上 dryRun 与真实发送测试。
2. API 使用 requireAdmin(request, env) 复用现有 Cloudflare Access 管理员鉴权。
3. dryRun=true 可预览 confirmed 订阅者数量，不写库、不发信。
4. dryRun=false 已完成真实发送验收，测试结果 success_count=2、failed_count=0。
5. 文章信息来源复用 /search-index.json。
6. 只发送给 status='confirmed' 的订阅者。
7. 同一文章默认防重复发送。
8. 发送任务写入 email_post_sends，每个订阅者结果写入 email_send_logs。
9. 中性链接补丁已将文章提醒邮件改为固定标题与中性正文，不包含文章标题、经文、摘要或真实 slug；阅读链接改为 /go/post/<neutral_id>。
```

本地验证：

```text
node --check functions/_utils/email.js：通过
node --check functions/api/admin/email/send-post.js：通过
git diff --check：通过
npm.cmd run build：通过，212 page(s) built，Build Complete
npm.cmd run check:admin-save：通过，Errors: 0
npm.cmd run check:knowledge：通过，Posts checked: 176，Errors: 0，Warnings: 0
```

第二阶段远程 D1 migration 执行结果：

```text
0005_create_email_post_sends.sql：成功，Total queries executed: 3，Rows read: 5，Rows written: 5，Database size: 0.23 MB，bookmark: 00000488-0000000e-0000509e-003dab5a0755fdb1ba7a31a98fc90af8。
0006_create_email_send_logs.sql：成功，Total queries executed: 4，Rows read: 7，Rows written: 5，Database size: 0.25 MB，bookmark: 00000488-00000014-0000509e-3316600230764936f85e26d508ea8992。
0007_create_email_post_links.sql：成功，Total queries executed: 3，Rows read: 5，Rows written: 6，Database size: 0.27 MB，finalBookmark: 0000048e-00000006-0000509f-af9224370fde22433a5260cb1c54309a。
```

线上 dryRun 验证结果：

```text
POST /api/admin/email/send-post dryRun=true：成功，status=200，ok=true，dryRun=true。
测试文章：2026-07-04-马可福音-6-30-52好牧人的供应。
返回标题：马可福音 6:30-52 | 好牧人的供应。
返回 URL：https://ronniecross.com/posts/2026-07-04-马可福音-6-30-52好牧人的供应/。
recipientCount=2。
D1 验证：email_post_sends count=0，email_send_logs count=0。
```

第一次真实发送测试结果：

```text
POST /api/admin/email/send-post dryRun=false：成功，status=200，ok=true。
测试文章：2026-07-04-马可福音-6-30-52好牧人的供应。
API 返回：recipientCount=2，successCount=2，failedCount=0。
email_post_sends：status=sent，recipient_count=2，success_count=2，failed_count=0，sent_at=2026-07-04T15:35:29.938Z，error_message=null。
email_send_logs：2 条记录，status=sent，error_message=null，resend_id 均有值。
测试邮箱：soueitetsu@gmail.com，6611987@qq.com。
```

第二阶段最终状态：

```text
1. 远程 D1 migration 0005 / 0006 / 0007 均已执行成功。
2. 线上 dryRun 已通过：ok=true，文章信息正确，recipientCount=2，且未写发送记录。
3. 第一次真实发送测试已成功：recipient_count=2，success_count=2，failed_count=0。
4. 中性链接版真实发送也已通过，邮件内容与跳转均已验收。
5. 第二阶段实现已 commit / push：17c28cb feat: add manual email post notification flow。
```



中性链接 dryRun 验证结果：

```text
POST /api/admin/email/send-post dryRun=true：成功，status=200，ok=true，dryRun=true。
测试文章：2026-07-05-罗马书-16-17-27被福音坚固。
返回 neutralUrl：https://ronniecross.com/go/post/0bb64e58f60340b7810a28eeb4d3eccb。
recipientCount=2。
neutralUrl 跳转成功，最终跳转到真实文章页。
email_post_links：已生成映射，neutral_id=0bb64e58f60340b7810a28eeb4d3eccb，post_slug=2026-07-05-罗马书-16-17-27被福音坚固，created_at=2026-07-05T11:58:28.632Z。
email_post_sends：未出现 2026-07-05 文章记录；仅保留此前 2026-07-04 测试文章 sent 记录。
email_send_logs：未新增本次 dryRun 发送日志；仅保留此前 2026-07-04 两条测试发送日志。
```



中性链接版真实发送结果：

```text
POST /api/admin/email/send-post dryRun=false：成功，status=200，ok=true，dryRun=false。
测试文章：2026-07-05-罗马书-16-17-27被福音坚固。
返回 neutralUrl：https://ronniecross.com/go/post/0bb64e58f60340b7810a28eeb4d3eccb。
API 返回：recipientCount=2，successCount=2，failedCount=0。
email_post_sends：status=sent，recipient_count=2，success_count=2，failed_count=0，sent_at=2026-07-05T12:25:23.249Z，error_message=null。
email_send_logs：2 条新记录，status=sent，error_message=null，resend_id 均有值。
测试邮箱：soueitetsu@gmail.com，6611987@qq.com。
邮件内容已确认：标题为 RonnieCross 新文章提醒；正文不包含文章标题、经文、摘要、真实 slug；包含中性阅读链接与退订链接；无乱码。
阅读链接跳转成功，最终页面：https://ronniecross.com/posts/2026-07-05-罗马书-16-17-27被福音坚固/。
```

## 本轮 source 路径审计结论

Phase 0 已确认线上 `ronniecross.com` 与本地 `src/content/posts` 的文章数量一致，没有发现线上有而本地没有的文章，也没有发现正文内容需要从线上反向同步。

Phase 1/2/3/4/5 已确认：当前 `source` missing 的主因不是 Markdown 中的路径拼写错误，而是历史 raw 文件或 raw 目录没有进入当前仓库的 `data/raw/`。

最终决策：

```text
不执行批量 source 路径替换。
不把 source 改成 processed 文件路径。
不把 source 改成正式 posts 文件路径。
不伪造不存在的 raw 文件。
保留现有 source 历史记录，等待真实 raw 文件恢复。
```

## 关键统计

```text
Checked: 323
No source: 1
Missing: 312
OK: 10
```

分类结果：

```text
2024 年旧讲道 archive：49 个
2026-06-14 新增讲道批次：145 个
2026-06-29/30 新增讲道/分享批次：24 个
2026-07-01 新增讲道批次：16 个
2026-07-02 新增讲道批次：35 个
2026-07-03 新增讲道批次：8 个
2026-07-04 新增讲道批次：4 个
2026-07-05 新增讲道批次：1 个
manual-added 旧资料导入：30 个
已存在 raw：10 个
无 source：1 个
```

已生成审计清单：

```text
docs/source-raw-recovery-checklist.md
```

## 路径审计任务修改文件

```text
docs/source-raw-recovery-checklist.md
docs/tasks/current.md
STATUS.md
scripts/audit_source_repair_plan.mjs
scripts/check_source_paths.py
scripts/create_source_raw_recovery_checklist.mjs
```

## 路径审计验证

```text
npm run build：通过，215 page(s) built，Build Complete
python scripts/check_source_paths.py：Checked: 323，No source: 1，Missing: 312，OK: 10
node scripts/audit_source_repair_plan.mjs：生成四阶段审计与 candidates
node scripts/create_source_raw_recovery_checklist.mjs：生成恢复清单
```

## 后续建议

```text
1. 优先从旧仓库、NAS 归档或 Windows 电脑恢复真实 raw 文件。
2. 恢复 raw 文件后再运行 python scripts/check_source_paths.py。
3. 如果找不到 raw，宁可保留 missing 状态，也不要伪造 source。
```

## 重要环境限制

当前 CodexPro 不能穿透 `C:\Users\caoyi\Projects\NAS` 下指向 `\\RonnieNAS\...` 的符号链接。

因此，source 恢复任务中应避免直接依赖 CodexPro 访问 NAS。后续如需处理 NAS，应另开独立任务，并先由用户手动复制目标文件到仓库内，或等待 CodexPro 环境支持 NAS allowed roots。

## 后续独立任务

### 任务 A：近期 3 篇分享 raw 找回

```text
data/raw/分享/圣经所说的“魔鬼的诡计”是什么意思？.txt
data/raw/分享/神的话语如何在信徒里面运行？.txt
data/raw/分享/耶稣叫我们“背起自己的十字架”到底是什么意思？.md
```

### 任务 B：no_source 文章来源追溯

```text
src/content/posts/2026-06-27-以弗所书-28-9耶稣为什么行神迹.md
```

当前已知：

```yaml
title: "以弗所书 2:8-9｜耶稣为什么行神迹？"
scripture: "以弗所书 2:8-9"
source: ""
```

文件名中的 `以弗所书-28-9` 与 frontmatter 的 `以弗所书 2:8-9` 不一致，疑似 slug 生成时丢失冒号。本轮不改名，避免改变既有 URL。

### 任务 C：历史 raw 归档恢复

```text
data/raw/分享/*.docx
data/raw/教会讲道/<历史讲道目录>/
```

## 接手提醒

1. 新任务开始前仍按 `docs/task-handoff-protocol.md` 读取一级必读文件。
2. 遇到 source missing 时，以 `CONTENT_WORKFLOW.md` 的新规则为准。
3. 不要把历史 missing source 批量改成不可验证路径。
4. 如果用户提供 raw 文件，先放入对应 `data/raw/...` 路径，再重新运行 `python scripts/check_source_paths.py`。
5. 邮件提醒第二阶段另开任务处理，不要把发送新文章提醒、后台手动发送或统计追踪混入第一阶段收尾。

## 邮件提醒 MVP 第二阶段本地收尾

新文章邮件提醒系统 MVP 第二阶段已完成本地代码初稿：新增手动发送文章提醒 API、发送任务/发送日志 migration 文件，并扩展邮件工具。当前只完成本地实现与验证，尚未执行远程 D1 migration，尚未真实发送邮件。

```text
第二阶段新增文件：
scripts/migrations/0005_create_email_post_sends.sql
scripts/migrations/0006_create_email_send_logs.sql
functions/api/admin/email/send-post.js

第二阶段修改文件：
functions/_utils/email.js
STATUS.md
docs/tasks/current.md
.ai-bridge/agent-status.md

第二阶段验证：
node --check functions/_utils/email.js 通过
node --check functions/api/admin/email/send-post.js 通过
npm.cmd run build 待记录
npm.cmd run check:admin-save 待记录
npm.cmd run check:knowledge 待记录

第二阶段边界：
未执行远程 D1 migration
未真实发送邮件
未新增 Cron
未新增 /go/post/<neutral_id>
未新增打开率/点击率统计
未新增分类订阅
未新增后台 UI
```

### 第二阶段验证结果（本地）

```text
node --check functions/_utils/email.js：通过
node --check functions/api/admin/email/send-post.js：通过
git diff --check：通过
npm.cmd run build：通过，212 page(s) built，Build Complete
npm.cmd run check:admin-save：通过，Errors: 0
npm.cmd run check:knowledge：通过，Posts checked: 176，Errors: 0，Warnings: 0
```

本轮未执行远程 D1 migration，未真实发送邮件。

## 继承文档整理补充（2026-07-06）

资料来源：`C:\Users\caoyi\Desktop\codex++` 导出的 Codex Markdown 会话备份。本次只整理长期继承文档，没有修改业务代码、样式代码、脚本代码或文章内容。

新增继承文档：

```text
docs/workflows/website-maintenance-workflow.md
docs/decisions/website-decisions.md
docs/tasks/style-structure-refactor-plan.md
```

后续 Codex / CodexPro / Mac mini 接手网站维护、样式重构、内容发布或 Windows→Mac 迁移时，应把这些文档与 `AGENTS.md`、`docs/tasks/current.md` 一起阅读。
