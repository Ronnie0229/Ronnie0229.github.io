# Article Workflow

## Purpose

This document is the operating workflow for another Codex account handling RonnieCross content. It covers two related but different tasks:

1. Publishing content to the RonnieCross website.
2. Rewriting or adapting source material into Chinese faith articles suitable for public reading.

When the user says “分享”, “讲道”, “整理发布”, or asks to publish material already placed in the intake folders, follow the website publishing workflow first. When the user asks for公众号版本 or article variants, follow the article adaptation workflow.

## Required Reading

Before doing any content task, read these files in this repository:

- `AGENTS.md`
- `docs/codex-handoff-memory.md`
- `docs/统一内容整理与发布流程.md`
- `docs/content-style.md`
- `docs/content-publishing-error-prevention.md`

## Sermon Translation Rules

- Translate sermon source material faithfully and completely; do not summarize in place of translation.
- 原文已经写明引用经文出处时，中文翻译必须自然保留并译出对应经文章节，不得省略；例如原文写 Galatians 2:14，中文应保留为“加拉太书 2:14”。
- 中文正文中直接引用圣经经文时，默认全部使用《和合本》译文；如需解释英文词语、原文词义或其他译本差异，可在和合本经文之外另加说明，但不得用其他中文译本替代正文经文。
- When sermon workflow rules change, update both the sermon workflow project and this website project, or explicitly report the unsynced side.
- 涉及讲道整理项目的规则变更时，必须同步检查个人网页项目对应文档；如果未同步，最终汇报必须明确说明。

## Source Of Truth

- Formal local development repository: `C:\Users\caoyi\Projects\个人网页项目`
- GitHub repository is the durable code/content source of truth.
- NAS is for intake, raw material, and protected archive. Do not run Node, Astro, Git, or file watchers on NAS.
- Share intake: `\\RonnieNAS\tmp\分享`
- Sermon intake: `\\RonnieNAS\tmp\讲道`
- Protected sermon archive: `\\RonnieNAS\share\教会讲道`

## Website Publishing Workflow

### Step 1: Inspect

Start with read-only checks:

- Check Git status in the formal local repository.
- Inspect the relevant NAS intake directory.
- Identify file names, sizes, dates, and whether the task is “分享” or “讲道”.

Do not move or edit files before this check.

### Step 2: Ingest Raw Material

Use the unified script when possible:

```shell
python scripts/content_workflow.py inspect share
python scripts/content_workflow.py ingest share
```

For sermons:

```shell
python scripts/content_workflow.py inspect sermon
python scripts/content_workflow.py ingest sermon --date YYYYMMDD --title "经文与标题" --speaker "讲员"
```

Rules:

- Move new sources into `data/raw/分享/` or `data/raw/教会讲道/`.
- Verify moves with SHA-256.
- After verified ingest, the intake folder should no longer contain processed files.
- Do not overwrite an existing raw file or folder.

### Step 3: Prepare Content

For share articles:

- Preserve the source’s main scripture anchor when clear.
- Clean OCR or formatting problems.
- Keep the article category normally as `灵命成长` unless the project has an explicit mapping.

For sermon material:

- Confirm date, scripture, title, and speaker.
- Extract PDF text into `*.extracted.txt`.
- Produce a final Chinese TXT.
- Preserve Markdown paragraph blank lines in the final Chinese TXT; do not compact the whole sermon into single-newline paragraphs.
- Remove production-only markers such as `[WD]`, `[SLIDE]`, `[slide]`, `[SLIDE - ...]`, `[TIMELINE SLIDE - ...]`, `[MAP]`, and `[PAGE ...]`. If the marker line has no正文, delete the line; if it prefixes real正文, keep the正文.
- Exclude `*.extracted.txt` from publishing; it is only a machine extraction aid.
- Follow the translation fidelity rules in `docs/content-style.md`.

### Step 4: Archive Sermons

For sermons only, copy the completed sermon folder to:

```text
\\RonnieNAS\share\教会讲道
```

Rules:

- `share` is protected archive storage.
- Only add and read there.
- Do not move, delete, overwrite, rename, or clean up files in `share`.
- Verify archive file count, byte total, and SHA-256.

### Step 5: Publish

Use the import script through the unified entry point. Never run publish without selecting one source object.

For a share article:

```shell
python scripts/content_workflow.py publish share --source-file "data/raw/分享/<file>" --dry-run --description "人工概括型摘要。"
python scripts/content_workflow.py publish share --source-file "data/raw/分享/<file>" --description "人工概括型摘要。"
```

For a sermon:

```shell
python scripts/content_workflow.py publish sermon --folder "data/raw/教会讲道/<folder>" --dry-run --description "人工概括型摘要。"
python scripts/content_workflow.py publish sermon --folder "data/raw/教会讲道/<folder>" --description "人工概括型摘要。"
```

