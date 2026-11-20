# Stage C Source Identity Hardening Remediation 03 — Independent Re-Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR`
- Audit date: 2026-11-17
- Audit mode: independent, read-only re-audit
- Exact Website construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Staged changes before audit: 0
- **Formal verdict: FAIL**
- Stage C: `REMEDIATION_03_WITH_LEGACY_COMPATIBILITY_BLOCKER`
- Stage D: **BLOCKED**
- Stage E: **NOT STARTED**
- Stage F: **DISABLED**

## 1. Executive conclusion

Remediation 03 independently closes the three previously identified implementation defects in the requested scope:

1. F-02: workflow now requires a real existing regular Share source and rejects missing files, directories and broken symlinks before renderer/importer invocation.
2. Source identity helper API: initial resolution and package-bound resolution are separate; `expected_source` is mandatory and strict canonical package identity is enforced.
3. Owner mirror: Website's shared invariant helper and both schemas are byte-identical to the Sermon Owner copies; Website-only selector code is isolated in `scripts/share_source_identity.py`.

The path-based TOCTOU limitation is real but **not material under the current documented trust boundary**, where the configured Share raw root is trusted configuration and caller input is restricted to a single filename. It remains a disclosed hardening consideration if untrusted concurrent writers are later included in the threat model.

However, the mandatory legacy compatibility proposition does not pass. A safe direct invocation of the actual legacy `import_shares.main()` path without `--presentation-file` and without `--author` fails with `AttributeError: 'NoneType' object has no attribute 'strip'` at `scripts/import_shares.py:614`. The normal workflow parser documents that `--author` defaults to Ronnie, but the argument is declared without `default="Ronnie"`; the workflow also omits the argument when author is unset. This is not caused by Remediation 03's source-identity changes, but it means the explicitly required legacy route compatibility is not established. Supplying `--author Ronnie` plus valid manual description/tags allows the legacy direct dry-run to pass.

Because the Re-Audit 03 contract requires every mandatory proposition to pass, the overall verdict is **FAIL**, despite F-01 v1.3 source identity, F-02, helper API and Owner mirror passing. Do not accept Stage C or unblock Stage D on this report.

## 2. Workspace identity, write-set and isolation

### Website construction workspace

- Exact root confirmed.
- Branch and HEAD match the requested frozen baseline.
- `show_changes` before audit report creation showed 6 tracked modified paths, 36 untracked paths, and no staged changes. The write-set corresponds to the existing Stage C construction/remediation lineage.
- This Auditor did not modify implementation, tests, schemas, status, task index, plans, implementation reports or historical audit reports.
- The only file written by this Auditor is the explicitly authorized report:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_03_REPORT.md`.

### Canonical Website

- Root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Branch: `main`, HEAD `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- `show_changes`: 0 changed files. Canonical Website remains clean and synchronized with origin.

### Sermon Owner worktrees

