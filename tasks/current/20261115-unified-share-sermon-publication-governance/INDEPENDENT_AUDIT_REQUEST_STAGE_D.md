# Independent Audit Request — Stage D Share / Sermon Unified Publication Governance

- Role: `INDEPENDENT_AUDITOR` (not Master; read-only reviewer)
- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D
- Date: 2026-11-18
- Frozen plan: `STAGE_D_IMPLEMENTATION_PLAN.md`
- Plan SHA-256: `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e`
- Master implementation report: `STAGE_D_IMPLEMENTATION_REPORT.md`
- Implementation report SHA-256: `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529`
- Canonical DESIGN.md SHA-256: `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f`

## 1. Auditor role and authority

You are the Independent Auditor, not the Master. Perform a fresh, independent, read-only audit of Stage D implementation against the frozen plan, canonical DESIGN.md and D-01..D-12 denominator. Do not rely solely on the Master's PASS table. Verify source documents, actual CLI behavior, tests, hashes and workspace evidence yourself.

Do not implement fixes, update project status, accept Stage D, start Stage E, or enable Stage F. If a blocker is found, record FAIL/BLOCKED with exact evidence and return it to Master. Preserve all prior Stage A/B/C chronology.

## 2. Exact workspaces

Website construction worktree (primary audit/report destination):
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`

Sermon construction worktree:
`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`

Canonical Website (read-only only):
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`

Canonical Sermon Owner (read-only only):
`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`

First call `open_current_workspace`. Then open each exact workspace path. If any root differs, switch immediately to the exact path. Record each workspace ID, root, branch, HEAD and current dirty/staged state.

## 3. Sole permitted write path

Only this file may be created or written by the Auditor:

`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_AUDIT_REPORT.md`

Write no other file in either construction worktree or either canonical worktree. Do not modify the implementation report, plan, STATUS, task indexes, docs, scripts, tests, schemas, fixtures or historical reports. If the designated report already exists, do not overwrite it; stop and report the collision.

## 4. Required fresh reads

At minimum, read and verify:

1. Canonical Sermon Owner `tasks/current/20261115-unified-share-sermon-publication-governance/DESIGN.md` and its stated SHA.
2. Both construction copies of `STAGE_D_IMPLEMENTATION_PLAN.md`; recompute SHA and confirm exact byte identity.
3. Both construction copies of `STAGE_D_IMPLEMENTATION_REPORT.md`; recompute SHA and confirm exact byte identity.
4. Website docs: `AGENTS.md`, `CONTENT_WORKFLOW.md`, `docs/统一内容整理与发布流程.md`, `docs/sermon-content-rendering-binding.md`, `docs/content-style.md`, `docs/content-publishing-error-prevention.md`, `skills/article-workflow.md`.
5. Sermon docs: `AGENTS.md`, `docs/end-to-end-content-publishing-workflow.md`, `docs/chinese-to-prepublish-md-workflow.md`, `docs/prepublish-md-metadata-quality-gate.md`, `docs/sermon-and-publishing-metadata.md`, `docs/scripture-reference-display-normalization.md`, `docs/translation-fidelity-policy.md`, and `docs/translation-fidelity-orchestration.md`.
6. Actual Website code: `scripts/content_workflow.py`, `scripts/consume_publication_package.py`, `scripts/import_shares.py`, `scripts/import_sermons.py`, `scripts/validate_publication_package_v13.py`, `scripts/validate_content_presentation.mjs`, and the related Stage C/v1.3 tests.
7. Actual Sermon producer code: `scripts/generate_prepublish_md.py`, `scripts/build_website_publication_package.py`, `scripts/export_to_website_project.py`, and related producer/fidelity/contract tests.
8. Current STATUS/current indexes in both construction worktrees, plus the Stage C Re-Audit 04 report and Master acceptance evidence.

Search for contradictory operational instructions, not only the documents changed by Master. Distinguish historical/handoff records from current operational authority. In particular, verify that any legacy `publish share` / `publish sermon` examples are clearly labeled as Stage F前 current compatibility routes, not the v1.3 unified production path.

## 5. Mandatory D-01..D-12 denominator

Return one explicit result for every ID; do not collapse or omit rows.

