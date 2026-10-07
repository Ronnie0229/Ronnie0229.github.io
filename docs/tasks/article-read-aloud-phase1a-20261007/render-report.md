# Render Report — Phase 1A

状态：PASS_RENDER_VIEW_V0

## Frozen source

- articleId：`post-32d30724d859c99c`
- source：`src/content/posts/2026-10-06-does-james-4-say-not-to-make-plans.md`
- frozen source SHA-256：`14dcd20d98b1b644a6613d4f54813b065842af3b221d8347c8713d20957c7398`
- fresh source SHA-256：`14dcd20d98b1b644a6613d4f54813b065842af3b221d8347c8713d20957c7398`
- baseline：`ef1f8a8d85ab62d278f7eddc6d540943fe0d1b74`

## Render result

- output：`tts-readaloud.txt`
- output SHA-256：`5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`
- UTF-8 bytes：`10658`
- VOICE_AI request size limit：`262144`
- size gate：PASS

## Fidelity mapping

- source body paragraphs：51
- Render View paragraphs：53
- extra Render View paragraphs：2
  1. article title
  2. normalized main scripture reference
- source body paragraph sequence：51/51 exact preserved after the first two Render View paragraphs
- proposition/question/quotation/scripture quotation/ending：no deletions observed
- paragraph order：unchanged
- body text rewrites：none

## Deterministic normalization

Only the YAML main scripture reference was normalized:

- source frontmatter：`雅各书 4:13-17`
- Render View：`雅各书4章13节到17节`

The body already uses spoken-form references such as `雅各书4章13节到17节`, `箴言16章1节`, `诗篇33篇10节到11节`; these were preserved exactly as source text.

No scripture body text was replaced, retranslated, summarized, or normalized to another Bible version.

## Exclusions

Excluded from Render View:

- YAML delimiters and metadata keys
- articleId
- description
- date / publishedAt
- tags
- category
- author
- reviewed
- source path
- website/navigation/comment/subscription/player data

## Markdown/YAML control check

PASS. The Render View contains no YAML delimiters and no Markdown heading/bold/blockquote control markers introduced by the source.

## Verification chronology

1. First local verification command: FAIL because the shell parsed a backtick inside the command string as unmatched shell syntax.
2. No source or Render View content changed because of that failure.
3. Equivalent read-only verification without the ambiguous shell quoting: PASS.

This command-level FAIL is retained as chronology and is not a content fidelity failure.
