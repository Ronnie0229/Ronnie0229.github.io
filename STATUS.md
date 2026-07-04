# 项目状态

最后更新：2026-07-04 +09:00

## 当前结论

新文章邮件提醒系统 MVP 第一阶段已完成本地实现与验证，尚未提交、推送或部署。当前功能范围仅包含订阅、确认、退订，不包含新文章提醒发送、后台手动发送、Cron、newsletter 模板、打开率/点击率统计或分类订阅。

```text
正式开发目录：C:\Users\caoyi\Projects\个人网页项目
当前主分支：main
当前任务状态：邮件提醒 MVP 第一阶段本地实现完成，Codex 已复核 diff 并重新跑完验证，等待提交/push；远程 D1 migration 尚未执行
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

上线前必须先执行远程 D1 migration：

```powershell
npx wrangler d1 execute ronniecross-comments --remote --file scripts/migrations/0004_create_email_subscribers.sql
```

部署说明：

```text
1. Cloudflare Pages 需要重新部署后，新 Functions API 与新静态页面才会生效。
2. 未执行远程 D1 migration 前，不要直接测试线上 /api/subscribe。
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
6. 远程 D1 migration 尚未执行，需用户明确确认后再运行。
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
