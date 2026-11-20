# Stage D Independent Audit Report — Share / Sermon Unified Publication Governance

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D
- Role: `INDEPENDENT_AUDITOR` (not Master)
- Audit date: 2026-11-18
- Overall verdict: **FAIL**
- Stage D acceptance: **NOT ACCEPTED**
- Stage E: **NOT STARTED**
- Stage F: **DISABLED**

## 1. Executive verdict

The independent audit confirms that the frozen Stage D plan, mirrored implementation report, shared schemas/helper, most documentation alignment, producer contract checks, legacy compatibility boundary, and Stage F fail-closed behavior are consistent with the canonical design. The independently rerun Website and Sermon test suites passed.

However, **D-07 FAILS**. The v1.3 Sermon package-aware path exposed by `content_workflow.py publish sermon` does not bind the caller-supplied `--folder` to the source folder identified by the validated v1.3 package. The normal `publish-contract` consumer derives the correct folder from package-bound prepublish source metadata, but the lower-level workflow entrypoint can be invoked directly with a different existing sermon folder while supplying the valid package and its bound presentation artifact. The workflow validates the package and artifact path, then passes the caller folder to `import_sermons.py` without comparing it to the package-bound source. This leaves a package/source identity bypass in the v1.3 Sermon path.

This is a mandatory Stage D acceptance proposition, not a cosmetic documentation finding. Stage F remains disabled, which currently prevents v1.3 production writes, but it does not make the Stage D contract complete. Master should receive this finding for bounded remediation and a fresh independent re-audit. This Auditor does not accept Stage D or authorize Stage E/F.

## 2. Authority, frozen artifacts and prerequisites

| Object | Independently verified SHA-256 | Result |
|---|---|---|
| Canonical Sermon Owner `tasks/current/20261115-unified-share-sermon-publication-governance/DESIGN.md` | `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f` | Matches request |
| Website Stage D plan | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | Matches frozen SHA |
| Sermon Stage D plan | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | Matches; byte-identical to Website |
| Website Stage D implementation report | `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529` | Matches request |
| Sermon Stage D implementation report | `442a37c7f706ed513774c383449378cd7fc0e573239b7c3a7230097c5f574529` | Matches; byte-identical to Website |
| `content-presentation/v1` schema (Website / Sermon) | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | SHA matches; byte-identical |
| `website-publication-package/v1.3` schema (Website / Sermon) | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | SHA matches; byte-identical |
| `publication_contract_invariants.py` (Website / Sermon) | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | SHA matches; byte-identical |
| Stage D audit request | `8a5f62cc66c9a6fe17540dbbb37e808f6be6bc8221c6ce920a4e9105ecf14db8` | Matches request |

Commands for the five mirror comparisons were `cmp -s` on the Website construction worktree against the corresponding Sermon construction worktree paths; all five exited 0. SHA commands for both plan/report/schema/helper sets and canonical DESIGN exited 0.

Prerequisites were independently checked in Website `STATUS.md`, `docs/tasks/current.md`, task `TASK_INDEX.md`, the Stage C Re-Audit 04 report and the Master acceptance record:
- Stage A PASS.
- Stage B PASS / Master accepted.
- Stage C Re-Audit 04 `PASS_WITH_FINDINGS`, followed by Master `ACCEPTED · PASS_WITH_FINDINGS`.
- Stage C RF-01 path-based TOCTOU remains disclosed as a bounded non-blocking residual under the trusted raw-root threat model.
- Stage C earlier FAIL reports remain present and explicitly preserved; the later Re-Audit 04 result does not erase them.

The frozen Stage D plan's authority, purpose, bounded write-set and exclusions align with the canonical DESIGN. The actual changed paths in both construction worktrees are confined to the Stage D documented files plus pre-existing Stage A/B/C task artifacts and implementation changes. No Stage D scope expansion was identified.

## 3. D-01..D-12 mandatory result table

