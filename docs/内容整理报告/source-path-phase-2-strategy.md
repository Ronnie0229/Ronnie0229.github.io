# Source 路径修复 Phase 2 策略判断

生成日期：2026-06-30

## 背景

Phase 0 已确认线上 `ronniecross.com` 与本地 `src/content/posts` 的文章数量一致：本地 161 篇、线上 161 篇，没有发现线上有而本地没有的文章，也没有发现正文内容需要从线上反向同步。

Phase 1 已生成：

- `docs/内容整理报告/source-path-check.csv`
- `docs/内容整理报告/source-path-repair-plan.csv`

检查范围包括：

- `data/processed/整理后的分享文章/*.md`
- `data/processed/整理后的讲道文章/*.md`
- `src/content/posts/*.md`

## 当前统计

```text
Checked: 323
No source: 1
Missing: 312
OK: 10
```

Phase 1 分类结果：

```text
ok: 10
no_source: 1
missing_share_docx: 114
missing_share_raw: 6
missing_sermon_raw_directory: 192
```

## Phase 2 结论

这批 `source` 缺失的主因不是 Markdown 中的路径拼写错误，而是历史原始资料没有进入当前仓库的 `data/raw/`。

因此，不建议执行“批量改 source 路径”。目前没有发现可安全自动修复的高置信度路径项。

如果现在强行修改 `source` 字段，只会把原本准确记录的历史来源路径改成不可靠的占位路径，反而降低可追溯性。

## 分类说明

### 1. `missing_sermon_raw_directory`: 192

含义：讲道文章的 `source` 指向类似：

```text
data/raw/教会讲道/<日期标题_讲员>/文本.txt
```

但整个历史讲道 raw 子目录不在当前仓库中。

建议动作：

```text
recover_raw_directory
```

也就是从旧项目、NAS、受保护归档目录或讲道整理项目中找回对应讲道原始目录，再放回 `data/raw/教会讲道/`。

不建议：

- 不要把 `source` 改成 processed 文件路径。
- 不要把 `source` 改成正式 posts 路径。
- 不要伪造不存在的 raw 文件。

### 2. `missing_share_docx`: 114

含义：分享文章的 `source` 指向历史 `.docx`，例如：

```text
data/raw/分享/20220402 婚姻和教会.docx
```

但这些 `.docx` 文件不在当前 `data/raw/分享/` 中。

建议动作：

```text
recover_raw_file
```

也就是从旧资料目录、备份、NAS 或旧内容整理项目中找回原始 docx，并按当前 `source` 记录的路径放回。

不建议：

- 不要把 docx 路径改成同名 Markdown。
- 不要把 source 清空。
- 不要用正式发布文章代替原始资料。

### 3. `missing_share_raw`: 6

含义：最近几篇分享文章指向 `.txt` 或 `.md` raw 文件，但对应文件缺失。涉及 processed 与 posts 两份副本，所以实际文章大约是 3 篇：

```text
data/raw/分享/圣经所说的“魔鬼的诡计”是什么意思？.txt
data/raw/分享/神的话语如何在信徒里面运行？.txt
data/raw/分享/耶稣叫我们“背起自己的十字架”到底是什么意思？.md
```

建议优先级最高。原因：这些是近期文章，应该更容易从收件目录、旧工作目录或 ChatGPT/Codex 处理记录中找回。

建议动作：

```text
recover_raw_file_or_manual_review
```

如果原始文件已经找不到，才进入 legacy 缺失策略。

### 4. `no_source`: 1

文章：

```text
src/content/posts/2026-06-27-以弗所书-28-9耶稣为什么行神迹.md
```

建议动作：

```text
manual_review
```

需要先核对：

- 文件名中的 `以弗所书-28-9` 是否是经文识别错误。
- 文章来源是否来自分享文章、讲道、或手动发布。
- 是否应补充真实 `source`。

## 推荐执行顺序

### Step 1：先找回近期 3 篇分享 raw 文件

优先处理 `missing_share_raw` 中的 3 个实际来源文件。成功后，processed 与 posts 中对应 6 条 missing 会转为 ok。

### Step 2：人工核对 no_source 文章

核对 `2026-06-27-以弗所书-28-9耶稣为什么行神迹.md` 的标题、经文和来源。不要在未确认来源前自动补 source。

### Step 3：查找历史 raw 根目录

重点确认是否有旧资料目录包含：

```text
data/raw/分享/*.docx
data/raw/教会讲道/<历史讲道目录>/
```

如果能找到，应优先补 raw 文件，而不是改 Markdown source。

### Step 4：若历史 raw 确认无法找回，再制定 legacy 策略

可选方案：

```yaml
source: "data/raw/.../原记录路径"
sourceStatus: "missing_raw_archive"
```

但当前 `src/content/config.ts` 还没有 `sourceStatus` 字段。若采用该策略，需要先更新 schema、文档和检查脚本。

## Phase 2 决策

本阶段不修改任何文章 `source` 字段。

当前建议：

1. 不做批量路径替换。
2. 先补齐 raw 文件，尤其是最近 3 篇分享 raw。
3. 单独核对 1 篇 no_source。
4. 历史 raw 如果无法找回，再进入 legacy missing raw 设计。
