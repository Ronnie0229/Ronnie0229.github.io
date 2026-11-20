# Stage D Remediation 02 — Independent Re-Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR` (not Master)
- Re-audit target: Website consumer remediation for `D07-F01-R01`
- Date: 2026-11-19
- Overall verdict: **PASS_WITH_FINDINGS**
- Stage D: **AUDITOR PASS_WITH_FINDINGS / MASTER ACCEPTANCE PENDING**
- Stage E: **NOT STARTED**
- Stage F: **DISABLED**

## 1. Executive verdict

The Remediation 02 implementation closes the material source-folder identity gap found in Re-Audit 01 under the current trusted raw-intake threat model.

Independent inspection and isolated verification confirm:

1. The package-bound Sermon folder is resolved against the configured raw Sermon intake root. The selected folder itself may not be a symlink; the resolved directory must be a direct child of the canonical root and retain the package-bound basename.
2. The exact Re-Audit 01 adversarial shape — package source `package-bound-alias`, an in-root symlink to `real-sermon`, and caller `--folder package-bound-alias` — is rejected after package validation and before renderer/importer dispatch. The subprocess evidence is exactly one call, to the package validator.
3. The normal canonical folder passes. The lower-level v1.3 workflow passes its canonical expected source directory to the importer through `--expected-source-folder`.
4. The importer independently rejects a selected symlink alias and an in-root different real folder before its presentation gate. It accepts the matching canonical folder.
5. The expected-source argument is optional and is only added by the package-aware v1.3 workflow; the no-package legacy/v1.2 route remains compatible.
6. Package-aware iteration skips symlink directory entries and selects the canonical source folder even when an alias sorts earlier.

No mandatory D-01..D-12 failure remains. The disclosed path-based TOCTOU limitation is retained as a non-blocking risk under the current trusted raw-intake threat model. Therefore the verdict is **PASS_WITH_FINDINGS**, not an assertion of race-free filesystem security.

This is an Auditor verdict only. It does not accept Stage D on behalf of Master and does not authorize Stage E or Stage F.

## 2. Authority, workspace identity and frozen evidence

### 2.1 Exact workspaces opened

The initial `open_current_workspace` resolved to RonnieCross root (not a Git repository). The exact Website construction worktree was then opened, followed by the three required read-only comparison workspaces.

| Workspace | Workspace ID | Branch | HEAD |
|---|---|---|---|
| Website construction | `ws_36904a3d8e03f8682750de45` | `task/unified-share-sermon-publication-stage-a-20261116` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` |
| Sermon construction | `ws_0c1dbdff4bf12c1dc97eee92` | `task/unified-share-sermon-publication-stage-a-20261116` | `812ace500102bac54cb54cb0fa2249341118a3da` |
| Website canonical | `ws_24bb9de8a7d62a054469455b` | `main` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` |
| Sermon canonical Owner | `ws_8e32016bc287b4ef40f8e9d5` | `master` | `812ace500102bac54cb54cb0fa2249341118a3da` |

The Website construction HEAD is aligned with `origin/main`; Sermon construction HEAD remains its recorded task branch tip. Sermon canonical remains `ahead 2` of `origin/master`.

### 2.2 Current dirty lineage

The following is the state observed at the end of audit; no staging was present:

- Website construction: 13 tracked modified paths, 52 untracked paths, 0 staged. Compared with Re-Audit 01's recorded baseline (12 modified / 46 untracked / 0 staged), the current delta is +1 modified and +6 untracked; this includes the Remediation 02 evidence/test artifacts and this Auditor report.
- Sermon construction: 19 tracked modified paths; pre-existing untracked contracts, tests, validator and task evidence remain present; 0 staged.
- Website canonical: 4 tracked modified files (`AGENTS.md`, `STATUS.md`, `docs/task-handoff-protocol.md`, `docs/tasks/current.md`); no untracked files. These four modifications were already present when opened.
- Sermon canonical Owner: 15 tracked modified paths, 57 untracked paths; branch remains `ahead 2`.

