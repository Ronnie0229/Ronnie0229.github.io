# Stage D Remediation 01 — Independent Re-Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D
- Re-audit: Remediation 01
- Role: `INDEPENDENT_AUDITOR` (not Master)
- Date: 2026-11-18
- Overall verdict: **FAIL**
- Stage D: **FAIL / NOT ACCEPTED**
- Stage E: **NOT STARTED**
- Stage F: **DISABLED**

## 1. Executive verdict

The original caller-folder mismatch cases are fixed: after the v1.3 package validator passes, the lower-level package-aware Sermon workflow parses the package-bound prepublish frontmatter, calls the existing `v13_source_selector`, requires a caller `--folder`, and compares it exactly with the selector result. The correct-folder, wrong-folder, missing-folder and no-package legacy tests all pass. Wrong/missing folders fail after package validation and before the Sermon renderer or importer subprocess.

However, **D07-F01 is not fully closed**. A package-bound Sermon source folder can still be represented by an in-root symlink alias. `v13_source_selector` checks `target.is_dir()` and returns the lexical folder name without resolving and binding the real directory identity. The caller can provide that same alias and pass the exact string comparison. The Sermon importer then resolves the alias to a different real folder under the same raw intake and accepts it, because its containment check only verifies that the resolved folder remains under `SOURCE_DIR`; it does not compare the resolved folder identity with the package-bound selector identity.

An isolated adversarial fixture reproduced this:
- package-bound source selector returned `package-bound-alias`;
- caller folder exactly matched `package-bound-alias`;
- importer `resolve_folder` resolved it to `.../教会讲道/real-sermon`;
- the resolved folder remained inside the raw intake, so the importer's current containment check accepted it;
- `same_identity=false`.

This permits the package/presentation/prepublish evidence for one path identity to be dispatched against a different Sermon folder through an in-root symlink alias. The original mismatch and missing-folder tests do not cover this case. This is a material source-identity bypass within the mandatory D07 proposition; the overall verdict is therefore **FAIL**, not PASS_WITH_FINDINGS.

This Auditor did not implement a fix. Master must close the symlink/canonical-folder identity gap and add a negative regression proving rejection before renderer/importer dispatch, then request a fresh independent re-audit.

## 2. Authority, workspaces and frozen evidence