- Owner construction root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `812ace500102bac54cb54cb0fa2249341118a3da`
- Existing Stage A/B dirty lineage remains present. `show_changes` showed the existing modified/untracked Owner write-set; no write was performed in this worktree.
- Canonical Sermon root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`
- Branch: `master`, ahead 2 of origin, with its pre-existing tracked modifications and untracked work. It was only opened/read; no write was performed.

## 3. Proposition 1 — Website-local source identity helper

**Result: PASS.**

Inspected `scripts/share_source_identity.py` directly:

- `resolve_share_source_path(selector, source_root)` delegates to the common existing-file resolver and performs initial path resolution only; it requires an existing direct regular file.
- `resolve_package_bound_share_source(selector, source_root, *, expected_source)` is a distinct package-bound operation. `expected_source` has no default and is keyword-only.
- Omitting `expected_source` raises `TypeError`; `None` and empty values raise `ValueError`.
- Package source must be the exact normalized POSIX path `data/raw/分享/<filename>`. Absolute paths, nested paths, traversal, dot aliases and non-normalized spellings fail. Caller selectors reject slash and backslash, absolute paths and dot aliases.
- The selected filename must equal the package-bound filename.
- The common resolver canonicalizes the configured root with `resolve(strict=True)`, rejects a selected symlink before resolving the candidate, and requires the resolved candidate's parent to equal the resolved root and the candidate to be a regular file.
- Missing files, directories, broken symlinks, internal symlink aliases and external symlink aliases are covered by direct-importer/workflow adversarial tests. Valid package-bound source dry-run is covered.

### Trusted root, symlinked parent and TOCTOU

The configured `source_root` is trusted configuration, not caller-controlled selector data. `Path(source_root).resolve(strict=True)` follows a symlink at the configured root or its parent and uses the canonical resolved directory as the trust anchor. A caller cannot select a nested parent because selector validation rejects path separators. A selected child symlink is rejected, whether its target is internal or external.

The checks are path-based (`is_symlink()`, then `resolve()`, followed later by a separate importer read); they are not an atomic no-follow descriptor handoff. A process able to mutate the trusted raw directory concurrently could race validation and use. No concurrent mutation was simulated. Under the current task's trusted configured raw-root model, with no evidence that untrusted concurrent writers are in scope, this is a **non-blocking residual hardening consideration**, not an independent Stage C blocker. If the raw root becomes writable by untrusted concurrent actors, descriptor-based no-follow opening and identity-preserving handoff should be reconsidered.

## 4. Proposition 2 — F-01 direct importer entrypoint

**Result: PASS for v1.3 source identity and package boundary; legacy compatibility sub-proposition FAIL (see LEGACY-01).**

Inspected and safely exercised actual `import_shares.main()`:

- v1.3 path first resolves the source through the strict existing-file resolver, then independently validates package/schema, presentation artifact binding, prepublish metadata, strict package-bound source identity and caller-supplied metadata.
- Validation occurs before output directory creation.
- Valid package-bound v1.3 dry-run passes.
- Missing source, nested selector, traversal, dot alias, absolute selector, different existing file, internal symlink alias and external symlink alias are rejected by the actual main-entrypoint test matrix; tests assert processed/posts/report output directories are not created.
- v1.3 non-dry-run remains blocked before Stage F.
- Presentation import without package remains blocked.

### LEGACY-01 — legacy Share direct import without author fails

**Disposition: FAIL — mandatory legacy compatibility proposition not met.**

Evidence:

- `scripts/import_shares.py:229-247`: `--author` is optional and has no default.
- `scripts/import_shares.py:614`: legacy and v1.3 paths evaluate `args.author.strip() or "Ronnie"`; if `args.author` is omitted, this raises `AttributeError`.
- `scripts/content_workflow.py:379`: help text says `--author` defaults to Ronnie, but the parser declaration has no `default` argument.
- `scripts/content_workflow.py:330-332`: workflow forwards author only when truthy; therefore the ordinary legacy workflow path with omitted author does not supply `--author`.

Safe direct probe of the real main entrypoint with a temporary raw file, `--source-file legacy.txt --dry-run`, and no presentation/package/author exited 1 with:
`AttributeError: 'NoneType' object has no attribute 'strip'` at line 614.

A second temporary direct-main probe supplying `--author Ronnie`, a valid manual description and tags completed dry-run successfully and created no output directories. This confirms the failure is specifically the missing default path, not an unconditional failure of legacy import.

This issue appears outside the Remediation 03 source-identity change set; it is nevertheless within the explicit Re-Audit 03 mandatory compatibility proposition and prevents an overall PASS. The audit does not authorize fixing it.

## 5. Proposition 3 — F-02 workflow boundary

**Result: PASS.**

Inspected actual `content_workflow.publish()` and its call order:

- The v1.3 Share path validates package, extracts package-bound prepublish source, then calls `resolve_package_bound_share_source()` before the Share renderer and importer.
- Valid package + valid existing source reaches the expected renderer then importer dry-run sequence. The test asserts exact three-call sequence: package validator, renderer, importer; package path/content root and dry-run are forwarded.
- Valid package + missing source, directory or broken symlink fails after the package validator only; renderer/importer invocation count remains zero.
- Nested path, traversal, dot alias, absolute selector, internal/external symlink aliases and distinct-basename mismatch fail before renderer/importer.
- Metadata spoofing tests fail after package validation and before renderer/importer.
- v1.3 non-dry-run remains blocked before Stage F.
- The tests invoke the actual `content_workflow.publish()` function and use temporary package/raw-root fixtures. The missing-source fixture's raw root genuinely has no source file.

## 6. Proposition 4 — Owner helper/schema mirror

**Result: PASS.**

Fresh-read exact Website and Sermon Owner files. SHA-256 values match the required identities:

| Contract | Website | Sermon Owner | Result |
|---|---|---|---|
| `scripts/publication_contract_invariants.py` | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | same | PASS |
| `content-presentation-v1.schema.json` | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | same | PASS |
| `website-publication-package-v1.3.schema.json` | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | same | PASS |

Website-only selector logic is isolated in `scripts/share_source_identity.py`. Search and direct read confirmed `scripts/publication_contract_invariants.py` contains only the shared `validate_package_presentation_bindings()` invariant and no Website source-selector logic.

## 7. Proposition 5 — regression and test quality

All required suite commands exited 0. Counts were independently observed:

| Verification | Actual result | Exit |
|---|---:|---:|
| Full Python suite, verbose run plus quiet count confirmation | 266/266 PASS | 0 |
| Stage C focused six-module suite | 65 executions PASS; 48 unique after removing 17 inherited duplicates | 0 |
| Legacy compatibility suite | 25/25 PASS | 0 |
| Share Tag Pipeline | 27/27 PASS | 0 |
| Python compile | PASS | 0 |
| Node syntax check | PASS | 0 |
| `git diff --check` | PASS | 0 |

Commands executed:

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q
python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -v
python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v
npm run check:tags
python3 -m py_compile scripts/share_source_identity.py scripts/content_workflow.py scripts/import_shares.py scripts/consume_publication_package.py scripts/validate_publication_package_v13.py
node --check scripts/validate_content_presentation.mjs
git diff --check
```