| ID | Result | Independent evidence and disposition |
|---|---|---|
| D-01 | **PASS** | Canonical DESIGN SHA matches the frozen plan's stated authority. Stage D plan SHA matches in both construction worktrees and its bounded documentation/entrypoint write-set aligns with DESIGN §6 and plan §3. Stage A/B/C prerequisites and Master acceptance were confirmed from current status/index and Stage C Re-Audit 04 evidence. No scope expansion or canonical-worktree mutation observed. |
| D-02 | **PASS** | Website `CONTENT_WORKFLOW.md` lines 10–12 and the unified workflow document explicitly bind Share to `NAS/分享收件`, Ronnie fallback-only, category `灵命成长`, `archive_status=not_applicable` / `SHARE_ARCHIVE_NOT_APPLICABLE`, and no NAS archive access; Sermon to `NAS/讲道收件`, Patrick fallback-only, category `教会讲道`, and protected append-only archive. Sermon Owner end-to-end workflow and metadata documents express the same distinctions. Package builder and v1.3 validator enforce Share archive `not_applicable` and disallow Sermon `not_applicable`. |
| D-03 | **PASS** | Website `scripts/validate_content_presentation.mjs` lines 65–138 implements an article-native Share profile: heading, paragraph, list, blockquote and internal-note integrity; it does not require sermon outline, Full Sermon Mode, discussion or benediction. Lines 148–159 delegate the Sermon profile to the existing sermon-specific validator. Owner docs preserve Full Sermon Mode and sermon-only structure gates. |
| D-04 | **PASS** | Sermon `docs/translation-fidelity-policy.md` adds only an explicit Share/Sermon integration statement; `docs/translation-fidelity-orchestration.md` changes the purpose sentence to clarify content-type neutrality. No fidelity loop, orchestration library, denominator, reviewer isolation, attempt/repair limit or release implementation was changed in the Stage D construction diff. The policy retains the same paired-record contract, bidirectional review and Attempt 01–03 / repair 01–03 release semantics. Website docs defer fidelity and Project Bible verdict authority to Sermon Owner. |
| D-05 | **PASS** | Sermon `scripts/run_translation_fidelity_loop.py` imports the existing `normalize_document` and lines 344–351 fail closed when candidate scripture normalization has not passed, instructing normalization before SHA freeze. `scripts/normalize_scripture_references.py` loads the controlled Project Bible 66-book inventory, rejects ambiguous aliases, and reports unresolved compact/non-normalized or English references as non-PASS. Owner normalization policy and both projects' Stage D docs place display normalization before candidate SHA freeze and retain compact machine metadata as an exception. |
| D-06 | **PASS** | Both schema copies and the shared invariant helper are byte-identical with matching hashes. Website consumer validates v1.3 package, content-root-bound prepublish and presentation artifacts, profile, exact identity and rendered structure; Sermon producer binds the candidate, paired records, presentation manifest/artifact and package. The v1.3 Share and Sermon fixtures use the correct distinct profiles. |
| D-07 | **FAIL** | Share direct-import protections remain present: `scripts/import_shares.py` lines 456–542 require v1.3 package/content root, validate the package, frontmatter metadata, bound presentation artifact, package-bound source identity and caller metadata, and block non-dry-run. But the Sermon v1.3 workflow path is not equivalently source-bound. See finding `D07-F01` below. |
| D-08 | **PASS** | Producer CLI help independently exposes explicit contract version 1.3 and required content-presentation manifest. Builder CLI help exposes explicit fidelity/archive/metadata and v1.3 manifest fields; implementation checks v1.3 manifest identity/profile/status and Share/Sermon archive semantics. Exporter CLI requires `--publication-package`, one explicit `--source`, and defaults to dry-run; exporter validates package version/type, prepublish path/SHA, official Chinese and English source SHAs, metadata, presentation manifest and cross-document identity. |
| D-09 | **PASS** | Stage D code changes do not rewrite historical packages/posts/URLs/articleIds or old audit evidence. Consumer retains explicit v1.1/v1.2 branches and the existing Sermon `sermon-presentation/v1` validator. Stage F前 docs distinguish current v1.2 Sermon / approved legacy Share production compatibility from v1.3 controlled plan/dry-run. Historical handoff and publication-record command strings remain historical evidence, not current operational instructions. |
| D-10 | **PASS** | Website `consume_publication_package.py` lines 260–264 rejects v1.3 `mode=publish` even when `allow_write=True`. `content_workflow.py` lines 275–276 independently rejects v1.3 non-dry-run. Share direct importer lines 540–541 also blocks non-dry-run. The exact negative test `V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f` passed. CLI help explicitly says `--allow-write` cannot override the Stage F block. Current production defaults/routes remain unchanged; Stage E/F were not executed. |
| D-11 | **PASS** | Independently rerun tests, CLI help, Python compile, Node syntax and `git diff --check` all exited 0. Exact commands/counts are in §5. The full Website suite ran 269 tests; focused v1.3/Stage C suite 68 executions; legacy suite 25 tests; Tag Pipeline 27/27; Sermon full suite 59 tests and producer/fidelity focused suite 35 tests. |
| D-12 | **PASS** | Exact roots, branch names and HEADs verified. Both construction worktrees retained their dirty lineages; staged count remained zero. Canonical Website remained clean; canonical Sermon's pre-existing dirty/untracked lineage and ahead-2 state were preserved. Final status inventory matches the pre-test inventory. Only the designated report was written. No prohibited Git or external side effects occurred. |

