# Source 路径修复 Phase 4：仓库内可验证项收尾

生成日期：2026-06-30

## 目标

Phase 4 的目标是在移除 NAS 恢复后，确认当前仓库内部还能安全处理哪些 `source` 问题。

本阶段遵守以下边界：

- 不访问 `\\RonnieNAS\tmp\分享`。
- 不访问 `\\RonnieNAS\tmp\讲道`。
- 不访问 `\\RonnieNAS\share\教会讲道`。
- 不通过 `C:\Users\caoyi\Projects\NAS` 下的符号链接穿透 NAS。
- 不把 `source` 改成 processed 文件路径。
- 不把 `source` 改成正式 posts 路径。
- 不伪造不存在的 raw 文件。

## 已确认的当前状态

Phase 0 已确认线上和本地文章数量一致，且没有正文需要从线上反向同步。

Phase 1/2/3 已确认 source 缺失的主要原因是历史 raw 文件没有进入当前仓库，而不是 Markdown 里的路径拼写错误。

当前 source 检查核心统计为：

```text
Checked: 323
No source: 1
Missing: 312
OK: 10
```

分类统计为：

```text
ok: 10
no_source: 1
missing_share_docx: 114
missing_share_raw: 6
missing_sermon_raw_directory: 192
```

## 仓库内可验证项核对

### 1. `missing_share_docx`

结论：本轮不处理。

原因：这些路径指向历史 `.docx` raw 文件。当前仓库内没有对应文件；不应把它们改成发布后的 Markdown 或 processed Markdown。

后续动作：作为历史 raw 恢复任务处理。

### 2. `missing_sermon_raw_directory`

结论：本轮不处理。

原因：这些路径指向历史讲道 raw 子目录。当前仓库内没有对应目录；不应只靠 posts 或 processed 文件重建 source。

后续动作：作为历史讲道 raw 归档恢复任务处理。

### 3. `missing_share_raw`

结论：本轮不处理。

原因：涉及最近 3 篇分享 raw 文件，但当前仓库内没有对应 raw 文件。由于 NAS 恢复已从本轮移除，不能在本阶段找回这些文件。

涉及目标：

```text
data/raw/分享/圣经所说的“魔鬼的诡计”是什么意思？.txt
data/raw/分享/神的话语如何在信徒里面运行？.txt
data/raw/分享/耶稣叫我们“背起自己的十字架”到底是什么意思？.md
```

后续动作：由用户手动提供 raw 文件，或另开 NAS raw 恢复任务。

### 4. `no_source`

文章：

```text
src/content/posts/2026-06-27-以弗所书-28-9耶稣为什么行神迹.md
```

当前 frontmatter：

```yaml
title: "以弗所书 2:8-9｜耶稣为什么行神迹？"
scripture: "以弗所书 2:8-9"
source: ""
```

仓库内搜索未找到可验证的对应 raw 文件或 processed 副本。本轮不补 source。

注意事项：文件名中的 `以弗所书-28-9` 与 frontmatter 中的 `以弗所书 2:8-9` 不一致，疑似 slug 生成时丢失冒号。此项只记录，不在本阶段改名，避免改变既有 URL。

后续动作：单独追溯来源。如果能找到原始 raw，再补 `source`。

## Phase 4 决策

本阶段不修改任何文章内容或 frontmatter。

当前仓库内没有可安全自动修复的 `source` 路径项。继续保留现有 `source` 原始记录，比改成不可验证路径更安全。

本轮 source 路径任务到此形成稳定结论：

1. 线上与本地内容一致。
2. source 缺失主要是 raw 文件未入库，不是 source 字段写错。
3. NAS 恢复已从本轮移除。
4. 仓库内没有可自动修复项。
5. 后续若要降低 missing 数量，应先补真实 raw 文件，而不是批量改 Markdown。

## 后续独立任务建议

### 任务 A：近期 3 篇分享 raw 找回

由用户手动提供或另开任务恢复以下文件：

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

### 任务 C：历史 raw 归档恢复

在 NAS 权限或手动复制条件满足后，再处理：

```text
data/raw/分享/*.docx
data/raw/教会讲道/<历史讲道目录>/
```
