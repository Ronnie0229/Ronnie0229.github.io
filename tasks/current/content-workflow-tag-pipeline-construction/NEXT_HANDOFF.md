# NEXT HANDOFF

## Current Status

`CONSTRUCTION_COMPLETE_PENDING_INDEPENDENT_REVIEW`

## Required Next Session

下一步只能开启新的、完全独立的 Tag Pipeline 建设后复审会话。复审会话必须从 `task.md`、本文件、`tag-pipeline-design.md`、`progress.md`、`verification.md` 和 `files-changed.md` 恢复事实，不能依赖本建设对话。

本会话不得继续承担独立复审、复审后修复、AI 标签、历史标签迁移或生产发布。

## Implemented Scope

- 单一权威规则源：`assets/admin/tag-rules.json`。
- Python：`scripts/tag_pipeline.py`。
- Browser：`assets/admin/tag-pipeline.js`。
- 入口：分享、讲道、`content_workflow.py`、v1.1 契约消费后的导入边界、Custom Admin 保存/发布、备用 Decap preSave。
- 规则：scripture 多书卷、确定性人物/地点/事件/主题、CLI/Admin 人工标签、NFKC、别名、二次去重、generic、歧义、字符、context-only、2–6、fail closed。
- 教会讲道不再默认生成 `讲道`、`教会讲道` 或讲员姓名。
- Python/JavaScript 共享 JSON，并以 17 个 fixture 比较 tags/evidence/error code。
- 历史读取保持兼容；没有全局 schema 收紧或历史迁移。

## Not Implemented

- AI Provider 或模型标签。
- 历史文章 tag 批量迁移/补正。
- 未来 API、移动端、批量同步、RonnieAutomation 或 n8n 入口。
- 真实 Admin GitHub 保存、真实文章发布、部署、通知、NAS。
- 跨项目接口升级；`metadata.tags` 仍是 v1.1 兼容可选字段。

## Independent Review Attack Surface

1. 搜索是否仍有入口在 frontmatter 写入前自行拼装或绕过 `tags`。
2. 直接执行 `import_sermons.py` 是否在任何分支仍能输出 `讲道`、`教会讲道` 或 speaker 默认标签。
3. Custom Admin 草稿、Custom Admin 发布、Decap preSave 是否都在 GitHub PUT/commit 前 fail closed。
4. `/admin/tag-rules.json` 加载失败、JSON schema/version 错误时是否拒绝保存。
5. `Jacob/雅各`、`Abram/Abraham/亚伯兰`、`Noah/挪亚`、`Cain/该隐`、`Paul/使徒保罗` 是否统一且二次去重。
6. `Israel/以色列` 是否始终歧义失败，而不是无条件映射雅各。
7. `1 John` 与 `John`、中文短书卷别名、多段经文是否不会重叠误标。
8. alias 规范化后是否可绕过 generic、author/context-only 或数量 Gate。
9. 超过 6 个是否明确失败，不能静默截断；少于 2 个是否不能 fallback。
10. Python/浏览器算法是否在 fixture 之外存在排序、Unicode、长度或错误码差异。
11. v1.1 无 tags 契约是否仍能读取/plan，而网站新写入边界不足时正确失败。
12. Git diff 是否确实没有 posts、raw、processed、Knowledge Layer、历史审计、接口 Schema、RonnieAutomation 或 n8n 修改。

## Recommended Read-Only Review Commands

```shell
python3 -m unittest discover -s scripts/tests
npm run check:tags
npm run check:admin-save
npm run check:knowledge
npm run build
python3 -m py_compile scripts/tag_pipeline.py scripts/import_shares.py scripts/import_sermons.py scripts/content_workflow.py scripts/consume_publication_package.py
node --check assets/admin/tag-pipeline.js
node --check assets/admin/editor.js
node --check assets/admin/decap.js
git diff --check
git status --short
```

复审可以新增临时 fixture 或只读测试，但不得生产发布、操作 NAS、push、迁移历史标签或修改 Knowledge Layer。

## Construction Verification Baseline

- Python：21 tests PASS。
- Browser fixtures：17/17 PASS。
- Admin Save Flow：Errors 0。
- Knowledge Layer：286 posts，0 errors，0 warnings。
- Astro build：PASS。
- Source/dist Tag Pipeline 与规则文件 SHA 一致。
- Protected diff search：无输出。

## Git And Side Effects

- 分支：`main`，开始时与 `origin/main` 一致。
- 当前实现与任务资料均未 commit、未 push。
- `tasks/` 在接管时已经是未跟踪目录，本会话保留并更新任务产物。
- 没有生产发布、部署、通知、NAS、RonnieAutomation 或 n8n 副作用。

## Safe Stop

等待独立复审裁决。未经新授权，不进入修复或后续阶段。
