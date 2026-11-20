# Stage C Source Identity Hardening Remediation 02 — Independent Re-Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR`
- Audit mode: independent read-only re-audit
- Audit date: 2026-11-17
- Exact workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Frozen baseline: exact match
- Staged changes: 0
- **Formal verdict: FAIL**
- F-01: PASS
- F-02: FAIL
- Stage C: `REMEDIATION_02_WITH_RESIDUAL_BLOCKERS`
- Stage D: **BLOCKED**
- Stage F: **DISABLED**

## 1. Executive conclusion

Remediation 02 closes the previous nested-path and symlink-alias source selector bypasses on the direct importer and the normal workflow path. The direct `import_shares.main()` entrypoint now independently validates the package, presentation binding, package-bound source identity and metadata before output-directory creation. The tested invalid selector classes fail closed. Legacy Share import and the Stage F write block remain intact.

However, Stage C still cannot PASS for two independently evidenced reasons:

1. **F-02 (P2) remains FAIL:** the workflow calls `resolve_share_source_selector(..., require_exists=False)`. The helper therefore accepts a package-bound filename whose raw source file does not exist. An actual `content_workflow.publish()` invocation with a valid package and an empty raw Share root proceeded past identity validation and attempted both renderer and importer subprocess calls. This violates the explicit requirement that the workflow reject invalid source selectors before either downstream invocation and that the selected path resolve to a direct regular file.
2. **Owner mirror acceptance criterion FAIL:** Website's `scripts/publication_contract_invariants.py` now differs byte-for-byte from the authoritative Sermon Owner copy. Stage C's frozen implementation plan explicitly requires the shared helper mirror to remain byte-identical. The new Website-only selector helper was added inside the mirrored shared file rather than an isolated Website-local helper.

The helper also has two permissive API modes that do not satisfy the helper-level proposition when used alone: omitting `expected_source` (or passing `None`) is accepted, and `require_exists=False` accepts a missing file. Actual importer package binding compensates for the first mode with a later mandatory identity recheck; the workflow's use of the second mode does not compensate before renderer/importer.

## 2. Workspace identity, write-set and isolation

### Website construction workspace

- Exact root confirmed.
- Branch and HEAD match the requested frozen baseline.
- `show_changes` before and after verification shows the same implementation write-set: 6 tracked modified paths, 27 untracked paths, 0 staged.
- The only file added by this Auditor is the explicitly authorized report.
- No implementation, test, schema, status, index, plan or historical report was edited.

### Canonical Website

- Root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Branch: `main`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- `show_changes`: 0 changed files; clean and synchronized with origin.

### Canonical Sermon

