# Stage C Remediation 04 — Independent Re-Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR` (not Master)
- Audit date: 2026-11-17
- Exact Website construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- Frozen HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Overall verdict: **PASS_WITH_FINDINGS**
- Stage C disposition: `REMEDIATION_04_INDEPENDENT_REAUDIT_PASS_WITH_FINDINGS`
- Stage D: **BLOCKED**
- Stage E: **NOT STARTED**
- Stage F: **DISABLED**

## 1. Executive conclusion

The sole blocker from Re-Audit 03, LEGACY-01, is independently resolved.

Actual direct `import_shares.main()` legacy probes passed for omitted, explicit-empty, and explicit non-empty authors. The omitted CLI case leaves `args.author is None`; the code's `(args.author or "").strip() or "Ronnie"` safely resolves that None to Ronnie. Explicit empty resolves to Ronnie; explicit `Patrick` remains Patrick.

Actual `content_workflow.publish()` calls were connected to the actual `import_shares.main()` entrypoint for all three author cases. The workflow passed Ronnie for omitted and empty authors, and passed/retained exact `Patrick` for the explicit case. The executed legacy commands contained no v1.3 presentation/package/content-root arguments. All raw and output paths were temporary; dry-run created no processed/posts/report output directories.

A valid v1.3 Share package with package-bound author `PackageAuthor` was independently exercised through the actual importer. With caller author omitted, importer used `PackageAuthor`, not Ronnie. Explicit caller author `Ronnie` failed closed as `V13_PACKAGE_IDENTITY_MISMATCH` before output directories. v1.3 non-dry-run was blocked before Stage F.

The previously passing source identity, F-01 direct-importer boundary, F-02 workflow boundary, Owner mirror, and Stage F disabled controls were rechecked and passed. Required test commands all exited 0 with the expected counts. All five historical report hashes match exactly.

The only bounded non-blocking finding retained is the already-disclosed path-based TOCTOU limitation in source identity validation: validation and later file read are not one atomic no-follow descriptor handoff. Under the currently documented trusted configured raw-root threat model, this is not a material Stage C blocker. It is recorded transparently; hence the verdict is `PASS_WITH_FINDINGS`, not an unqualified `PASS`.

## 2. Workspace identity and write boundary

### Website construction workspace

- Exact root verified.
- Branch and HEAD match the frozen baseline exactly.
- Before this Auditor's report write: staged files 0; unstaged tracked files 6; untracked files 38.
- Existing tracked modifications: `CONTENT_WORKFLOW.md`, `STATUS.md`, `docs/tasks/current.md`, `scripts/consume_publication_package.py`, `scripts/content_workflow.py`, `scripts/import_shares.py`.
- Existing untracked files include the Stage A/B/C contract, schemas, tests, implementation reports, prior independent audit reports and Re-Audit 04 request. These were pre-existing construction lineage, not created by this Auditor.
- This Auditor's sole repository write is the explicitly authorized file:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_REAUDIT_04_REPORT.md`.
- No product code, test, schema, workflow document, STATUS, task index, prior report, or other file was modified.

### Canonical Website

- Root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Branch: `main`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Git status: clean; 0 changed files.
- Only opened and checked; no writes.

### Sermon Owner

