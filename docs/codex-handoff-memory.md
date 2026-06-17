# Codex Handoff Memory

This file is the project-level memory for another Codex account. Read it before handling RonnieCross content.

## Canonical Project

- Formal repository: `C:\Users\caoyi\Projects\各人网页项目`
- GitHub is the source of truth for code and website content.
- Do all Node, Astro, Git, build, commit, and push work in the formal local repository.
- The old desktop workspace is only a pointer/transition location.
- NAS is not the development workspace.

## Content Intake

- Share intake: `\\RonnieNAS\tmp\分享`
- Sermon intake: `\\RonnieNAS\tmp\讲道`
- Protected sermon archive: `\\RonnieNAS\share\教会讲道`

Directory roles:

- `data/raw/分享/`: raw share sources after verified ingest.
- `data/raw/教会讲道/`: raw sermon folders, PDFs, final Chinese TXT, and extracted helper text.
- `data/processed/整理后的分享文章/`: generated share Markdown.
- `data/processed/整理后的讲道文章/`: generated sermon Markdown.
- `src/content/posts/`: website content.
- `docs/内容整理报告/`: CSV reports and audit notes.

## Required Files To Read

For every new account or new session, read:

- `AGENTS.md`
- `skills/article-workflow.md`
- `docs/content-style.md`
- `docs/统一内容整理与发布流程.md`

## Operating Defaults

- When the user says “分享”, run the full share workflow end to end.
- When the user says “讲道”, run the full sermon workflow end to end.
- End to end means: inspect, ingest, preserve raw source, process, generate article, update report, build, commit, push, and verify live.
- For sermons, also archive the completed folder to protected `share` and verify file count, bytes, and SHA-256.
- Prefer user-provided metadata over timestamps or guesses.
- If sermon date, scripture, title, or speaker cannot be known reliably, ask before ingest/publish.

## Important Safety Rules

- Start NAS work with a read-only listing check.
- Do not run Git, Node, Astro, or file watchers on NAS.
- Do not move, delete, rename, or overwrite anything inside `\\RonnieNAS\share`.
- `data/raw/` is preservation storage. Do not casually edit raw sources.
- If a target exists, stop and inspect. Do not overwrite.
- Do not delete unrelated files.
- Do not revert user changes.

## Translation Rule

The user explicitly corrected the workflow: translation must be faithful and complete.

For sermons and foreign-language source material:

- Translate sentence by sentence.
- Preserve the full information load.
- Keep every argument, example, scripture, quote, transition, repeated emphasis, tone, and conclusion.
- Do not replace translation with a shorter summary or sermon outline.
- Natural Chinese is allowed, but omission is not.

## Common Commands

Inspect share:

```shell
python scripts/content_workflow.py inspect share
```

Ingest share:

```shell
python scripts/content_workflow.py ingest share
```

Inspect sermon:

```shell
python scripts/content_workflow.py inspect sermon
```

Ingest sermon:

```shell
python scripts/content_workflow.py ingest sermon --date YYYYMMDD --title "经文与标题" --speaker "讲员"
```

Archive sermon:

```shell
python scripts/content_workflow.py archive-sermon --folder "data/raw/教会讲道/<folder>"
```

Publish:

```shell
python scripts/content_workflow.py publish share
python scripts/content_workflow.py publish sermon
node scripts/add_article_ids.mjs
npm run build
```

## Known Pitfalls

- Astro content cache can become stale after deleted/renamed posts. If a build warns about duplicate IDs or misses new files, remove `.astro/data-store.json` and rebuild.
- Import scripts must not wipe unrelated posts or another category’s reports.
- `*.extracted.txt` is not the final sermon manuscript.
- A short description generated from the first body characters can appear truncated. Prefer a complete standalone description for important articles.
- Console encoding on Windows may garble Chinese; inspect files with UTF-8-aware commands.

## Successful Completion Standard

A content task is complete only when:

- Raw source is preserved.
- Hash verification or equivalent integrity check is done.
- Generated article is checked.
- Reports are updated.
- Build passes.
- Commit is pushed.
- Live URL is verified with expected title, category, scripture/speaker, and body text.
