# Independent Re-Audit Request — Stage D Remediation 01

Role: `INDEPENDENT_AUDITOR` (not Master)
Task: `20261115-unified-share-sermon-publication-governance`
Stage: D
Audit target: Master Remediation 01 for finding `D07-F01`
Date: 2026-11-18

## 1. Exact workspaces

Open in this order:
1. Call `open_current_workspace`.
2. Open Website construction:
   `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
3. Open Sermon construction:
   `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
4. Open Website canonical read-only:
   `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
5. Open Sermon canonical read-only:
   `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`

If the configured root differs, switch to the exact target. Preserve all existing dirty/untracked lineage. Do not write to either canonical worktree or the Sermon construction worktree.

## 2. Fresh-read authority and evidence

Website construction:
- `AGENTS.md`
- `STATUS.md`
- `docs/tasks/current.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_D_IMPLEMENTATION_PLAN.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_D_IMPLEMENTATION_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_D_REMEDIATION_01_REPORT.md`
- Original audit: `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_AUDIT_REPORT.md`
- `scripts/content_workflow.py`
- `scripts/consume_publication_package.py`
- `scripts/validate_publication_package_v13.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- Stage C Re-Audit 04 report and Stage D frozen contracts as needed.

Sermon construction:
- `AGENTS.md`, `STATUS.md`, `tasks/current/index.md`
- canonical Sermon Owner `DESIGN.md` at the formal authority path
- mirrored frozen Stage D plan and implementation report
- producer scripts/tests only as needed to verify no unintended change.

Recompute hashes for the frozen plan, original Stage D implementation report, original Auditor FAIL report, and Remediation 01 report. Verify that the original audit report remains unchanged.

## 3. Required audit propositions

### A. D07-F01 remediation — mandatory

1. Confirm the package-aware Sermon workflow reads the package-bound prepublish file only after the v1.3 package validator passes.
2. Confirm the frontmatter `source` is parsed and resolved through the existing `v13_source_selector`.
3. Confirm selector validation requires the source to be within the Website raw Sermon intake and that the resolved folder is an existing directory.
4. Confirm caller `--folder` must exactly equal the package-derived folder.
5. Confirm missing or mismatched `--folder` fails closed with `V13_PACKAGE_IDENTITY_MISMATCH`.
6. Confirm both failures occur before the Sermon renderer and importer subprocess dispatch.
7. Confirm package-bound prepublish SHA, metadata, presentation artifact/manifest and other v1.3 checks remain enforced and were not weakened.
8. Confirm the unified `publish-contract` path still derives the expected source folder and remains compatible.

### B. Required test behavior

Independently inspect and rerun the relevant focused tests. Verify:
- correct package-bound folder: PASS; package validator, renderer gate and dry-run importer dispatch occur;
- wrong existing folder: rejected before renderer/importer;
- missing caller folder: rejected before renderer/importer;
- legacy/v1.2 Sermon route without publication package: unchanged and still dispatches via the existing presentation gate/importer route.

The mismatch/missing tests must prove that no renderer or importer call occurred, not merely assert an error string.

### C. Regression / stage boundary

- Spot-check D-01..D-06 and D-08..D-12 against the original audit report and current evidence; identify any regression or scope drift.
- Verify Stage F non-dry-run remains blocked even with `--allow-write`.
- Verify Stage E remains NOT STARTED and Stage F remains DISABLED.
- Verify current production routes/defaults remain unchanged.
- Verify Stage C historical FAIL chronology and the original Stage D FAIL report remain intact.

### D. Worktree and side effects

- Confirm exact roots, branches, HEADs, staged/unstaged/untracked status.
- Website construction may contain the pre-existing Stage A/C/D dirty lineage plus bounded Remediation 01 changes.
- Sermon construction dirty lineage and Sermon canonical dirty/untracked lineage must be preserved and not attributed to this remediation.
- Website canonical must remain clean and untouched.
- No Git staging/commit/push/merge/reset/clean/rebase/amend.
- No production import, content mutation, Astro build, deployment, NAS, email/notification or dependency install/upgrade.
- Only isolated test fixtures may be written by tests.

## 4. Verdict rules

Return one overall verdict:
- `PASS`: D07-F01 is fully closed, required tests/evidence pass, no mandatory regression.
- `PASS_WITH_FINDINGS`: blocker closed but bounded non-blocking findings remain; explain each.
- `FAIL`: D07-F01 remains exploitable or a mandatory proposition regressed.
- `BLOCKED`: authority/evidence/workspace access is insufficient.

Do not accept Stage D on behalf of Master. Do not start Stage E or Stage F.

## 5. Sole permitted write

Write exactly one file, only in Website construction:
`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_REAUDIT_01_REPORT.md`

Do not modify source, tests, plan, implementation report, remediation report, STATUS, task indexes, schemas, contracts, canonical worktrees or Sermon worktree. Do not overwrite the original `STAGE_D_AUDIT_REPORT.md`.

The report must include:
- overall verdict and D07-F01 disposition;
- explicit test commands/results/counts;
- correct/mismatch/missing/legacy test evidence;
- source binding code references and fail-before-dispatch evidence;
- D-01..D-06 and D-08..D-12 regression spot-check table;
- recomputed hashes;
- exact workspace/Git status and write-set;
- explicit statement of prohibited side effects not performed.

Stop after writing and readback-verifying the sole report. Return its path and SHA-256 to Master.

Stage D remains FAIL / NOT ACCEPTED until Master makes a separate final acceptance decision. Stage E remains NOT STARTED; Stage F remains DISABLED.
