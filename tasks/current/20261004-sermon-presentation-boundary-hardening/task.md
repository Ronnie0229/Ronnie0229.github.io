# Sermon Presentation Boundary Hardening — 2026-10-04

状态：PASS_INDEPENDENT_AUDIT_CLOSED / CANONICAL_ADOPTION_AUTHORIZED

## 目标

闭合《前方弯道》事故暴露的 presentation boundary 缺口：

1. fidelity record boundary 不得再被当作 Website paragraph boundary；
2. canonical sermon dry-run/publish 必须消费已验证 presentation artifact；
3. 长篇正文 paragraph collapse / rendered block density / heading integrity 必须 deterministic fail-closed；
4. 旧 incident-only mechanical PASS 不得再被解释为完整结构验收；
5. 历史 package 保持 read-only compatibility。

## 实现

- `scripts/validate_sermon_presentation.mjs` → `sermon-publication-presentation-structure/v2`
  - `paragraph_collapse_guard`
  - `rendered_block_density`
  - `heading_render_integrity`
  - success=`SERMON_PRESENTATION_STRUCTURE_PASS`
  - ceiling=`publication_structure_ready`
  - legacy mechanical status 仅兼容/chronology。
- `validate_publication_package.py` 验证 optional presentation binding；历史无 binding sermon package 可 read-only validate/plan。
- `consume_publication_package.py`：new sermon dry-run/publish 缺 binding → `PRESENTATION_ARTIFACT_REQUIRED`。
- `content_workflow.py` / `import_sermons.py`：canonical sermon publish 必须 `--presentation-file`；不再从 plain TXT 猜正式 presentation structure。
- 新 incident regression fixtures + consumer/fixed-dry-run/tag regression。
- current workflow/AGENTS/skill 文档同步。

## 验证

- Website Python suite：61/61 PASS。
- Website presentation Node suite：14/14 PASS。
- mirrors：600/600 PASS。
- Knowledge：300 posts / 0 errors / 0 warnings。
- tag fixtures：27/27 PASS。
- forced build：344 pages / Complete。
- `git diff --check`：PASS（初次发现 test EOF extra blank line 后 targeted 修正，再跑 PASS）。
- 真实 Curve Ahead presentation artifact：3947 rendered chars / 138 p / 6 H2 / 144 content blocks，`SERMON_PRESENTATION_STRUCTURE_PASS / publication_structure_ready`。
- 历史只读扫描：219 sermon posts；same-class structural collapse=1（`2026-07-09-马太福音-7-1-6｜论断人.md`，4300 chars / 1 p / 0 H2）。只报告，不在本整改自动修改。

## 边界

本任务没有 production publish/deploy/notification 副作用。正式 adoption 仍需按普通治理/代码任务 Git Gate 完成 canonical integration/commit/push。