The canonical workspaces were reopened after verification and their status remained unchanged from their opening state. Sermon construction remains 19 modified / 39 untracked / 0 staged, matching the prior Re-Audit 01 baseline. Website canonical remains 4 / 0 / 0; Sermon canonical remains 15 / 57 / 0. No writes were made to either canonical workspace or the Sermon construction workspace. Existing dirty/untracked lineage was not cleaned, staged, stashed, reset or otherwise rewritten.

**Pre-existing stale SHA pointers remain an Owner/Master follow-up, not modified in this audit.** Sermon construction `STATUS.md:14` and `tasks/current/index.md:13` still cite Website Remediation 01 SHA `cfa9f93db1a27113a27499237e32d7a8ac05231753bb3cfc84b9a54da7f9d5c3` and Sermon mirror SHA `864bd776571953d24bf4c189699ba67f74e117e98eb4db46882b23eb872d77ae`. Current files hash to Website `0959df7fa2f6e0d78891c1a8c3ef8f083324a562677ce24dc270ca2634f80e92` and Sermon `b00433e9ec251860d63adc64adf00ea07587288736401ce18c8c2781e38ab992`. The Remediation 02 task explicitly excludes updating these Sermon-side pointers; preserve them for a separately authorized status/index reconciliation.

### 2.3 Recomputed SHA-256

| Object | SHA-256 | Result |
|---|---|---|
| Canonical Sermon Owner `tasks/current/.../DESIGN.md` | `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f` | Matches frozen design authority |
| Stage D plan — Website | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | Matches |
| Stage D plan — Sermon construction mirror | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | Byte-identical |
| Stage D implementation report — Website | `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529` | Matches |
| Stage D implementation report — Sermon construction mirror | `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529` | Byte-identical |
| Remediation 01 report — Website | `0959df7fa2f6e0d78891c1a8c3ef8f083324a562677ce24dc270ca2634f80e92` | Matches |
| Remediation 01 report — Sermon construction mirror | `b00433e9ec251860d63adc64adf00ea07587288736401ce18c8c2781e38ab992` | Matches current mirror; stale STATUS/index pointer disclosed above |
| Remediation 02 task | `25f37bed122c07f2513f6a673391e9642708fb6b3b9c60bc453feb4605c07ebd` | Matches |
| Remediation 02 report | `f7a21b22af3fc56ecc362b040c470a57af9a0c3dc0250ee3a619eb1cd66868bd` | Matches |
| Original Stage D audit request | `8a5f62cc66c9a6fe17540dbbb37e808f6be6bc8221c6ce920a4e9105ecf14db8` | Matches |
| Re-Audit 01 request | `92b5a238d254949d2063d5f560beacf04db0016f0148e5350724c0c059004dd6` | Matches |
| Re-Audit 02 request | `2ddb1dbd30cd8bc8a153d1dd4e638e810506af61eb1516b3d37d5686f0c9055b` | Matches |
| Original Stage D Auditor FAIL report | `1670f52a665f4c0db14fd6329884f376c24d6f8cdd0c1f8d34e39866977957c1` | Unchanged |
| Stage D Re-Audit 01 FAIL report | `60181632307336e1c194581ffea095d84617cc7740ce789529b741aa45869df4` | Unchanged |
| `content-presentation/v1` schema (Website / Sermon) | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | Byte-identical |
| `website-publication-package/v1.3` schema (Website / Sermon) | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | Byte-identical |
| `publication_contract_invariants.py` (Website / Sermon) | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | Byte-identical |

The original Stage D FAIL and Re-Audit 01 FAIL reports were read and re-hashed; neither was modified or overwritten. The Remediation 02 report and request remain frozen at the hashes above.

### 2.4 Current implementation/test file hashes