- Owner construction root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `812ace500102bac54cb54cb0fa2249341118a3da`
- Existing dirty lineage retained: staged 0, unstaged 19, untracked 34. No writes.
- Canonical Sermon root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`
- Branch: `master`, ahead 2 of origin; existing tracked modifications and untracked task lineage present at opening. Read-only; no writes.

## 3. LEGACY-01 — actual direct importer

**Result: PASS.**

Inspected `scripts/import_shares.py`:

- `parse_args()` leaves `--author` unset when omitted; argparse yields `args.author is None`.
- At line 614, author resolution is `(args.author or "").strip() or "Ronnie"`. It handles `None`, empty string and whitespace without dereferencing None.
- For v1.3, `validate_v13_import_identity()` first fills `args.author` from package metadata when caller omitted it (line 559); only then does the shared author resolution run. This ordering is central to the v1.3 isolation check below.

Actual `import_shares.main()` direct legacy probes, each using a temporary raw directory, temporary output paths and `--dry-run`:

| Input | Resolved author observed at importer author-consuming function | Result |
|---|---|---|
| Omit `--author` (`args.author=None`) | `Ronnie` | PASS |
| `--author ""` | `Ronnie` | PASS |
| `--author Patrick` | `Patrick` | PASS |

The author-consuming function was instrumented in memory to capture the actual value passed by the real `main()`; its original behavior was still invoked. Every probe completed; `organized`, `posts`, and `reports` output directories remained absent. No repository or production data path was used for source or output.

## 4. LEGACY-01 — actual Workflow → Importer chain

**Result: PASS.**

The real `content_workflow.publish()` function was invoked for each case. Its subprocess boundary was intercepted only to dispatch the exact generated importer command into the actual `import_shares.main()` function with the process arguments and temporary directory constants bound to the fixture. The importer itself was not mocked; it performed its normal dry-run path and its author-consuming function received the resolved author.

| Workflow input | Actual importer received | Importer result |
|---|---|---|
| Author omitted | `--author Ronnie` | PASS |
| `author=""` | `--author Ronnie` | PASS |
| `author="Patrick"` | `--author Patrick` | PASS |

For all three runs:

- No `--presentation-file`, `--publication-package`, or `--content-root` argument appeared.
- Actual importer `main()` completed dry-run.
- The author observed by the importer was respectively Ronnie, Ronnie and Patrick.
- Temporary raw file existed; temporary processed/posts/report output directories did not exist after the run.
- No production raw, processed, posts, or report directory was accessed for writing.

This verifies the real Python workflow function through the actual importer entrypoint rather than only inspecting a command list or replacing the importer with a fake success result. The subprocess process boundary itself was adapted in-memory so the real importer function could run against temporary path constants safely.

## 5. v1.3 author identity isolation

**Result: PASS.**

A valid Share v1.3 fixture was constructed in a temporary content root. Both package metadata and the SHA-bound prepublish frontmatter were changed consistently to package-bound author `PackageAuthor`; the prepublish SHA was recomputed and the package validator accepted the package.

Actual direct `import_shares.main()` results:

| Scenario | Result | Filesystem |
|---|---|---|
| Valid v1.3 package, caller omits `--author`, dry-run | PASS; importer uses `PackageAuthor` | No output directories |
| Same package, caller explicitly supplies `--author Ronnie` | FAIL-CLOSED: `V13_PACKAGE_IDENTITY_MISMATCH: author does not match package-bound prepublish metadata` | No output directories |
| Same package, non-dry-run | BLOCKED: `v1.3 publish is disabled before Stage F` | No output directories |

The parser has no unconditional Ronnie default. The importer adopts package author before the legacy fallback expression is evaluated. Explicit mismatching caller identity is compared against package-bound metadata before output directory creation. This demonstrates the legacy fallback does not override v1.3 author identity.

## 6. Previously passing Stage C invariants

### Website-local source identity helper — PASS

Fresh-read `scripts/share_source_identity.py` and its tests:

- `resolve_package_bound_share_source(selector, source_root, *, expected_source)` requires keyword-only `expected_source`; omission raises `TypeError`; `None` and empty values raise `ValueError`.
- The expected path is restricted to the exact normalized POSIX form `data/raw/分享/<filename>`; nested, traversal, dot-alias, absolute and non-normalized forms are rejected.
- Selector must be a single canonical filename; slash/backslash, absolute, nested, traversal and dot aliases are rejected.
- Missing file, directory, broken symlink and selected symlink aliases fail closed. Internal and external symlink alias rejection is also covered through the actual direct importer and workflow attack tests.
- A valid existing direct regular file under the configured Share raw root resolves successfully.
- Website-specific source selector code remains isolated in `scripts/share_source_identity.py`; the shared helper has no Website-specific selector logic.

### F-01 — direct importer package boundary — PASS

Fresh-read and re-exercised actual `import_shares.main()`:

- v1.3 presentation import requires package and content-root arguments.
- Importer independently invokes the package v1.3 validator, verifies prepublish author/date/category/contentType against package metadata, verifies presentation artifact path binding, resolves package-bound source identity, and checks caller metadata against package-bound values.
- Missing source, nested/traversal/dot/absolute selectors, different file, internal symlink alias and external symlink alias are rejected.
- Invalid package/artifact/source/metadata cases are rejected before output directory creation.
- v1.3 non-dry-run is blocked before Stage F.
- Legacy no-presentation/no-package route remains available.

### F-02 — workflow source boundary — PASS

Fresh-read `content_workflow.publish()` and its adversarial tests:

- Workflow package validation and strict package-bound source resolution occur before Share renderer/importer.
- Missing source, directory and broken symlink are rejected after package validation and before renderer/importer.
- Nested path, traversal, dot alias, absolute path, internal/external symlink aliases and distinct-basename mismatch are rejected before renderer/importer.
- Metadata spoofing is rejected before renderer/importer.
- Valid package + existing source retains the expected validator → renderer → importer dry-run path.
- v1.3 non-dry-run remains blocked.

### Owner shared helper/schema mirror — PASS

Fresh-read exact Website and Sermon Owner copies; both SHA and byte identities match:

| File | Website SHA-256 | Sermon Owner SHA-256 | Result |
|---|---|---|---|
| `scripts/publication_contract_invariants.py` | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | same | PASS |
| `content-presentation-v1.schema.json` | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | same | PASS |
| `website-publication-package-v1.3.schema.json` | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | same | PASS |

Website selector implementation remains in `scripts/share_source_identity.py`; the shared invariant helper remains the shared contract-only implementation.

### Stage F boundary — PASS

Both workflow and direct importer reject v1.3 non-dry-run before any output directory creation. Current production route/default selection remains unchanged.

## 7. Regression and test quality

All requested commands were independently run in the exact Website construction workspace. Runtime bytecode writes were disabled or redirected to `/tmp`; tests' filesystem fixtures use temporary directories.

| Command | Actual result | Exit |
|---|---:|---:|
| `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q` | 269 tests, OK | 0 |
| Stage C focused six-module command | 68 executions, OK; 51 unique after removing 17 inherited duplicates | 0 |
| Legacy compatibility command | 25 tests, OK | 0 |
| `npm run check:tags` | 27/27 PASS | 0 |
| Python compile (9 source/test modules) | PASS | 0 |
| `node --check scripts/validate_content_presentation.mjs` | PASS | 0 |
| `git diff --check` | PASS | 0 |

Exact commands:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -q
npm run check:tags
PYTHONPYCACHEPREFIX=/tmp/ronniecross-reaudit04-pycache python3 -m py_compile scripts/content_workflow.py scripts/import_shares.py scripts/share_source_identity.py scripts/publication_contract_invariants.py scripts/consume_publication_package.py scripts/validate_publication_package_v13.py scripts/tests/test_import_share_presentation.py scripts/tests/test_content_workflow_v13_share.py scripts/tests/test_share_source_identity.py
node --check scripts/validate_content_presentation.mjs
git diff --check
```

