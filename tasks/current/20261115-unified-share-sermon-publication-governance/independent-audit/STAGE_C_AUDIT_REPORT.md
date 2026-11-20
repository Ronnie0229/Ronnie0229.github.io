# Stage C Website Consumer — Independent Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR`
- Workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Audit date: 2026-11-17
- Mode: independent read-only audit
- **Verdict: FAIL**
- Stage D: **BLOCKED pending remediation and a fresh independent re-audit**

## 1. Executive conclusion

The Stage C implementation passes its declared regression suites and most inspected contract, schema, profile, identity and compatibility checks. The cross-project schemas and shared invariant helper are byte-identical to the Sermon Owner copies. Canonical Website remains clean at the frozen baseline; the Stage B accepted audit and historical reports retain their expected SHA-256 values.

However, the implementation has a material Share import security-boundary defect:

**The direct `scripts/import_shares.py --presentation-file` entrypoint accepts and imports a v1.3 presentation artifact without any publication package.** It does not accept a package argument, does not validate a package, and does not enforce the Stage F activation boundary. A controlled temporary-directory execution proved that this path writes the processed article and proceeds to the post-copy path. This directly violates the Stage C audit contract requirement that direct Share presentation import without a package must fail closed.

A second, related identity-binding gap exists in the underlying `content_workflow.publish()` v1.3 branch: it revalidates the package and confirms the presentation artifact path, but does not bind the caller-supplied Share source selector or caller-supplied title/author/date values to the package's SHA-bound prepublish frontmatter. A temporary controlled invocation with a valid package forwarded a different source filename and spoofed title/author to the importer. The v1.3 publish mode remains blocked in this function, so this second finding affects the integrity of direct controlled dry-run/acceptance invocation rather than demonstrating a production publish. It nevertheless violates the required source selector/metadata binding boundary.

These are implementation defects, not test-suite failures. Stage C cannot receive PASS until both are corrected and independently re-audited. No implementation remediation was performed by this Auditor.

## 2. Workspace identity and isolation

### Website construction target

- Exact root verified: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`.
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`.
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`, matching the Stage C frozen baseline.
- Git top-level resolves to the exact requested root.
- Construction worktree is dirty with the expected Stage C implementation write-set: 6 modified tracked paths and 23 untracked paths at initial inspection; no staged changes.
- No Auditor implementation/test/document changes were made. The only authorized write is this report.

### Canonical and Owner worktrees

- Canonical Website `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`: `main...origin/main`, clean; HEAD is the same frozen baseline `09ce7eb588a21745d0286d3eec6a890c16a26aea`.
- Canonical Sermon remains on its pre-existing dirty lineage; no files there were changed by this Auditor.
- Sermon construction Stage B remains on `task/unified-share-sermon-publication-stage-a-20261116`, HEAD `812ace500102bac54cb54cb0fa2249341118a3da`; its pre-existing dirty implementation lineage remains untouched.
- No staged changes were introduced.

### Stage B accepted evidence and chronology

Recomputed from the Owner worktree:

| Evidence | SHA-256 | Result |
|---|---|---|
| Stage B Remediation 01 implementation report | `3a0842e98471407849f3603b57240b850e72d8f7dec98db9c1af09e53e49cd55` | unchanged |
| Original Stage B independent audit — historical FAIL | `700eadd8c4216bce2b349e89042e1c2b134a4c78edee27af545a361b7d01131e` | unchanged |
| Stage A Re-Audit 02 — PASS | `87a7341398601aadfbe475fbd831d6a707a8a12c77ed5ad5e966e2bae80d84dd` | unchanged |
| Stage B Re-Audit 01 — accepted PASS | `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea` | exact match to Stage C request |

The Stage B initial FAIL, Stage A audit chronology and later accepted Stage B PASS remain separate historical facts. No historical report was edited or reclassified.

## 3. Contract mirror and schema enforcement

**Result: PASS for the frozen current schemas; see residual note below.**

The three required Owner mirrors were compared byte-for-byte:

| Website file | Owner file | SHA-256 | Result |
|---|---|---|---|
| `contracts/content-presentation-v1.schema.json` | `讲道整理.../docs/contracts/content-presentation-v1.schema.json` | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | identical |
| `contracts/website-publication-package-v1.3.schema.json` | `讲道整理.../docs/contracts/website-publication-package-v1.3.schema.json` | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | identical |
| `scripts/publication_contract_invariants.py` | `讲道整理.../scripts/publication_contract_invariants.py` | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | identical |

Inspected `schema_definition_errors` and `validate_schema_node` in `scripts/validate_publication_package_v13.py`:
- The frozen schemas use the implemented keyword subset: `$ref/$defs`, `type`, `const`, `enum`, `required`, `properties`, `additionalProperties`, `items`, `minItems`, `uniqueItems`, `minLength`, `pattern`, `minimum`, `format=date-time`, `allOf`, `if`, and `then`.
- The schema-definition walk rejects unknown keyword names and unsupported formats; the node validator implements the keywords used by the two frozen schemas.
- Local `#/$defs/fileRef` resolution works; type checks distinguish booleans from integers/numbers.
- Both frozen schemas use closed-world object constraints, nested metadata/fileRef/presentation fields are checked, and conditional Share/Sermon profile/category/person/archive plus translation/fidelity constraints are present.
- Website fixtures and the Stage C schema tests exercise positive/negative Share and Sermon cases, nested unknown fields, wrong profile, missing category, archive mismatch and fidelity mismatch.

