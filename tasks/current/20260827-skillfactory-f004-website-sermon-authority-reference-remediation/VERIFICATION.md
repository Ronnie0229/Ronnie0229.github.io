# VERIFICATION｜F-P0-004 网站 Owner sermon authority reference 最小整改

## Upstream / authority

- 讲道 Owner F004 上游：`PASS_CANDIDATE / F004S-01..F004S-06 = 6/6`。
- sermon canonical reference：`讲道整理/docs/end-to-end-content-publishing-workflow.md §4.4.1/§4.4.2/§4.4.3`、`讲道整理/docs/translation-fidelity-quality-control.md`、`讲道整理/docs/sermon-independent-audit-orchestration.md`。
- Owner→consumer interface：既有 `website-publication-package/v1.1`，未修改 schema/interface。

## Current-effective inventory / remediation

定向检查并修订：

1. `个人网页项目/AGENTS.md`
2. `个人网页项目/CONTENT_WORKFLOW.md`
3. `个人网页项目/docs/统一内容整理与发布流程.md`
4. `个人网页项目/docs/content-publishing-error-prevention.md`
5. `个人网页项目/skills/article-workflow.md`

修订后定向 residual search 对上述 5 文件检查：`Full Sermon Mode / 完整讲章模式 / 全文逐段v2 / 达到E1 / E1证据 / 翻译、修复和独立审计 / 祝祷、荣耀颂 / needs_confirmation / 双边同步规则`，结果 `0 matches`。

这不表示网站不再处理经文或显示结构；网站保留的是自身 display/import/rendering/metadata 技术 Gate，而非 sermon scripture fidelity 业务判定。

## Website-owned responsibilities preserved

- `website-publication-package/v1.1` consumption
- package / identity / SHA / metadata / target-path validation
- raw / processed / posts consistency and locked identity
- Markdown/rendering and TTS-friendly scripture display
- frontmatter / SEO / scripture metadata machine format
- slug / articleId / description / tags
- build / Git / deploy / SEO / notification / online verification

## Scope verification

- 讲道整理修改：0
- publication schema/interface 修改：0
- validator/schema/service/database/watcher 新建：0
- website implementation/tests/article body 修改：0
- 联合独立审核：0
- reviewer/model/provider/n8n/runtime/production：0
- build/commit/push/deploy/email/NAS/真实发布：0
- F-P0-005 / Owner amendment adoption / L4 / P2 / Skill build-release：0

结论：`F004W-01..F004W-07 = 7/7 PASS candidate`。
