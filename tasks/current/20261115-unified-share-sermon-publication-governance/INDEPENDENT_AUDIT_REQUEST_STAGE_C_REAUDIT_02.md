# Independent Re-Audit Request — Stage C Source Identity Hardening / Remediation 02

## Role

You are the **INDEPENDENT_AUDITOR** for Stage C Website Consumer Source Identity Hardening Remediation 02. This is a read-only independent re-audit, not implementation.

## Exact workspace

/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116

First call open_current_workspace, then open this exact workspace. Confirm exact root, branch, HEAD, staged/unstaged/untracked state.

Expected branch: task/unified-share-sermon-publication-stage-a-20261116  
Expected frozen HEAD: 09ce7eb588a21745d0286d3eec6a890c16a26aea

## Fresh-read

Read all of:

- AGENTS.md
- STATUS.md
- docs/tasks/current.md
- CONTENT_WORKFLOW.md
- tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_PLAN.md
- tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_REPORT.md
- tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_01_REPORT.md
- tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_02_REPORT.md
- tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C_REAUDIT_01.md
- tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_AUDIT_REPORT.md
- tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_01_REPORT.md
- scripts/publication_contract_invariants.py
- scripts/import_shares.py
- scripts/content_workflow.py
- scripts/consume_publication_package.py
- scripts/validate_publication_package_v13.py
- scripts/tests/test_import_share_presentation.py
- scripts/tests/test_content_workflow_v13_share.py
- scripts/tests/test_validate_publication_package_v13.py
- contracts/website-publication-package-v1.3.schema.json
- contracts/content-presentation-v1.schema.json

Historical report identities to verify unchanged:

- Stage C initial FAIL: 967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47
- Stage C Re-Audit 01 FAIL: 48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c
- Stage B accepted Re-Audit 01 PASS: 9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea

## Scope and permissions

- Independently inspect the actual CLI/main call path of scripts/import_shares.py and actual content_workflow.publish() path.
- Adversarially inspect and safely exercise the source selector helper. Do not rely on implementation report assertions alone.
- No implementation/test/schema/doc/status/index edits.
- The only authorized write path is:
  tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_02_REPORT.md
- No dependency installation/upgrade, production import, Astro build, NAS access/write, notification/email, commit, push, merge or deploy.
- Do not start Stage D/E/F.

## Mandatory propositions

### 1. Shared source identity helper

Verify that the helper:

- requires the package source to be exactly a normalized POSIX relative path data/raw/分享/<filename>;
- rejects absolute paths, nested paths, traversal, dot aliases (including ./sample.txt), backslash separators and non-normalized paths;
- rejects missing/malformed package-bound source values;
- rejects symlink aliases both when they point inside the Share raw root and outside it;
- confirms the resolved file is a direct regular file in the configured Share source root;
- compares the selected filename to the exact package-bound filename, not merely a caller-supplied basename detached from the canonical source path.

Check for symlinked directory/parent edge cases and TOCTOU gaps where relevant. Distinguish the configured trusted source root from caller-controlled selector input.

### 2. F-01 — direct importer entrypoint (P1)

Independently invoke or safely test import_shares.main() with a valid Share v1.3 package and:

- normal package-bound source filename (must pass dry-run);
- nested raw path;
- traversal;
- dot alias;
- absolute path;
- a different existing file in raw root;
- internal symlink alias to the package-bound source;
- external symlink alias to a file outside raw root.

Every invalid selector must fail closed before output directories/files are created. Verify package and presentation validation still happen independently at importer boundary, metadata binding remains intact, and non-dry-run remains blocked before Stage F.

Also verify the legacy Share route without --presentation-file is not inadvertently changed.

### 3. F-02 — workflow boundary (P2)

Exercise actual content_workflow.publish() with a valid package and the same selector attack classes.

For every invalid selector, prove rejection occurs before renderer and importer invocation. In particular, nested selector sub/sample.txt must not be normalized to sample.txt and forwarded.

Verify the distinct-basename source mismatch and metadata mismatch tests remain effective; package path/content root still reach the importer; valid package-bound dry-run remains usable; v1.3 non-dry-run remains blocked.

### 4. Regression and test quality

Run and report exact exit codes and actual counts:

- Full Python: python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v (expected 260/260 from Master run)
- Stage C focused five modules:
  python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation -v
  (expected 59 executions; account for 17 inherited duplicate test executions; deduplicated independent count 42)
- Legacy compatibility:
  python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v
  (expected 25/25)
- Share Tag Pipeline: npm run check:tags (expected 27/27)
- Python compile, Node syntax, git diff --check.

Review that direct importer tests call main(), assert zero output directories on rejection, and workflow tests prove zero renderer/importer calls. Do not count inherited duplicate tests as independent coverage.

### 5. Workspace and chronology

- Confirm branch/HEAD and no staged changes.
- Confirm the historical FAIL reports retain exact hashes.
- Confirm this remediation did not change canonical Website main or canonical Sermon worktree; if external access is not available, mark that proposition BLOCKED rather than infer.
- Confirm no prohibited side effects.
- Confirm Stage F remains disabled and current production routes remain unchanged.

## Required report

Write only:

tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_02_REPORT.md

Include:

- formal verdict: PASS / PASS_WITH_FINDINGS / PARTIAL / FAIL / BLOCKED;
- separate F-01 and F-02 dispositions;
- helper-level security analysis and adversarial evidence;
- exact source locations and test evidence;
- each mandatory proposition result;
- exact commands, counts, exit codes and duplicate-test accounting;
- workspace identity and staged/unstaged/untracked state;
- historical report SHA read-back;
- prohibited side effects not performed;
- report SHA-256 after read-back.

Stage C remains unaccepted until Master independently reads and separately accepts a formal independent PASS. Stage D remains BLOCKED; Stage F remains disabled.
