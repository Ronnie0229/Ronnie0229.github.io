# 2026-07-22 remote main integration audit

## Scope

- Repository: `个人网页项目`
- Branch: `main`
- Upstream: `origin/main`
- Purpose: audit the remote `main` update that blocked the Psalm 7 publication push.
- Excluded scope: `电子书整理项目/`

## Fetch Baseline

- Before fetch local `HEAD`: `c48bc4abe7336a69920b7e4d54d072bbba52b1ac`
- Before fetch local `origin/main`: `f81d927d5f3abf802a53ef5b64f97fd15c26dd5f`
- Before fetch ahead/behind: `6/0`
- Fetch command: `git fetch --prune origin`
- After fetch remote `origin/main`: `25820f0f32d978e5111e5a3bce8df1ef3724ff7f`
- After fetch local `HEAD`: `c48bc4abe7336a69920b7e4d54d072bbba52b1ac`
- After fetch ahead/behind: `6/1`

## Remote-only Commits

- `25820f0 Update article: 使徒行传 17:1-9｜帖撒罗尼迦：在逼迫中持守福音的教会`

Remote-only file change:

- `src/content/posts/2026-07-21-使徒行传-17-1-9-帖撒罗尼迦-在逼迫中持守福音的教会.md`

Observed purpose:

- Restores/adds source attribution line below the title.
- Changes frontmatter formatting for date, publishedAt and tags.
- Removes `draft: false`.
- Does not touch Psalm 7 raw, processed or post files.
- Does not touch package manifests, Astro config, GitHub Actions or publication scripts.

## Local-only Commits Before Rebase

- `c48bc4a publish(content): add Psalm 7 righteousness article`
- `e17c2d4 fix(publication): derive final result from acceptance evidence`
- `d533be9 fix(content): synchronize registry source mirrors`
- `e32244e docs(tasks): adopt unified task status policy`
- `717e60b docs(status): separate current website state from history`
- `806aee2 docs(tasks): converge website current task history`

Local-only scope includes:

- Psalm 7 raw, processed and post files.
- Publication result script and tests.
- Website task/current-state governance documents.
- Source mirror additions under `data/raw/教会讲道/`.
- ArticleId synchronization for recent processed/post files.

## File Intersection

The only direct remote commit file is:

- `src/content/posts/2026-07-21-使徒行传-17-1-9-帖撒罗尼迦-在逼迫中持守福音的教会.md`

This file is also touched by local commit `c48bc4a` to preserve/add `articleId: "post-cbd229e515b89111"`.

Related local-only processed files also carry metadata changes:

- `data/processed/整理后的分享文章/2026-07-21-使徒行传-17-1-9-帖撒罗尼迦-在逼迫中持守福音的教会.md`
- `data/processed/整理后的分享文章/2026-07-21-帖撒罗尼迦前书-4-16-在基督里死了的人必先复活是什么意思.md`
- `data/processed/整理后的分享文章/2026-07-21-帖撒罗尼迦前书-5-17-不住地祷告是什么意思.md`

## Risk Review

- Psalm 7 formal output risk: low. Remote commit does not modify Psalm 7 paths.
- Same-file risk: moderate but explainable. Remote modifies the Acts 17 post content/frontmatter; local adds/preserves articleId.
- Credential or unknown binary risk: none observed in the remote-only commit.
- Dependency/config risk: none observed. No `package.json`, `package-lock.json`, Astro config, GitHub Actions or publication script changes in remote-only commit.
- Status/current task risk: remote-only commit does not modify those files.
- Data path risk: remote-only commit does not modify `data/raw`, `data/processed`, or publication scripts.

## Recommendation

Use a non-interactive `git rebase origin/main` if the worktree is otherwise clean. If a conflict occurs, preserve both sides by retaining the remote Acts 17 source attribution/content changes and the local `articleId`/Psalm 7 publication changes. Do not skip commits and do not use whole-file ours/theirs replacement.

Safe rebase allowed: yes, subject to the conflict-handling rule above.

## Rebase Result

- Rebase command: `git rebase origin/main`
- Result: success
- Conflict occurred: no
- New local `HEAD`: `7b2e63aca8ce38d5b71b98ed806ca9486b383a7b`
- Current `origin/main`: `25820f0f32d978e5111e5a3bce8df1ef3724ff7f`
- Post-rebase ahead/behind before this audit commit: `6/0`

Rewritten local commit mapping:

- `806aee2 docs(tasks): converge website current task history` -> `91c1e45 docs(tasks): converge website current task history`
- `717e60b docs(status): separate current website state from history` -> `783448f docs(status): separate current website state from history`
- `e32244e docs(tasks): adopt unified task status policy` -> `44889a4 docs(tasks): adopt unified task status policy`
- `d533be9 fix(content): synchronize registry source mirrors` -> `69c6556 fix(content): synchronize registry source mirrors`
- `e17c2d4 fix(publication): derive final result from acceptance evidence` -> `1100b9d fix(publication): derive final result from acceptance evidence`
- `c48bc4a publish(content): add Psalm 7 righteousness article` -> `7b2e63a publish(content): add Psalm 7 righteousness article`

Preservation review:

- All six local commits remain present after rebase.
- The remote Acts 17 update is now the base of local `main`.
- Psalm 7 raw, processed and post files remain present.
- No force push, merge, branch switch, checkout overwrite, skipped commit or dropped commit was used.
