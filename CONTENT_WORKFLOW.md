# CONTENT_WORKFLOW.md

本文件是 RonnieCross 内容整理与发布的项目级入口。详细脚本步骤见 `docs/统一内容整理与发布流程.md`，风格规则见 `docs/content-style.md`，Codex 专项流程见 `skills/article-workflow.md`。

## 内容类型

项目主要处理：

1. 分享文章
2. 讲道资料
3. 信仰随笔
4. 圣经学习笔记
5. 翻译整理稿
6. 公众号迁移稿
7. 网站正式 Markdown / Content Collections 文章

## 重要目录

| 路径 | 用途 |
| --- | --- |
| `\\RonnieNAS\tmp\分享` | 分享收件目录 |
| `\\RonnieNAS\tmp\讲道` | 讲道收件目录 |
| `data/raw/分享/` | 分享原始资料 |
| `data/raw/教会讲道/` | 讲道原始资料 |
| `data/processed/整理后的分享文章/` | 分享中间稿 |
| `data/processed/整理后的讲道文章/` | 讲道中间稿 |
| `src/content/posts/` | 正式网站文章 |
| `docs/内容整理报告/` | 目录、审计、待确认报告 |

## 跨项目文档同步规则

讲道整理项目与个人网页项目共同维护讲道发布流程。以后只要新增或修改讲道整理、讲道翻译、讲道发布、NAS 归档、日期、元数据、发布前 MD、导出或质量门禁相关规则，都要同步检查两个项目的对应文档。

对应文档至少包括讲道整理项目的 AGENTS.md 和 docs 下相关工作流文档，以及个人网页项目的 AGENTS.md、CONTENT_WORKFLOW.md、docs/统一内容整理与发布流程.md、docs/content-publishing-error-prevention.md、skills/article-workflow.md。若只更新其中一个项目，最终汇报必须说明另一个项目尚未同步及原因。

## 内容事实来源优先级

处理内容时，按以下优先级判断：

1. 原始资料本身。
2. 用户本次明确要求。
3. `docs/统一内容整理与发布流程.md`。
4. `docs/content-style.md`。
5. `skills/article-workflow.md`。
6. 过去聊天记录或旧草稿。

## 翻译原则

翻译任务必须忠实原文，尤其是讲道 PDF、讲章、双语稿、英文资料、日文资料。

要求：

- 逐句完整翻译，不能用摘要代替翻译；讲道默认采用“完整讲章模式（Full Sermon Mode）”。
- 保留论点、例子、经文、引用、过渡句、重复强调和结论。
- 完整讲章模式必须保留讲员结束语（如“让我们祷告”）、讲道后的应用/反思/小组讨论（包括 Discussion、WAKACHIAI、Reflection Questions 等）、祝祷、荣耀颂（Doxology）及结束经文。
- 可以调整中文语序，但不能删减信息，也不能因网站发布而只保留讲道正文主体。
- 仅可删除与讲章内容无关的内部制作标记和噪音，例如 `[SLIDE]`、`JP`、`NOTE`、Speaker Notes、页码、OCR 噪音和完全重复标题。
- 不添加原文没有的解释、应用或神学判断。
- 原文已经写明引用经文出处时，中文翻译必须自然保留并译出对应经文章节，不得省略；例如原文写 Galatians 2:14，中文应保留为“加拉太书 2:14”。
- 中文正文中直接引用圣经经文时，默认全部使用《和合本》译文；如需解释英文词语、原文词义或其他译本差异，可在和合本经文之外另加说明，但不得用其他中文译本替代正文经文。
- 如果源资料有多语言版本，先确认以哪一种语言为翻译源。

## 信仰文章整理原则

适合网站发布的信仰文章，应当：

- 保持神学核心不变。
- 语气温和、清楚、可读。
- 保留经文逻辑和核心论证。
- 避免无必要的攻击性表达。
- 不把文章改成空泛鸡汤。
- 对公众平台版本，可在不改变核心意义的前提下调整表达。

## 正文 Markdown 规范

网站正文必须使用标准 Markdown 段落：段落之间保留一个空行。只有单换行、没有空行时，Astro/Markdown 前台会把多行合并成同一个段落；Admin 编辑区虽然能看到换行，但公开页面不会显示为分段。

讲道、分享、翻译稿进入 `data/processed/` 或 `src/content/posts/` 前，必须清理只用于讲稿制作或投影片提示的标记，例如：

```text
[WD]
[SLIDE]
[slide]
[SLIDE - ...]
[TIMELINE SLIDE - ...]
[MAP]
[PAGE ...]
```

如果标记独占一行，整行删除；如果标记后面还有正文，只删除标记，保留正文。清理规则必须同时应用在中文原稿合并、发布前 Markdown 生成、导出到网站三个阶段，避免任一入口漏掉。

## 网站文章 frontmatter

正式文章位于 `src/content/posts/`。具体字段以 `src/content/config.ts` 为准。新增文章前必须先查看当前 schema。

一般文章至少应包含：