| File | SHA-256 |
|---|---|
| `scripts/consume_publication_package.py` | `c959da7adbba54b06a7cfcb1e0e9e1c36c0085aaa6f6aec4bcf673a65bf7d11f` |
| `scripts/content_workflow.py` | `840057dd3661ee426bbecc5e370a4187afeb02e2e1c53ef55d2f50df5250c428` |
| `scripts/import_sermons.py` | `1c208495b82df0d2560536553684c97588909f888724b156b0003b70d68a750d` |
| `scripts/tests/test_content_workflow_v13_share.py` | `c93b3512407d98e92b57de27278554d375322819cbf86cf6e3475ac2e0046067` |
| `scripts/tests/test_import_sermon_source_identity.py` | `91a1407ae1fb953618bfda5c9f3c596be4100edbf6ec30ebe736b17232cbca11` |

## 3. D07-F01-R01 proposition-by-proposition result

| # | Required proposition | Result | Current evidence |
|---|---|---|---|
| 1 | Package-bound source folder resolves against configured raw Sermon root | PASS | `consume_publication_package.py:138-155`; strict resolution of root and target, direct-child and basename checks |
| 2 | In-root package-bound symlink alias is rejected even when caller folder equals alias | PASS | `consume_publication_package.py:143-155`; workflow test `test_content_workflow_v13_share.py:192-223` |
| 3 | Rejection is after package validation but before renderer/importer dispatch | PASS | Workflow test records exactly one subprocess call, the package validator; no renderer/importer call |
| 4 | Canonical folder passes package-bound checks | PASS | `test_content_workflow_v13_share.py:130-168`; normal canonical source reaches renderer then importer in order |
| 5 | Wrong existing and missing caller folders remain rejected before renderer/importer | PASS | `test_content_workflow_v13_share.py:170-190` and `:225-243`; package validator is the only subprocess call |
| 6 | v1.3 workflow passes canonical expected source directory to importer | PASS | `content_workflow.py:288-305`, `:332-334`; positive test asserts `--expected-source-folder` equals canonical absolute path |
| 7 | Importer independently checks selected folder against expected canonical directory before presentation gate | PASS | `import_sermons.py:597-623`, `:723-747`; `resolve_folder` precedes the presentation-gate subprocess |
| 8 | Importer rejects selected alias, different in-root folder, expected path symlink and expected path outside direct-child intake | PASS | `test_import_sermon_source_identity.py:33-47`, `:49-72`; additional isolated direct probes rejected expected-path symlink and outside path |
| 9 | Importer accepts the correct canonical folder | PASS | `test_import_sermon_source_identity.py:23-31` |
| 10 | Package-aware iteration cannot choose an alias ahead of canonical folder | PASS | `import_sermons.py:780-784`; `test_import_sermon_source_identity.py:74-126` places a lexically earlier alias and confirms canonical selection |
| 11 | Legacy/no-package v1.2 behavior remains compatible | PASS | `content_workflow.py` only appends expectation for package-aware path; legacy workflow test at `test_content_workflow_v13_share.py:244-263` passes without package expectation |
| 12 | Path-based TOCTOU residual is accurately bounded | PASS_WITH_FINDINGS | Importer rechecks at entry, but does not use descriptor-based/no-follow handles for all later filesystem operations; see §5 |

### 3.1 Exact adversarial shape

An isolated temporary fixture reproduced the prior finding:

- `data/raw/教会讲道/real-sermon/` was created.
- `data/raw/教会讲道/package-bound-alias` was created as a symlink to `real-sermon`.
- The package-bound prepublish source used `data/raw/教会讲道/package-bound-alias/source.pdf`.
- Caller supplied the exact same lexical folder, `package-bound-alias`.

Observed behavior: package validation ran; the workflow then rejected the symlink alias. The mocked subprocess call count was exactly one and its command was `validate_publication_package_v13.py`. No Node renderer or `import_sermons.py` subprocess was dispatched.

This directly closes the Re-Audit 01 mismatch: the caller can no longer make the lexical alias comparison pass and then have the importer resolve to `real-sermon`.

