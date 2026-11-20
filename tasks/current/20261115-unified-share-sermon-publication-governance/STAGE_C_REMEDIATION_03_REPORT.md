# Stage C Source Identity Hardening — Remediation 03 Implementation Report

## 1. Disposition

Master implementation disposition: **Remediation 03 implemented; local verification PASS; independent Re-Audit 03 required.**

This report records implementation evidence only. It does not close the historical Stage C FAIL findings, does not accept Stage C, and does not authorize Stage D/E/F.

## 2. Exact workspace and baseline

- Workspace root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Workspace ID: `ws_36904a3d8e03f8682750de45`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea` (unchanged; construction worktree remains uncommitted)
- Staged changes: none.
- Canonical Website `main` was not used for writes.
- Sermon Owner construction and canonical worktrees were read-only; no file was modified there.

## 3. Remediation 03 changes

### F-02 — workflow must require an existing regular source file

`scripts/content_workflow.py` now calls `resolve_package_bound_share_source()` before the Share renderer or importer. The strict resolver uses `Path.resolve(strict=True)`, rejects a selected symlink, and requires the resolved target to be a direct regular file under the configured Share raw root.

The actual workflow test now exercises a valid package with each of these raw-root states:
- source file missing;
- selected path is a directory;
- selected path is a broken symlink.

All three fail with `V13_PACKAGE_IDENTITY_MISMATCH`. The package validator is the only subprocess call recorded; neither renderer nor importer is invoked.

### Helper API — separate initial resolution from package-bound identity

Website-only source identity code has been moved to the new `scripts/share_source_identity.py`:

- `resolve_share_source_path(selector, source_root)`: initial path resolution before package identity is available; requires an existing direct regular file and rejects path aliases/symlinks.
- `resolve_package_bound_share_source(selector, source_root, *, expected_source)`: strict package-bound resolution; `expected_source` is a required keyword-only argument with no default. Missing argument raises `TypeError`; `None` or empty values raise `ValueError`. It requires the exact normalized POSIX path `data/raw/分享/<filename>`, matches the selected filename, and requires the existing direct regular file.

Both workflow and direct importer use the strict package-bound helper. The direct importer still performs its own package/schema, presentation, metadata, and source validation before output directory creation. The initial importer resolver uses the separate unbound path-resolution function only as an early file/path check.

### Restore Owner helper mirror

Website `scripts/publication_contract_invariants.py` has been restored to the Stage A shared invariant implementation. Its SHA-256 now exactly matches the Sermon Owner copy:

`b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0`

The new Website-only source selector implementation is isolated in `scripts/share_source_identity.py`; the Sermon Owner worktree was not modified.

Schema mirrors were also re-read and remain byte-identical:
- `content-presentation-v1.schema.json`: `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5`
- `website-publication-package-v1.3.schema.json`: `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e`

## 4. Tests added or updated

- New `scripts/tests/test_share_source_identity.py`: initial resolver existence/type checks; strict helper required argument / `None` / empty handling; canonical path validation; selector alias and missing-file rejection.
- `test_content_workflow_v13_share.py`: valid package + missing source, directory, broken symlink; asserts renderer/importer are not called. Existing valid dry-run, metadata spoofing, nested/traversal/dot/absolute/symlink attack tests remain.
- `test_import_share_presentation.py`: valid package + missing source fails before output directories. Existing direct-main attack matrix, package/artifact/metadata checks, Stage F write block and legacy route coverage remain.

## 5. Final verification

All commands below were run after the final source/test edits; exit codes are exact.

| Verification | Result | Exit |
|---|---:|---:|
| Full Python suite | **266/266 PASS** | 0 |
| Stage C focused suite (six modules, including new helper tests) | **65 executions PASS; 48 unique tests** after removing 17 inherited duplicate executions | 0 |
| Legacy compatibility suite | **25/25 PASS** | 0 |
| Share Tag Pipeline | **27/27 PASS** | 0 |
| Python compile (all changed Python modules/tests) | PASS | 0 |
| Node syntax check (`validate_content_presentation.mjs`) | PASS | 0 |
| `git diff --check` | PASS | 0 |

Focused command:

```text
python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -v
```

The focused command executes 65 tests. `test_import_share_presentation` inherits 17 tests from `PublicationPackageV13ConsumerValidationTests`, which are already run by the separate v1.3 validator module. Deduplicated independent count: 48.

Full Python command:

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
```

Legacy command:

```text
python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v
```

Other commands:
- `npm run check:tags` — 27/27.
- `python3 -m py_compile scripts/share_source_identity.py scripts/publication_contract_invariants.py scripts/import_shares.py scripts/content_workflow.py scripts/tests/test_share_source_identity.py scripts/tests/test_import_share_presentation.py scripts/tests/test_content_workflow_v13_share.py`
- `node --check scripts/validate_content_presentation.mjs`
- `git diff --check`

## 6. Changed files

- `CONTENT_WORKFLOW.md` — documents source existence/type requirements and strict helper split.
- `scripts/content_workflow.py` — strict package-bound source validation before renderer/importer.
- `scripts/import_shares.py` — separate initial resolver and strict package-bound direct-import recheck.
- `scripts/share_source_identity.py` — new Website-local initial and strict source identity helpers.
- `scripts/publication_contract_invariants.py` — restored byte-identical Owner mirror.
- `scripts/tests/test_content_workflow_v13_share.py` — missing/directory/broken-symlink workflow probes and valid-source fixtures.
- `scripts/tests/test_import_share_presentation.py` — missing-source direct importer probe.
- `scripts/tests/test_share_source_identity.py` — new helper contract tests.
- `STATUS.md`, `docs/tasks/current.md` — current state and chronology.
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_REMEDIATION_03_REPORT.md` — this report.
- `tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C_REAUDIT_03.md` — independent audit contract.

## 7. Historical chronology — preserved

1. Stage C initial independent audit: **FAIL**, SHA-256 `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47`.
2. Remediation 01 Re-Audit 01: **FAIL**, SHA-256 `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c`.
3. Remediation 02 Re-Audit 02: **FAIL**, SHA-256 `88b6c116ee2087e5e5a0d12c627aaa7e7d471d470f8eb8b7cdb206fde5178963`.
4. Remediation 03: implemented; awaiting independent Re-Audit 03.

All historical reports remain unchanged. F-01 was PASS in Re-Audit 02 and remains a regression-protected invariant; F-02 and Owner mirror findings are addressed by this implementation but are not considered closed until independent review.

## 8. Side-effect and stage boundary

- No production import or production raw/processed/posts writes.
- No Astro build.
- No NAS access/write, notification/email, dependency install/upgrade.
- No commit, push, merge or deploy.
- Stage F v1.3 non-dry-run remains disabled.
- Current production routes/defaults remain unchanged.
- Stage D remains BLOCKED; Stage E not started; Stage F disabled.

## 9. Residual review point

The source identity checks are path-based checks against the trusted configured raw root. They reject caller-selected symlinks and non-regular/missing targets, but they are not an atomic no-follow file-descriptor handoff across validation and later importer reads. The Auditor should assess whether this filesystem race is material under the project's trusted raw-root threat model; this implementation does not claim race-free atomic source opening.