```yaml
title: "文章标题"
description: "文章摘要"
date: 2026-06-20
category: "分类"
tags:
  - 标签
draft: false
```

如果项目当前使用 `articleId`，必须运行：

```shell
node scripts/add_article_ids.mjs
```

## 发布前远端同步规则

所有内容整理和发布任务，在开始修改、导入、导出、构建、提交或推送之前，必须先执行：

```shell
npm run sync
```

`npm run sync` 必须等价于 `git pull --rebase origin main`。如果本地已有未提交改动、同步失败或发生 rebase 冲突，必须暂停并与用户确认，不能跳过同步继续发布。

## 分享流程摘要

0. 同步远端：`npm run sync`
1. 只读检查：`python scripts/content_workflow.py inspect share`
2. 入库：`python scripts/content_workflow.py ingest share`
3. 预览发布：`python scripts/content_workflow.py publish share --source-file "data/raw/分享/<file>" --dry-run --description "人工概括型摘要。"`
4. 正式发布：`python scripts/content_workflow.py publish share --source-file "data/raw/分享/<file>" --description "人工概括型摘要。"`
5. 检查文章、报告、Git 差异。
6. 运行 `node scripts/add_article_ids.mjs`（如需要）。
7. 运行 `npm run build`。
8. 更新 `docs/tasks/current.md`。

分享发布必须指定单个 `--source-file`，不得无参数全量扫描 `data/raw/分享/`。`description` 必须是人工概括型摘要，不能使用正文截取、模板句或占位符。`--dry-run` 不写入 processed、posts、CSV 报告或审计摘录。

## 讲道流程摘要

0. 同步远端：`npm run sync`
1. 只读检查：`python scripts/content_workflow.py inspect sermon`
2. 确认日期、经文标题和讲员。
3. 入库：`python scripts/content_workflow.py ingest sermon --date YYYYMMDD --title "经文与标题" --speaker "讲员"`
4. 检查 PDF 提取稿。
5. 逐句完整翻译并校订中文 TXT。
6. 归档：`python scripts/content_workflow.py archive-sermon --folder "data/raw/教会讲道/<folder>"`
7. 预览发布：`python scripts/content_workflow.py publish sermon --folder "data/raw/教会讲道/<folder>" --dry-run --description "人工概括型摘要。"`
8. 正式发布：`python scripts/content_workflow.py publish sermon --folder "data/raw/教会讲道/<folder>" --description "人工概括型摘要。"`
9. 如需更新同一 source folder 对应的既有文章，必须显式加 `--update-existing`，且只能复用 registry 中的既有 slug/path。
10. 检查文章、报告、Git 差异。
11. 运行构建并记录结果。

讲道发布必须指定单个 `--folder`，不得无参数全量扫描 `data/raw/教会讲道/`。脚本会记录 `docs/内容整理报告/sermon-import-registry.csv`，用于固定 source folder、slug、source SHA-256 与正式文章路径。经文识别若在 folder、文件名、正文前部之间冲突，会停止并要求人工确认。

## 公众号迁移稿

从公众号或聊天稿迁移到网站时：

1. 不要直接复制含平台格式的 HTML。
2. 转成清晰 Markdown。
3. 保留标题、小标题、经文、核心段落。
4. 删除与平台无关的引导语。
5. 根据网站分类和标签重设 frontmatter。
6. 检查公开表达是否温和、清楚、适合长期留存。

## 整理后 Markdown 命名规则

`data/processed/整理后的分享文章/` 和 `data/processed/整理后的讲道文章/` 中的整理后 Markdown 文件名，默认使用中文命名，格式保持为 `YYYY-MM-DD-经文-中文标题.md` 或项目现有中文命名风格。

正式网站文章位于 `src/content/posts/`，可以根据公开 URL、SEO 或稳定性需要另行使用英文 slug；但 processed 中间稿用于人工复查、追溯和对照原始资料，应优先保留中文可读文件名，不要为了统一 URL 把 processed 文件批量改成英文。

## data/raw 原始资料留存规则

`data/raw/` 是个人网页项目内的原始资料留存区，不是临时缓存目录。文章发布后，默认继续保留对应原始资料，以便后续追溯、复查和修订。

历史文章的 `source` 可能指向当前仓库中尚未恢复的 raw 文件或 raw 目录。遇到 `scripts/check_source_paths.py` 报告 missing 时，优先判断是否为历史 raw 未入库；不要把 `source` 批量改成 processed 文件、正式 posts 文件或其他不可验证路径。

当前 CodexPro 环境不能穿透 `C:\Users\caoyi\Projects\NAS` 下指向 `\\RonnieNAS\...` 的符号链接。除非用户明确提供文件到仓库内，或环境后续支持 NAS allowed roots，否则不要把 NAS raw 恢复作为本轮自动修复步骤。

讲道流程中的 `archive-sermon` 表示把 `data/raw/教会讲道/<folder>` 复制到 NAS 或其他受保护归档区；它不是移动，也不代表发布后删除 `data/raw` 里的源目录。NAS 讲道归档只保存三类内容：原始文件、英文原稿文件、翻译后的中文原稿文件。除上述三类以外，不归档发布前 MD、审计报告、中间目录、网站 posts、processed 副本、脚本日志、`*.extracted.txt` 或其他可再生成资料。

