# 当前任务：source 路径修复审计与 raw 找回

## 任务状态

正在处理“批量修复 source 路径”任务。当前已经完成 Phase 0、Phase 1、Phase 2，并启动 Phase 3 raw 文件找回清单。

```text
当前工作树：C:\Users\caoyi\Projects\个人网页项目
当前分支：main
远端状态：Phase 0/1/2 已 push 到 origin/main，最新远端提交 e73aad7
Phase 0 提交：03c5753 Audit live and local content parity
Phase 1 提交：5ad1b25 Audit missing content source paths
Phase 2 提交：e73aad7 Document source path repair strategy
Phase 3 状态：已生成 raw 找回清单；当前 allowed roots 内未实际找回 P0 raw 文件
```

## Phase 0：线上与本地内容一致性检查

新增脚本：

```text
scripts/audit_live_vs_local.mjs
```

生成报告：

```text
docs/内容整理报告/live-vs-local-posts.csv
```

结论：

```text
Local posts: 161
Live posts: 161
same: 159
metadata_diff: 2
```

未发现线上有、本地没有的文章；未发现正文内容需要从线上反向同步。

## Phase 1：source missing 分类报告

已运行：

```text
python scripts/check_source_paths.py
node scripts/audit_source_repair_plan.mjs
```

生成报告：

```text
docs/内容整理报告/source-path-check.csv
docs/内容整理报告/source-path-repair-plan.csv
```

分类结果：

```text
Rows: 323
ok: 10
no_source: 1
missing_share_docx: 114
missing_share_raw: 6
missing_sermon_raw_directory: 192
```

## Phase 2：策略判断

新增策略报告：

```text
docs/内容整理报告/source-path-phase-2-strategy.md
```

结论：

- 当前 312 个 missing 的主因不是 Markdown 路径拼写错误，而是历史原始资料没有进入当前仓库的 `data/raw/`。
- 目前没有发现可以安全自动修复的高置信度路径项。
- 不建议批量修改 `source` 字段。
- 本阶段不修改任何文章内容，也不修改任何文章 `source`。

## Phase 3：raw 文件找回清单

新增脚本：

```text
scripts/create_source_raw_recovery_checklist.mjs
```

生成报告：

```text
docs/内容整理报告/source-raw-recovery-checklist.csv
docs/内容整理报告/source-path-phase-3-raw-recovery.md
```

去重后的找回目标：

```text
Recovery targets: 158
missing_share_raw: 3
no_source: 1
missing_share_docx: 58
missing_sermon_raw_directory: 96
```

本地搜索结论：

- 已在允许访问的 `C:\Users\caoyi\Projects` 内检查 `个人网页项目`、`讲道整理` 和 `NAS` 入口。
- 未找到 P0 的 3 个近期分享 raw 文件。
- 未找到 `2026-06-27-以弗所书-28-9耶稣为什么行神迹.md` 的原始来源文件。
- `\\RonnieNAS\tmp\分享`、`\\RonnieNAS\tmp\讲道`、`\\RonnieNAS\share\教会讲道` 当前不在 CodexPro allowed roots 内，无法自动读取。

## 推荐下一步

1. 优先找回最近 3 篇分享 raw 文件：

```text
data/raw/分享/圣经所说的“魔鬼的诡计”是什么意思？.txt
data/raw/分享/神的话语如何在信徒里面运行？.txt
data/raw/分享/耶稣叫我们“背起自己的十字架”到底是什么意思？.md
```

2. 单独核对 1 篇 `no_source`：

```text
src/content/posts/2026-06-27-以弗所书-28-9耶稣为什么行神迹.md
```

需要确认标题、经文和真实来源。注意文件名中的 `以弗所书-28-9` 与 frontmatter 的 `以弗所书 2:8-9` 不一致，疑似 slug 生成时丢失冒号。

3. 若要让 CodexPro 继续自动查找 NAS，需要把以下路径加入 allowed roots，或手动复制资料到 `C:\Users\caoyi\Projects` 下临时目录：

```text
\\RonnieNAS\tmp\分享
\\RonnieNAS\tmp\讲道
\\RonnieNAS\share\教会讲道
```

4. 如果找回 raw 文件后，重新运行：

```text
python scripts/check_source_paths.py
node scripts/create_source_raw_recovery_checklist.mjs
```

5. 再决定是否展开 P1/P2 的历史 raw 大规模补齐。

## 注意事项

- 不要把 `source` 改成 processed 文件路径。
- 不要把 `source` 改成正式 posts 路径。
- 不要伪造不存在的 raw 文件。
- 在没有找回 raw 文件前，不要批量清空或替换历史 `source`。
