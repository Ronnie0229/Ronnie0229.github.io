# Stage F — v1.3 Production Entry-Point Activation Plan

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: F — Production enablement
- Status: `FROZEN_REVISION_01 / IMPLEMENTATION_IN_PROGRESS`
- Date: 2026-11-20
- Plan revision chronology: initial plan draft SHA-256 `4030b9ac8918cf0be7c8622c69d535863bb8310d514768951f660cf761d5ca7e` was superseded before implementation after fresh inspection identified (a) both Sermon producer entrypoints still defaulting to v1.2 and (b) lower-level workflow/importer write paths needing propagated `--allow-write`. This revision expands only F-02/F-03/F-04 within the original fixed F-01..F-11 denominator. Initial Website consumer guard changes had begun under the initial draft; the producer-default and layered write-authorization additions were incorporated before their implementation. No production side effects occurred.
- Final revision SHA-256 is recorded in the Stage F implementation report and current status records; remaining implementation and audit must follow this frozen revision.
- Website construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Sermon construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Website canonical: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目` (read-only comparison / later deployment target)
- Sermon canonical: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理` (read-only comparison)
- Canonical design authority: Sermon Owner `tasks/current/20261115-unified-share-sermon-publication-governance/DESIGN.md`, SHA-256 `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f`
- Prerequisites: Stage A/B PASS; Stage C/D/E PASS_WITH_FINDINGS formally accepted by Master; Owner explicitly authorized Stage F on 2026-11-20.

## 1. Goal and exact interpretation

Enable the already implemented `website-publication-package/v1.3` + `content-presentation/v1` controlled production entrypoint for new Share and Sermon content. This is a capability/default-route cutover, not authorization to publish any particular article.

After activation:
- New Share and Sermon publication work must use the v1.3 package consumer and its complete producer, identity, fidelity, Project Bible, presentation, rendered structure, metadata, archive, and source-binding gates.
- Share retains `archive_status=not_applicable` and must never access the NAS sermon archive.
- Sermon retains protected append-only NAS archive semantics; actual archive writes remain part of a separately identified exact publication object's authorized publication transaction.
- Historical v1.0/v1.1/v1.2 packages and already in-flight legacy work retain their frozen compatibility behavior; no historical package or post is rewritten.
- The old v1.2/current compatibility routes are not to be used for new content after the v1.3 cutover. They remain available only for explicitly identified legacy/in-flight compatibility cases.

Stage F does not publish a real Share or Sermon object. It enables the production-capable route. A later real article still requires an exact frozen publication object and its ordinary publication authorization / Publication Fast Lane.

## 2. Frozen acceptance denominator

| ID | Mandatory proposition | Required evidence |
|---|---|---|
| F-01 | Authority and prerequisites | Fresh-read Stage E accepted report, this frozen plan, Owner authorization, and both construction workspaces; no stale or canonical dirty worktree used as an implementation target |
| F-02 | Producer production default | Sermon producer package builder defaults to v1.3 for new Share/Sermon objects; explicit v1.2 remains available for identified legacy/in-flight work; no producer business logic/fidelity rule is forked or weakened |
| F-03 | Website consumer activation | v1.3 `publish-contract --mode publish --allow-write` dispatches to the package-bound workflow; explicit write authorization is propagated and required at consumer, workflow, and importer boundaries; plan/dry-run remain read-only |
| F-04 | Layered write-path integrity | Direct calls to workflow, Share importer, or Sermon importer cannot bypass explicit `--allow-write`; each v1.3 write boundary independently requires package/source/metadata/presentation/artifact/rendered-structure/profile/archive evidence before writes |
| F-05 | Sermon source and archive safety | The v1.3 workflow and direct importer independently bind the canonical source folder, package/schema, prepublish metadata, presentation artifact and archive semantics; sermon archive remains append-only and pending states never masquerade as archived |
| F-06 | Share no-archive semantics | Share package/result remains `not_applicable` / `SHARE_ARCHIVE_NOT_APPLICABLE`; no NAS archive path is resolved or accessed |
| F-07 | Legacy compatibility | Existing v1.0/v1.1/v1.2 compatibility tests and legacy publication behavior remain unchanged; no historical content/package migration |
| F-08 | Reproducible verification | Targeted tests, relevant full suites, CLI help, Python/Node syntax, schema checks, and `git diff --check` pass; any test stub is explicitly labelled |
| F-09 | Documentation and chronology | Both projects' current workflow/status/index state accurately describes v1.3 as the new-content production route while preserving all historical FAIL/BLOCKED/PARTIAL/PASS chronology and Stage E finding E-AUDIT-01 |
| F-10 | Production cutover safety | No real article import, NAS operation, email/notification, subscription action, or historical content mutation in this activation implementation; production deployment occurs only after independent Stage F audit and Master acceptance |
| F-11 | Repository and release disposition | Exact repositories/branches/HEADs and task-local/unrelated dirty state inventoried; no unrelated dirty changes staged; commit/push/deploy decisions recorded separately and only for the bounded Stage F release |

Overall Stage F implementation may be submitted for independent audit only when F-01..F-11 are evidenced. Fixed denominator cannot be reduced or redefined after execution starts.

## 3. Bounded implementation write-set

### Website construction worktree