The focused six-module command executes 65 tests, of which 17 are inherited duplicate executions; deduplicated independent count is 48. The full suite independently reports `Ran 266 tests`.

The required legacy suite's 25/25 result does not cover the direct legacy importer no-author path; the explicit additional probe above found LEGACY-01. Therefore passing regression suites do not override that finding.

## 8. Proposition 6 — workspace, chronology and side effects

### Historical hashes

Recomputed Stage C historical report hashes match exactly:

| Historical report | SHA-256 | Result |
|---|---|---|
| Stage C initial independent FAIL | `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47` | unchanged |
| Stage C Re-Audit 01 FAIL | `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c` | unchanged |
| Stage C Re-Audit 02 FAIL | `88b6c116ee2087e5e5a0d12c627aaa7e7d471d470f8eb8b7cdb206fde5178963` | unchanged |
| Stage B accepted Re-Audit 01 PASS (Sermon Owner worktree) | `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea` | unchanged |

No historical report was edited, replaced, renamed or reclassified.

### Side effects

- No production import or production raw/processed/posts write.
- No Astro build.
- No NAS access/write.
- No notification/email.
- No dependency installation/upgrade.
- No commit, push, merge or deploy.
- No canonical Website or Sermon write.
- Temporary adversarial fixtures were used only in temporary directories; direct legacy probes used temporary raw/output paths and dry-run only.
- Stage F v1.3 non-dry-run remains disabled.
- Current production route/default selection remains unchanged; Stage D remains BLOCKED and Stage E has not started.

## 9. Final disposition

| Proposition | Result |
|---|---|
| Website-local source identity helper | PASS |
| F-01 v1.3 direct importer package/source boundary | PASS |
| F-01 legacy Share compatibility without `--author` | **FAIL — LEGACY-01** |
| F-02 workflow boundary | PASS |
| Owner helper/schema mirror | PASS |
| Regression/test quality | PASS, with LEGACY-01 found by additional probe |
| Workspace isolation and chronology | PASS |
| TOCTOU residual | Non-blocking under current trusted-root threat model |

**Overall verdict: FAIL.**

Remediation 03 closes the prior F-02 missing-source defect and Owner mirror divergence, and the package-bound helper API is now strict. But the required legacy compatibility proposition fails for the omitted-author path. Stage C therefore remains unaccepted; Stage D remains BLOCKED; Stage E remains NOT STARTED; Stage F remains DISABLED.

This Auditor recommends that the Master handle LEGACY-01 as a separately bounded compatibility correction (for example, provide the documented Ronnie default consistently in the workflow and importer boundary, then test the actual legacy `publish()` → `import_shares.main()` path without `--author`). This report does not authorize that correction.