### 3.2 Importer entry and canonical identity probes

The importer entry test supplied an alias already present when `main()` began, with the canonical expected folder. It raised `SERMON_SOURCE_IDENTITY_MISMATCH` and asserted that `subprocess.run` was not called, proving rejection before the presentation gate. This represents the required case where a link appears after workflow validation but is present at importer entry.

Additional isolated temporary probes independently confirmed:

- selected canonical folder + expected canonical folder: accepted;
- selected in-root alias + expected canonical folder: rejected;
- selected different real folder still inside raw intake + expected canonical folder: rejected;
- expected-source path itself a symlink: rejected;
- expected-source path outside the direct-child raw intake boundary: rejected.

The package-aware iteration fixture puts `000-alias` before the canonical folder in lexical order; the importer skips the symlink entry and selects only the canonical directory.

## 4. Regression and boundary verification

All commands below ran in the Website construction worktree. Exit code was 0 for every final command.

| Command | Result |
|---|---:|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_sermon_source_identity -v` | 17/17 PASS |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity scripts.tests.test_import_sermon_source_identity -q` | 77/77 PASS |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -q` | 25/25 PASS |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q` | 278/278 PASS |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package_v13.V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f -v` | 1/1 PASS with `allow_write=True` |
| `PYTHONPYCACHEPREFIX=/tmp/ronniecross-stage-d-reaudit02-pycache python3 -m py_compile scripts/content_workflow.py scripts/consume_publication_package.py scripts/import_sermons.py scripts/tests/test_content_workflow_v13_share.py scripts/tests/test_import_sermon_source_identity.py` | PASS |
| `python3 scripts/import_sermons.py --help` | PASS |
| `python3 scripts/content_workflow.py publish-contract --help` | PASS; help says `--allow-write` cannot override Stage F |
| `git diff --check` | PASS |
| Isolated expected-source symlink/outside-path probe | Both rejected as required |

One initial custom probe invocation had a Python `-c` quoting/newline SyntaxError (exit 1); it did not execute the probe or modify project files. The command was corrected to pass a multiline program through `exec()`; the corrected probe exited 0 and verified both rejection cases. No product/test failure was concealed or reclassified.

The first focused suite, Stage C/v1.3 suite, legacy suite, full Python suite, compile, CLI help and diff-check all passed. No Astro build was run.

## 5. TOCTOU residual and threat-model boundary

The implementation performs path-based checks at multiple boundaries:

- package selector resolves the configured root and package-selected directory and rejects a selected symlink;
- workflow derives the canonical expected directory after package validation and passes that exact path to the importer;
- importer entry rejects a selected symlink, resolves both selected and expected paths, enforces direct-child containment and exact equality before presentation validation;
- package-aware iteration skips symlink directory entries.

These checks close the observed in-root alias substitution when the alias exists at workflow validation or importer entry. They do **not** provide complete race-free filesystem security if a hostile concurrent actor can replace directory entries after the importer check and before later file opens/reads. Path strings and repeated `resolve()` calls are not equivalent to descriptor-based `openat` / no-follow identity handoff.

Under the current project threat model, the configured raw intake is a trusted local workflow area and untrusted concurrent mutation is not an accepted normal operating condition. The remaining race is therefore disclosed as **non-blocking hardening**, not a D07 blocker. If the project later admits untrusted concurrent writers to the raw intake, a separate authorized descriptor-based/no-follow design would be required. This report does not claim race-free security.

## 6. D-01..D-12 regression spot-check

| Gate | Result | Independent basis |
|---|---|---|
| D-01 Scope / canonical design | PASS | Canonical Sermon Owner design SHA and frozen Stage D plan SHA match; Remediation 02 stays within Website consumer/importer boundary |
| D-02 Share/Sermon business differences | PASS | Website `AGENTS.md:14-18` and `CONTENT_WORKFLOW.md:8-16` retain intake, Ronnie/Patrick fallback-only identity, category and archive distinctions |
| D-03 Separate content profiles | PASS | Website `AGENTS.md:14-17`, `docs/sermon-content-rendering-binding.md:9-13`; Share remains article-native, Sermon retains Full Sermon Mode |
| D-04 Fidelity / Project Bible ownership | PASS | Website `AGENTS.md:19-20`; canonical Sermon Owner remains authority; Remediation 02 did not modify fidelity or Bible implementation |
| D-05 TTS scripture normalization | PASS | Website `AGENTS.md:19-20`; normalization remains before candidate freeze and ambiguous/non-contiguous/uncontrolled references fail closed |
| D-06 Presentation/package chain | PASS | Website `AGENTS.md:20-22`, `CONTENT_WORKFLOW.md:21-32`; schema/invariant hashes match across Website and Sermon construction worktrees |
| D-07 Website no-bypass/source identity | PASS | §3; alias, mismatch, importer entry, expected path, canonical positive and legacy cases independently verified |
| D-08 Producer compatibility | PASS | Sermon construction worktree remains at its prior 19/39/0 dirty baseline; producer-side files were not written in this remediation/audit; schema and invariant mirrors are byte-identical by SHA |
| D-09 Legacy compatibility | PASS | Legacy test suite 25/25; no-package workflow behavior remains on prior path |
| D-10 Production gate | PASS | Stage F negative test passes with `allow_write=True`; CLI explicitly states the flag cannot override the block; no production/default route change observed |
| D-11 Reproducibility | PASS | All listed tests, compile, CLI help and diff-check exit 0 |
| D-12 Workspace/side-effect safety | PASS_WITH_FINDINGS | Exact workspace roots/branches/HEADs captured; no staged changes; pre-existing canonical Website dirty state (4 tracked files) and Sermon canonical dirty/untracked/ahead-2 lineage preserved unchanged |

No producer/Owner schema, package contract, presentation identity, fidelity state machine, Project Bible authority, historical package or production/default route change was found in the bounded Remediation 02 implementation.

## 7. Auditor write-set and prohibited side effects

The sole permitted Auditor write is this report:

`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_REAUDIT_02_REPORT.md`

No source, test, plan, implementation report, remediation report, STATUS, task index, schema, contract, fixture, content or other project file was edited, created or deleted by the Auditor.

Not performed:

- No Git staging, commit, push, merge, reset, clean, rebase, amend, branch/worktree mutation or stash.
- No production import/export or raw/processed/posts content mutation.
- No NAS access.
- No email or notification.
- No Astro build or deployment.
- No dependency installation or upgrade.
- No Stage E synthetic E2E execution.
- No Stage F enablement or production activation.
- No write to Sermon construction, Website canonical or Sermon canonical worktrees.

Tests used isolated temporary fixtures only. Test commands disabled Python bytecode or redirected compile cache to `/tmp`. The custom expected-source probes used temporary directories and cleaned them up.

## 8. Chronology and final disposition

The chronology is preserved without rewriting earlier outcomes:

1. Stage D initial independent audit: **FAIL / D07-F01** — caller folder was not bound to package source.
2. Master Remediation 01: lexical caller/package folder comparison added.
3. Stage D Remediation 01 independent re-audit: **FAIL / D07-F01-R01** — in-root symlink alias could still resolve to another actual Sermon directory.
4. Master Remediation 02: canonical source identity binding, importer-side expectation check and symlink-safe package iteration implemented.
5. Stage D Remediation 02 independent re-audit: **PASS_WITH_FINDINGS** — D07-F01-R01 closed; path-based TOCTOU remains disclosed as non-blocking under the trusted raw-intake threat model.

**Auditor final verdict: PASS_WITH_FINDINGS.** Return to Master for its independent acceptance decision. This Auditor does not accept Stage D.

- Stage D: Auditor PASS_WITH_FINDINGS; Master acceptance pending.
- Stage E: **NOT STARTED**.
- Stage F: **DISABLED**.
