# Independent Re-Audit Request — Stage C Source Identity Hardening / Remediation 03

## Role

You are the **INDEPENDENT_AUDITOR** for Stage C Website Consumer Source Identity Hardening Remediation 03. This is an independent, read-only audit. Do not implement or repair findings.

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
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_PLAN.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_01_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_02_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_03_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C_REAUDIT_02.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_AUDIT_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_01_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_02_REPORT.md`
- `scripts/share_source_identity.py`
- `scripts/publication_contract_invariants.py`
- `scripts/content_workflow.py`
- `scripts/import_shares.py`
- `scripts/consume_publication_package.py`
- `scripts/validate_publication_package_v13.py`
- `scripts/tests/test_share_source_identity.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- `scripts/tests/test_import_share_presentation.py`
- `scripts/tests/test_validate_publication_package_v13.py`
- `contracts/content-presentation-v1.schema.json`
- `contracts/website-publication-package-v1.3.schema.json`

## Historical evidence identity — recompute and preserve

- Stage C initial FAIL: `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47`
- Stage C Re-Audit 01 FAIL: `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c`
- Stage C Re-Audit 02 FAIL: `88b6c116ee2087e5e5a0d12c627aaa7e7d471d470f8eb8b7cdb206fde5178963`
- Stage B accepted Re-Audit 01 PASS: `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`

Do not edit, replace, rename, or reclassify historical reports.

## Scope and permissions

- Independently inspect the real `content_workflow.publish()` and `import_shares.main()` call paths.
- Adversarially exercise both source identity helper functions and the package-bound helper API.
- Read the Sermon Owner construction workspace only to verify the shared helper/schema mirror; do not write there.
- Canonical Website `main` and canonical Sermon worktree are read-only.
- No implementation/test/schema/docs/status/index edits.
- The only authorized write path is:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_03_REPORT.md`
- No dependency install/upgrade, production import, Astro build, NAS access/write, notification/email, commit, push, merge or deploy.
- Do not start Stage D/E/F.

## Mandatory propositions

### 1. Website-local source identity helper

Verify directly:
- `resolve_share_source_path(selector, source_root)` is only the initial path-resolution operation and requires an existing direct regular file.
- `resolve_package_bound_share_source(selector, source_root, *, expected_source)` is distinct and strictly package-bound.
- Omitting `expected_source` raises `TypeError`; `None`, empty, malformed, absolute, nested, traversal, dot-alias, backslash, non-normalized values fail closed.
- Package source is exactly normalized POSIX `data/raw/分享/<filename>`, and selected filename must match it.
- Missing file, directory, selected symlink, broken symlink, internal symlink alias, external symlink alias all fail closed.
- Existing valid source resolves to a direct regular file under the trusted configured Share raw root.
- Inspect trusted-root/symlinked parent and TOCTOU behavior. The implementation report explicitly discloses that validation is path-based rather than an atomic no-follow descriptor handoff. Determine whether this is a material finding under the current threat model; do not silently ignore it or assume it is a failure without analysis.

### 2. F-01 — direct importer entrypoint

Safely exercise actual `import_shares.main()` with valid Share v1.3 package:
- package-bound source filename: dry-run passes;
- missing source: fail before output directories;
- nested path, traversal, dot alias, absolute path;
- different existing source;
- internal and external symlink aliases.

For every invalid case, verify no processed/posts/report output directories or files are created. Confirm importer independently validates package/schema, artifact binding, prepublish metadata, package-bound source and caller metadata. Confirm non-dry-run remains blocked before Stage F and legacy Share import without presentation package remains compatible.

### 3. F-02 — workflow boundary

Exercise actual `content_workflow.publish()`:
- valid package + valid existing source: renderer and importer dry-run route remains usable; package path/content root are forwarded.
- valid package + missing source, directory, broken symlink: reject before renderer/importer invocation.
- nested path, traversal, dot alias, absolute path, internal/external symlink alias and distinct-basename mismatch: reject before renderer/importer.
- metadata spoofing still fails before renderer/importer.
- v1.3 non-dry-run remains blocked.
- Assert exact subprocess call sequence/count; package validator may run, renderer/importer must not run for invalid source.

### 4. Owner mirror and contract

Read exact files in:
`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`

Verify byte identity:
- Website `scripts/publication_contract_invariants.py` vs Sermon Owner `scripts/publication_contract_invariants.py`; expected SHA both `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0`.
- Website `contracts/content-presentation-v1.schema.json` vs Sermon Owner `docs/contracts/content-presentation-v1.schema.json`; expected SHA both `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5`.
- Website `contracts/website-publication-package-v1.3.schema.json` vs Sermon Owner `docs/contracts/website-publication-package-v1.3.schema.json`; expected SHA both `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e`.
- Confirm Website-only source identity logic is isolated in `scripts/share_source_identity.py`; shared invariant helper contains no Website-specific selector logic.

### 5. Regression and test quality

Run and report exact exit codes and actual counts:
- Full Python: `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` (Master run: 266/266).
- Stage C focused six modules:
  `python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -v`
  (Master run: 65 executions; subtract 17 inherited duplicate executions; 48 unique).
- Legacy compatibility:
  `python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v` (25/25).
- Share Tag Pipeline: `npm run check:tags` (27/27).
- Python compile, Node syntax, `git diff --check`.

Independently inspect that tests call actual `publish()` / `main()`, that missing source is represented by a genuinely empty raw root, and that no renderer/importer call or output write occurs for rejected cases. Do not count inherited duplicates as independent coverage.

### 6. Workspace, chronology and side effects

- Confirm exact workspace root, branch, frozen HEAD and staged/unstaged/untracked state.
- Confirm Stage C historical FAIL reports retain exact hashes above.
- Verify canonical Website remains unchanged/clean; verify Sermon Owner worktree was read-only and retains existing dirty lineage. If evidence is unavailable, mark BLOCKED rather than infer.
- Confirm no production import, build, NAS, notification, email, dependency change, commit, push, merge or deploy occurred.
- Confirm current production routes/defaults are unchanged, v1.3 non-dry-run remains disabled, Stage D BLOCKED, Stage E not started and Stage F disabled.

## Verdict

Use the fixed overall verdict vocabulary:
- `PASS`: all mandatory propositions pass, no material residual finding.
- `PASS_WITH_FINDINGS`: all mandatory propositions pass but a bounded non-blocking finding remains.
- `FAIL`: one or more mandatory propositions fail.
- `BLOCKED`: required evidence/access unavailable.

Report each proposition separately. Do not treat Master's implementation report or local tests as independent proof. The audit report must include exact evidence, commands/counts, hashes, write-set, and chronology.

