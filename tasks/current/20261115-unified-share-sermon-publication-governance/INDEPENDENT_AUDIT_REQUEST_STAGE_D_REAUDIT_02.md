# Stage D Remediation 02 — Independent Re-Audit Request

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR` (not Master)
- Re-audit target: Website consumer remediation for `D07-F01-R01`
- Website construction workspace:
  `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Sole permitted report write:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_REAUDIT_02_REPORT.md`

## 1. Authority and required fresh reads

First call `open_current_workspace`; then open and confirm the exact Website construction workspace above. Open the other three exact workspaces for read-only comparison:
- Sermon construction: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Website canonical: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Sermon canonical Owner: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`

Fresh-read:
- Root/project `AGENTS.md`, Website `STATUS.md`, Website `docs/tasks/current.md`, and the task handoff protocol.
- Canonical Sermon Owner `DESIGN.md` and the frozen Stage D implementation plan.
- Stage D implementation report, Remediation 01 report, this Remediation 02 task, and Remediation 02 report.
- Original Stage D FAIL report and Stage D Remediation 01 Re-Audit FAIL report.
- Actual current implementation and tests, not only the reports:
  - `scripts/consume_publication_package.py::v13_source_selector`
  - `scripts/content_workflow.py::publish`
  - `scripts/import_sermons.py::resolve_folder` and `main`
  - `scripts/tests/test_content_workflow_v13_share.py`
  - `scripts/tests/test_import_sermon_source_identity.py`
- Recompute SHA-256 for all relevant frozen and current reports/plans and confirm the original FAIL reports remain unchanged.

## 2. Primary audit proposition — D07-F01-R01

Independently determine whether package-derived folder identity, caller folder identity, and the importer-resolved final directory identity are now the same.

Specifically verify:
1. The package-bound prepublish source folder is resolved against the configured Website raw Sermon root.
2. A package-bound in-root symlink alias (for example `package-bound-alias -> real-sermon`) is rejected even when caller `--folder` exactly equals the alias string.
3. Rejection occurs after package validation but before Sermon renderer or importer dispatch.
4. The normal canonical folder still passes the workflow's package-bound checks.
5. Wrong existing folder and missing caller folder remain rejected before renderer/importer.
6. The lower-level v1.3 workflow passes the canonical expected source directory to `import_sermons.py`, not merely a lexical folder name.
7. Importer entry independently checks the selected folder against the expected canonical directory before its presentation gate.
8. Importer rejects:
   - the selected in-root symlink alias;
   - a different real directory that is still within the raw Sermon intake;
   - an expected source path that is itself a symlink or is outside the direct-child intake boundary.
9. Importer accepts the correct canonical folder when it matches the expected canonical directory.
10. Package-aware iteration cannot select a symlink alias as the source directory in preference to the canonical folder.
11. Legacy/no-package v1.2 behavior remains compatible and does not accidentally receive or require the v1.3-only expected-source argument.
12. Assess whether any path-based TOCTOU residual remains and state its exact threat-model boundary. Do not infer race-free security from canonical path string comparison alone.

## 3. Required independent adversarial verification

Use isolated temporary fixtures only. Reproduce the exact Re-Audit 01 adversarial shape:
- package source: `data/raw/教会讲道/package-bound-alias`;
- `package-bound-alias` is an in-root symlink to `real-sermon`;
- caller provides `--folder package-bound-alias`.

Capture subprocess dispatch evidence proving the workflow rejects before renderer/importer. Separately exercise the importer entry path with an alias present at importer entry (representing a link introduced after workflow validation); prove the importer rejects before invoking the presentation gate. Test an in-root different-real-folder mismatch and the canonical positive case.

Do not modify the source implementation or tests. If a test exposes a defect, record it and return FAIL; do not repair it.

## 4. Regression and boundary verification

Independently run or verify reproducibly:
- Remediation-focused workflow/importer tests.
- Stage C/v1.3 focused suite.
- Legacy compatibility suite.
- Full Website Python suite.
- Python compile and `git diff --check`.
- Stage F negative test with `--allow-write=True`.
- CLI help where relevant.

Spot-check frozen Stage D D-01..D-06 and D-08..D-12 for regression, with particular attention to:
- unchanged producer/Owner schemas and contract mirrors;
- Share/Sermon profile separation and legacy compatibility;
- no changes to fidelity state machine or Project Bible authority;
- Stage F still disabled in code/docs, including `--allow-write` not overriding the block;
- no production/default route changes.

## 5. Worktree, chronology and side-effect controls

Capture exact workspace roots, branches, HEADs, staged/unstaged/untracked state. Compare against the pre-existing dirty lineage described in prior reports. Confirm no canonical or Sermon worktree mutation. Preserve:
- original Stage D FAIL / D07-F01;
- Remediation 01 implementation;
- Re-Audit 01 FAIL / D07-F01-R01;
- Remediation 02 implementation and this new verdict.

Auditor is read-only except the single designated report file. Do not edit source, tests, plans, implementation/remediation reports, STATUS, task indexes, schemas, contracts, fixtures, or any other files.

Do not perform Git staging/commit/push/merge/reset/clean/rebase/amend, production import, content mutation, NAS, build, deployment, notification, dependency installation/upgrade, Stage E execution, or Stage F enablement.

## 6. Verdict and report

Write only:
`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_REAUDIT_02_REPORT.md`

The report must include:
- Overall verdict: PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED.
- D07-F01-R01 proposition-by-proposition results and exact source line evidence.
- Adversarial reproduction and no-dispatch proof.
- Importer entry check evidence and positive/mismatch cases.
- Regression commands, counts, exit codes and any corrected command invocation.
- Residual TOCTOU assessment and threat model.
- Recomputed SHA table.
- Workspace identities, dirty lineage, exact Auditor write-set and prohibited side effects.
- Explicit Stage E NOT STARTED / Stage F DISABLED disposition.

Read back the report and recompute its SHA-256. Stop after verifying the report. Auditor must not accept Stage D or authorize Stage E/F; return the result to Master.
