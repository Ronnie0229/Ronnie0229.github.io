# 项目状态

最后更新：2026-06-30 +09:00

## 当前结论

“批量修复 source 路径”任务已完成审计、范围调整、流程固化和交接记录。本轮没有批量修改任何文章的 `source` 字段，也没有修改文章正文。

```text
正式开发目录：C:\Users\caoyi\Projects\个人网页项目
当前主分支：main
最新远端提交：677ae82 Document source path audit workflow
当前任务状态：source 路径审计收尾完成
构建状态：本轮未运行 npm.cmd run build；最终收尾仅涉及文档和审计报告
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

## 本轮新增或更新的主要文件

```text
scripts/audit_live_vs_local.mjs
scripts/audit_source_repair_plan.mjs
scripts/create_source_raw_recovery_checklist.mjs
docs/内容整理报告/live-vs-local-posts.csv
docs/内容整理报告/source-path-check.csv
docs/内容整理报告/source-path-repair-plan.csv
docs/内容整理报告/source-path-phase-2-strategy.md
docs/内容整理报告/source-path-phase-3-raw-recovery.md
docs/内容整理报告/source-raw-recovery-checklist.csv
docs/内容整理报告/source-path-phase-4-in-scope-closure.md
CONTENT_WORKFLOW.md
docs/tasks/current.md
```

## 重要环境限制

当前 CodexPro 不能穿透 `C:\Users\caoyi\Projects\NAS` 下指向 `\\RonnieNAS\...` 的符号链接。

因此，本轮已明确移除以下范围：

```text
从 \\RonnieNAS\tmp\分享 恢复分享 raw 文件
从 \\RonnieNAS\tmp\讲道 恢复讲道 raw 文件
从 \\RonnieNAS\share\教会讲道 查找历史归档
批量复制 NAS 文件进入 data/raw
```

后续如需处理 NAS，应另开独立任务，并先由用户手动复制目标文件到仓库内，或等待 CodexPro 环境支持 NAS allowed roots。

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

## 验证结果

本轮已运行：

```text
node scripts/audit_live_vs_local.mjs
python scripts/check_source_paths.py
node scripts/audit_source_repair_plan.mjs
```

`python scripts/check_source_paths.py` 仍会返回 missing，这是预期结果，因为历史 raw 文件尚未恢复。

本轮未运行：

```text
npm.cmd run build
```

原因：最终收尾只涉及文档、审计脚本和 CSV 报告，没有修改 Astro 页面、组件、内容正文或配置。

## 接手提醒

1. 新任务开始前仍按 `docs/task-handoff-protocol.md` 读取一级必读文件。
2. 遇到 source missing 时，以 `CONTENT_WORKFLOW.md` 的新规则为准。
3. 不要把历史 missing source 批量改成不可验证路径。
4. 如果用户提供 raw 文件，先放入对应 `data/raw/...` 路径，再重新运行 `python scripts/check_source_paths.py`。
