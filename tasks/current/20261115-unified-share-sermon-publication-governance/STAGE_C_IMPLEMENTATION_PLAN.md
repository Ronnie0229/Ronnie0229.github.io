# Stage C — Website Consumer Implementation Plan

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: C — Website consumer
- Owner: Website project
- Executor: Master / Website Owner implementation authority
- Status: `REMEDIATION_03_IMPLEMENTED_PENDING_INDEPENDENT_REAUDIT`
- Baseline branch: `task/unified-share-sermon-publication-stage-a-20261116`
- Baseline HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Canonical Website remains `main` and must remain clean.
- Stage B Owner acceptance: PASS, report SHA-256 `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`.

## 1. Authority and frozen contracts

The Sermon Owner contract is authoritative:
- `content-presentation/v1`
- `website-publication-package/v1.3`
- Stage A schemas, fixtures and `scripts/publication_contract_invariants.py` mirror.

Website consumes Owner evidence; it does not adjudicate translation fidelity, Project Bible correctness, source completeness or sermon theology. Website must verify package/file identity, schema/profile, archive semantics, prepublish/presentation consistency, rendered HTML and import safety.

## 2. Bounded Stage C write-set

Implement only the Website consumer/rendering/import boundary:
1. Extend package validation to support v1.3 without weakening v1.0/v1.1/v1.2 historical compatibility.
2. Enforce v1.3 closed-world top-level, nested metadata, fileRef and presentation fields; enforce conditional Share/Sermon category/person/archive semantics and translation/fidelity relationship.
3. Verify all package-bound file paths are within the supplied content root, exist, and match SHA-256. Verify manifest/report/paired-package identities, candidate/artifact/report/paired SHA bindings, five-way identity path distinctness, record count/IDs/order and call the shared `validate_package_presentation_bindings` helper.
4. Add profile-aware rendered structure validation using the existing Astro Markdown renderer. Share profile must validate article structure without imposing sermon-only outline/Full Sermon Mode requirements. Sermon profile must retain all existing sermon-specific gates.
5. Apply Website controlled scripture display normalization as a fail-closed pre-freeze check for v1.3: any compact Chinese or unresolved/English scripture reference in the frozen presentation artifact must block; do not mutate package-bound bytes or guess book names.
6. Add a v1.3 Share import adapter that consumes the verified presentation artifact as the body, preserving its headings, paragraphs, lists, quotations, dialogue, prayers, questions and ending exactly. Read publication-facing metadata from the SHA-bound prepublish frontmatter plus package metadata. Do not re-run legacy text cleanup/formatting on the frozen artifact.
7. Add v1.3 Sermon controlled consumer support while retaining the existing sermon presentation validator and importer semantics.
8. Keep v1.3 behind explicit package selection for controlled plan/dry-run/acceptance. Do not wire v1.3 into current production entrypoints or alter current production defaults; Stage D handles documentation/entrypoint cutover and Stage F enables production.
9. Keep the existing Share production route and v1.2 Sermon route operational until Stage F. Do not break historical read-only compatibility.

## 3. Explicit exclusions

- No production content import, raw/processed/posts write, build/deploy, commit/push, email/notification, NAS access/write, historical article rewrite or production default switch.
- No dependency installation or upgrade.
- No change to canonical Website `main`; no mutation of canonical Sermon.
- No duplication or redefinition of Sermon Owner fidelity, Project Bible or theology rules.
- No broad importer refactor outside the exact v1.3 package adapter.
- Do not add a new service/daemon/registry/platform.

## 4. Required tests

- v1.3 positive Share and Sermon packages.
- v1.3 rejection: unknown top-level/nested/fileRef fields, wrong profile/content_type, missing identity fields, wrong category/person, wrong archive status, invalid translation/fidelity pair, SHA drift, missing/out-of-root file, manifest/report/paired mismatch, path collision, record count/order/pair-set mismatch.
- Historical v1.0/v1.1/v1.2 fixtures remain accepted/rejected exactly as before.
- Share structure positive fixtures: normal article headings, paragraphs, lists, blockquotes, quotes/dialogue; no sermon three-point outline requirement.
- Share structure negative fixtures: lost heading/list/blockquote, collapsed long text, compact Chinese reference, unresolved English reference.
- Sermon structure suite remains fully passing, including all sermon-only rules.
- v1.3 Share importer consumes the exact body artifact and preserves byte/text identity; it must not apply legacy `normalize_text` / `format_body` transformations to the artifact.
- Direct existing production routes remain unchanged and tests prove v1.3 is not selected implicitly.
- Full relevant Python and Node regression suites, Python compile, `git diff --check`.

## 5. Acceptance / handoff

Stage C is complete only after:
- all required tests pass with exact counts recorded;
- schemas/helper remain byte-identical to Sermon Owner copies;
- Website canonical `main` remains clean and unchanged;
- Stage C implementation report and independent read-only audit request are written;
- independent Auditor returns formal PASS and Master accepts it.

Stage D remains BLOCKED until Stage C independent PASS is accepted. Stage F remains disabled.
