# 2026-08-29《大卫是一个有罪的人，为什么仍被称为“合神心意的人”？》分享文章发布

## 状态

`LOCAL_PUBLICATION_PASS_PENDING_GIT_PUSH_DEPLOY_NOTIFY_VERIFY`

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

## 待完成

仅剩：

1. 只提交本篇文章及其必要整理记录，不夹带原正式 worktree 的治理改动；
2. push 到 `origin/main`；
3. 验证 Cloudflare `/deployment.json` 对应同一 commit；
4. 验证正式 URL HTTP 200 与正文指纹；
5. 验证首次发布邮件 workflow；
6. 更新 `STATUS.md` / `docs/tasks/current.md` 为最终完成态。