- Root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`
- Branch: `master`
- HEAD: `812ace500102bac54cb54cb0fa2249341118a3da`
- It remains `ahead 2` with pre-existing tracked modifications and untracked work. This Auditor performed no writes there. The Stage B Owner helper and schema copies retain their expected hashes (below); no Stage C Website source was written into this canonical worktree.

### Sermon construction / Owner workspace

- Root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `812ace500102bac54cb54cb0fa2249341118a3da`
- Existing Stage A/B dirty implementation lineage remains; no write was performed there.

## 3. Historical chronology and hashes

All three required historical report identities were recomputed and match exactly:

| Historical evidence | Recomputed SHA-256 | Result |
|---|---|---|
| Stage C initial independent FAIL | `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47` | unchanged |
| Stage C Re-Audit 01 FAIL | `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c` | unchanged |
| Stage B accepted Re-Audit 01 PASS | `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea` | unchanged |

Stage A/B chronology and both Stage C FAIL reports remain separate historical facts. No prior report was overwritten, renamed or reclassified.

## 4. Mandatory proposition 1 — shared source identity helper

**Result: PARTIAL / FAIL.**

Implementation: `scripts/publication_contract_invariants.py:6-38`.

### Behaviors confirmed

When called with a valid `expected_source` and `require_exists=True`, the helper:

- accepts only a single filename selector; slash, backslash, absolute path, nested path, dot alias and traversal are rejected (`14-18`);
- requires the package source to be exactly four normalized POSIX components `data/raw/分享/<filename>`, and checks the filename against the selector (`19-26`);
- resolves the configured source root, rejects a selected file that is itself a symlink, and requires the resolved target to be a direct regular file beneath the resolved root (`27-35`);
- rejects different existing filenames through the expected-source comparison.

Adversarial direct helper probe results:

| Probe | Result |
|---|---|
| `sub/sample.txt` | rejected |
| `../sample.txt` | rejected |
| `./sample.txt` | rejected |
| absolute selector | rejected |
| backslash selector | rejected |
| malformed nested package source | rejected |
| empty package source | rejected |

Existing direct-importer tests separately exercise internal and external symlink aliases and assert no output directories are created.

### Helper-level gaps

The function signature makes `expected_source` optional (`10`). If omitted or explicitly `None`, the helper accepts a valid existing selector without any package identity binding. My isolated probe confirmed both cases are accepted. This is used as an initial resolution phase by `resolve_v13_source_file()`, and the direct importer later compensates with a second package-bound call; therefore this alone did not bypass the complete direct-import path. Nevertheless, it does not satisfy the stated helper-level requirement that missing package-bound source values be rejected.

More importantly, `require_exists=False` weakens the direct-file proposition: at `36-38`, a missing candidate is returned without proving that it exists or is a regular file. The workflow uses precisely this mode (see F-02).

### Symlinked directory / parent and TOCTOU review

- Caller-controlled nested parents cannot be selected because the selector rejects path separators before joining it to the configured root.
- The configured `source_root` is treated as trusted configuration and canonicalized with `resolve(strict=True)`; it is not supplied by the caller. A symlink at that configured root would therefore be followed and treated as the trusted resolved root, rather than being treated as a caller selector alias.
- The selected child is checked with `candidate.is_symlink()` and then resolved. These are path-based checks, not an atomic no-follow open. A concurrent writer able to mutate the trusted raw directory could create a check/use race. No concurrent filesystem mutation was simulated; this remains a hardening consideration if that actor is within the threat model. The present F-02 missing-file acceptance is independently reproducible without any race.

## 5. F-01 — direct importer entrypoint

**Disposition: PASS — previous P1 package-bypass and source-selector findings are closed in the inspected direct entrypoint.**

Relevant code:

- `scripts/import_shares.py:269-280`: v1.3 source resolution uses the shared helper with `require_exists=True`.
- `scripts/import_shares.py:456-476`: package path/content root are mandatory; the importer independently invokes the v1.3 package validator and requires PASS.
- `scripts/import_shares.py:494-514`: presentation artifact is bound to the package; prepublish source must exist and be a nonempty string; the source selector is checked again against the exact package-bound source with `require_exists=True`; the resolved source must match.
- `scripts/import_shares.py:515-541`: caller metadata is compared to bound metadata and v1.3 non-dry-run is blocked before output creation.
- `scripts/import_shares.py:552-569`: the main entrypoint performs v1.3 identity validation before any output directories are created.

### Actual `import_shares.main()` test coverage

The tests in `scripts/tests/test_import_share_presentation.py` call the real `main()` through a controlled temporary-directory harness:

- valid package-bound source filename: dry-run passes and creates no output directories (`45-64`);
- no package: fails closed with zero output directories (`29-43`);
- unbound artifact and spoofed metadata: fail closed with zero output directories (`66-82`, `101-117`);
- nested path, traversal, dot alias, absolute path, different existing file, internal symlink and external symlink: all fail closed with zero processed/posts/report directories (`120-160`);
- non-dry-run before Stage F: blocked before output directories (`84-99`).

The legacy Share route without `--presentation-file` remains covered and passed in the regression suite.

**F-01 result: PASS.** No bypass was reproduced in the direct importer path.

## 6. F-02 — underlying workflow boundary

**Disposition: FAIL — missing raw source is accepted and reaches renderer/importer.**

Relevant code:

- `scripts/content_workflow.py:192-220`: package version/content type, artifact binding and v1.3 package validator are rechecked.
- `scripts/content_workflow.py:232-244`: package-bound source is required to be a nonempty string, then passed to the shared helper.
- **Line 241 passes `require_exists=False`.** The helper consequently returns a nonexistent direct child path instead of rejecting it.
- `scripts/content_workflow.py:245-264`: author/date/category/contentType and caller metadata checks remain in place.
- `scripts/content_workflow.py:267-274`: the workflow replaces the caller selector with the package-bound basename and derives metadata.
- `scripts/content_workflow.py:309-329`: the Share renderer is invoked and the importer command is assembled.
- `scripts/content_workflow.py:275-276`: non-dry-run remains blocked before Stage F.

### Independent actual workflow invocation

I built a valid Share v1.3 package in a temporary directory, configured an empty temporary raw Share root, and invoked the actual `content_workflow.publish()` with `source_file="sample.txt"`. The package-bound prepublish source was `data/raw/分享/sample.txt`, but the file did not exist in the configured raw root.

Subprocess calls were intercepted only to record which commands the real workflow attempted; no renderer or importer process was launched and no project files were written. Observed:

- `raw_source_exists = False`;
- package validator call recorded;
- Share renderer call recorded;
- importer call recorded.

Thus the workflow did not reject the missing source before downstream calls. The importer itself would later reject the missing source through its `require_exists=True` path, but that does not satisfy the workflow contract, which explicitly requires rejection before renderer/importer invocation.

### Existing tests and gap

`scripts/tests/test_content_workflow_v13_share.py` covers nested, traversal, dot, absolute and internal/external symlink selectors (`197-229`); the fixture creates `raw/sample.txt` at `203-204`, so those cases do not exercise a missing source. The existing distinct-basename mismatch and metadata mismatch tests remain effective (`75-115`). The positive workflow test also confirms package path/content root forwarding and a valid dry-run route.

**F-02 result: FAIL.** Change the workflow helper call to require an existing regular file and add a missing-source adversarial test asserting zero renderer/importer calls.

## 7. Owner mirror / contract acceptance

**Result: FAIL against the frozen Stage C acceptance criterion.**

Stage C plan:

- `STAGE_C_IMPLEMENTATION_PLAN.md:15-20` identifies the Sermon Owner's schemas, fixtures and `scripts/publication_contract_invariants.py` as the authoritative mirrored contract.
- `STAGE_C_IMPLEMENTATION_PLAN.md:58-63` explicitly requires schemas/helper to remain byte-identical to Sermon Owner copies.

Recomputed hashes:

| File | Website construction | Sermon Owner construction | Result |
|---|---|---|---|
| `content-presentation-v1.schema.json` | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | identical |
| `website-publication-package-v1.3.schema.json` | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | identical |
| `publication_contract_invariants.py` | `71cbe7b1c8bff962492469b0618cb5b32651ff0f32e3c02b87c1da59fb93ca98` | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | **different** |

The Website helper now contains the new `resolve_share_source_selector()` function, while the Owner copy retains the Stage A shared invariant helper. The two frozen schemas remain byte-identical. The new Website-specific source selector logic should be isolated from the mirrored Owner helper, or the mirror authority must be explicitly reconciled through a separately authorized cross-project change. This Auditor made no such change.

## 8. Regression and test quality

All requested commands exited 0:

| Command | Actual result | Exit |
|---|---:|---:|
| Full Python suite, verbose | 260/260 PASS | 0 |
| Full Python suite, quiet recount | 260/260 PASS | 0 |
| Stage C five-module focused suite | 59 executions PASS; 42 unique tests after removing 17 inherited duplicate executions | 0 |
| Legacy compatibility suite | 25/25 PASS | 0 |
| Share Tag Pipeline | 27/27 PASS | 0 |
| Python compile (shared helper, importer, workflow and two tests) | PASS | 0 |
| Node syntax check | PASS | 0 |
| `git diff --check` | PASS | 0 |

Exact commands:

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q
python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation -v
python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -v
npm run check:tags
python3 -m py_compile scripts/publication_contract_invariants.py scripts/import_shares.py scripts/content_workflow.py scripts/tests/test_import_share_presentation.py scripts/tests/test_content_workflow_v13_share.py
node --check scripts/validate_content_presentation.mjs
git diff --check
```

