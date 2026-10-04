# Sermon Presentation Boundary Hardening — Independent Audit Result

## Formal terminal

`BLOCKED_INDEPENDENT_AUDIT_WEBSITE_NODE_DEPENDENCIES_NOT_MATERIALIZED`

This audit does **not** adopt the Owner's reported PASS. The exact Website construction worktree was opened and reviewed independently.

## Blocking reason

The exact Website construction worktree cannot fresh-run the required rendered structural verification:

- `node --test scripts/tests/test_sermon_presentation_gate.mjs` → 14 tests discovered, 0 pass / 14 fail because the validator cannot load `@astrojs/markdown-remark` (`ERR_MODULE_NOT_FOUND`).
- `npm run build` → fails before Astro build because `node_modules/astro/astro.js` is absent.

These are environment/dependency-materialization blockers, not observed implementation assertion failures. Under this audit's strict READ_ONLY / ZERO_REMEDIATION contract, installing dependencies, creating a construction-only symlink, or silently borrowing canonical `node_modules` is prohibited.

Therefore the auditor cannot truthfully establish the required fresh facts:

1. Website Node presentation suite = 14/14 PASS;
2. real Curve Ahead Website structure validator = `SERMON_PRESENTATION_STRUCTURE_PASS / publication_structure_ready`;
3. forced build = 344 pages / Complete.

## Independently established facts

All non-blocked checks completed without implementation findings:

- Contract boundary is correctly separated: frozen fidelity candidate != presentation artifact.
- Sermon producer Python suite: 20/20 PASS; relevant py_compile PASS.
- Independent producer attacks: wording change, record omission, record reorder, and forbidden construct all fail closed.
- v1.2 sermon package requires presentation manifest; prepublish v1.2 contract emission without it fails closed.
- Website Python suite: 61/61 PASS.
- Historical no-binding sermon package retains read-only validate/plan compatibility, while sermon dry-run/publish requires `PRESENTATION_ARTIFACT_REQUIRED`.
- Canonical importer requires `--presentation-file` and does not use plain TXT line boundaries through `normalize_body()` for formal paragraph structure.
- Curve Ahead fresh identity: candidate SHA `096a21672fc3a353b94b86749ae31d3bb5e0e17de553d83bc8a4ca0d083d8b73`; 144 frozen records; presentation restores 144/144 exact text+order; 138 paragraphs + 6 H2; artifact SHA `cee4791eab18fea14e0df5775641771d2adeca65a53a5ac45b06a00d1d239328`; package SHA `1b68bdde1754fdfde4390db0c588a54ae4465845ab8c760491de34d19375f8eb`.
- Curve Ahead Website package validator PASS and consumer plan PASS.
- Historical read-only scan: denominator 219; exact one same-class collapse hit `2026-07-09-马太福音-7-1-6｜论断人.md`, approximately 4287 chars / 1 paragraph / 0 H2.
- Content mirrors 600/600 PASS; Knowledge 300/0/0 PASS; tag fixtures 27/27 PASS.
- Changed-path review found no production article mutation, unrelated business article, node_modules change, construction symlink change, workspace-control schema mutation, deploy/notification/NAS side effect, or unrelated asset contamination.
- Website and Sermon current authority documents consistently separate fidelity, presentation identity, and rendered structural acceptance. Current authority is `SERMON_PRESENTATION_STRUCTURE_PASS / publication_structure_ready`; legacy `MECHANICAL_PRESENTATION_PASS` is compatibility/chronology only.

## Audit disposition

No implementation FAIL is issued because the blocked dynamic checks never reached the implementation assertions. No PASS is permitted because required fresh structural/build verification is incomplete.

The formal audit remains BLOCKED until the exact Website construction worktree can execute its declared Node/Astro dependencies without violating the worktree/audit boundary, followed by a fresh independent rerun of the blocked checks.
