# Stage F Implementation Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: F — v1.3 production entry-point activation
- Status: `IMPLEMENTATION_COMPLETE / INDEPENDENT_AUDIT_PENDING / PRODUCTION_RELEASE_NOT_STARTED`
- Date: 2026-11-20
- Owner authorization: explicit Stage F authorization received 2026-11-20.
- Frozen plan Revision 01: `STAGE_F_ACTIVATION_PLAN.md`
- Frozen plan SHA-256: `46fb82aabb7f2e248b946e010d757e1b5bfc01aa42338af4d751c9e4bf4e9b3f`
- Plan mirror in Website and Sermon construction worktrees: SHA-256 matches exactly.
- Fixed acceptance denominator: F-01 through F-11; unchanged.

## 1. Authority and implementation scope

Stage E was independently audited and formally accepted by Master as `PASS_WITH_FINDINGS` on 2026-11-20. Its report SHA-256 is `6121e3b95145f93c79792a2f411fbc7d63b4f06ed8a4b3d589afea952b7131d3`. E-F01 is CLOSED. E-AUDIT-01 (the integrated synthetic E2E final workflow dispatch uses a stub, not the real importer) remains a non-blocking finding and is not rewritten.

The initial Stage F plan draft SHA-256 `4030b9ac8918cf0be7c8622c69d535863bb8310d514768951f660cf761d5ca7e` was superseded by Revision 01. Fresh inspection found both Sermon producer entrypoints still defaulted to v1.2 and found that write authorization needed to be propagated and enforced at each lower-level boundary. The fixed F-01..F-11 denominator did not change. The initial Website consumer guard edits had begun under the draft; the producer-default and layered authorization additions were incorporated into Revision 01 before their implementation. No production side effects occurred.

