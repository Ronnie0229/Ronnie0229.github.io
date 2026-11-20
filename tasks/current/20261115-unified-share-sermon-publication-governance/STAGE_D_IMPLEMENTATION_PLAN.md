# Stage D — Documentation and Entrypoint Cutover Plan

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D — Documentation and entrypoint cutover
- Status: `FROZEN / IMPLEMENTATION_IN_PROGRESS`
- Date: 2026-11-18
- Website construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Sermon construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Canonical design authority: Sermon Owner `tasks/current/20261115-unified-share-sermon-publication-governance/DESIGN.md`, SHA-256 `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f`
- Prerequisites: Stage A PASS; Stage B PASS / Master accepted; Stage C PASS_WITH_FINDINGS / Master accepted.

## 1. Purpose and interpretation

Stage D synchronizes the two projects' operational documentation and prepares a unified new-content entrypoint for Share and Sermon. It removes contradictory instructions that still describe separate/unequal production paths, while preserving content-type-specific profiles and the exact legacy compatibility boundary.

Stage D does **not** enable v1.3 production writes. The unified entrypoint may expose and validate the v1.3 controlled path, but all v1.3 non-dry-run production operations remain fail-closed until Stage E synthetic end-to-end acceptance is independently accepted and Stage F is separately authorized and executed.

## 2. Frozen business invariants

1. Share and Sermon use the same publication governance, identity/fidelity/package/rendering gates.
2. Share retains its own article structure. No sermon three-point outline, Full Sermon Mode, sermon discussion/benediction requirements are imposed on Share.
3. Sermon retains Full Sermon Mode and all current sermon-specific presentation requirements.
4. The only business differences are:
   - intake: `NAS/分享收件` vs `NAS/讲道收件`;
   - fallback identity: author Ronnie vs speaker Patrick; explicit source/Owner identity always wins;
   - archive: Share `not_applicable` / `SHARE_ARCHIVE_NOT_APPLICABLE`, with no NAS archive-path access; Sermon keeps protected append-only NAS archive.
5. Any source-language-to-Chinese translation uses the existing common fidelity state machine and its unchanged three-attempt / three-repair release semantics. Stage D must not fork or redefine fidelity logic.
6. TTS scripture display normalization occurs before candidate SHA freeze; non-contiguous/ambiguous or unresolved English references fail closed. Machine metadata may retain compact scripture notation.
7. v1.3 package and `content-presentation/v1` are the new controlled contract. v1.0/v1.1/v1.2 behavior and historical records remain compatible and immutable.
8. Historical posts, URLs, articleIds, metadata, audit outcomes and FAIL/BLOCKED/PARTIAL/PASS chronology are not batch-rewritten.
9. Sermon Owner remains authority for source extraction, translation fidelity, Project Bible and sermon theology. Website remains authority for consumer validation, rendered structure, raw/processed/posts, metadata display, build, Git, deployment, SEO and notifications.

## 3. Bounded write-set

### 3.1 Sermon construction worktree

Documentation alignment:
- `AGENTS.md`
- `docs/end-to-end-content-publishing-workflow.md`
- `docs/chinese-to-prepublish-md-workflow.md`
- `docs/prepublish-md-metadata-quality-gate.md`
- `docs/sermon-and-publishing-metadata.md`
- `docs/scripture-reference-display-normalization.md`
- `docs/translation-fidelity-policy.md` and `docs/translation-fidelity-orchestration.md` only for minimal entrypoint/compatibility clarifications; no fidelity rule changes.

Entrypoint alignment, only if current inspection proves a mismatch:
- `scripts/generate_prepublish_md.py`
- `scripts/build_website_publication_package.py`
- `scripts/export_to_website_project.py`
- existing generic presentation validator / fidelity loop CLI help and dispatch.
No new state machine, service, registry, daemon or parallel producer.

### 3.2 Website construction worktree

Documentation alignment:
- `AGENTS.md`
- `CONTENT_WORKFLOW.md`
- `docs/统一内容整理与发布流程.md`
- `docs/sermon-content-rendering-binding.md`
- `docs/content-style.md`
- `docs/content-publishing-error-prevention.md`
- `skills/article-workflow.md`

Entrypoint alignment, only if current inspection proves a mismatch:
- `scripts/content_workflow.py`
- `scripts/import_shares.py` / `scripts/import_sermons.py` only to preserve/clarify controlled dispatch and fail-closed behavior; no weakening of Stage C boundaries.
- existing v1.3 consumer/validator interfaces remain authoritative; no new consumer implementation.

### 3.3 Task evidence

Both construction worktrees:
- this Stage D plan (identical content);
- Stage D implementation report;
- STATUS and current task index updates;
- independent audit request and Auditor report path (request authored after implementation evidence is frozen).

