# Stage C Source Identity Hardening — Remediation 02 Report

## 1. Disposition

Master implementation disposition: **Remediation 02 implemented; local verification PASS; independent Re-Audit 02 required.**

This report records implementation evidence only. It does not close the historical Stage C FAIL findings, does not accept Stage C, and does not authorize Stage D/E/F.

## 2. Exact workspace and baseline

- Workspace root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Workspace ID: `ws_36904a3d8e03f8682750de45`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea` (unchanged; construction branch remains uncommitted)
- Staged changes: none.
- The worktree already contained the Stage A/Stage C construction write-set and Remediation 01 artifacts. This remediation adds only the bounded source-identity hardening and its evidence; pre-existing construction files and audit chronology remain present.
- Canonical Website `main` and canonical Sermon worktree were not used for writes.

## 3. Findings addressed

### F-01 — direct importer source identity (P1)

`scripts/import_shares.py` now takes the v1.3 path through `resolve_v13_source_file()` before any output-directory creation. The direct importer then independently rechecks the package-bound source identity inside `validate_v13_import_identity()`.

The shared `resolve_share_source_selector()` in `scripts/publication_contract_invariants.py` enforces:

- The package-bound source must be exactly one normalized POSIX relative path of the form `data/raw/分享/<filename>`.
- The caller selector is one filename only; slash, backslash, nested path, dot alias, traversal and absolute path are rejected.
- A symlink at the selected source filename is rejected, whether it points inside or outside the raw Share root.
- The resolved file must be a direct regular file in the configured Share source root.
- The selected filename must equal the package-bound filename; a different existing file with the same source-root parent is rejected.

The v1.3 direct importer still independently validates package/schema, presentation artifact binding, prepublish metadata and caller-supplied metadata. Stage F pre-activation write blocking remains unchanged.

### F-02 — workflow source identity before downstream calls (P2)

`scripts/content_workflow.py` calls the same shared selector validator against `RAW_DIRS["share"]` and the package-bound prepublish `source` before invoking the Share renderer or importer.

Invalid selectors fail with `V13_PACKAGE_IDENTITY_MISMATCH`. The workflow does not normalize a nested selector to its basename. Existing metadata checks and package/content-root forwarding remain intact.

### Shared invariant

The shared helper retains the existing `validate_package_presentation_bindings()` behavior and adds the source-selector rule; it does not change the v1.3 schema or the Sermon Owner contract.

## 4. New adversarial tests

Direct `import_shares.main()` entrypoint test covers:

- nested raw path (`sub/sample.txt`);
- traversal (`../sample.txt`);
- dot alias (`./sample.txt`);
- absolute path;
- different existing source file;
- internal symlink alias;
- external symlink alias.

Each case asserts fail-closed and confirms processed/posts/report output directories are not created.

Actual `content_workflow.publish()` test covers:

- nested raw path;
- traversal;
- dot alias;
- absolute path;
- internal symlink alias;
- external symlink alias.

Each case asserts rejection after package validation but before renderer/importer invocation. The existing distinct-basename source mismatch test also remains and asserts no renderer/importer invocation.

The existing valid package-bound direct dry-run test remains passing and asserts no writes.

## 5. Final verification

All commands below were rerun after the final source changes. Exit codes are exact.

| Verification | Result | Exit |
|---|---:|---:|
| Stage C five-module focused suite | 59 executions PASS; 42 unique tests after removing 17 inherited duplicate executions | 0 |
| Legacy consumer compatibility suite | 25/25 PASS | 0 |
| Share Tag Pipeline | 27/27 PASS | 0 |
| Full Python suite | 260/260 PASS | 0 |
| Python compile (changed Python modules/tests) | PASS | 0 |
| Node syntax check (`validate_content_presentation.mjs`) | PASS | 0 |
| `git diff --check` | PASS | 0 |

Focused command:

```text
python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation -v
```

The focused command executes 59 tests because `test_import_share_presentation` inherits the 17 tests from `PublicationPackageV13ConsumerValidationTests`, which are already run as a separate focused module. The deduplicated count is therefore 42, not 59 independent tests.

Full Python command:

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
```

Legacy command:

```text
python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v
```

Tag command: `npm run check:tags`.

Compile command:

```text
python3 -m py_compile scripts/publication_contract_invariants.py scripts/import_shares.py scripts/content_workflow.py scripts/tests/test_import_share_presentation.py scripts/tests/test_content_workflow_v13_share.py
```

Node command: `node --check scripts/validate_content_presentation.mjs`.

Diff check: `git diff --check`.

## 6. Changed files in this remediation

- `CONTENT_WORKFLOW.md` — documents canonical source identity and fail-closed path rules.
- `STATUS.md` — records Remediation 01 Re-Audit 01 FAIL chronology and Remediation 02 pending audit.
- `docs/tasks/current.md` — records current disposition and next gate.
- `scripts/publication_contract_invariants.py` — shared source identity resolver; existing package/presentation invariant retained.
- `scripts/import_shares.py` — strict v1.3 source resolver and direct importer identity recheck.
- `scripts/content_workflow.py` — pre-render/pre-import source selector validation.
- `scripts/tests/test_import_share_presentation.py` — direct importer adversarial cases.
- `scripts/tests/test_content_workflow_v13_share.py` — workflow adversarial cases.
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_02_REPORT.md` — this report.
- `tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C_REAUDIT_02.md` — independent audit contract.

Other pre-existing Stage A/Stage C dirty construction files remain part of the same construction worktree; they are not newly introduced by this remediation.

## 7. Historical chronology — preserved

1. Stage C initial independent audit: **FAIL**, report SHA-256 `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47`.
2. Stage C Remediation 01 implemented.
3. Stage C Independent Re-Audit 01: **FAIL**, report SHA-256 `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c`.
4. Stage C Source Identity Hardening Remediation 02: implemented; independent Re-Audit 02 pending.

Neither historical FAIL report was edited, replaced, renamed or reclassified.

## 8. Side effects and gate state

- No production import or content mutation.
- No Astro build.
- No NAS access or write.
- No email/notification.
- No dependency installation or upgrade.
- No commit, push, merge or deploy.
- No Stage D/E/F work.
- v1.3 production activation remains disabled.
- Existing production routes remain unchanged: Sermon v1.2 and the previously approved Share path.

## 9. Current state

- Stage A: PASS.
- Stage B: PASS; Master accepted.
- Stage C: `REMEDIATION_02_IMPLEMENTED_PENDING_INDEPENDENT_REAUDIT`; not accepted.
- Stage D: BLOCKED.
- Stage E: not started.
- Stage F: disabled.

The next permitted step is a read-only independent Auditor re-audit using the separate request. Stage C may advance only after a formal independent PASS and separate Master acceptance.