后续如需清理 `data/raw/`，必须先运行 source 路径检查：

```shell
python scripts/check_source_paths.py
```

然后确认：

```text
1. 对应 processed / posts 文章的 source 不再依赖该路径；或
2. 已同步更新 source 到新的受保护归档路径；并且
3. 用户明确同意清理。
```

检查报告输出到：

```text
docs/内容整理报告/source-path-check.csv
```

独立的 `讲道整理` 项目不得直接写入个人网页项目的 `data/raw/`。它应先在自身项目内生成 `发布前MD/待发布/` 或 `发布前MD/待补元数据/`，只有用户明确进入网站发布流程时，才由个人网页项目执行导入、发布和归档。

从 `讲道整理` 项目导入讲道时，不得只把发布前 MD 或导出后的 posts 文件复制进 `src/content/posts/` 就视为完整发布。个人网页项目必须确认 raw/source 资料交接、`data/processed/整理后的讲道文章/` 副本、正式 posts、`articleId`、构建、线上验证和 NAS 归档状态。讲道内容默认必须执行 `archive-sermon` 或等价的只新增复制归档，但 NAS 实际归档内容仅限原始文件、英文原稿文件、翻译后的中文原稿文件；若因权限或环境无法完成，必须记录 `archive_status=pending`，并在最终回复和交接文档中明确说明。

## 安全边界

- `data/raw/` 只新增，不直接改写或删除原始文件。
- NAS 受保护归档区只新增和读取，不移动、不删除、不覆盖。
- 导入脚本不得清空 `src/content/posts/`。
- 不得因为整理某一类文章而删除另一类文章。
- 目标文件已存在时，停止并核对，不要自动覆盖。
- 分享发布必须使用 `publish share --source-file ...`，讲道发布必须使用 `publish sermon --folder ...`；无参数全量导入已禁用。
- 正式发布前优先运行 `--dry-run`，确认目标路径、标题、经文、摘要和 Git diff 范围。
- `description` 必须由整理者人工概括正文主旨；脚本不得用正文前部、模板句或占位符代替。
- 讲道 `slug` 由 source folder 日期稳定生成，正式发布记录在 `sermon-import-registry.csv`；更新旧文必须显式使用 `--update-existing`。

## 完成前检查

- [ ] 原始资料是否已保留。
- [ ] 中间稿是否保留。
- [ ] 正式文章是否在 `src/content/posts/`。
- [ ] 讲道内容是否已执行 `archive-sermon` 或等价只新增复制归档；如未完成，是否记录 `archive_status=pending`。
- [ ] frontmatter 是否符合 `src/content/config.ts`。
- [ ] 标题、日期、分类、标签是否正确。
- [ ] 讲道内容的 `date` 是否使用本次整理发布日期；不得从文件名、讲道内容、历史讲道日期或旧日期线索推断。非讲道文章如用户明确指定日期，按对应内容流程处理。
- [ ] 翻译是否没有遗漏原文信息。
- [ ] 正文段落之间是否保留 Markdown 空行，前台不会合并成一整段。
- [ ] `[WD]`、`[SLIDE]` 等讲稿/投影片标记是否已从中文稿、processed 和 posts 中清理。
- [ ] 是否更新整理报告。
- [ ] 是否运行文章 ID 脚本。
- [ ] 是否运行 `npm run build`。
- [ ] 是否更新 `docs/tasks/current.md`。

## 发布防错清单

每次“分享”或“讲道”整理发布，都必须同时阅读并执行：

```text
docs/content-publishing-error-prevention.md
```

上次讲道发布暴露出的固定风险：

- 双语 PDF 普通文本提取可能丢句、错序，`*.extracted.txt` 只能作为辅助，不是最终翻译源。
- 讲道翻译必须逐句忠实，不能变成摘要、提纲或主题整理。
- `description` 不能由脚本硬截正文、不能用模板句凑数，也不能只抽取正文原句；必须由整理者阅读标题、经文和正文主旨后，写成一两句可独立阅读的大意摘要。
- 讲道文章的 frontmatter `date` 固定使用整理发布时的日期；不得从原始文件名、讲道内容、历史讲道日期、文件修改时间或用户旧日期线索推断。补录旧讲道也按整理发布当天进入网站时间线。非讲道文章如用户明确指定发布日期，仍按对应内容流程处理。
- 自动识别的 `scripture`、中文 slug 和 `articleId` 可能不准，提交前必须人工核对。
- 讲道 publish 脚本可能重写旧讲道文章，提交前必须检查并排除无关旧文覆盖。
- 新文章不出现在构建产物或出现 Duplicate id 时，优先清理 `.astro` 本地缓存后重建。
- 线上验证优先使用正式域名 `https://ronniecross.com/`，不要只凭 GitHub Pages 默认域名判断失败。

