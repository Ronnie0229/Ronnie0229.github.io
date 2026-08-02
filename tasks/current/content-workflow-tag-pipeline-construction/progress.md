# Progress

## Current Status

`CONSTRUCTION_COMMITTED_PUSHED_PENDING_INDEPENDENT_REVIEW`

## Completed

- 完整读取根总控、项目入口、全部任务文件、SEO/内容发布规范与后台使用规范。
- 只读审查 `content_workflow.py`、分享/讲道导入器、发布契约消费、Custom Admin、备用 Decap Admin 和现有测试。
- 在任何实现前完成 `tag-pipeline-design.md`。
- 建立单一权威规则源 `assets/admin/tag-rules.json`：66 卷书卷及中英文别名、generic 集合、歧义集合、人物/地点/事件/主题字典和确定性推断词。
- 建立 Python Tag Pipeline `scripts/tag_pipeline.py` 和浏览器 Tag Pipeline `assets/admin/tag-pipeline.js`，统一错误码、顺序、别名、去重、字符、上下文和 2–6 Gate。
- 分享导入保留 `--tags`，支持自动书卷/规则生成，不足时 fail closed。
- 讲道导入新增并保留 `--tags`，已删除 `讲道`、`教会讲道`、讲员姓名默认标签。
- `content_workflow.py` 与 `website-publication-package/v1.1` 消费路径继续转发兼容可选 tags；未升级接口。
- Custom Admin 草稿保存与正式发布、备用 Decap preSave 均调用同一浏览器流水线和同一 JSON。
- 建立 17 个固定跨运行时 fixture，以及分享、讲道、Admin、generic、duplicate、alias、rule generation、边界、歧义和回归测试。
- 更新 SEO、内容工作流、防错清单、Admin 使用说明和 Codex 内容工作流文档。
- 完成全部规定验证；结果见 `verification.md`。
- 用户在建设完成后另行明确批准 commit 和 push；实现提交 `d47bf6e` 已成功推送到 `origin/main`。

## Boundaries Preserved

- 未修改 `src/content/posts/`、`data/raw/`、`data/processed/` 或历史审计记录。
- 未修改 GEO Knowledge Layer 实现、content schema、sitemap、RSS、canonical 或相关文章逻辑。
- 未修改 RonnieAutomation、n8n workflow 或 NAS。
- 未接入 AI Provider，未使用模型生成标签。
- 未执行真实文章生产发布、部署、邮件或 NAS。Git commit/push 仅在用户后续明确授权后执行。
- 未修改 `website-publication-package/v1.1`；`metadata.tags` 继续兼容可选。

## Not Implemented

- 历史文章标签迁移或补正。
- AI 标签阶段。
- 未来 API、移动端、批量同步或自动化入口的具体实现。
- 真实 GitHub Admin 保存、真实文章发布或生产部署验收。
- 独立复审与复审后修复。

## Remaining Risks

- 初始确定性词典有意保持保守；新人物、地点、事件或主题不在字典时会 fail closed，需要人工 `--tags` 或后续受审字典扩展。
- Python 与浏览器必须维护两份算法实现；同一 JSON 和逐项 parity test 能自动发现已覆盖 fixture 的漂移，但未来改算法时仍必须同步扩展测试。
- Decap 的异步 preSave 已通过静态护栏和浏览器运行时 fixture 验证，但本任务未进行真实 GitHub/生产保存。
- 上游 v1.1 包可继续省略 tags；若网站规则不能推断足够标签，会在网站 dry-run/write Gate 失败。这是保持契约兼容和 fail-closed 的预期行为。

## Safe Stop

建设已完成。按任务合同停止，等待新的、完全独立的复审会话；不得在本会话自动进入复审、修复、AI 标签或历史迁移。
