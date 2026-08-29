# 2026-08-29《大卫是一个有罪的人，为什么仍被称为“合神心意的人”？》分享文章发布

## 状态

`COMPLETE_COMMITTED_PUSHED_DEPLOYED_NOTIFIED`

## 来源与受控交付

- 上游 batch：`20260829-share-how-can-david`
- publication package：`website-publication-package/v1.1`
- source PDF SHA-256：`2f7beb46cc37ddccb465d5167ea268490070e92e0db96d32c15aece6178ac651`
- 中文正式稿 SHA-256：`c4ec217df9deb4873a37661887d7e684e9ef1cb5c23ba31b8a87611d63cbdea4`
- content_type：`share`
- category：`灵命成长`
- author：`Ronnie`
- publish_date：`2026-08-29`
- scripture：`使徒行传 13:22`
- website slug：`2026-08-29-david-man-after-gods-own-heart`
- articleId：`post-8e46079a73cab736`
- publishedAt：`2026-08-29T12:20:31+09:00`
- tags：`使徒行传 / 大卫 / 悔改 / 赦免 / 恩典 / 信靠神`
- archive_status：`not_applicable`
- notification_policy：`normal_first_publish`

## 关键 chronology

1. 原网站正式目录存在与本篇无关的 F004 / Project Standard 未提交治理改动，因此未在该脏 worktree 中发布。
2. 按 `docs/branch-workflow.md` 为本篇建立独立 worktree `个人网页项目-share-20260829`，分支 `task/share-how-can-david-20260829`，从最新 `origin/main` 开始；`npm run sync` PASS。
3. publication package v1.1 plan PASS。
4. 首轮无主经文 dry-run 能生成 processed 预览，但正式 apply 仅生成 processed，不生成 post，并记录 `Missing scripture: 1`。该结果不作为发布成功。
5. 重新依据内容事实与受控 Project Bible/CUV 裁决：题目核心短语“合神心意的人”与使徒行传 13:22 精确对应，原文亦明确提到《使徒行传》；本篇属于经文型分享，因此网站编辑性主经文重判为 `使徒行传 13:22`。
6. v2 publication package 重建后 dry-run PASS：`Missing scripture: 0`；Tag Pipeline 自动补入 `使徒行传`，最终 6 个精准标签。
7. 正式 apply v2 PASS，生成 processed 与正式 post；未覆盖任何既有文章。

## 本地验证

- publication-package consumer validation：PASS
- v2 dry-run：PASS / Missing scripture=0
- v2 publish：PASS
- `node scripts/add_article_ids.mjs`：292 篇 / 0 缺失
- `python3 scripts/check_content_mirrors.py`：584 checked / 0 errors
- `npm run check:knowledge`：292 posts / 0 errors / 0 warnings
- `npm run check:tags`：27/27 PASS
- `npm run build`：PASS / 334 pages；新路由 `/posts/2026-08-29-david-man-after-gods-own-heart/` 已生成

## 生产验收

- 内容提交：`e678e246863a968746a7b1558a113f6d9e836b64`，已 push 到 `origin/main`。
- Cloudflare：`/deployment.json` 确认 commit=`e678e246863a968746a7b1558a113f6d9e836b64`，`builtAt=2026-08-29T03:25:34.378Z`。
- 正式 URL：`https://ronniecross.com/posts/2026-08-29-david-man-after-gods-own-heart/`，HTTP 200。
- 线上正文指纹：标题 / `使徒行传 13:22` / “没有任何一件他做过的事能够抹去神对他的爱和赦免”全部 PASS。
- GitHub Actions `Email published posts`：run `33231300691`，completed / success；`postCount=1`、`recipientCount=2`、`successCount=2`、`failedCount=0`。
- 原正式 worktree 的 F004 / Project Standard 未提交治理改动未进入本篇内容提交。

结论：`PASS / PUBLICATION_COMPLETE`。
