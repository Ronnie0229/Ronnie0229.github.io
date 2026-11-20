# Stage D Remediation 01 Report — D07-F01 Sermon Package/Source Binding

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D
- Remediation: 01
- Date: 2026-11-18
- Status: `IMPLEMENTATION_COMPLETE_PENDING_INDEPENDENT_REAUDIT`
- Trigger: Stage D Independent Audit `FAIL`
- Original Auditor report: `independent-audit/STAGE_D_AUDIT_REPORT.md`
- Original Auditor report SHA-256: `1670f52a665f4c0db14fd6329884f376c24d6f8cdd0c1f8d34e39866977957c1`
- Frozen Stage D plan SHA-256: `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e`

## 1. Executive result

Master completed a bounded remediation for the sole Stage D blocker `D07-F01`.

The package-aware Sermon branch of Website `scripts/content_workflow.py publish sermon` now independently resolves the source folder from the package-bound prepublish frontmatter and requires the caller-provided `--folder` to match exactly before invoking the Sermon presentation renderer or importer.

The existing `v13_source_selector` is reused. It now accepts an optional `raw_sermon_root` so the lower-level workflow can validate against its configured Website raw Sermon intake without introducing a second selector implementation. The unified `publish-contract` consumer retains its existing default behavior.

The no-package legacy/v1.2 Sermon path is unchanged. No Stage F production enablement, production import, build, deployment, NAS, notification or Git write operation was performed.

This report is implementation evidence only. It does not self-accept Stage D.

## 2. Finding disposition

### D07-F01 — CLOSED BY MASTER REMEDIATION CANDIDATE; PENDING INDEPENDENT RE-AUDIT

Original defect:
- The package-aware lower-level Sermon workflow validated the v1.3 package and presentation artifact.
- It then accepted caller-supplied `--folder` without comparing it to the source folder encoded in the package-bound prepublish frontmatter.
- The importer therefore could be dispatched with a different sermon folder while retaining another Sermon's package/presentation evidence.

Remediation:
1. After successful v1.3 package validation, the Sermon branch reads the package-bound prepublish file.
2. It parses the prepublish frontmatter using the existing consumer parser.
3. It resolves the expected Sermon source selector through the existing `v13_source_selector`, using configured `RAW_DIRS["sermon"]` as the raw intake root.
4. It rejects a missing caller folder with `V13_PACKAGE_IDENTITY_MISMATCH`.
5. It rejects any caller folder not exactly equal to the package-derived folder with `V13_PACKAGE_IDENTITY_MISMATCH`.
6. These checks occur before the Sermon presentation renderer and before importer command dispatch.
7. The existing package validator continues to bind prepublish SHA, package metadata, presentation artifact/manifest and cross-document identity. No replacement or weakening of those checks was made.

### Changed files

Website construction worktree only:
- `scripts/content_workflow.py`
- `scripts/consume_publication_package.py`
- `scripts/tests/test_content_workflow_v13_share.py`

No schema, package contract, presentation identity, Sermon Owner business rule, fidelity state machine, Project Bible rule, producer code or canonical worktree was changed.

## 3. Focused regression coverage

The existing Sermon v1.3 route test now creates the package-bound raw source folder and verifies that the correct caller folder proceeds through:
- package validation;
- Sermon presentation renderer gate;
- dry-run importer dispatch.

New tests verify:
- wrong existing folder: rejected after package validation but before renderer/importer;
- missing caller folder: rejected after package validation but before renderer/importer;
- legacy Sermon route without a v1.3 publication package: retains the prior presentation-gate and importer dispatch behavior.

The mismatch and missing-folder tests assert that only the package validator subprocess was called; neither renderer nor importer was invoked.

## 4. Verification results

Website construction worktree:
- Full Python suite: **272/272 PASS**.
- Stage C / v1.3 focused suite: **71/71 PASS**.
- Legacy compatibility suite: **25/25 PASS**.
- `py_compile` for `content_workflow.py`, `consume_publication_package.py`, both importers and v1.3 validator: PASS.
- `git diff --check`: PASS.

Chronology note:
- The first full-suite attempt after the initial patch exposed a test-fixture isolation issue: the test patched the consumer module's root while the shared selector resolved against the configured raw intake root. The fixture was corrected to patch the workflow's `RAW_DIRS["sermon"]` and the selector was given an optional raw-root argument. The focused suite then passed 11/11, and the full suite was rerun successfully at 272/272. The initial test error is disclosed here and is not represented as a production-code failure.

Previously established Stage D evidence remains available in the original implementation report and Auditor report. This remediation did not rerun unrelated Sermon Owner producer suites because the changed files and behavior are confined to the Website consumer workflow.

## 5. Compatibility and safety boundaries

- v1.2 / legacy Sermon route without `--publication-package`: unchanged and explicitly regression-tested.
- v1.3 package-aware Sermon workflow: caller folder must match package-derived source folder.
- v1.3 non-dry-run remains blocked before Stage F.
- Stage E remains NOT STARTED.
- Stage F remains DISABLED.
- No production import or content mutation.
- No Astro build or deployment.
- No NAS probe/read/write/archive.
- No email or notification.
- No dependency install/upgrade.
- No Git staging, commit, push, merge, reset, clean, rebase or amend.

## 6. Worktree protection

Implementation target:
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`

The following were not modified:
- Website canonical worktree `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`;
- Sermon canonical worktree `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`.

In Sermon construction, no Sermon source/producer code changed. Master updated only the mirrored remediation report/request and current STATUS/index records. All pre-existing dirty/untracked lineages remain protected. No staging or Git history operation occurred.

## 7. Re-audit handoff

A fresh Independent Auditor is requested to:
- independently verify the original D07-F01 evidence and the exact remediation;
- verify correct folder, mismatched folder, missing folder and legacy compatibility tests;
- confirm package-bound source is derived from the validated prepublish frontmatter and mismatch fails before renderer/importer dispatch;
- confirm v1.3 non-dry-run remains blocked and Stage F remains disabled;
- spot-check the previously passing D-01..D-06 and D-08..D-12 boundaries for regression;
- verify worktree identities and dirty-lineage protection;
- write only `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_REAUDIT_01_REPORT.md` in the Website construction worktree.

Stage D remains **FAIL / NOT ACCEPTED** until the separate Independent Auditor returns a new verdict and Master subsequently makes a final acceptance decision. Stage E must not start; Stage F remains DISABLED.
