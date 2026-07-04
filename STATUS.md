# 项目状态

最后更新：2026-07-04 +09:00

## 当前结论

新文章邮件提醒系统 MVP 第一阶段已完成实现、远程 D1 migration、部署后线上订阅/确认/退订测试，并已提交推送。About 页邮件提醒卡片深浅模式透明效果已验收。MVP 第二阶段“手动发送新文章提醒”已完成本地实现、验证、commit/push，并已执行远程 D1 migration 0005 / 0006；线上 dryRun 已通过，确认不会写入 email_post_sends / email_send_logs；第一次真实发送测试已成功，2 个测试邮箱全部发送成功。暂不实现 Cron、自动检测、打开率/点击率统计或分类订阅。

```text
正式开发目录：C:\Users\caoyi\Projects\个人网页项目
当前主分支：main
当前任务状态：邮件提醒 MVP 第二阶段已完成提交与远程 D1 migration，下一步等待 Cloudflare Pages 部署后进行线上 dryRun
构建状态：npm.cmd run build 通过，212 page(s) built，Build Complete
附加检查：npm.cmd run check:admin-save 通过，Errors: 0；npm.cmd run check:knowledge 通过，Posts checked: 176，Errors: 0，Warnings: 0
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
1. POST /api/admin/email/send-post 已新增。
2. API 使用 requireAdmin(request, env) 复用现有 Cloudflare Access 管理员鉴权。
3. 默认 dryRun=true，只预览文章信息和 confirmed 订阅者数量，不写库、不发信。
4. dryRun=false 代码路径已实现，但尚未调用，不会真实发送。
5. 文章信息来源复用 /search-index.json。
6. 只发送给 status='confirmed' 的订阅者。
7. 同一文章默认防重复发送。
8. 发送任务写入 email_post_sends，每个订阅者结果写入 email_send_logs。
9. 邮件正文为中文温和版，包含文章标题、阅读链接和退订链接，不包含完整正文和追踪跳转。
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
