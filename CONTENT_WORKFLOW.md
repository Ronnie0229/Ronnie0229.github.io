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

- 逐句完整翻译，不能用摘要代替翻译。
- 保留论点、例子、经文、引用、过渡句、重复强调和结论。
- 可以调整中文语序，但不能删减信息。
- 不添加原文没有的解释、应用或神学判断。
- 如果源资料有多语言版本，先确认以哪一种语言为翻译源。

## 信仰文章整理原则

适合网站发布的信仰文章，应当：

- 保持神学核心不变。
- 语气温和、清楚、可读。
- 保留经文逻辑和核心论证。
- 避免无必要的攻击性表达。
- 不把文章改成空泛鸡汤。
- 对公众平台版本，可在不改变核心意义的前提下调整表达。

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

## 分享流程摘要

1. 只读检查：`python scripts/content_workflow.py inspect share`
2. 入库：`python scripts/content_workflow.py ingest share`
3. 发布：`python scripts/content_workflow.py publish share`
4. 检查文章、报告、Git 差异。
5. 运行 `node scripts/add_article_ids.mjs`（如需要）。
6. 运行 `npm run build`。
7. 更新 `docs/tasks/current.md`。

## 讲道流程摘要

1. 只读检查：`python scripts/content_workflow.py inspect sermon`
2. 确认日期、经文标题和讲员。
3. 入库：`python scripts/content_workflow.py ingest sermon --date YYYYMMDD --title "经文与标题" --speaker "讲员"`
4. 检查 PDF 提取稿。
5. 逐句完整翻译并校订中文 TXT。
6. 归档：`python scripts/content_workflow.py archive-sermon --folder "data/raw/教会讲道/<folder>"`
7. 发布：`python scripts/content_workflow.py publish sermon`
8. 检查文章、报告、Git 差异。
9. 运行构建并记录结果。

## 公众号迁移稿

从公众号或聊天稿迁移到网站时：

1. 不要直接复制含平台格式的 HTML。
2. 转成清晰 Markdown。
3. 保留标题、小标题、经文、核心段落。
4. 删除与平台无关的引导语。
5. 根据网站分类和标签重设 frontmatter。
6. 检查公开表达是否温和、清楚、适合长期留存。

## 安全边界

- `data/raw/` 只新增，不直接改写原始文件。
- NAS 受保护归档区只新增和读取，不移动、不删除、不覆盖。
- 导入脚本不得清空 `src/content/posts/`。
- 不得因为整理某一类文章而删除另一类文章。
- 目标文件已存在时，停止并核对，不要自动覆盖。

## 完成前检查

- [ ] 原始资料是否已保留。
- [ ] 中间稿是否保留。
- [ ] 正式文章是否在 `src/content/posts/`。
- [ ] frontmatter 是否符合 `src/content/config.ts`。
- [ ] 标题、日期、分类、标签是否正确。
- [ ] 翻译是否没有遗漏原文信息。
- [ ] 是否更新整理报告。
- [ ] 是否运行文章 ID 脚本。
- [ ] 是否运行 `npm run build`。
- [ ] 是否更新 `docs/tasks/current.md`。
