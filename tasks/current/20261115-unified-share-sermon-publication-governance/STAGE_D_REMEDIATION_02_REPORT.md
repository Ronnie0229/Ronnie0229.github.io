# Stage D Remediation 02 Report — D07-F01-R01 Canonical Sermon Folder Identity

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D
- Remediation: 02
- Date: 2026-11-18
- Role: Master / Executor
- Status: `IMPLEMENTATION_COMPLETE_PENDING_INDEPENDENT_REAUDIT`
- Trigger: Stage D Remediation 01 Independent Re-Audit `FAIL`
- Auditor report: `independent-audit/STAGE_D_REAUDIT_01_REPORT.md`
- Auditor report SHA-256: `60181632307336e1c194581ffea095d84617cc7740ce789529b741aa45869df4`
- Frozen Stage D plan SHA-256: `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e`

## 1. Executive result

Master completed the bounded Website-consumer remediation for `D07-F01-R01`.

The package-bound Sermon selector now rejects an in-root directory symlink alias and verifies that the selected directory resolves to the exact direct child identity named by the package-bound source. The lower-level v1.3 workflow derives and passes the canonical expected source directory to the Sermon importer. The importer independently revalidates the selected folder against that expected canonical directory before running its presentation gate; it rejects symlink aliases and in-root folder mismatches. The package-aware importer iteration also skips symlink directory entries.

The adversarial case from Re-Audit 01 is now covered: package source `package-bound-alias` → symlink to `real-sermon`, with caller supplying the exact same alias, is rejected after package validation and before renderer/importer dispatch.

The no-package legacy/v1.2 route retains its previous resolver behavior because the new expected-source argument is optional and is passed only by the package-aware v1.3 workflow.

This report is implementation evidence only. It does not self-accept Stage D. Stage E remains NOT STARTED; Stage F remains DISABLED.

## 2. Finding disposition

### D07-F01-R01 — MASTER REMEDIATION CANDIDATE; PENDING INDEPENDENT RE-AUDIT

Original residual:
- The package-bound selector returned the lexical alias folder name without resolving its canonical directory identity.
- The caller could provide the same alias and pass exact string comparison.
- The importer resolved the alias to another real folder inside the raw intake and accepted it because containment alone did not prove package-to-importer identity.

Remediation:
1. `v13_source_selector` rejects a selected Sermon folder when the selected path is a symlink.
2. It strictly resolves the configured raw Sermon root and selected target; the resolved target must be a directory, a direct child of the canonical root, and retain the package-bound folder basename.
3. `content_workflow.py` derives the canonical expected folder from that same configured raw root after package validation and passes it as `--expected-source-folder` to the importer. The workflow checks remain before renderer/importer dispatch.
4. `import_sermons.py` accepts the hidden/internal expectation argument only as an optional additive guard. When present, it rejects a symlink selected path, requires the requested and expected canonical paths to be direct children of the resolved raw intake, and requires exact resolved-path equality before the presentation gate.
5. During package-aware import iteration, symlink directory entries are skipped so a second alias cannot be selected in preference to the canonical directory; a regression test places an alias before the canonical folder and proves only the canonical folder is selected.
6. Legacy/no-package invocation does not pass the expectation argument and retains the legacy resolution branch.

## 3. Regression coverage

Added:
- `scripts/tests/test_import_sermon_source_identity.py`

Updated:
- `scripts/tests/test_content_workflow_v13_share.py`

New adversarial and importer tests:
- Package-bound in-root symlink alias with matching caller alias: rejected before renderer/importer; exactly one subprocess call (package validator only).
- Importer expected canonical directory: correct canonical folder accepted.
- Importer selected in-root symlink alias: rejected.
- Importer selected different real directory still inside intake: rejected.
- Importer `main()` entrypoint rejects alias before presentation-gate subprocess dispatch.
- Package-aware import iteration skips an earlier-sorting symlink alias and selects only the canonical source folder.
- Existing package-bound correct-folder test now verifies canonical expected folder is passed to importer.
- Existing wrong-folder, missing-folder, legacy/no-package, Share symlink/source identity tests remain passing.