### D07-F01 — v1.3 Sermon package/source folder identity is not enforced at the lower-level workflow entrypoint

- Severity: **High / Stage D acceptance blocker**.
- Affected file: Website construction `scripts/content_workflow.py`.
- Relevant code:
  - Lines 192–220: when `--publication-package` is supplied, workflow checks package version/content type, presentation artifact path and v1.3 package validator result.
  - Lines 221–274: additional frontmatter/source/metadata-to-package identity resolution is implemented only inside `if kind == "share"`.
  - Lines 279–301: Sermon branch requires `--folder`, runs the sermon presentation structure validator, then appends the caller-provided `folder` to the `import_sermons.py` command. It does not compare that folder to the Sermon source selector derived from the package-bound prepublish `source`.
- Contrast:
  - `scripts/consume_publication_package.py` lines 114–140 derives and validates the package-bound Sermon source folder from prepublish frontmatter.
  - Lines 256–257 then correctly passes that derived `source_name` to the workflow.
  - This protection exists only when callers enter through `publish-contract`; the lower-level package-aware `content_workflow.py publish sermon` entrypoint remains directly callable and trusts its caller-supplied `--folder`.
  - `scripts/import_sermons.py` parse/main path (lines 582–593 and 695–720) accepts folder and presentation file but has no publication-package/source-identity argument or package validation of its own.
- Impact: a caller can supply a valid v1.3 Sermon package and its bound presentation artifact but a different existing Sermon folder to the package-aware workflow command. Package validation and artifact-path binding pass, while the import command is constructed for the caller-selected folder. This breaks the required package/source identity binding and could associate one sermon package's fidelity/presentation/metadata evidence with another sermon source.
- Current mitigation: all v1.3 non-dry-run paths remain fail-closed before Stage F. This finding does not establish that a production write occurred or is currently enabled. It does establish that the v1.3 dry-run/controlled workflow boundary is incomplete and that Stage D's D-07 acceptance requirement is not met.
- Required remediation boundary for Master: make the package-aware Sermon workflow independently derive/validate the package-bound source folder and reject any caller mismatch before the importer/renderer dispatch; preserve the separate v1.2 legacy compatibility route. Add focused negative tests for mismatched folder, correct folder, missing folder, and package-bound metadata/source identity; then rerun relevant full/focused tests and request a fresh independent audit. This Auditor does not implement that remediation.