| ID | Mandatory proposition | Required independent verification |
|---|---|---|
| D-01 | Scope and authority | Stage D plan/write-set match canonical DESIGN.md and accepted A/B/C prerequisites; no scope drift or unauthorized write-set expansion |
| D-02 | Business differences | Intake paths, Ronnie/Patrick fallback-only identity, explicit source/Owner precedence, Share no-NAS archive, Sermon protected append-only archive agree in both projects |
| D-03 | Content profiles | Share article-native structure is not forced into sermon outline/Full Sermon Mode/benediction; Sermon retains all existing sermon-specific gates |
| D-04 | Fidelity and Bible | Both types use the same existing fidelity state machine; no changed denominator, reviewer isolation, attempt/repair or release semantics; gate order is correct; Website does not own fidelity/Bible verdict |
| D-05 | TTS scripture normalization | Pre-candidate-freeze position, controlled book-name authority, non-contiguous/ambiguous fail-closed behavior, and compact machine metadata exception are consistent |
| D-06 | Presentation/package chain | `content-presentation/v1`, profiles, artifacts/manifests, exact record identity and `website-publication-package/v1.3` bindings agree across producer and consumer |
| D-07 | Website entrypoint/no bypass | One controlled v1.3 Share/Sermon consumer entrypoint; direct import cannot bypass package/source/metadata identity; package-bound author is not overridden by legacy Ronnie fallback |
| D-08 | Producer compatibility | Explicit v1.3 contract-version/manifest/profile/fidelity/archive requirements are implemented and documented; exporter requires and validates publication package |
| D-09 | Legacy compatibility | v1.0/v1.1/v1.2 behavior and `sermon-presentation/v1` readers remain intact; no historical package/article/URL/articleId/metadata/chronology migration |
| D-10 | Stage F disabled | v1.3 non-dry-run remains fail-closed even with `--allow-write`; Stage F is disabled in code/docs; current production routes/defaults unchanged |
| D-11 | Reproducible verification | Independently rerun or otherwise verify relevant full/focused tests, CLI help, compile/syntax and `git diff --check`; report exact commands, exit codes and counts |
| D-12 | Workspace/chronology/side effects | Exact roots/branches/HEAD; construction dirty lineage and canonical dirty lineage preserved; only bounded write-set changed; no staging/commit/push/merge/reset/clean/rebase/build/NAS/production import/deploy/notification/dependency change |

Any D-row not independently evidenced must be `BLOCKED` or `FAIL`, not inferred PASS.

## 6. Critical checks

- Confirm Website `publish-contract --mode publish --allow-write` is still blocked by the actual v1.3 consumer. Existing focused test `V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f` is relevant, but inspect the code as well.
- Confirm v1.3 package-bound Share author comes from package metadata and cannot be replaced by the legacy Ronnie fallback.
- Confirm v1.3 Share direct importer still independently validates package, content root, source path identity and metadata, and that Stage C F-01/F-02 protections did not regress.
- Confirm current legacy production routes remain as they were before Stage F and are labeled as compatibility routes in docs.
- Confirm Share cannot access NAS archive paths; Sermon archive remains protected append-only.
- Confirm no fidelity rule was copied/relaxed or changed by Stage D.
- Recompute schema/helper/plan/report SHA values and verify Website/Sermon mirror equality.
- Verify Stage E was not executed and Stage F remains disabled.

## 7. Prohibited actions

- No implementation, test, schema, fixture, documentation or status/index edits.
- No production import/export, raw/processed/posts writes, Astro build, deployment, notification/email, dependency install/upgrade.
- No NAS probe/read/write/archive.
- No Git staging, commit, push, merge, reset, clean, rebase, amend or branch changes.
- No Stage E synthetic E2E execution or Stage F enablement.
- No changes to canonical worktrees.

## 8. Audit report requirements

Write only the designated `STAGE_D_AUDIT_REPORT.md`. Include:

1. Verdict: `PASS`, `PASS_WITH_FINDINGS`, `FAIL` or `BLOCKED`.
2. D-01..D-12 complete result table, one row each, with evidence paths/lines, command outputs, hashes or precise findings.
3. Documentation conflict matrix findings, including unresolved out-of-write-set historical references if material.
4. Actual CLI/consumer/producer code review and Stage F fail-closed result.
5. Test commands, exact counts and exit codes.
6. Exact workspace IDs/roots/branches/HEAD, staged/unstaged/untracked status and canonical worktree read-only verification.
7. Explicit statement of every file written by Auditor; it must be exactly the designated report.
8. Explicit confirmation of prohibited side effects not performed.
9. Any residual risks or non-blocking findings, with threat model and re-evaluation triggers.
10. Preserve prior FAIL/BLOCKED/PASS chronology; do not rewrite prior evidence.

Stop after writing the audit report. Return the report path and SHA-256 to Master. Do not accept Stage D or start Stage E/F.