If updating the same already-registered sermon source folder, add `--update-existing`; do not use it to create a new post or new slug.

Then add missing article IDs:

```shell
node scripts/add_article_ids.mjs
```

Check generated files:

- `data/processed/整理后的分享文章/`
- `data/processed/整理后的讲道文章/`
- `src/content/posts/`
- `docs/内容整理报告/`

### Step 6: Verify Locally

Run:

```shell
npm run build
```

If Astro shows a stale duplicate-content warning after deleted or renamed content, clear `.astro/data-store.json` and rebuild. This cache is local build state, not source content.

### Step 7: Commit, Push, Verify Online

Before commit:

- Review `git diff`.
- Ensure only the intended category changed.
- Ensure import scripts did not delete unrelated posts or reports.
- Ensure share publish used `--source-file` and sermon publish used `--folder`; unscoped publish commands are invalid.
- Ensure `description` is a manual summary, not a body excerpt, template, or placeholder.
- Ensure Markdown paragraph blank lines are preserved in processed and posts, so the public article page renders separate paragraphs.
- Ensure `[WD]`, `[SLIDE]`, `[MAP]`, `[PAGE]`, and similar source-only markers are absent from the final body.
- If the user explicitly specified a publication date for a backfilled sermon/article, ensure frontmatter `date` preserves that date rather than the export day.
- For sermons imported from the sermon-prep project, do not treat direct posts export as complete publishing until raw/source handoff, processed copy, articleId, build, online verification, and NAS archive status are all checked. NAS archive contents must be limited to the original source file, English source text, and final Chinese source text; do not archive prepublish MD, audit folders, website posts, or processed copies.
- For sermons, check `sermon-import-registry.csv` and confirm slug/path stability before using `--update-existing`.
- Ignore unrelated untracked folders unless the user asks about them.

After push:

- Verify the live article URL returns `200`.
- Confirm the live page contains expected title, category, scripture, author/speaker, and representative body text.

## Article Adaptation Workflow

Use this when the user asks for article drafts, WeChat/公众号 style, or multiple publication variants rather than direct website publishing.

### Default Output

Unless the user says otherwise, produce three versions:

1. 忠实整理版
2. 公众号温和版
3. 更安全表达版

### Step 1: Understand The Source

Identify:

- Main topic
- Scripture anchor
- Core argument
- Important examples
- Intended application
- Sensitive or easily misunderstood wording

### Step 2: Structure

Default structure:

1. 引言
2. 经文背景
3. 核心观察
4. 生命反思
5. 结尾呼应

### Step 3: Language

Shape the writing to be:

- Warm
- Clear
- Sincere
- Companionable
- Suitable for Chinese public reading
- Less argumentative unless the source itself requires direct confrontation

### Step 4: Safer Expression

When publishing context requires softer wording, consider replacements such as:

- “教会” -> “群体 / 信仰群体”
- “讲道” -> “分享 / 信息”
- “罪” -> “偏离 / 破碎 / 深处的问题”
- “悔改” -> “转向 / 重新回到正确方向”

Do not use these replacements mechanically. Preserve the theological meaning and scripture logic.

### Step 5: Output Format

Default output:

- Title
- Short summary if needed
- Body
- Subheadings
- Closing reflection

For a draft-only request, do not run build, commit, or push unless the user explicitly asks to publish.

## Non-Negotiable Rules

- Do not summarize when the user asks for translation.
- Do not convert sermon translation into a shorter sermon outline.
- Do not invent missing metadata.
- Do not change scripture meaning to make the text smoother.
- Do not delete, move, or overwrite NAS protected archive files.
- Do not touch unrelated untracked files.

## Publishing Error Prevention

Before any end-to-end website publishing task, read and follow:

```text
docs/content-publishing-error-prevention.md
```

Non-negotiable checks added after the 2026-06-21 sermon workflow:

- Do not publish from `*.extracted.txt`; create and inspect a final source-based Chinese TXT.
- For bilingual PDFs, state which source language is being followed and verify that the source-language extraction did not lose page-end lines.
- Manually check `description`, `scripture`, slug, `articleId`, `author`, `category`, `tags`, and `source` before build.
- Check paragraph blank lines, source-only marker cleanup, and user-specified `date` preservation before build.
- Check sermon NAS archive status and archive scope before commit; if it is pending, state that explicitly and do not mark the publishing workflow fully complete. Confirm the archive does not include prepublish MD, audit folders, website posts, or processed copies.
- If the importer rewrites older posts, restore unrelated old-post changes before commit.
- If a new post is missing from `dist` or Astro reports duplicate IDs after renames, clear `.astro` and rebuild.
- Verify live pages on `https://ronniecross.com/` and require title, category, scripture, author/speaker, summary, and body text to be present.