The full Python suite printed intentional FAIL evidence from negative sermon presentation fixtures; unittest's actual summary was `Ran 269 tests ... OK`, exit 0. This is expected negative-fixture output, not a suite failure.

The focused tests include inherited duplicates: 68 executions, 17 inherited duplicate executions, 51 unique. The additional audit probes above supplement tests by actually invoking the omitted/empty/explicit direct importer and workflow-to-importer paths and a non-Ronnie v1.3 package author.

## 8. Historical chronology SHA-256 — all unchanged

All five required historical reports were re-hashed from their authoritative worktrees and match the frozen values:

| Historical report | Recomputed SHA-256 | Result |
|---|---|---|
| Stage C Initial FAIL | `967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47` | unchanged |
| Stage C Re-Audit 01 FAIL | `48dfec6ce2ef11e86776d024ba747729e2096c6b9c0cfb511fc5b965cf43e77c` | unchanged |
| Stage C Re-Audit 02 FAIL | `88b6c116ee2087e5e5a0d12c627aaa7e7d471d470f8eb8b7cdb206fde5178963` | unchanged |
| Stage C Re-Audit 03 FAIL / LEGACY-01 | `8656e20ed2f421b69dff0b9f39d9dba8d3ef6474e7b434168394badd296a63a5` | unchanged |
| Stage B accepted Re-Audit 01 PASS | `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea` | unchanged |

