# 当前任务：source 路径修复审计收尾

## 任务状态

已完成“批量修复 source 路径”任务的审计、范围调整、流程固化和交接记录。本轮没有批量修改任何文章的 `source` 字段，也没有修改文章正文。

```text
当前工作树：C:\Users\caoyi\Projects\个人网页项目
当前分支：main
远端状态：Phase 0-5 已 push 到 origin/main，最新远端提交 677ae82
本轮最终状态：source 路径审计完成；仓库内无可安全自动修复项
```

## 已完成阶段

### Phase 0：线上与本地内容一致性检查

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

提交：

```text
03c5753 Audit live and local content parity
```

### Phase 1：source missing 分类报告

新增脚本：

```text
scripts/audit_source_repair_plan.mjs
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

提交：

```text
5ad1b25 Audit missing content source paths
```

### Phase 2：策略判断

新增策略报告：

```text
docs/内容整理报告/source-path-phase-2-strategy.md
```

结论：

- 当前 312 个 missing 的主因不是 Markdown 路径拼写错误，而是历史原始资料没有进入当前仓库的 `data/raw/`。
- 没有发现可以安全自动修复的高置信度路径项。
- 不建议批量修改 `source` 字段。
- 不修改任何文章内容，也不修改任何文章 `source`。

提交：

```text
e73aad7 Document source path repair strategy
```

### Phase 3：raw 文件找回清单

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

后续因 CodexPro 不能穿透 `C:\Users\caoyi\Projects\NAS` 下指向 `\\RonnieNAS\...` 的符号链接，NAS raw 恢复被移出本轮任务。

### Phase 4：仓库内可验证项收尾

新增文档：

```text
docs/内容整理报告/source-path-phase-4-in-scope-closure.md
```

结论：

- 仓库内没有可安全自动修复的 `source` 路径项。
- `missing_share_docx`、`missing_sermon_raw_directory`、`missing_share_raw` 都需要真实 raw 文件，不能靠改 Markdown 修复。
- `no_source` 文章在仓库内未找到可验证 raw 来源，本轮不补 source。

提交：

```text
a879ba6 Close in-scope source path audit
```

### Phase 5：流程固化

更新：

```text
CONTENT_WORKFLOW.md
docs/内容整理报告/source-path-phase-4-in-scope-closure.md
```

固化规则：

- 遇到 `source` missing，先判断是否为历史 raw 未入库。
- 不要把 `source` 批量改成 processed 文件、正式 posts 文件或其他不可验证路径。
- 当前 CodexPro 环境不能穿透 `C:\Users\caoyi\Projects\NAS` 下指向 `\\RonnieNAS\...` 的符号链接。
- NAS raw 恢复不作为当前自动修复流程的一部分。

提交并 push：

```text
677ae82 Document source path audit workflow
```

## 本轮最终结论

本轮 source 路径任务已经完成审计和收尾，但不执行批量修复。

原因：当前 missing 的根本原因是历史 raw 文件或 raw 目录不在仓库中，而不是 `source` 字段写错。直接改 `source` 会破坏历史追溯链。

## 后续独立任务

### 任务 A：近期 3 篇分享 raw 找回

需要用户手动提供，或另开 NAS raw 恢复任务：

```text
data/raw/分享/圣经所说的“魔鬼的诡计”是什么意思？.txt
data/raw/分享/神的话语如何在信徒里面运行？.txt
data/raw/分享/耶稣叫我们“背起自己的十字架”到底是什么意思？.md
```

### 任务 B：no_source 文章来源追溯

单独核对：

```text
src/content/posts/2026-06-27-以弗所书-28-9耶稣为什么行神迹.md
```

当前已知：

```yaml
title: "以弗所书 2:8-9｜耶稣为什么行神迹？"
scripture: "以弗所书 2:8-9"
source: ""
```

注意：文件名中的 `以弗所书-28-9` 与 frontmatter 的 `以弗所书 2:8-9` 不一致，疑似 slug 生成时丢失冒号。本轮不改名，避免改变既有 URL。

### 任务 C：历史 raw 归档恢复

在用户手动提供文件、或 NAS 访问条件变化后，再处理：

```text
data/raw/分享/*.docx
data/raw/教会讲道/<历史讲道目录>/
```

## 验证与构建

本轮主要是审计脚本与文档更新。未修改 Astro 页面、组件、内容正文或配置。

已运行过的检查：

```text
python scripts/check_source_paths.py
node scripts/audit_source_repair_plan.mjs
node scripts/audit_live_vs_local.mjs
```

未运行 `npm.cmd run build`。原因：最终收尾只涉及文档和审计报告，不影响站点构建产物。

## 下一位接手者注意事项

1. 不要继续尝试从 `C:\Users\caoyi\Projects\NAS` 穿透访问 `\\RonnieNAS`。
2. 不要把 missing source 改成 processed 或 posts 路径。
3. 如果用户提供 raw 文件，先放入对应 `data/raw/...` 路径，再运行 `python scripts/check_source_paths.py`。
4. 如果要继续处理 NAS，应另开独立任务，并先解决 CodexPro allowed roots 或手动复制文件问题。
