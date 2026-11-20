# Independent Re-Audit Request — Stage C Legacy Share Author Compatibility / Remediation 04

## Role

You are the **INDEPENDENT_AUDITOR** for Stage C Remediation 04. This is an independent, read-only audit. Do not implement or repair findings.

## Exact workspace

`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`

First call `open_current_workspace`, then open this exact workspace. Confirm exact root, branch, HEAD, staged/unstaged/untracked state.

Expected branch: `task/unified-share-sermon-publication-stage-a-20261116`  
Expected frozen HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`

## Fresh-read

Read:
- `AGENTS.md`
- `STATUS.md`
- `docs/tasks/current.md`
- `CONTENT_WORKFLOW.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_03_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_04_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C_REAUDIT_03.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_03_REPORT.md`
- prior Stage C initial / Re-Audit 01 / Re-Audit 02 reports
- `scripts/content_workflow.py`
- `scripts/import_shares.py`
- `scripts/share_source_identity.py`
- `scripts/publication_contract_invariants.py`
- `scripts/consume_publication_package.py`
- `scripts/validate_publication_package_v13.py`
- `scripts/tests/test_import_share_presentation.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- `scripts/tests/test_share_source_identity.py`
- `contracts/content-presentation-v1.schema.json`
- `contracts/website-publication-package-v1.3.schema.json`

## Historical evidence identity — recompute and preserve

- Stage C initial FAIL: `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47`
- Stage C Re-Audit 01 FAIL: `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c`
- Stage C Re-Audit 02 FAIL: `88b6c116ee2087e5e5a0d12c627aaa7e7d471d470f8eb8b7cdb206fde5178963`
- Stage C Re-Audit 03 FAIL / LEGACY-01: `8656e20ed2f421b69dff0b9f39d9dba8d3ef6474e7b434168394badd296a63a5`
- Stage B accepted Re-Audit 01 PASS: `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`

Do not edit, replace, rename, or reclassify historical reports.

## Scope and permissions

- Independently verify Remediation 04 and all Stage C invariants that must remain in force.
- Exercise the real direct importer and workflow-to-importer path using temporary files/directories only.
- Read the Sermon Owner construction workspace only to verify shared helper/schema mirrors; do not write there.
- Canonical Website `main` and canonical Sermon worktree are read-only.
- No implementation/test/schema/docs/status/index edits.
- The only authorized write path is:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_04_REPORT.md`
- No production import, Astro build, NAS access/write, notification/email, dependency install/upgrade, commit, push, merge or deploy.
- Do not start Stage D/E/F.

## Mandatory propositions

### 1. LEGACY-01 — direct importer author default

Independently exercise the actual `import_shares.main()` legacy path (no `--presentation-file`, no package):

- Omitted `--author`: no AttributeError; dry-run completes with Ronnie fallback.
- Explicit empty `--author ""`: safe Ronnie fallback; no AttributeError.
- Explicit non-empty `--author`: value is preserved.
- Confirm all probes use temporary raw/output paths and dry-run; no output directories/files are created.
- Inspect parser and author resolution to confirm `None` is safe, not merely the argparse CLI case.

### 2. LEGACY-01 — actual workflow-to-importer chain

Exercise actual `content_workflow.publish()` and actual `import_shares.main()` together, not only mocked command construction:

- Omitted author: workflow dispatches Ronnie and importer completes dry-run.
- Empty author: workflow dispatches Ronnie and importer completes dry-run.
- Explicit non-empty author: exact author is forwarded and retained.
- Verify the legacy path remains the one without presentation/package arguments.
- Verify no production/raw/processed/posts/report write occurs.

### 3. v1.3 author identity isolation

The legacy fallback must not override v1.3 package-bound metadata:

- Exercise a valid v1.3 Share package whose package-bound author is a non-Ronnie value, with caller author omitted; the importer must use the package-bound value.
- Exercise explicit mismatching author; it must fail closed as an identity mismatch before writes.
- Confirm v1.3 remains dry-run only before Stage F.
- Inspect that the parser default/fallback design does not accidentally force Ronnie into v1.3.

### 4. Previously passing Stage C invariants

Recheck at least the following, using actual entrypoints where practical:

- Website-local source helper: strict `expected_source` API; missing, directory, broken symlink, nested/traversal/dot/absolute and internal/external symlink selectors fail closed.
- F-01: direct v1.3 importer requires and independently validates package, artifact, source and metadata; invalid cases fail before output directory creation.
- F-02: workflow rejects missing/non-regular source before renderer/importer; metadata spoofing and invalid source selectors do not reach renderer/importer.
- Owner shared helper and both schemas remain byte-identical to the Sermon Owner copies at the known expected hashes:
  - helper: `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0`
  - content-presentation schema: `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5`
  - publication package schema: `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e`
- Website-only selector code remains isolated in `scripts/share_source_identity.py`.
- Stage F v1.3 non-dry-run remains disabled.

### 5. Regression and test quality

Run and report exact exit codes and counts:

- Full Python: `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q` (Master run: 269/269).
- Stage C focused six modules:
  `python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -q`
  (Master run: 68 executions; subtract 17 inherited duplicates; 51 unique).
- Legacy compatibility:
  `python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -q` (25/25).
- Share Tag Pipeline: `npm run check:tags` (27/27).
- Python compile, Node syntax, `git diff --check`.

Do not treat Master's report or local test results as independent proof. Inspect whether tests truly execute the actual functions and whether all filesystem effects are contained in temporary directories.

### 6. Workspace, chronology and side effects

- Confirm exact workspace root, branch, frozen HEAD and staged/unstaged/untracked state.
- Recompute the historical report hashes above; all must remain unchanged.
- Verify canonical Website remains unchanged/clean; verify Sermon Owner worktree is read-only and retains existing dirty lineage. If evidence is unavailable, mark BLOCKED rather than infer.
- Confirm no production import, build, NAS, notification, email, dependency change, commit, push, merge or deploy occurred.
- Confirm production routes/defaults unchanged, Stage D BLOCKED, Stage E not started and Stage F disabled.

## Verdict

Use the fixed overall verdict vocabulary:
- `PASS`: all mandatory propositions pass, no material residual finding.
- `PASS_WITH_FINDINGS`: all mandatory propositions pass but a bounded non-blocking finding remains.
- `FAIL`: one or more mandatory propositions fail.
- `BLOCKED`: required evidence/access unavailable.

Report each proposition separately. Include exact evidence, commands/counts, hashes, write-set, and chronology. Preserve the Re-Audit 03 FAIL as historical chronology even if this Re-Audit 04 passes.