Residual note: the consumer is a bounded implementation of the exact current frozen schema subset, not a general Draft 2020-12 implementation. It should continue to reject unsupported schema keywords rather than silently expanding the contract.

## 4. Package/file identity and fail-closed checks

**Result: PASS for exercised package validation paths.**

Code review and tests cover:
- package top-level and nested unknown fields;
- required metadata and fileRef fields;
- path resolution under the supplied content root, regular-file checks and SHA-256 verification;
- symlink/path escape protection for package-bound file references through strict resolution and `relative_to(content_root)`;
- five-way distinct identity paths: official Chinese candidate, presentation artifact, manifest, validator report and paired package;
- manifest/report/paired package cross-bindings, candidate/artifact/report/paired hashes, record count, record IDs/order, record-order digest, pair-set SHA and audit ID;
- prepublish body text identity with the bound presentation artifact after the declared frontmatter separator;
- malformed JSON and malformed nested report/manifest structures handled through object guards and fail-closed errors;
- validation is read-only and does not rewrite package-bound files.

The validator's `read_json` rejects non-object JSON and wraps malformed JSON/read errors. The five-way path check rejects missing identity members and resolved-path collisions.

## 5. Translation/fidelity boundary, archive semantics and Scripture/TTS

**Result: PASS for the inspected v1.3 consumer boundary.**

- Website reads and validates the package's publication-facing `translation_status` and `fidelity_status` values; it does not adjudicate translation fidelity, Project Bible correctness, source completeness or theology.
- The schema and consumer enforce translated statuses only with `independently_verified`, `pass_by_max_audit_policy` or `authorized_exception`; not-translated requires `not_required`.
- Share archive status is constrained to `not_applicable`; Sermon requires one of the protected archive states.
- Share source selection points only to a direct child under Website `data/raw/分享`; the Share consumer path contains no NAS/archive access.
- Website scripture normalization is detection-only on the frozen presentation artifact. Compact Chinese references, detected English book/chapter:verse references and references changed by normalization fail closed; the frozen artifact is not rewritten.
- The package tests exercise spoken Chinese references, compact Chinese references, discontinuous lists and English references.

## 6. Share/Sermon rendered structure profiles

**Result: PASS for profile separation and inspected renderer gates.**

- Share uses Astro's `@astrojs/markdown-remark` processor and checks H2/H3 heading identity, list item count, blockquote block count, paragraph boundaries, nonempty rendered content and internal workflow-note residue.
- Share does not inherit sermon-only Full Sermon Mode, three-point outline, discussion, prayer or benediction requirements.
- Sermon delegates to the existing `validate_sermon_presentation.mjs` validator, preserving sermon-specific hard gates.
- The focused renderer tests exercise Share article structure, no sermon-outline requirement, workflow-note rejection and unknown-profile rejection.

## 7. Share import identity and security

