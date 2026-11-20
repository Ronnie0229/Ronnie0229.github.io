# Stage C Implementation Report — Website Consumer

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: C — Website consumer
- Workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- Baseline HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Status: `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`
- Stage B prerequisite: Master accepted independent PASS on 2026-11-17; report SHA-256 `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`.

## 1. Implementation result

Stage C Website consumer is implemented as an explicitly selected v1.3 candidate path. It does not replace the current production entrypoints.

### Package v1.3 validation

Added `scripts/validate_publication_package_v13.py`:
- Validates the Website mirror v1.3 package schema and the bound `content-presentation/v1` manifest.
- Implements the complete keyword subset currently used by the two frozen schemas: `$ref/$defs`, `type`, `const`, `enum`, `required`, `properties`, `additionalProperties`, `items`, `minItems`, `uniqueItems`, `minLength`, `pattern`, `minimum`, `format=date-time`, `allOf`, `if`, and `then`.
- Fails closed if either schema introduces an unsupported keyword or format.
- Verifies package file references are regular files within the supplied content root and SHA-256 matches.
- Verifies candidate, artifact, manifest, validator report and paired package are five distinct resolved paths.
- Verifies manifest/report/paired-package cross-bindings, record IDs/order/count, candidate/artifact/report/paired hashes, audit ID and pair-set identity through the shared Owner helper plus consumer-side checks.
- Requires the prepublish Markdown body to be text-identical to the bound body-only presentation artifact.
- Checks TTS scripture display without mutating frozen bytes: compact Chinese references, discontinuous reference lists and detected English book/chapter:verse forms fail closed; spoken Chinese forms pass.
- Enforces Share/Sermon profile, category/person, translation/fidelity and archive semantics.

### Profile-aware rendered structure

Added `scripts/validate_content_presentation.mjs`:
- Share uses the Astro Markdown renderer and checks H2/H3 heading identity, paragraph boundaries, list item count, blockquote block count, nonempty rendered content and internal workflow-note residue.
- Share does not inherit sermon-only Full Sermon Mode, three-point outline, discussion, prayer or benediction requirements.
- Sermon delegates to the existing sermon presentation validator, retaining all sermon-only hard gates.

### Controlled consumer and Share import

Updated `scripts/consume_publication_package.py`, `scripts/content_workflow.py` and `scripts/import_shares.py`:
- v1.3 is selected only by an explicit package and exact v1.3 schema path.
- v1.3 Share and Sermon flows bind the package path, content root and presentation artifact; the workflow revalidates the package before continuing.
- v1.3 Share imports the exact body-only presentation artifact. It does not run legacy `normalize_text`, `strip_leading_title` or `format_body` transformations over frozen presentation content.
- Share title, description, scripture, tags, category, author, date and source selector are checked/derived from the SHA-bound prepublish frontmatter and package metadata.
- Source selectors reject path traversal and require a single Website raw Share file or a Sermon source folder.
- A v1.3 Share presentation import without its publication package is blocked.
- v1.3 publish mode is blocked both in the package consumer and the underlying workflow until Stage F. Only plan and dry-run are permitted.
- Existing Share production route and existing v1.2 Sermon route remain operational and unchanged pending Stage F.

### Documentation

Updated `CONTENT_WORKFLOW.md` to state that current production entrypoints remain unchanged before Stage F and the new v1.3 consumer is a controlled plan/dry-run candidate only.

## 2. Test evidence

**237/237 PASS**

- Full Website Python suite: `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` — **237/237 PASS**.
- Stage C focused new tests: **36/36 PASS** across five test modules.
- Share Tag Pipeline: `npm run check:tags` — **27/27 PASS**.
- Python compile: all four modified consumer/import scripts compile.
- Node syntax check: `node --check scripts/validate_content_presentation.mjs` — PASS.
- `git diff --check` — PASS.
- Stage A v1.3 schemas and shared `publication_contract_invariants.py` mirror are byte-identical to the Sermon Owner copies.

Negative tests include unknown schema/package fields, unsupported schema keywords, wrong profile/category/archive/fidelity, missing identity, candidate/report SHA drift, path escape/traversal, identity-path collision, pair-set mismatch, prepublish/artifact mismatch, compact/English/discontinuous scripture references, Share presentation import without package, v1.3 publish attempts, and Share/sermon structural failures.

## 3. Workspace and side-effect boundary

- Website construction remains on the designated task branch and baseline HEAD; implementation is unstaged.
- Canonical Website `main` remains clean and synchronized with origin.
- Canonical Sermon was not modified; its pre-existing dirty lineage remains preserved.
- Sermon construction Stage B files were not modified by Stage C implementation.
- No dependency installation/upgrade, build, production content import, NAS access/write, email/notification, commit, push, merge or deploy occurred.
- No production entrypoint was switched to v1.3.

## 4. Known limitations / retained chronology

- Stage B first independent audit remains historical FAIL (B-01/B-02/B-03); Remediation 01 Re-Audit 01 is the later independent PASS accepted by Master. Both reports and hashes remain intact.
- Moses broader suite remains 9 PASS / 1 ERROR as the disclosed non-blocking legacy coverage limitation from Stage B; Stage C does not alter or conceal it.
- Stage A chronology remains unchanged: initial FAIL → Re-Audit 01 PASS_WITH_FINDINGS → Remediation 02 / Re-Audit 02 PASS.

## 5. Stage status

- Stage A: PASS.
- Stage B: PASS, independent re-audit accepted by Master.
- Stage C: implementation complete, awaiting independent read-only audit.
- Stage D: BLOCKED until Stage C independent PASS is accepted.
- Stage E: not started.
- Stage F: disabled; no v1.3 production activation.

No commit/push/deploy authorization is implied by this report.
