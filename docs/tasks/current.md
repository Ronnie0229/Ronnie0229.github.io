# 当前任务：source 路径修复审计与策略

## 任务状态

正在处理“批量修复 source 路径”任务。当前已经完成 Phase 0、Phase 1，并启动 Phase 2 策略判断。

```text
当前工作树：C:\Users\caoyi\Projects\个人网页项目
当前分支：main
远端状态：已 push 到 origin/main，最新远端提交 5ad1b25
Phase 0 提交：03c5753 Audit live and local content parity
Phase 1 提交：5ad1b25 Audit missing content source paths
Phase 2 状态：已生成策略报告，未修改文章 source 字段
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

需要确认标题、经文和真实来源。

3. 查找历史 raw 根目录：

```text
data/raw/分享/*.docx
data/raw/教会讲道/<历史讲道目录>/
```

如果能从旧项目、NAS、归档目录或讲道整理项目中找回，应优先补 raw 文件，而不是改 Markdown source。

4. 如果历史 raw 确认无法找回，再设计 legacy missing raw 策略，例如新增 `sourceStatus` 字段；但这需要先更新 schema、文档和检查脚本。

## 注意事项

- 不要把 `source` 改成 processed 文件路径。
- 不要把 `source` 改成正式 posts 路径。
- 不要伪造不存在的 raw 文件。
- 在没有找回 raw 文件前，不要批量清空或替换历史 `source`。