## 4. Documentation conflict matrix

| Location | Finding | Classification |
|---|---|---|
| Website `CONTENT_WORKFLOW.md`, `docs/统一内容整理与发布流程.md`, `skills/article-workflow.md` | Current operating instructions now explicitly label `publish share` and `publish sermon` as Stage F前 compatibility routes and `publish-contract` as the v1.3 controlled consumer. | Resolved |
| Sermon `AGENTS.md`, `docs/end-to-end-content-publishing-workflow.md`, `docs/chinese-to-prepublish-md-workflow.md`, metadata and scripture normalization docs | New-content order, profile differences, identity fallback and archive semantics align with canonical DESIGN and Website docs. | Resolved |
| Sermon `docs/translation-fidelity-policy.md` and `docs/translation-fidelity-orchestration.md` | Changes clarify the existing common state machine; no fidelity implementation or release semantics changed. | Resolved |
| Website `docs/codex-handoff-memory.md` and historical publication-record command strings | Legacy `publish share` / `publish sermon` strings remain outside the Stage D write-set. Current workflow docs explicitly demote handoff memory to historical context; publication records are historical evidence and are not current entrypoint instructions. | Historical / non-blocking |
| Website package-aware Sermon workflow dispatch | The docs assert the direct importer/package/source/metadata boundary is independently enforced, but the actual v1.3 Sermon workflow branch does not bind caller `--folder` to package source. | **Unresolved material conflict — D07-F01** |

No historical reference was rewritten or reclassified. Stage C FAIL chronology remains intact; Stage C Re-Audit 04 PASS_WITH_FINDINGS and subsequent Master acceptance close Stage C only.

## 5. Independently executed verification

### Website construction worktree

| Command | Result | Exit |
|---|---:|---:|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q` | 269 tests, OK | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -q` | 68 executions, OK | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -q` | 25 tests, OK | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package_v13.V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f -v` | 1 test, OK | 0 |
| `npm run check:tags` | 27/27 PASS | 0 |
| `python3 scripts/content_workflow.py publish-contract --help` | Help rendered with plan/dry-run/publish and Stage F block | 0 |
| `PYTHONPYCACHEPREFIX=/tmp/ronniecross-stage-d-audit-pycache python3 -m py_compile scripts/content_workflow.py scripts/consume_publication_package.py scripts/import_shares.py scripts/import_sermons.py scripts/validate_publication_package_v13.py` | PASS | 0 |
| `node --check scripts/validate_content_presentation.mjs` | PASS | 0 |
| `git diff --check` | PASS | 0 |

### Sermon construction worktree

| Command | Result | Exit |
|---|---:|---:|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q` | 59 tests, OK | 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_build_website_publication_package scripts.tests.test_export_to_website_contract scripts.tests.test_unified_publication_producer_stage_b scripts.tests.test_share_fidelity_loop_stage_b scripts.tests.test_unified_publication_contract_stage_a -q` | 35 tests, OK | 0 |
| `python3 scripts/generate_prepublish_md.py --help` | Help rendered; explicit v1.3 manifest and contract flags present | 0 |
| `python3 scripts/build_website_publication_package.py --help` | Help rendered; explicit v1.3 and presentation/archive/fidelity fields present | 0 |
| `python3 scripts/export_to_website_project.py --help` | Help rendered; package required, explicit source, default dry-run | 0 |
| `PYTHONPYCACHEPREFIX=/tmp/sermon-stage-d-audit-pycache python3 -m py_compile scripts/generate_prepublish_md.py scripts/build_website_publication_package.py scripts/export_to_website_project.py scripts/run_translation_fidelity_loop.py` | PASS | 0 |
| `git diff --check` | PASS | 0 |