No writes to either canonical worktree. Existing dirty lineage in both canonical repositories and construction worktrees must be preserved; no stash/reset/clean/rebase/commit/push.

## 4. Explicit exclusions

- No Stage E synthetic E2E execution in this stage.
- No Stage F production enablement or v1.3 non-dry-run activation.
- No production import, content mutation, raw/processed/posts writes, Astro build, deploy, email/notification, NAS probe/read/write/archive.
- No dependency install/upgrade.
- No Git staging, commit, push, merge, reset, clean, rebase or amend.
- No historical article rewrite or metadata migration.
- No changes to frozen schemas, package contract, presentation identity, translation fidelity rules, Project Bible or sermon theology.
- No broad refactor or new infrastructure.

## 5. Required Stage D deliverables

1. Both projects' entrypoint documents tell one consistent Share/Sermon workflow and identify the same frozen v1.3 package/presentation contract.
2. Both projects accurately describe role ownership and the three permitted business differences.
3. Every new translation route explicitly invokes the existing shared fidelity state machine; pure-Chinese non-translation is the only `not_required` case.
4. Both projects describe candidate freeze, Project Bible gate, presentation artifact/manifest, package generation, Website consumer/render gate in the correct order.
5. Website CLI documentation and actual dispatch agree: no new Share bypass; v1.3 direct importer still independently validates package/source/metadata; package-bound author is not overridden by legacy fallback.
6. Sermon producer CLI and docs agree on explicit v1.3 package generation/export, profile, archive semantics and fail-closed requirements.
7. v1.0/v1.1/v1.2 compatibility remains unchanged; no historical package is rewritten.
8. Stage F remains disabled in code and documentation; current production routes/defaults remain unchanged.

## 6. Acceptance matrix

| ID | Mandatory proposition | PASS evidence |
|---|---|---|
| D-01 | Stage D scope respects canonical DESIGN.md and Stage A/B/C accepted evidence | Plan and write-set match the original Stage D definition; no scope drift |
| D-02 | Share/Sermon business differences are exact | Intake, fallback identity and archive branch consistently documented in both projects |
| D-03 | Content structure profiles remain distinct | Share article structure is preserved without sermon-only requirements; Sermon Full Sermon Mode gates remain |
| D-04 | Fidelity and Project Bible ownership/order unchanged | Common existing fidelity loop; correct gate order; no duplicated/relaxed fidelity rules |
| D-05 | TTS scripture rule consistent | Examples, non-contiguous fail-closed, controlled book names, metadata exception, pre-freeze position |
| D-06 | Presentation/package producer-consumer chain consistent | Both projects agree on content-presentation/v1 + website-publication-package/v1.3 paths and bindings |
| D-07 | Website entrypoint has no bypass | Share and Sermon entrypoints converge on controlled validation; direct importer cannot bypass package/source/metadata gates |
| D-08 | Producer entrypoint is consumer-compatible | v1.3 package emission/export requires valid manifest/profile/fidelity/archive bindings and is explicit |
| D-09 | Legacy compatibility preserved | v1.0/v1.1/v1.2 and existing sermon-presentation/v1 behavior unchanged |
| D-10 | Production enablement remains gated | v1.3 non-dry-run remains disabled; Stage F remains DISABLED; no production defaults/routes switched |
| D-11 | Tests and documentation are reproducible | Relevant unit/CLI tests, syntax/compile and diff checks pass; all commands and counts recorded |
| D-12 | Workspace/write-set/chronology safe | Exact roots/branches/HEAD, pre-existing dirty files preserved, only bounded write-set changed, no prohibited side effects |

Overall Stage D may be presented for independent audit only when all D-01..D-12 are evidenced. Any mandatory failure means FAIL; missing authority/evidence means BLOCKED. Independent Auditor must be a separate context and may write only the designated Stage D audit report.

## 7. Implementation sequence

1. Reconfirm both exact construction workspaces and their dirty baselines.
2. Complete a documentation conflict matrix against the frozen contracts and current scripts.
3. Update the bounded documentation set in each project.
4. Inspect CLI entrypoints against docs; make only the smallest required routing/guard changes and add focused tests.
5. Run targeted and full relevant regressions without build or production operations.
6. Update both project STATUS/current indexes and write implementation evidence.
7. Freeze implementation report SHA and issue independent audit request.
8. Stop for separate independent audit. Stage E/F remain out of scope.

## 8. Current decision

Stage D is authorized for implementation in the two named construction worktrees only. The above scope and acceptance matrix are frozen. Any need to expand the write-set, alter a frozen contract, change Owner boundaries, access production/NAS, or enable v1.3 production behavior is an authority breakpoint and must return to Owner before proceeding.
