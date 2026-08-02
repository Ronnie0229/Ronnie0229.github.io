# Files Changed

## Production Implementation

- `assets/admin/tag-rules.json`：新增单一权威 Tag Dictionary、书卷别名、generic、歧义与确定性规则源。
- `scripts/tag_pipeline.py`：新增 Python Tag Pipeline、错误模型、规范化、别名、规则生成、去重与 2–6 Gate。
- `assets/admin/tag-pipeline.js`：新增浏览器端同合同 Tag Pipeline。
- `scripts/import_shares.py`：移除局部标签实现，改用统一 Pipeline，保留人工 `--tags`。
- `scripts/import_sermons.py`：移除旧式默认标签，接入统一 Pipeline并新增 `--tags`。
- `scripts/content_workflow.py`：统一说明并向分享/讲道转发人工 tags。
- `assets/admin/editor.js`：Custom Admin 草稿保存和发布前调用 Pipeline；规则失败不执行 GitHub PUT。
- `assets/admin/decap.js`：备用 Decap Admin preSave 调用 Pipeline。
- `assets/admin/editor.html`：在 editor.js 前加载浏览器 Pipeline并更新提示。
- `assets/admin/decap.html`：在 decap.js 前加载浏览器 Pipeline。
- `assets/admin/config.yml`：保留人工标签输入并说明统一 Gate。

## Tests And Commands

- `scripts/tests/fixtures/tag_pipeline_cases.json`：新增 17 个跨运行时固定 fixture。
- `scripts/tests/test_tag_pipeline.py`：新增 Python、分享、讲道、workflow 转发和 Python/JS parity 测试。
- `scripts/run_tag_pipeline_fixtures.mjs`：新增浏览器运行时 fixture runner。
- `scripts/check-admin-save-flow.mjs`：扩展为 Custom Admin/Decap Tag Pipeline 保存护栏和浏览器 fixture 检查。
- `package.json`：新增 `npm run check:tags`。

## Long-Term Documentation

- `SEO.md`：登记统一 Tag Pipeline、单一规则源、兼容与 fail-closed 规则。
- `CONTENT_WORKFLOW.md`：更新分享/讲道 `--tags`、自动规则和旧式默认标签禁令。
- `docs/统一内容整理与发布流程.md`：登记网站新写入边界和接口兼容。
- `docs/content-publishing-error-prevention.md`：新增多入口规则漂移防错项。
- `docs/网站后台使用与配置.md`：更新 Admin 标签输入与错误行为。
- `skills/article-workflow.md`：更新 Codex 内容发布入口规则。
- `STATUS.md`：登记建设完成、验证和等待独立复审状态。
- `docs/tasks/current.md`：登记当前任务范围、结果、未实现项和下一步。

## Task Artifacts

- `tasks/current/content-workflow-tag-pipeline-construction/tag-pipeline-design.md`
- `tasks/current/content-workflow-tag-pipeline-construction/progress.md`
- `tasks/current/content-workflow-tag-pipeline-construction/verification.md`
- `tasks/current/content-workflow-tag-pipeline-construction/files-changed.md`
- `tasks/current/content-workflow-tag-pipeline-construction/NEXT_HANDOFF.md`

`task.md` 是未弱化的权威任务合同，本建设会话未修改其内容。整个 `tasks/` 目录仍为本地未跟踪任务资料；本会话没有覆盖、删除或提交既有任务文件。

## Protected Areas Confirmed Unchanged

- `src/content/posts/`
- `data/raw/`
- `data/processed/`
- `src/lib/knowledge/`
- `scripts/check-knowledge-layer.mjs`
- workspace-control interfaces/schemas
- RonnieAutomation / n8n / NAS