All five workspaces were opened in the exact order required by the handoff after `open_current_workspace`. The initial current workspace was RonnieCross root, not a Git repository; the exact Website construction worktree was then opened. The remaining exact workspaces were also opened:
- Website construction: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Sermon construction: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Website canonical: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Sermon canonical Owner: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`

### Recomputed SHA-256

| Object | Current SHA-256 | Result |
|---|---|---|
| Canonical Sermon Owner `DESIGN.md` | `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f` | Matches frozen authority |
| Stage D frozen plan — Website | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | Matches |
| Stage D frozen plan — Sermon mirror | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | Matches; `cmp -s` PASS |
| Stage D implementation report — Website | `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529` | Matches |
| Stage D implementation report — Sermon mirror | `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529` | Matches; `cmp -s` PASS |
| Original Stage D Auditor FAIL report | `1670f52a665f4c0db14fd6329884f376c24d6f8cdd0c1f8d34e39866977957c1` | Unchanged |
| Remediation 01 report — Website | `0959df7fa2f6e0d78891c1a8c3ef8f083324a562677ce24dc270ca2634f80e92` | Matches current Website file |
| Remediation 01 report — Sermon mirror | `b00433e9ec251860d63adc64adf00ea07587288736401ce18c8c2781e38ab992` | Current mirror hash |
| Re-audit request — Website | `92b5a238d254949d2063d5f560beacf04db0016f0148e5350724c0c059004dd6` | Matches |
| Re-audit request — Sermon mirror | `19dbcdab2e868e4fa21a1da100dac78f3710a0b7f0162c301f9aeb8adb775a08` | Mirror hash |

The original Stage D FAIL report was freshly read and its SHA recomputed after review; it remains unchanged. The re-audit report target was confirmed absent before writing.

### Status/evidence consistency observations

- Website `STATUS.md` and `docs/tasks/current.md` cite the current Website Remediation 01 report hash `0959df...`.
- Sermon construction `STATUS.md` / `tasks/current/index.md` cite Website report hash `cfa9f93d...` and Sermon report hash `864bd776...`; neither matches the current report files read and hashed in the two construction worktrees (`0959df...` Website and `b00433...` Sermon). These appear to be stale SHA pointers and should be reconciled by Master in a later authorized status/index update. This Auditor did not edit those files.
- The frozen plan and original implementation report are byte-identical across construction worktrees. No schema or producer changes were found in the bounded Remediation 01 write-set.

## 3. D07-F01 remediation verification

### 3.1 What is fixed

Website `scripts/content_workflow.py`:
- Lines 207–220 invoke the v1.3 package validator and reject invalid evidence before reading package-bound prepublish frontmatter.
- Lines 275–292 parse the prepublish file and call `v13_source_selector(package, frontmatter, raw_sermon_root=RAW_DIRS["sermon"])`.
- Lines 293–298 reject missing or mismatched caller `--folder` with `V13_PACKAGE_IDENTITY_MISMATCH`.
- Lines 302 onward are reached only after those checks; the Sermon renderer is dispatched at lines 309–324 and importer command at lines 325 onward.
- Lines 299–300 retain the v1.3 non-dry-run block.

The unified consumer `scripts/consume_publication_package.py` lines 262–263 still derives `--folder` from the package-bound `source_name` and passes it to the workflow. This path remains compatible with the new exact folder comparison.

Required tests in `scripts/tests/test_content_workflow_v13_share.py`:
- Lines 130–166: correct package-bound folder; package validator, renderer gate and dry-run importer dispatch are observed in order.
- Lines 168–188: wrong existing folder rejected; subprocess call count is exactly one (package validator only), proving no renderer/importer call.
- Lines 190–208: missing caller folder rejected; subprocess call count is exactly one, proving no renderer/importer call.
- Lines 209–228: no-package legacy Sermon route still dispatches through the existing presentation gate and importer.

The required four test behaviors pass. Package validator, presentation artifact path binding, prepublish SHA, metadata, presentation manifest/artifact and cross-document checks remain enforced by the existing v1.3 validator/consumer path; no weakening was observed.

### 3.2 Blocking residual — D07-F01-R01: in-root symlink alias breaks resolved source-folder identity

Affected code:
- `scripts/consume_publication_package.py` lines 114–146: `v13_source_selector` validates normalized project-relative syntax and the `data/raw/教会讲道/<folder>/...` prefix. For Sermon it sets `target = sermon_root / folder`, checks only `target.is_dir()`, then returns the lexical `folder` string. It does not resolve the target and compare the resolved path/identity with the canonical raw intake and selected folder.
- `scripts/content_workflow.py` lines 288–298: compares caller `folder` with that lexical selector result; an alias string therefore passes.
- `scripts/import_sermons.py` lines 596–612: `resolve_folder` resolves the caller path and verifies only that the resolved path is under `SOURCE_DIR`; it does not compare the resolved target to the package-bound canonical folder. An in-root symlink to another Sermon directory therefore passes this containment check and resolves to a different folder name/target.

Independent adversarial reproduction (temporary fixture only; no project files changed):
- Create `data/raw/教会讲道/real-sermon/`.
- Create symlink `data/raw/教会讲道/package-bound-alias -> real-sermon`.
- Package-bound frontmatter source: `data/raw/教会讲道/package-bound-alias/source.pdf`.
- `v13_source_selector(..., raw_sermon_root=intake)` returns `package-bound-alias`.
- Caller folder `package-bound-alias` equals selector output.
- `import_sermons.resolve_folder("package-bound-alias")` resolves to `.../教会讲道/real-sermon`.
- The resolved target is still inside the raw intake, but its identity/name differs from the package-bound selector result.

Observed output:
`{'selector_folder': 'package-bound-alias', 'caller_folder_matches_package': True, 'importer_resolved_folder': '<temp>/data/raw/教会讲道/real-sermon', 'importer_resolved_folder_name': 'real-sermon', 'same_identity': False, 'resolved_inside_intake': True}`

This is not the prior external-root symlink case: the target remains inside the trusted Website raw Sermon intake and passes the importer's current root containment check. The mismatch is between the package-bound alias and the actual folder selected by the importer. Therefore the downstream importer containment guard does not close this identity gap.

Required closure:
1. Resolve the selected folder against the configured raw Sermon root and enforce canonical containment.
2. Reject symlink aliases (or otherwise bind the exact canonical directory identity in a way the importer consumes without re-resolving to a different folder).
3. Ensure the package-derived identity, caller identity and importer-resolved identity are the same.
4. Add an in-root symlink-to-another-folder negative test proving failure before renderer/importer dispatch. Preserve the existing correct/mismatch/missing and legacy tests.

This Auditor did not implement or test a remediation for this new residual.

## 4. Regression / stage-boundary spot-check

| Proposition | Result | Evidence |
|---|---|---|
| D-01 | PASS | Canonical DESIGN SHA matches; frozen Stage D plan matches in both construction worktrees; plan and implementation report mirrors are byte-identical. |
| D-02 | PASS | Current Website/Sermon docs and original audit evidence retain the exact Share/Sermon intake, fallback identity, category and archive differences. |
| D-03 | PASS | Share article-native profile remains separate from Sermon Full Sermon Mode and sermon-specific presentation gate; no profile code changed in Remediation 01. |
| D-04 | PASS | Sermon Owner fidelity state machine and Project Bible authority were not changed; Remediation 01 write-set is Website consumer-only. |
| D-05 | PASS | TTS normalization remains pre-candidate-freeze in canonical DESIGN and current Owner docs; no normalization code or policy changed. |
| D-06 | PASS | v1.3 package validator, presentation manifest/artifact SHA bindings and producer/consumer chain remain in place; focused validator/consumer tests pass. |
| D-08 | PASS | No Sermon producer code changed; mirrored Stage D implementation report/plan match and existing producer/consumer contract evidence remains. |
| D-09 | PASS | Legacy/no-package Sermon route test passes; v1.2 route and current production defaults are unchanged. |
| D-10 | PASS | `test_v13_publish_mode_is_disabled_until_stage_f` passes with `allow_write=True`; CLI help explicitly states the Stage F block cannot be overridden. |
| D-11 | PASS | Independent focused/full test, compile, CLI help and diff-check commands all exit 0; exact results below. |
| D-12 | PASS_WITH_FINDINGS | Exact roots/branches/HEADs captured; no staged changes; no Auditor changes outside the sole report. Website canonical was already dirty at opening (4 tracked modifications, 0 untracked) and remains unchanged, rather than clean. Sermon canonical dirty/untracked lineage is preserved. Stale Sermon-side remediation report SHA pointers are noted in §2. |

Stage C chronology remains intact in current STATUS/index evidence: Stage C initial and Re-Audit 01/02/03 FAIL reports remain recorded; Remediation 04 Re-Audit 04 PASS_WITH_FINDINGS and Master acceptance remain later closure evidence. The original Stage D FAIL report remains present and unchanged. Stage D remains not accepted.

## 5. Independently executed verification

All commands below ran in the Website construction worktree unless stated otherwise.

| Command | Result | Exit |
|---|---:|---:|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_content_workflow_v13_share -v` | 11/11 PASS, including correct/mismatch/missing/legacy cases | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -q` | 71/71 PASS | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -q` | 25/25 PASS | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q` | 272/272 PASS | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package_v13.V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f -v` | PASS with `allow_write=True` | 0 |
| `PYTHONPYCACHEPREFIX=/tmp/ronniecross-stage-d-reaudit01-pycache python3 -m py_compile scripts/content_workflow.py scripts/consume_publication_package.py scripts/validate_publication_package_v13.py` | PASS | 0 |
| `git diff --check` | PASS | 0 |
| `python3 scripts/content_workflow.py publish-contract --help` | PASS; Stage F non-dry-run block and `--allow-write` limitation displayed | 0 |
| Isolated in-root symlink alias reproduction | **FAIL / reproduced identity mismatch** as detailed in §3.2 | 0 (reproduction completed) |