The focused five-module command runs 59 test executions because 17 tests from `PublicationPackageV13ConsumerValidationTests` are inherited/collected again through `test_import_share_presentation`. The deduplicated independent count is 42, not 59.

The regression suites pass but do not detect the workflow missing-source acceptance or the Owner helper mirror divergence. The workflow adversarial suite should add a missing-file case and assert the subprocess call count remains one (package validator only).

## 9. Mandatory proposition disposition

| Proposition | Result | Evidence |
|---|---|---|
| Helper requires normalized package-bound POSIX source path | PARTIAL | Exact format enforced when supplied; omitted/None `expected_source` is accepted by the helper API |
| Helper rejects absolute/nested/traversal/dot/backslash aliases | PASS | Helper checks plus isolated probes |
| Helper rejects internal/external file symlinks | PASS | `candidate.is_symlink()`; direct and workflow adversarial tests |
| Helper confirms direct regular file under configured raw root | PARTIAL / FAIL | True with `require_exists=True`; false with workflow's `require_exists=False` |
| Exact package filename binding, not detached basename | PASS when expected source supplied | `expected.name == selector` plus exact canonical path shape |
| Symlinked directory/parent and TOCTOU review | PASS_WITH_RESIDUAL_NOTE | Caller cannot select nested parent; configured root is trusted/resolved; path-based check is not atomic against concurrent mutation |
| F-01 direct importer | PASS | Actual main-entrypoint tests, zero-output rejection, independent package validation |
| F-02 workflow | **FAIL** | Missing source accepted; renderer/importer calls attempted |
| Metadata mismatch / distinct basename mismatch | PASS | Existing workflow negative tests |
| Legacy Share compatibility | PASS | Full and legacy suites |
| Stage F pre-activation write block | PASS | Direct importer/workflow non-dry-run guards and tests |
| Owner schemas/helper byte-identity acceptance | **FAIL** | Schemas match; shared helper hash diverges |
| Canonical Website main unchanged | PASS | Clean `main`, frozen HEAD, zero changed files |
| Canonical Sermon worktree unchanged | PASS_WITH_LIMITATION | Current dirty lineage retained; Owner schemas/helper hashes unchanged; no write occurred in this audit |
| Historical report hashes unchanged | PASS | All three exact hashes recomputed |
| Prohibited side effects absent | PASS | See below |