Implementation was confined to the two construction worktrees:
- Website: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Sermon: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`

Both canonical worktrees remained read-only.

## 2. Implementation changes

### 2.1 Sermon producer defaults

Changed only the new-content contract-version defaults:
- `scripts/build_website_publication_package.py`: default `--contract-version` changed from `1.2` to `1.3`.
- `scripts/generate_prepublish_md.py`: parser default and missing-attribute fallback changed from `1.2` to `1.3`.

Explicit `--contract-version 1.2` remains supported for identified legacy/in-flight compatibility. No producer business logic, fidelity state machine, Project Bible rule, schema, package contract, or exporter identity logic was changed.

Regression coverage:
- New default package generation for both Share and Sermon is v1.3.
- Explicit v1.2 package-builder compatibility remains.
- generate-prepublish command fallback now defaults to v1.3; explicit legacy v1.2 coverage remains.

### 2.2 Website v1.3 activation and layered write authorization

- `scripts/consume_publication_package.py`: removed only the pre-Stage-F v1.3 publish block. `publish` still requires `--allow-write` and passes it to the workflow.
- `scripts/content_workflow.py`: removed only the v1.3 dry-run-only block. Direct v1.3 package writes require `--allow-write`; the workflow propagates that authorization to the importer. Plan/dry-run remain read-only.
- `scripts/import_shares.py`: direct v1.3 writes require `--allow-write`, a package, content root and presentation artifact. Supplying package/content-root without the presentation artifact fails closed. Package/source/metadata/artifact validation and Share no-archive semantics remain enforced.
- `scripts/import_sermons.py`: package-aware v1.3 calls require `--allow-write`, package, content root and expected canonical source folder. The importer independently reruns the v1.3 package/schema validator and checks prepublish speaker/date/category/contentType, exact package-bound canonical source folder, and exact package-bound presentation artifact before the renderer/write path. Legacy direct calls that do not claim v1.3 package identity retain their existing compatibility behavior.
- `scripts/content_workflow.py` passes the exact v1.3 package/content-root identity and explicit write authorization to the Sermon importer.

No v1.3 direct write path can bypass the explicit authorization at consumer, workflow, or importer boundary. No schemas or package contracts changed.

### 2.3 Documentation and chronology

Updated:
- Website construction: `STATUS.md`, `docs/tasks/current.md`, task `TASK_INDEX.md`.
- Sermon construction: `AGENTS.md`, `STATUS.md`, `tasks/current/index.md`, `docs/end-to-end-content-publishing-workflow.md`, `docs/chinese-to-prepublish-md-workflow.md`, `docs/workflows/sermon-publication-presentation-readiness.md`.
- Exact Stage F plan mirrored to both construction worktrees with identical SHA-256.

Both projects now distinguish construction implementation from canonical production cutover. Historical FAIL/BLOCKED/PARTIAL/PASS chronology and Stage E finding E-AUDIT-01 remain preserved.

## 3. Fixed denominator F-01..F-11 evidence

| ID | Implementation evidence | Master implementation status |
|---|---|---|
| F-01 Authority and prerequisites | Stage E accepted report readback/SHA; Owner authorization; Revision 01 plan readback/SHA; exact Website/Sermon construction and canonical workspaces opened | EVIDENCED |
| F-02 Producer production default | Both producer entrypoints default to v1.3; explicit v1.2 remains; producer regression tests and full Sermon suite pass | EVIDENCED |
| F-03 Website consumer activation | `publish-contract --mode publish` rejects missing `--allow-write`; authorized command passes it into workflow; workflow requires and forwards it | EVIDENCED |
| F-04 Layered write-path integrity | Direct workflow, Share importer and Sermon importer require authorization for v1.3 writes; missing package/presentation/source/artifact and bypass cases fail before writes | EVIDENCED |
| F-05 Sermon source and archive safety | Workflow and direct importer validate package/schema, metadata, source folder and artifact; archive status is schema/package-bound; no NAS archive operation was run | EVIDENCED |
| F-06 Share no-archive semantics | Share package schema and importer retain `not_applicable` / `SHARE_ARCHIVE_NOT_APPLICABLE`; no NAS path is resolved or accessed | EVIDENCED |
| F-07 Legacy compatibility | Explicit v1.2 producer override and existing v1.0/v1.1/v1.2 compatibility suites pass; no historical content/package migration | EVIDENCED |
| F-08 Reproducible verification | Full and focused Python suites, Node structure suite, tag fixtures, CLI help, Python compilation and diff checks pass; dispatch stubs disclosed | EVIDENCED |
| F-09 Documentation and chronology | Both construction projects' AGENTS/status/current/task index/workflow docs updated; historical chronology and E-AUDIT-01 retained | EVIDENCED |
| F-10 Production cutover safety | No real article import, NAS, email/notification, subscription action, production build/deploy, or historical content mutation | EVIDENCED |
| F-11 Repository/release disposition | Exact branches/HEADs/dirty counts inventoried; all four worktrees have staged=0; canonical worktrees untouched; no Git history operation | EVIDENCED |

These are Master implementation evidence statements, not a substitute for the independent Auditor's verdict.

## 4. Verification results

### Website construction worktree

- Full Python suite: **305/305 PASS**
- Stage F focused suite (`test_consume_publication_package_v13`, `test_content_workflow_v13_share`, `test_import_share_presentation`, `test_import_sermon_source_identity`, `test_validate_publication_package_v13`): **94/94 PASS**
- Node Sermon rendered-structure suite: **21/21 PASS**
- Tag pipeline browser fixtures: **27/27 PASS**
- Python compilation: PASS
- CLI help: `publish`, `publish-contract`, Share importer, Sermon importer PASS
- `git diff --check`: PASS

The full Python suite includes positive/negative v1.3 schema fixtures, package identity, source identity, archive semantics, legacy behavior and workflow safety tests.

### Sermon construction worktree

- Full Python suite: **60/60 PASS**
- Producer-focused suite (`test_build_website_publication_package`, `test_generate_prepublish_contract`, `test_unified_publication_producer_stage_b`): **28/28 PASS**
- Python compilation: PASS
- `git diff --check`: PASS

### Test execution disclosure

- All write-path tests used temporary directories.
- Direct Share and Sermon importer tests exercise temporary output paths.
- Workflow-to-importer dispatch tests use mocked subprocess dispatch; they do not claim to be a full real production import.
- Package-validator calls inside focused Sermon importer tests are mocked where explicitly stated; the real package validator is independently exercised by the Website v1.3 package validation suite.
- No test used a production article, canonical intake directory, NAS archive, email, subscription, or notification endpoint.

## 5. Git and workspace inventory (fresh)

| Worktree | Branch | HEAD | Porcelain | Staged | Unstaged | Untracked |
|---|---|---|---:|---:|---:|---:|
| Website construction | `task/unified-share-sermon-publication-stage-a-20261116` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | 28 | 0 | 13 | 15 |
| Sermon construction | `task/unified-share-sermon-publication-stage-a-20261116` | `812ace500102bac54cb54cb0fa2249341118a3da` | 27 | 0 | 20 | 7 |
| Website canonical | `main` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | 4 | 0 | 4 | 0 |
| Sermon canonical | `master` | `812ace500102bac54cb54cb0fa2249341118a3da` | 41 | 0 | 15 | 26 |

Website canonical's four pre-existing dirty files remain:
- `AGENTS.md`
- `STATUS.md`
- `docs/task-handoff-protocol.md`
- `docs/tasks/current.md`

Sermon canonical's 41 pre-existing dirty entries (15 modified, 26 untracked) remain untouched. It is still two commits ahead of `origin/master`, as observed at the time of this audit; no Git operation was run.

At the Stage E baseline, Website construction had 28 dirty entries, Sermon construction had 26, Website canonical had 4, and Sermon canonical had 41. Current construction counts are 28 and 27; the additional Sermon construction untracked entry is the mirrored Stage F activation plan. Existing dirty Stage A–E files were not staged or committed.

No `git add`, commit, push, merge, reset, clean, rebase, amend, or deployment command was run. Construction HEADs did not move.

## 6. Production boundary and remaining sequence

Stage F implementation is ready for independent audit only. **Canonical production routes/defaults have not been switched.** v1.3 production capability changes exist only in construction worktrees.

Not performed:
- no real Share/Sermon publication/import;
- no NAS probe/read/write/archive;
- no TTS generation, email, notification or subscription action;
- no Astro production build/deploy;
- no Git staging/commit/push/merge or other history operation.

Next:
1. Independent Auditor performs read-only Stage F audit against frozen F-01..F-11.
2. Auditor writes only `independent-audit/STAGE_F_AUDIT_REPORT.md`, readbacks and verifies SHA-256, then stops.
3. Master independently accepts/rejects the implementation.
4. Only after acceptance, execute the bounded repository release and production deployment described in the frozen plan. This deploys the v1.3 capability only; it does not publish a real article or execute NAS/email/notification operations.
