# Source 路径修复 Phase 3：raw 文件找回清单

生成日期：2026-06-30

## 目标

Phase 3 的目标不是直接修改文章 `source`，而是把 Phase 1/2 中确认缺失的 raw 来源去重，形成可执行的找回清单。

本阶段仍遵守 Phase 2 结论：

- 不把 `source` 改成 processed 文件路径。
- 不把 `source` 改成正式 posts 路径。
- 不伪造不存在的 raw 文件。
- 优先找回真实 raw 文件或 raw 目录。

## 已执行

新增脚本：

```text
scripts/create_source_raw_recovery_checklist.mjs
```

输入报告：

```text
docs/内容整理报告/source-path-repair-plan.csv
```

输出报告：

```text
docs/内容整理报告/source-raw-recovery-checklist.csv
```

运行结果：

```text
Recovery targets: 158
missing_share_raw: 3
no_source: 1
missing_share_docx: 58
missing_sermon_raw_directory: 96
```

说明：Phase 1 中的 323 条检查项包含 processed 与 posts 两份副本。Phase 3 按 `current_source` 去重后，实际需要找回或核对的目标是 158 个。

## 当前本地搜索结果

已在允许访问的 `C:\Users\caoyi\Projects` 范围内检查：

- `个人网页项目`
- `讲道整理`
- `NAS` 入口本身

结果：

- `讲道整理` 中只发现最近 Kick against the Goads 相关资料。
- 未找到 3 个 P0 分享 raw 文件。
- 未找到 `2026-06-27-以弗所书-28-9耶稣为什么行神迹.md` 的原始来源文件。
- `C:\Users\caoyi\Projects\NAS` 下的 `分享收件`、`讲道收件`、`教会讲道归档` 看起来是 NAS 入口或链接；当前 CodexPro allowed roots 只包含 `C:\Users\caoyi\Projects`，无法直接打开 `\\RonnieNAS\tmp\分享` 或 `\\RonnieNAS\share\教会讲道`。

尝试打开 UNC 路径时被拒绝：

```text
Workspace root is outside allowed roots: \\RonnieNAS\tmp\分享
Workspace root is outside allowed roots: \\RonnieNAS\share\教会讲道
Allowed roots:
- C:\Users\caoyi\Projects
```

## P0：优先找回目标

这 4 项应最先处理。

### 1. 最近分享 raw：神的话语如何在信徒里面运行？

目标路径：

```text
data/raw/分享/神的话语如何在信徒里面运行？.txt
```

影响文件：

```text
data/processed/整理后的分享文章/2026-06-11-帖撒罗尼迦前书-2-13-神的话如何在信徒里面运行.md
src/content/posts/2026-06-11-帖撒罗尼迦前书-2-13-神的话如何在信徒里面运行.md
```

### 2. 最近分享 raw：魔鬼的诡计

目标路径：

```text
data/raw/分享/圣经所说的“魔鬼的诡计”是什么意思？.txt
```

影响文件：

```text
data/processed/整理后的分享文章/2026-06-11-以弗所书-6-11-魔鬼的诡计-如何识别并抵挡属灵欺骗.md
src/content/posts/2026-06-11-以弗所书-6-11-魔鬼的诡计-如何识别并抵挡属灵欺骗.md
```

### 3. 最近分享 raw：背起自己的十字架

目标路径：

```text
data/raw/分享/耶稣叫我们“背起自己的十字架”到底是什么意思？.md
```

影响文件：

```text
data/processed/整理后的分享文章/2026-06-11-马太福音-16-24-背起自己的十字架-舍己并跟随耶稣.md
src/content/posts/2026-06-11-马太福音-16-24-背起自己的十字架-舍己并跟随耶稣.md
```

### 4. no_source：耶稣为什么行神迹？

文章：

```text
src/content/posts/2026-06-27-以弗所书-28-9耶稣为什么行神迹.md
```

当前 frontmatter：

```text
title: "以弗所书 2:8-9｜耶稣为什么行神迹？"
scripture: "以弗所书 2:8-9"
source: ""
```

注意：文件名中的 `以弗所书-28-9` 与 frontmatter 的 `以弗所书 2:8-9` 不一致，疑似文件名 slug 生成时丢失冒号。此项应单独核对来源，不应自动补 source。

## P1：历史分享 docx

去重后共有 58 个目标，类别为：

```text
missing_share_docx
```

这些通常形如：

```text
data/raw/分享/*.docx
```

建议从旧分享 raw 归档、旧项目备份、NAS 或手动资料目录中找回，并按原 `source` 路径放回。

## P2：历史讲道 raw 目录

去重后共有 96 个目标，类别为：

```text
missing_sermon_raw_directory
```

这些通常形如：

```text
data/raw/教会讲道/<日期标题_讲员>/文本.txt
```

建议从受保护讲道归档中找回完整目录，而不是只补单个 `文本.txt`。

## 需要用户或环境调整的事项

若要让 CodexPro 继续自动查找 NAS，需要把以下路径加入 CodexPro allowed roots，或把对应资料先复制到 `C:\Users\caoyi\Projects` 下的临时目录：

```text
\\RonnieNAS\tmp\分享
\\RonnieNAS\tmp\讲道
\\RonnieNAS\share\教会讲道
```

如果不调整 allowed roots，也可以手动把找到的 raw 文件复制到项目中的目标路径。复制后运行：

```text
python scripts/check_source_paths.py
node scripts/create_source_raw_recovery_checklist.mjs
```

确认 missing 数量下降。

## Phase 3 当前结论

本阶段已经完成 raw 找回清单生成，但在当前 allowed roots 范围内没有实际找回 P0 raw 文件。

下一步建议：

1. 开放 NAS allowed roots，或手动复制 P0 的 3 个 raw 文件到 `data/raw/分享/`。
2. 单独核对 no_source 文章来源。
3. P0 处理后重新运行 source 检查。
4. 再决定是否展开 P1/P2 的历史 raw 大规模补齐。