The 272-test suite and all focused suites passed. Passing tests do not negate the uncovered symlink identity gap because no current test exercises a package-bound in-root symlink alias resolving to a different Sermon folder.

## 6. Workspace identity and Git lineage

Branches and HEADs were read with `git rev-parse`; status inventories were read after verification. All workspaces had zero staged changes.

| Workspace | Workspace ID | Branch | HEAD | Tracked modified | Untracked | Staged |
|---|---|---|---|---:|---:|---:|
| Website construction | `ws_36904a3d8e03f8682750de45` | `task/unified-share-sermon-publication-stage-a-20261116` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | 12 | 46 | 0 |
| Sermon construction | `ws_0c1dbdff4bf12c1dc97eee92` | `task/unified-share-sermon-publication-stage-a-20261116` | `812ace500102bac54cb54cb0fa2249341118a3da` | 19 | 39 | 0 |
| Website canonical | `ws_24bb9de8a7d62a054469455b` | `main` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | 4 | 0 | 0 |
| Sermon canonical Owner | `ws_8e32016bc287b4ef40f8e9d5` | `master` | `812ace500102bac54cb54cb0fa2249341118a3da` | 15 | 57 | 0 |

Website canonical's four modified files (`AGENTS.md`, `STATUS.md`, `docs/task-handoff-protocol.md`, `docs/tasks/current.md`) were present when that exact workspace was opened. A `show_changes(since="workspace")` check found no changes to that canonical workspace during this audit. It was not clean at opening; it was left untouched. Sermon canonical's pre-existing dirty/untracked lineage and `ahead 2` state were preserved. No writes were made to Sermon construction or either canonical worktree.