**Result: FAIL — blocking finding F-01; related finding F-02.**

### F-01 — Direct Share presentation importer bypasses the mandatory package boundary

- Severity: **P1 / BLOCKER**
- Exact location:
  - `scripts/import_shares.py:239` — parser accepts `--presentation-file` but has no `--publication-package` or package/schema argument.
  - `scripts/import_shares.py:464-472` — direct importer reads the supplied artifact and switches to the frozen-artifact body path without any package verification.
  - `scripts/import_shares.py:508` — presentation artifact is used directly as the rendered body.
  - `scripts/import_shares.py:547-557` — non-dry-run writes the processed Markdown and copies it to the Website post path when publishable.
- Contract violated: Stage C audit request §7 requires direct Share presentation import without a package to fail closed. Stage C implementation plan §2 requires v1.3 Share import to be a package-bound adapter; Stage F remains the only activation point.
- Adversarial verification: invoked `import_shares.main()` with `--source-file` and `--presentation-file`, with no package argument available, using temporary source/artifact/output directories. The importer returned successfully, created `unbound-direct-import.md` in the temporary processed directory, and preserved the unbound presentation body exactly. The code path then reaches the normal post-copy branch for publishable content. No real Website paths were used.
- Consequence: a caller can bypass `consume_publication_package.py` and `content_workflow.py`, import a presentation artifact without the SHA-bound publication package, and write a post through the direct importer before Stage F. This is a direct production activation-boundary bypass, not merely missing test coverage.
- Required remediation boundary: direct Share importer must fail closed for presentation mode unless a package identity is supplied and independently validated (or presentation mode must be made inaccessible except through a package-verified internal adapter). Existing legacy Share import without `--presentation-file` must remain unchanged. Re-test the direct CLI adversarially and verify no output files are created on rejection.

### F-02 — Underlying v1.3 workflow does not bind caller-supplied source/metadata to prepublish identity

- Severity: **P2 / MAJOR**
- Exact location:
  - `scripts/content_workflow.py:192-220` — package is revalidated and the artifact path is compared, but prepublish frontmatter is not parsed here and the caller-supplied source/title/author/date/scripture/tags are not checked against it.
  - `scripts/content_workflow.py:248-275` — caller-supplied Share source and metadata arguments are forwarded to `import_shares.py`.
- Contract violated: Stage C audit request §7 requires source selector binding and metadata identity; §3 requires package/file identity; the underlying workflow is an independent consumer entrypoint and must not trust caller arguments in place of the package-bound source selector.
- Adversarial verification: constructed a valid temporary v1.3 Share package whose SHA-bound prepublish frontmatter selected `data/raw/分享/sample.txt`. Called the real `content_workflow.publish()` with the same valid package and bound artifact but `source_file="different-source.txt"`, `title="Spoofed title"` and `author="Spoofed Author"`. The workflow ran the real package validator and real Share renderer gate, then forwarded the different source/title/author to the importer command. The final importer process was intercepted before execution; no files were written. This proves the workflow itself does not enforce those bindings.
- Qualification: the current v1.3 workflow correctly rejects non-dry-run publish before Stage F. F-02 demonstrates wrong identity can still enter a controlled dry-run/acceptance invocation; it does not demonstrate a v1.3 production write through this workflow.
- Required remediation boundary: derive or validate source selector and publication metadata from the SHA-bound prepublish/package within the underlying workflow itself, not only in the outer package consumer. Add real invocation tests proving mismatched source, title, author, date, scripture and tags fail before importer invocation.

## 8. Sermon import compatibility and v1.0/v1.1/v1.2 compatibility

**Result: PASS for inspected compatibility paths and regression coverage.**

- v1.3 Sermon consumer requires an explicit v1.3 package, package-bound presentation artifact, package validator PASS and existing sermon structure gate.
- The v1.2 Sermon compatibility route remains available through the legacy validator and existing presentation binding rules.
- Legacy Share without `--presentation-file` remains routed through its existing source-based cleanup/formatting path.
- The legacy package validator continues to accept versions `1.0`, `1.1` and `1.2`; version-bound SHA/fidelity behavior remains covered.
- Existing v1.0 validation, v1.1 prepublish SHA requirement and v1.2 nested enum/pattern/type/fidelity behavior were included in the full suite and focused compatibility suite.
- No changes were made to legacy validator schemas or production defaults in this audit.

