# 项目状态

最后更新：2026-07-07 +09:00

## 当前结论

Mac 移行后的本地项目可正常执行 CodexPro 维护任务。本轮已修复 About 页“本站累计访问量：暂时无法读取”问题：原因是前端在当前 session 已计数后请求无参数 `/api/visits` 读取计数，但后端为 SEO 将无参数 GET 设计为 204，导致前端 JSON 解析失败；现改为前端使用 `/api/visits?read=1` 显式读取，后端只对 `read=1` 或 `increment=1` 返回 JSON，仍保留无参数 GET/HEAD 的 noindex 204 行为。已通过本地验证，修复提交 `9ac0b8a` 与交接提交 `4f6f4a5` 已 push 到 `origin/main`。Cloudflare Pages 已成功部署 `4f6f4a5` 对应构建产物，线上 About HTML 已包含 `?read=1`，read、increment、无参数 GET 与 HEAD 路径均验证通过。邮件提醒 MVP 第二阶段此前已完成并验收；暂不实现 Cron、自动检测、打开率/点击率统计或分类订阅。

```text
正式开发目录：C:\Users\caoyi\Projects\个人网页项目
当前主分支：main
当前任务状态：About 页累计访问量读取 bug 已修复、验证、commit、push、部署并完成线上验证
构建状态：npm run build 通过，217 page(s) built，Build Complete
附加检查：node --check functions/api/visits.js 通过；npm run check:admin-save 通过，Errors: 0；npm run check:knowledge 通过，Posts checked: 181，Errors: 0，Warnings: 0；git diff --check 通过
```

## 继承文档入口

未来 Codex / CodexPro / 本地模型接手时，先读 `AGENTS.md` 和本文件；网站维护读 `docs/workflows/website-maintenance-workflow.md`，设计与架构决策读 `docs/decisions/website-decisions.md`，样式结构重构读 `docs/tasks/style-structure-refactor-plan.md`。

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
1. POST /api/admin/email/send-post 已新增。
2. API 使用 requireAdmin(request, env) 复用现有 Cloudflare Access 管理员鉴权。
3. 默认 dryRun=true，只预览文章信息和 confirmed 订阅者数量，不写库、不发信。
4. dryRun=false 代码路径已实现，但尚未调用，不会真实发送。
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

仍未执行：

```text
1. 远程 D1 migration 0005 / 0006 已执行成功。
2. 线上 dryRun 已通过：ok=true，dryRun=true，文章信息正确，recipientCount=2。
3. dryRun 后确认 email_post_sends=0，email_send_logs=0，未写发送记录。
4. 第一次真实发送测试已成功：recipient_count=2，success_count=2，failed_count=0。
4. 第二阶段实现已 commit / push：17c28cb feat: add manual email post notification flow。
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
ok: 10
no_source: 1
missing_share_docx: 114
missing_share_raw: 6
missing_sermon_raw_directory: 192
```

去重后的 raw 找回目标：

```text
Recovery targets: 158
missing_share_raw: 3
no_source: 1
missing_share_docx: 58
missing_sermon_raw_directory: 96
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