Expected minimal changes:
- `scripts/consume_publication_package.py`: remove only the pre-Stage-F v1.3 publish hard block; retain mandatory `--allow-write` and all package/structure validation; propagate the write authorization to workflow.
- `scripts/content_workflow.py`: remove only the pre-Stage-F v1.3 dry-run-only hard block; require and propagate `--allow-write` for v1.3 writes; retain package/source/metadata/folder identity validation and mandatory Share/Sermon profile gates.
- `scripts/import_shares.py`: remove only the pre-Stage-F v1.3 dry-run-only hard block; require `--allow-write` for v1.3 direct writes; retain mandatory package/schema/source/metadata/artifact validation and Share no-archive behavior.
- `scripts/content_workflow.py` + `scripts/import_sermons.py`: pass the exact v1.3 package/content-root identity and explicit write authorization into the Sermon importer; importer independently requires `--allow-write` and validates package-bound source folder, package/schema, prepublish metadata, presentation artifact and archive semantics before any write. Preserve the existing v1.2/legacy direct route only for explicitly legacy calls that do not claim v1.3 package identity.
- Corresponding focused tests: isolated temporary-fixture dispatch/guard tests prove write-capable dispatch is possible only through valid package-bound v1.3 inputs and explicit `--allow-write` at every layer; direct workflow/Share/Sermon importer v1.3 invocation without write authorization or package identity fails before writes. No production directories are written.
- Website `STATUS.md`, `docs/tasks/current.md`, task `TASK_INDEX.md`, implementation report and independent audit request.

No changes to schemas, package contracts, Project Bible, fidelity state machine, source extraction, presentation transformation allowlist, renderer semantics, article data, or historical records.

### Sermon construction worktree

Bounded producer default change plus documentation/status alignment:
- `scripts/build_website_publication_package.py` — default contract version only (`1.2` → `1.3`); explicit `--contract-version 1.2` remains supported.
- `scripts/generate_prepublish_md.py` — contract-version parser default and missing-attribute fallback only (`1.2` → `1.3`); explicit `--contract-version 1.2` remains supported.
- `scripts/tests/test_build_website_publication_package.py` and relevant `generate_prepublish_md` tests — assert new default and explicit legacy v1.2 compatibility.
- `AGENTS.md`
- `docs/end-to-end-content-publishing-workflow.md`
- `docs/chinese-to-prepublish-md-workflow.md`
- `docs/workflows/sermon-publication-presentation-readiness.md`
- `STATUS.md`
- `tasks/current/index.md`
- task `TASK_INDEX.md` / Stage F evidence mirror if present

Fresh inspection found both Stage B producer entrypoints still default `--contract-version` to `1.2`: `build_website_publication_package.py` and `generate_prepublish_md.py` (including its fallback). This fails F-02 for new-content default routing although the exporter requires v1.3. Bounded producer change is therefore included: change only both new-content defaults/fallbacks to `1.3`; preserve explicit `--contract-version 1.2` compatibility and add regression coverage proving both defaults and the legacy override. Do not alter producer business/fidelity logic or contract.

### Canonical worktrees

Both canonical Website and Sermon worktrees are read-only during Stage F implementation and audit. Do not sync, export, import, or overwrite them during this construction phase.

## 4. Explicit exclusions

- No real Share or Sermon content publication/import.
- No NAS probe/read/write/archive; no Share archive-path access.
- No TTS generation, email, notification, subscription action, or GitHub workflow dispatch.
- No Astro production build/deploy during implementation or independent audit.
- No historical article/package/registry rewrite or migration.
- No dependency installation or upgrade.
- No new service, registry, daemon, validator framework, or parallel producer.
- No Git staging/commit/push/merge/reset/clean/rebase/amend during implementation or audit.
- No writes to either canonical worktree.
- No changes to frozen schemas, package contracts, Project Bible, fidelity rules, or sermon theology.

## 5. Execution and release sequence

1. Freeze this plan and record its SHA-256.
2. Reconfirm exact construction/canonical workspace identities and dirty baselines; fresh-read all target files.
3. Implement the minimal Website write-gate cutover and bounded test updates.
4. Update Sermon producer-side workflow documentation/status to make the v1.3 new-content route explicit; preserve legacy compatibility boundaries.
5. Run the fixed F-01..F-11 verification set, including adversarial tests for package/source/metadata/artifact/archive/profile mismatch and explicit `--allow-write`.
6. Write Stage F implementation report and independent audit request; freeze hashes.
7. Stop for independent read-only Stage F audit. Auditor writes only the designated report.
8. Master independently reviews and accepts/rejects the Stage F implementation.
9. Only after acceptance, perform bounded repository release disposition and production cutover for the code capability (build, commit/push, deployment trigger and live deployment identity verification) under this explicit Stage F authorization. Do not publish any real article or run NAS/email/notification operations as part of this capability deployment.
10. Record deployment verification and final Git/repository disposition. If any production build/deploy or exact-repository authority check fails, keep Stage F implementation accepted but production cutover BLOCKED; do not bypass the gate.

## 6. Scope and overbuilding decision

- Goal alignment: Stage F is exactly the production entrypoint enablement described by the canonical design; it does not conflate capability activation with publication of an article.
- Scope: Website owns consumer/runtime write gate and deployment; Sermon owns producer workflow and fidelity/source authority. Website changes only the consumer-side guards; Sermon changes only the package-builder default to v1.3 after confirming the default-routing gap, while preserving explicit v1.2 legacy compatibility.
- Overbuilding: reuse current producer, consumer, validators, renderer and tests; change only default package version and v1.3 write guards; no new infrastructure.
- Disposition: `GOAL_ALIGNED / NO_SCOPE_DRIFT / NO_OVERBUILDING`.