## 4. Verification evidence

All final commands ran in the Website construction worktree:

| Command / suite | Result |
|---|---:|
| Workflow + importer source-identity focused tests | **17/17 PASS** |
| Stage C / v1.3 focused suite | **77/77 PASS** |
| Legacy compatibility suite | **25/25 PASS** |
| Full Website Python suite | **278/278 PASS** |
| Stage F non-dry-run negative test with `allow_write=True` | **1/1 PASS** |
| Python compile for all changed Python modules/tests | PASS |
| `python3 scripts/import_sermons.py --help` | PASS |
| `python3 scripts/content_workflow.py publish-contract --help` | PASS |
| `git diff --check` | PASS |

The first focused test invocation exposed a syntax error in the newly authored test's multiline context-manager statement. The test file was corrected before the final runs; the corrected focused suite and all subsequent suites passed. No product-code behavior was accepted on the basis of that failed invocation.

No Astro build was run. The full Python suite's existing fixture tests invoke isolated temporary render-gate fixtures and their expected negative evidence; no production content was used or modified.

## 5. Residual security limitation

The implementation now rejects symlink aliases at both the package selector/workflow boundary and the importer entry boundary, and the importer rechecks the canonical expected directory immediately before its presentation gate. It does **not** claim complete race-free protection against a hostile concurrent filesystem actor replacing directory entries between path checks and later file operations. This remains a path-based TOCTOU residual under the currently trusted raw-intake threat model. A future threat model that admits untrusted concurrent mutation would require a separate descriptor-based/no-follow design and authorization; this remediation does not claim to solve that broader problem.

## 6. Write-set and worktree protection

Changed implementation/test files:
- `scripts/consume_publication_package.py`
- `scripts/content_workflow.py`
- `scripts/import_sermons.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- `scripts/tests/test_import_sermon_source_identity.py` (new)

Task/evidence files:
- `STAGE_D_REMEDIATION_02_TASK.md`
- `STAGE_D_REMEDIATION_02_REPORT.md`
- `INDEPENDENT_AUDIT_REQUEST_STAGE_D_REAUDIT_02.md` (separate independent handoff)

Website `STATUS.md`, `docs/tasks/current.md`, and the task `TASK_INDEX.md` were updated to record the new FAIL → remediation chronology and pending independent re-audit.

Workspace:
- Website construction root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD remains `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- No staging; all changes remain unstaged.
- Pre-existing Stage A/C/D dirty and untracked lineage was preserved. This remediation added only the bounded importer source guard, regression coverage and its task/evidence records; no unrelated files were intentionally modified.

No changes were made to Website canonical, Sermon construction, or Sermon canonical worktrees. The Sermon-side stale SHA pointers previously identified by the Auditor were not modified in this Website-only bounded remediation and remain a separate reconciliation item.

## 7. Prohibited side effects

Not performed:
- No Git staging, commit, push, merge, reset, clean, rebase, amend, branch or worktree mutation.
- No production import/export or raw/processed/posts content mutation.
- No NAS access.
- No email or notification.
- No Astro build or deployment.
- No dependency installation or upgrade.
- No Stage E synthetic E2E execution.
- No Stage F enablement or production activation.

## 8. Chronology and final disposition

Preserved chronology:
1. Stage D initial independent audit: **FAIL / D07-F01** — lower-level caller folder was not bound to package source.
2. Master Remediation 01: exact lexical caller/package folder comparison added.
3. Stage D Remediation 01 independent re-audit: **FAIL / D07-F01-R01** — in-root symlink alias still allowed a different importer-resolved folder identity. Auditor report SHA-256: `60181632307336e1c194581ffea095d84617cc7740ce789529b741aa45869df4`.
4. Master Remediation 02: canonical folder identity checks and importer-bound expected canonical path added; verification above passed.

**Current status: Stage D FAIL / NOT ACCEPTED pending a fresh independent re-audit of Remediation 02. Stage E NOT STARTED. Stage F DISABLED.**
