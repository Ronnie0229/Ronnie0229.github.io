# Stage F Independent Audit Request

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR` (not Master; read-only)
- Date: 2026-11-20
- Owner authorization: Stage F explicitly authorized by Owner on 2026-11-20.
- Exact primary workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Exact comparison workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Canonical Website comparison (read-only): `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Canonical Sermon comparison (read-only): `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`
- Frozen Stage F plan: `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_F_ACTIVATION_PLAN.md`
- Frozen plan SHA-256: `46fb82aabb7f2e248b946e010d757e1b5bfc01aa42338af4d751c9e4bf4e9b3f`
- Master implementation report: `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_F_IMPLEMENTATION_REPORT.md`
- Implementation report SHA-256: `3e6a8c5e838dfd66ae1eb47768e4860e7c4cbb202accf8adb571d507ee9cf5dd`
- Fixed denominator: F-01..F-11; do not add, remove, combine, split or redefine any item.
- Expected report path (the only permitted write): `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_F_AUDIT_REPORT.md`

## 1. Workspace and authority procedure

1. First call `open_current_workspace`.
2. Open and confirm the exact Website construction workspace above. If current root differs, switch immediately.
3. Open the exact Sermon construction workspace and both canonical comparison workspaces above.
4. Fresh-read the primary workspace `AGENTS.md`, this request, frozen Stage F plan, Master implementation report, Stage E accepted independent report, and task `TASK_INDEX.md`.
5. Fresh-read Sermon construction `AGENTS.md`, producer scripts/tests, workflow docs/status/index, and the byte-identical Stage F plan mirror.
6. Treat canonical worktrees as read-only. Do not attribute or modify their existing dirty files.

## 2. Mandatory audit scope

Independently assess every fixed item F-01..F-11 against the frozen plan. Do not rely only on the Master report.

- F-01 Authority/prerequisites: verify Stage E Master acceptance and Auditor report SHA; Owner authorization; plan/report readback and SHA; exact workspaces.
- F-02 Producer default: verify `build_website_publication_package.py` and `generate_prepublish_md.py` default/fallback to v1.3; explicit v1.2 override remains; verify no producer fidelity/business logic or contract was changed.
- F-03 Consumer activation: verify `publish-contract --mode publish` rejects missing `--allow-write`; authorized mode passes it into the workflow; workflow requires and forwards it; plan/dry-run remain read-only.
- F-04 Layered write-path integrity: inspect direct workflow, Share importer and Sermon importer. Verify v1.3 writes require explicit `--allow-write` at every layer; missing package/content-root/presentation/source/artifact and mismatched package/source/metadata cases fail before writes; direct calls cannot bypass the package or authorization gates.
- F-05 Sermon source/archive: verify the importer independently validates package/schema, package-bound prepublish metadata, exact canonical source folder, exact presentation artifact and archive semantics; verify pending archive states do not masquerade as archived. Do not access NAS.
- F-06 Share no-archive: verify `archive_status=not_applicable` and `SHARE_ARCHIVE_NOT_APPLICABLE`; ensure no Share path resolves or accesses the NAS sermon archive.
- F-07 Legacy compatibility: verify existing v1.0/v1.1/v1.2 paths and tests remain intact; explicit v1.2 producer override works; no historical package/content migration occurred.
- F-08 Verification: independently run relevant focused and full Python suites in both construction worktrees, Website Node rendered-structure suite, tag fixtures, CLI help, syntax/compile and `git diff --check`. Verify reported counts. Any workflow dispatch or validator stub must remain explicitly labelled; do not treat it as a real production import.
- F-09 Documentation/chronology: verify both projects' current AGENTS/status/index/workflow documentation accurately distinguishes construction implementation from production cutover; Stage E E-F01 closure and E-AUDIT-01 finding remain preserved; historical FAIL/BLOCKED/PARTIAL/PASS chronology is not rewritten.
- F-10 Production side effects: verify no real article import, NAS operation, TTS, email/notification, subscription action, production build/deploy, or historical content mutation occurred.
- F-11 Repository/release disposition: independently inventory exact branch, HEAD, staged/unstaged/untracked counts for both construction and both canonical worktrees. Verify canonical worktrees were not modified by Stage F, all worktrees have staged=0, construction HEADs unchanged, and no Git history or deployment operation occurred. Reconcile the Website construction 28-entry baseline, Sermon construction 26-entry baseline, Website canonical 4-entry baseline and Sermon canonical 41-entry baseline recorded at Stage E.

## 3. Verification guidance and limits

The Master report discloses:
- Website Python 305/305; Stage F focused 94/94.
- Sermon Python 60/60; producer-focused 28/28.
- Website Node 21/21; tag fixtures 27/27.
- Python compilation, CLI help and both construction `git diff --check` PASS.
- Direct Share/Sermon importer tests use temporary directories.
- Workflow-to-importer dispatch tests use mocked subprocess dispatch; these are not full real production imports.
- Package-validator calls in focused Sermon importer tests are mocked where stated; real package validation is independently covered by the Website v1.3 package validation suite.

You may run read-only tests and inspect Git status/diffs. Test-generated files must remain in temporary directories or normal disposable caches; do not modify source/status/index/plan files. No real production import or NAS operation is permitted.

## 4. Write and stop contract

- Only permitted write: `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_F_AUDIT_REPORT.md`.
- Report must preserve fixed denominator F-01..F-11, list evidence per item, record PASS/FAIL/BLOCKED/PASS_WITH_FINDINGS, and give an overall verdict.
- If any failure is found, report it and stop; do not implement remediation.
- After writing, read the report back, calculate and record its SHA-256, verify the readback, then stop and return control to Master.
- Do not edit code, plan, implementation report, AGENTS, STATUS, current task index, task index, or any other file.
- Do not run Git staging/commit/push/merge/reset/clean/rebase/amend.
- Do not run Astro production build/deploy or any publication operation.
- Do not access NAS, real article content, email, notification, subscription, TTS provider or GitHub workflow.
- Do not accept Stage F or initiate the production release/cutover. Those are Master-only after independent audit.

