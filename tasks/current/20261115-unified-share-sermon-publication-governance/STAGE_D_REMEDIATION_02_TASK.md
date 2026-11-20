# Stage D Remediation 02 — D07-F01-R01 Canonical Sermon Folder Identity

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D
- Role: Master / Executor
- Trigger: Stage D Remediation 01 Independent Re-Audit verdict `FAIL`
- Auditor report: `independent-audit/STAGE_D_REAUDIT_01_REPORT.md`
- Auditor report SHA-256: `60181632307336e1c194581ffea095d84617cc7740ce789529b741aa45869df4`
- Frozen Stage D plan SHA-256: `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e`
- Implementation workspace: Website construction only:
  `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`

## 1. Objective

Close the single residual finding `D07-F01-R01`: an in-root Sermon directory symlink alias can pass package-bound lexical folder comparison but resolve inside the importer to a different real Sermon directory.

The package-derived source identity, caller-selected folder identity, and importer-resolved directory identity must be demonstrably identical. Reject symlink aliases before renderer/importer dispatch.

## 2. Required implementation

1. In `scripts/consume_publication_package.py::v13_source_selector`, validate the configured Sermon raw root and selected folder using strict canonical resolution. Reject a selected folder that is itself a symlink; require the resolved target to be a direct child of the resolved raw Sermon root and require its canonical basename/identity to match the package-bound folder. Preserve Share behavior.
2. In `scripts/content_workflow.py`, after package validation and package-bound prepublish parsing, derive the canonical expected Sermon directory from the same configured raw root. Reject missing, lexical mismatch, symlink, non-directory, non-direct-child, or canonical-identity mismatch before invoking the Sermon renderer or importer.
3. Pass the canonical expected source directory to `scripts/import_sermons.py` through an explicit internal expectation argument on the package-aware v1.3 path. Do not rely solely on the lexical `--folder` string.
4. In `scripts/import_sermons.py`, independently resolve the actual selected folder and compare it to the expected canonical directory when the expectation argument is present. Reject a symlink alias and any resolved mismatch before the importer presentation gate or content processing. Keep the argument optional so the legacy/v1.2 route remains compatible.
5. Keep v1.3 non-dry-run disabled. Do not alter package schemas, producer contracts, fidelity/Bible authority, Stage F boundary, or production defaults.

## 3. Mandatory regression evidence

Add focused tests proving:

- Existing correct package-bound folder still reaches renderer and dry-run importer in order.
- Existing wrong existing folder and missing caller folder still fail after package validation and before renderer/importer.
- New adversarial fixture: package binds `package-bound-alias`, that directory is an in-root symlink to `real-sermon`, and caller supplies the exact same alias. The workflow must reject it before renderer/importer; subprocess evidence must show only package validation was called.
- Direct importer resolver rejects an in-root symlink alias when a canonical expected folder is supplied, and rejects a different resolved directory even if it remains within raw intake.
- Direct importer accepts the correct canonical folder when it matches the expected canonical directory.
- No-package legacy/v1.2 Sermon route remains unchanged.
- Existing Share symlink/source identity tests remain unchanged and pass.
- Add a race-aware final check at importer entry so a symlink introduced after workflow validation is still rejected before the importer presentation gate. Do not claim full race-free filesystem security beyond the implemented checks; document any residual TOCTOU limitation accurately.

## 4. Verification

Run and record:
- Remediation-focused workflow and importer tests.
- Stage C/v1.3 focused suite.
- Legacy compatibility suite.
- Full Website Python suite.
- Python compile for changed modules/tests.
- `git diff --check`.
- Stage F negative test with `--allow-write=True`.
- CLI help if importer/workflow arguments change.

Use temporary isolated fixtures only. Do not touch real raw intake data.

## 5. Bounded write-set

Allowed Website construction files:
- `scripts/consume_publication_package.py`
- `scripts/content_workflow.py`
- `scripts/import_sermons.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- `scripts/tests/test_import_sermon_source_identity.py` (new, if needed)
- This remediation task/report, `TASK_INDEX.md`, and Website `STATUS.md` / `docs/tasks/current.md` chronology.

Do not modify canonical worktrees, Sermon construction worktree, frozen Stage D plan, original Stage D audit report, Remediation 01 report, Stage D Re-Audit 01 report, schemas/contracts/fixtures, producer code, historical articles, or unrelated files. Do not update stale Sermon-side SHA pointers in this bounded remediation; record them as a separate follow-up if still applicable.

## 6. Prohibited operations / stop boundaries

- No Git staging, commit, push, merge, reset, clean, rebase, amend, branch/worktree mutation.
- No production import, raw/processed/posts content mutation, NAS access, email/notification, Astro build, deployment, dependency installation/upgrade.
- No Stage E synthetic E2E execution.
- No Stage F enablement or production activation.
- No broad refactor or new infrastructure.
- Do not self-accept Stage D.

## 7. Deliverables and handoff

Create `STAGE_D_REMEDIATION_02_REPORT.md` in this task directory. Record exact changed paths, implementation semantics, commands/results/counts, adversarial symlink reproduction before/after, residual race limitations, hashes where available, worktree identity/dirty baseline preservation, and prohibited side effects not performed.

Update Website `STATUS.md` and `docs/tasks/current.md` to retain:
- original Stage D FAIL / D07-F01;
- Remediation 01 followed by Re-Audit 01 FAIL / D07-F01-R01;
- Remediation 02 implementation result as pending independent re-audit;
- Stage E NOT STARTED and Stage F DISABLED.

After implementation and verification, stop at the independent Auditor boundary. Prepare a concise CodexPro prompt that only summarizes the task and points to a separate complete independent re-audit handoff document. Do not embed this task's full checklist in the prompt.