## 7. Auditor write-set and prohibited side effects

The only file written by this Auditor is:

`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_REAUDIT_01_REPORT.md`

No other file was created, edited or deleted by this Auditor. The report path was absent before writing; the original `STAGE_D_AUDIT_REPORT.md` was not overwritten.

Not performed:
- No source, test, plan, implementation report, remediation report, STATUS, task index, schema, contract, fixture or documentation edits.
- No write to Sermon construction or either canonical worktree.
- No Git staging, commit, push, merge, reset, clean, rebase, amend, branch change or stash.
- No production import/export or content mutation; no raw/processed/posts writes.
- No Astro build or deployment.
- No NAS probe/read/write/archive.
- No email or notification.
- No dependency installation or upgrade.
- No Stage E synthetic E2E execution.
- No Stage F enablement or production activation.

Tests used isolated temporary fixtures. Python bytecode generation was disabled or redirected to `/tmp`. The symlink identity reproduction used only a temporary directory and changed no project files.

## 8. Chronology and final disposition

Original Stage D chronology remains: initial independent audit **FAIL** / D07-F01 → Master Remediation 01 candidate → this independent re-audit **FAIL** because package-bound in-root symlink aliases can still redirect the actual imported Sermon folder identity. The original FAIL report and all Stage C FAIL/PASS chronology remain intact.

**Formal verdict: FAIL.** Return to Master for bounded remediation of D07-F01-R01 and a fresh independent re-audit. This Auditor does not accept Stage D. Stage E remains NOT STARTED; Stage F remains DISABLED.