## 10. Side-effect boundary and final disposition

Not performed:

- production import or content mutation;
- Astro build;
- NAS access/read/write;
- notification or email;
- dependency install/upgrade;
- commit, push, merge or deploy;
- Stage D, Stage E or Stage F work.

Adversarial package/source fixtures were created only in temporary directories and cleaned up. Workflow subprocesses were intercepted for call recording. Python test/compile commands may refresh ignored `__pycache__` files; no Git-visible change outside the authorized report was introduced.

**Final verdict: FAIL.** F-01 is closed in the direct importer. F-02 remains open because the workflow does not require the selected raw source to exist before invoking the renderer/importer. The helper's optional unbound mode and the Website/Owner helper mirror divergence also prevent the Stage C acceptance criteria from being met.

Recommended bounded follow-up:

1. Make the workflow require an existing direct regular raw Share file before renderer invocation; add a missing-source test proving no renderer/importer calls.
2. Make the package-bound helper contract explicit (or separate the unbound initial resolver from the package-bound identity helper) so missing/None package source cannot be mistaken for a valid bound identity.
3. Move the Website-specific selector function out of the byte-identical Owner helper, or obtain explicit authority to reconcile the cross-project mirror. Do not mutate the Sermon Owner copy under this audit.
4. If concurrent raw-directory mutation is in scope, replace path-check-then-use with an atomic no-follow file access strategy.

Stage C remains unaccepted. Stage D remains BLOCKED; Stage F remains DISABLED. A separate independent PASS and separate Master acceptance are required before progression.

The report's own SHA-256 is supplied in the Master handback after read-back; it is not embedded in this file.