Negative Sermon presentation fixture output printed during the Website full suite is expected test evidence; unittest summary was `Ran 269 tests ... OK`, exit 0. The focused suite reports executions, not unique tests; no claim is made that 68 executions are 68 unique test cases.

## 6. Workspace identity and Git lineage

All roots below were opened exactly as specified. Branch/HEAD were read independently using `git rev-parse`; status inventories were captured with CodexPro review status. No staged changes were present.

| Workspace | Workspace ID | Branch | HEAD | Final status inventory |
|---|---|---|---|---|
| Website construction | `ws_36904a3d8e03f8682750de45` | `task/unified-share-sermon-publication-stage-a-20261116` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | 12 modified tracked; 43 untracked; 0 staged |
| Sermon construction | `ws_0c1dbdff4bf12c1dc97eee92` | `task/unified-share-sermon-publication-stage-a-20261116` | `812ace500102bac54cb54cb0fa2249341118a3da` | 19 modified tracked; 37 untracked; 0 staged |
| Canonical Website (read-only) | `ws_24bb9de8a7d62a054469455b` | `main` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | clean; 0 modified; 0 untracked; 0 staged |
| Canonical Sermon Owner (read-only) | `ws_8e32016bc287b4ef40f8e9d5` | `master` | `812ace500102bac54cb54cb0fa2249341118a3da` | pre-existing 15 modified tracked; 57 untracked; 0 staged; branch was ahead 2 of origin at opening |

Construction worktree dirty states are the implementation lineage under audit, not Auditor-created changes. Canonical Sermon dirty state includes unrelated ongoing sermon/fidelity work and was not modified or cleaned. Canonical Website remained clean.

## 7. Auditor writes and prohibited side effects

The only file written by this Auditor is:

`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_AUDIT_REPORT.md`

No other file was created, edited or deleted by this Auditor. The report path was confirmed absent before writing; no prior report was overwritten.

The following were not performed:
- No implementation or remediation; no changes to STATUS, current indexes, plan, implementation report, docs, scripts, tests, schemas, fixtures or historical evidence.
- No Git staging, commit, push, merge, reset, clean, rebase, amend, branch change or stash.
- No production import/export; no raw/processed/posts writes.
- No Astro build, deployment, notification or email.
- No NAS probe, read, write or archive.
- No dependency installation or upgrade.
- No Stage E synthetic E2E execution.
- No Stage F enablement or production activation.
- No canonical worktree writes.

Test runners used temporary test fixtures. Python bytecode generation was disabled or redirected to `/tmp`. The `git diff --check` commands were read-only.

## 8. Residual risks and re-evaluation triggers

1. **D07-F01 must be closed before Stage D can pass or Stage E is started.** Re-audit the package-aware Sermon workflow after remediation, including adversarial source-folder mismatch. Preserve the current v1.2 compatibility route as a separately versioned path.
2. Stage C RF-01 (path-based TOCTOU in Share source identity) remains the previously accepted, disclosed non-blocking residual under the current trusted raw-root threat model. Re-evaluate if untrusted concurrent writers can modify the configured raw root; consider descriptor-based no-follow open and identity-preserving handoff.
3. Historical legacy command references outside the frozen Stage D write-set remain historical only. Re-evaluate if any is promoted back into current operational docs or automation.

## 9. Chronology and final disposition

Stage C chronology remains: initial FAIL → Re-Audit 01 FAIL → Re-Audit 02 FAIL → Re-Audit 03 FAIL / LEGACY-01 → Remediation 04 independent Re-Audit 04 PASS_WITH_FINDINGS → Master accepted PASS_WITH_FINDINGS. No prior report or status was overwritten.

Stage D implementation remains `IMPLEMENTATION_COMPLETE_PENDING_INDEPENDENT_AUDIT`, but this independent audit finds D-07 unsatisfied. **Formal verdict: FAIL.** Return to Master for the bounded D07-F01 remediation and a fresh independent re-audit. This report does not accept Stage D and does not authorize Stage E or Stage F.