## 9. Production activation boundary

**Result: PARTIAL — the controlled consumer/workflow gates pass, but F-01 bypasses them.**

Positive evidence:
- `consume_publication_package.py` selects v1.3 only with the exact Website v1.3 schema path.
- v1.3 publish mode is rejected by the consumer even when `--allow-write` is supplied.
- The underlying `content_workflow.publish()` v1.3 branch rejects `dry_run=False`.
- `CONTENT_WORKFLOW.md` and `STATUS.md` state that production remains on the existing Share route and Sermon v1.2 route until Stage F.
- Canonical Website is clean at the frozen baseline and the v1.3 consumer was not wired into the current canonical production route.

Blocking qualification:
- The direct `import_shares.py --presentation-file` route bypasses the above consumer/workflow gates and can write a post without a package. Therefore the statement “v1.3 publish is disabled before Stage F” is not true across all Website import entrypoints.

## 10. Regression and verification evidence

All commands were run from the exact Website construction worktree. No dependencies were installed or upgraded.

| Check | Command | Exit | Result |
|---|---|---:|---|
| Full Website Python suite | `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` | 0 | 237/237 PASS |
| Stage C focused five-module suite | `python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation` | 0 | 36/36 PASS |
| Legacy consumer compatibility suite | `python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run` | 0 | 25/25 PASS |
| Share Tag Pipeline | `npm run check:tags` | 0 | 27/27 PASS |
| Python compile | `python3 -m py_compile scripts/consume_publication_package.py scripts/content_workflow.py scripts/import_shares.py scripts/validate_publication_package_v13.py scripts/publication_contract_invariants.py` | 0 | PASS |
| Node syntax | `node --check scripts/validate_content_presentation.mjs` | 0 | PASS |
| Whitespace/diff check | `git diff --check` | 0 | PASS |

The tests pass but do not cover the direct Share importer bypass. The existing test `test_share_presentation_import_without_package_is_blocked` exercises `content_workflow.publish()`; it does not invoke `import_shares.py` directly. The positive Share presentation import test calls the importer directly with an artifact and therefore demonstrates the missing package gate rather than guarding against it.

The focused workflow tests mock subprocesses; the adversarial F-02 verification supplemented them by running the actual package validator and actual Share renderer before intercepting the final importer invocation.

## 11. Stage state and side-effect confirmation

- Stage A: PASS; Re-Audit 02 chronology preserved.
- Stage B: PASS and accepted by Master; accepted report SHA verified.
- Stage C: **FAIL — implementation remediation required**.
- Stage D: BLOCKED pending remediation and fresh independent PASS acceptance.
- Stage E: not started.
- Stage F: disabled; no production activation is authorized by this audit.

This Auditor performed read-only workspace inspection, file reads, SHA-256 checks, code review, Git metadata/status inspection, regression tests, and adversarial checks using temporary directories. The only repository write is this report.

No implementation, test, schema, fixture, plan, STATUS, task-index or historical report was edited. No production import, real raw/processed/posts write, build, NAS access/read/write, email, notification, commit, push, merge, deploy, Stage D, Stage E or Stage F operation was performed. The direct-import adversarial test wrote only inside an automatically cleaned temporary directory; the workflow identity test intercepted the importer before execution.

## 12. Final verdict and handback

**FAIL — Stage C Website Consumer is not ready for Master acceptance.**

Blocking items:
1. F-01 P1: direct Share presentation importer can import and write without a publication package and bypasses Stage F.
2. F-02 P2: direct v1.3 workflow invocation does not bind caller-supplied source/metadata to the SHA-bound prepublish identity.

All declared regression suites passed, but they do not override the adversarially demonstrated boundary failures.

Return to Master for one bounded remediation round covering F-01 and F-02, followed by a fresh independent re-audit. Do not start Stage D until the new independent audit returns PASS and Master accepts it.

The report's SHA-256 is calculated after read-back and returned separately in the formal Master handback; it is not embedded in the file because embedding a file's own full SHA-256 would change the digest.