No historical report was deleted, overwritten, renamed, or reclassified. Re-Audit 04's PASS_WITH_FINDINGS does not erase the earlier Stage C FAIL chronology.

## 9. Residual finding and limitations

### RF-01 — path-based TOCTOU (non-blocking under current threat model)

Source identity validation uses path-based checks (`is_symlink()`, `resolve()`, regular-file check) and later importer file reads; it is not an atomic no-follow file-descriptor handoff. A concurrent actor with write access to the trusted configured raw directory could theoretically replace the file between validation and use. No concurrent mutation was simulated.

The current contract treats the configured Share raw root as trusted configuration and caller selectors cannot choose nested parents. Under this threat model, RF-01 is bounded and non-blocking; it was already disclosed in the Remediation 03 review and is not newly introduced by Remediation 04. If the raw root later admits untrusted concurrent writers, descriptor-based no-follow opening and identity-preserving handoff should be reconsidered.

### Probe setup note

An initial author-capture probe stopped at the pre-existing manual-description minimum-length validation because its temporary description was too short. No product write occurred. The probe was corrected with a valid longer description and rerun; omitted/empty/explicit direct author cases all passed with captured values Ronnie/Ronnie/Patrick. This setup correction did not alter source or test files.

## 10. Side-effect and stage boundary

- No production import or production raw/processed/posts/report write.
- No Astro build.
- No NAS access or write.
- No email or notification.
- No dependency installation or upgrade.
- No commit, push, merge or deploy.
- No Stage D/E/F operation.
- Canonical Website and both Sermon worktrees were read-only.
- All importer probes used temporary raw/output paths and dry-run only; output directories remained absent.
- Python bytecode cache was disabled or redirected outside the repository.
- Production routes/defaults remain unchanged.
- Stage D remains BLOCKED; Stage E remains NOT STARTED; Stage F remains DISABLED.

## 11. Final proposition matrix and disposition

| Proposition | Result |
|---|---|
| LEGACY-01 direct importer omitted/empty/explicit author | PASS |
| LEGACY-01 actual workflow → actual importer omitted/empty/explicit author | PASS |
| v1.3 non-Ronnie package-bound author isolation | PASS |
| v1.3 explicit mismatching author fail-closed | PASS |
| v1.3 non-dry-run Stage F block | PASS |
| Website-local source identity helper | PASS |
| F-01 direct importer package boundary | PASS |
| F-02 workflow source boundary | PASS |
| Owner helper/schema byte identity | PASS |
| Regression and test quality | PASS |
| Workspace/Git/write-set isolation | PASS |
| Historical chronology hashes | PASS |
| Side-effect/stage boundary | PASS |
| RF-01 path-based TOCTOU | Non-blocking finding |

**Overall verdict: PASS_WITH_FINDINGS.**

LEGACY-01 is resolved. All mandatory Stage C propositions in this Re-Audit 04 passed. RF-01 remains a bounded, previously disclosed non-blocking filesystem race consideration under the current trusted-root threat model. Stage C may be presented to Master for formal acceptance; this Auditor does not itself perform Master acceptance or authorize Stage D, Stage E, or Stage F.
