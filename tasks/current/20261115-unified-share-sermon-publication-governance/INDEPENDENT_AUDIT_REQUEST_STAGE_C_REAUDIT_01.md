# Independent Re-Audit Request — Stage C Website Consumer / Remediation 01

You are the independent read-only Auditor for the Stage C Website Consumer remediation round.

## Exact workspace

`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`

First call `open_current_workspace`, then open the exact workspace above. Confirm exact root, branch, HEAD and staged/unstaged/untracked state before auditing.

Expected branch: `task/unified-share-sermon-publication-stage-a-20261116`
Frozen baseline HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`

## Required fresh-read

Read:
- `AGENTS.md`
- `STATUS.md`
- `docs/tasks/current.md`
- `CONTENT_WORKFLOW.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_PLAN.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_01_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C_REAUDIT_01.md`
- `scripts/import_shares.py`
- `scripts/content_workflow.py`
- `scripts/consume_publication_package.py`
- `scripts/validate_publication_package_v13.py`
- `scripts/tests/test_import_share_presentation.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- Both Website schemas and `scripts/publication_contract_invariants.py`.

Read the authoritative Owner copies in:
`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`

Confirm Stage B accepted Re-Audit 01 SHA-256:
`9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`

## Historical chronology — preserve exactly

The initial Stage C independent audit was **FAIL**. Its report remains unchanged at:
`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_AUDIT_REPORT.md`

Auditor-reported SHA-256:
`967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47`

Findings:
- F-01 P1: direct Share presentation importer bypassed mandatory publication package validation and could write.
- F-02 P2: underlying workflow did not bind caller-supplied source and metadata to SHA-bound prepublish identity.

Do not edit, replace, rename, or reclassify this FAIL report. A new PASS, if supported, is a later chronology event and does not erase the FAIL.

## Role and permissions

- Role: `INDEPENDENT_AUDITOR`.
- Read-only audit. Do not edit implementation, tests, schemas, plans, implementation reports, STATUS or task indexes.
- The only authorized write path is:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_01_REPORT.md`
- No dependency installation/upgrade, production import, build, NAS access/write, notification/email, commit, push, merge or deploy.
- Do not start Stage D/E/F.
- Do not assume tests passing proves the security boundary; perform adversarial code review and safe temporary-directory tests.

## Mandatory re-audit propositions

### 1. Workspace isolation and chronology
- Confirm exact root, branch, frozen HEAD, staged state and changed paths.
- Confirm canonical Website `main` remains clean/unchanged.
- Confirm canonical Sermon pre-existing dirty lineage is untouched.
- Confirm Stage B construction artifacts and accepted report remain unchanged.
- Confirm original Stage C FAIL report SHA remains exact.

### 2. F-01 — importer entrypoint security (P1)
Independently inspect the actual `scripts/import_shares.py` CLI and `main()` call path, not only helper functions.

Adversarially verify:
- `--presentation-file` without `--publication-package` and `--content-root` fails closed.
- Rejection occurs before creation of processed/posts/report directories or files.
- Invalid package, wrong version/content_type, package validator FAIL, malformed package and missing package-bound files all fail closed.
- A valid package paired with a different presentation artifact fails closed, even if that artifact is otherwise valid Markdown.
- A valid package with source selector different from package-bound prepublish source fails closed.
- A valid package with caller-supplied metadata mismatch fails closed.
- Direct non-dry-run v1.3 presentation import remains blocked before Stage F and creates no output.
- A valid package-bound direct dry-run can pass without writes.
- The package is independently validated at the importer boundary; this must not rely on workflow having run first.
- Legacy Share path without `--presentation-file` remains unchanged.

### 3. F-02 — underlying workflow identity binding (P2)
Inspect and adversarially exercise the actual `content_workflow.publish()` implementation:
- caller source must match the exact source selector in package-bound prepublish frontmatter;
- title, description, scripture, tags, author, publish date and slug must be checked against prepublish/package metadata;
- prepublish author/date/category/contentType must agree with package metadata;
- mismatches must fail before renderer and importer invocation;
- omitted optional values must be derived from the bound package rather than arbitrary defaults;
- package path and content root must be forwarded to the importer for its independent validation;
- valid package + valid values must continue through the intended dry-run route;
- v1.3 non-dry-run must remain blocked.

Do not accept a test that only asserts a helper return value. Verify invocation boundaries and zero downstream calls for mismatches.

### 4. Package and presentation identity
- Verify exact artifact path binding and SHA verification.
- Verify prepublish body equals the bound artifact after only the declared frontmatter separator.
- Verify source path traversal, wrong root, symlink aliases, wrong source type and path collision remain blocked.
- Verify all package, manifest, report, paired package and candidate identities and hashes remain enforced.
- Verify the importer does not transform the frozen body through legacy normalization/formatting.

### 5. Existing contract/profile behavior
Recheck the Stage C contract mirror/schema, fidelity boundary, Share/Sermon profile separation, TTS/scripture detection-only behavior, Share archive not_applicable semantics, Sermon protected archive semantics, and v1.0/v1.1/v1.2 compatibility. Confirm no Stage F production default was enabled.

### 6. Regression and test quality
Run and report exact exit codes and actual counts:
- Full Python suite: `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` (previous remediation result 258/258).
- Stage C focused five modules: `python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation -v` (previous remediation result 57/57).
- Legacy compatibility: `python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v` (25/25).
- Share Tag Pipeline: `npm run check:tags` (27/27).
- Python compile, Node syntax and `git diff --check`.

Inspect whether new tests contain meaningful assertions, actually call the importer, assert zero writes on rejection, and prove mismatches fail before renderer/importer invocation. Correctly account for overlapping test module counts.

### 7. Required report

Write only:
`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_01_REPORT.md`

Report must contain:
- formal verdict: PASS / PASS_WITH_FINDINGS / PARTIAL / FAIL / BLOCKED;
- separate F-01 and F-02 disposition, with exact source locations and adversarial evidence;
- each proposition result;
- actual test counts and command exit codes;
- workspace identity and dirty/staged state;
- historical FAIL report SHA read-back;
- explicit confirmation of all prohibited side effects not performed;
- report SHA-256 after read-back.

Stage C remains unaccepted until Master independently reads and accepts a formal independent PASS. Stage D remains BLOCKED until then. Stage F remains disabled.
