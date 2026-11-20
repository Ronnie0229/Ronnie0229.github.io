# Stage D Implementation Report — Share / Sermon Unified Publication Governance

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: D — Documentation and Entrypoint Cutover
- Status: `IMPLEMENTATION_COMPLETE_PENDING_INDEPENDENT_AUDIT`
- Date: 2026-11-18
- Frozen plan: `STAGE_D_IMPLEMENTATION_PLAN.md`
- Frozen plan SHA-256: `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e`
- Canonical design authority: Sermon Owner `DESIGN.md`, SHA-256 `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f`

## 1. Executive result

Stage D's bounded documentation alignment and CLI/entrypoint consistency work is complete in the two named construction worktrees. The D-01..D-12 acceptance denominator is presented for independent review. This report does not self-accept Stage D.

The main conflict found and resolved was that Website operating sections still presented `publish share` / `publish sermon` as unqualified unified routes, even though Stage F is not enabled and v1.3 is still a controlled candidate. The docs now explicitly distinguish:
- Stage F前现行兼容生产路径：Share legacy approved route; Sermon v1.2 / `sermon-presentation/v1` route.
- v1.3 controlled contract path: `content-presentation/v1` + `website-publication-package/v1.3`, consumed through `publish-contract`, limited to `plan` / `dry-run` before Stage F.
- Stage F production enablement: remains DISABLED and requires separate Stage E acceptance and Owner authorization.

No production route/default was switched. No v1.3 non-dry-run write was enabled.

## 2. Implementation scope and changed files

### Website construction worktree

Documentation aligned:
- `AGENTS.md`
- `CONTENT_WORKFLOW.md`
- `docs/统一内容整理与发布流程.md`
- `docs/sermon-content-rendering-binding.md`
- `docs/content-style.md`
- `docs/content-publishing-error-prevention.md`
- `skills/article-workflow.md`

Entrypoint alignment:
- `scripts/content_workflow.py`: CLI help now labels `publish` as the current compatibility route and `publish-contract` as the v1.3 controlled consumer. `--mode publish` and `--allow-write` help explicitly state that `--allow-write` cannot override the Stage F block.
- No new consumer, state machine, registry, service, daemon, or parallel workflow was added.

### Sermon construction worktree

Documentation aligned:
- `AGENTS.md`
- `docs/end-to-end-content-publishing-workflow.md`
- `docs/chinese-to-prepublish-md-workflow.md`
- `docs/prepublish-md-metadata-quality-gate.md`
- `docs/sermon-and-publishing-metadata.md`
- `docs/scripture-reference-display-normalization.md`
- `docs/translation-fidelity-policy.md`

Entrypoint review:
- `scripts/generate_prepublish_md.py`, `scripts/build_website_publication_package.py`, and `scripts/export_to_website_project.py` CLI help/dispatch were checked against the docs.
- Existing explicit v1.3 contract-version, content-presentation manifest, package builder and `--publication-package` export interface already match the controlled contract; no producer behavior change was required.
- `docs/translation-fidelity-orchestration.md` and `docs/nas-access-policy.md` were reviewed and left unchanged because their current content-type-neutral fidelity and no-Share-archive boundaries already align.

### Task evidence

This report, the independent audit request, and the current status/index updates are mirrored in both construction worktrees. The plan remains byte-identical and unchanged.

## 3. Documentation conflict matrix

| Area / evidence | Conflict found | Resolution / final interpretation |
|---|---|---|
| Website `CONTENT_WORKFLOW.md` and `docs/统一内容整理与发布流程.md` legacy Share/Sermon sections | Old `publish share` / `publish sermon` instructions could be mistaken for the new v1.3 unified route | Sections now explicitly label them Stage F前 legacy/current production compatibility paths; v1.3 package validation is documented separately through `publish-contract --mode plan|dry-run` |
| Website `skills/article-workflow.md` | It described v1.2 as current sermon default without the Stage F migration boundary, and its Step 5 commands appeared to be the unified entrypoint | Clarified v1.2 as the current production sermon route until Stage F; legacy commands are labeled as such; v1.3 uses the controlled package consumer; handoff-memory file is historical context only |
| Website `docs/content-publishing-error-prevention.md` | References to v1.2 current default and v1.1 compatibility lacked explicit v1.3 candidate boundary | Clarified Stage F前 v1.2 production, v1.1 historical compatibility, and v1.3 controlled candidate semantics |
| Sermon `AGENTS.md` | v1.2 package binding could be read as a permanent default | Clarified current v1.2 / `sermon-presentation/v1` production route before Stage F and v1.3 controlled candidate path |
| Sermon end-to-end and prepublish workflows | Needed one unambiguous order and activation boundary | Aligned TTS scripture normalization → candidate SHA/structured-pair freeze → shared fidelity release (when translation occurs) → Project Bible/CUVMPS gate → profile-specific presentation artifact/manifest → v1.3 package → Website consumer/render gate; Stage F remains the production cutover |
| Metadata/person/archive docs | Risk of default identity overriding explicit identity or Share being routed to NAS archive | Both projects state Ronnie/Patrick are fallback-only; explicit source/Owner identity wins; Share is `not_applicable` and never accesses NAS archive; Sermon keeps protected append-only archive |
| Fidelity policy/orchestration | Risk of content-specific fidelity fork or `not_required` for translated content | One existing common state machine; unchanged three-attempt/three-repair release semantics; only pure-Chinese non-translation may use `not_required`; no fidelity implementation changed |
| `docs/codex-handoff-memory.md` (outside frozen write-set) | Contains historical legacy command references | Not modified; Website skill now explicitly marks it historical context only and prevents it overriding current workflow docs, frozen contracts or actual CLI behavior |

## 4. Frozen business invariants confirmed

- Share intake: `NAS/分享收件`; category `灵命成长`; `author` fallback Ronnie only; explicit source/Owner author wins; `archive_status=not_applicable`; terminal `SHARE_ARCHIVE_NOT_APPLICABLE`; no NAS archive path access.
- Sermon intake: `NAS/讲道收件`; category `教会讲道`; `speaker` fallback Patrick only; explicit source/Owner speaker wins; protected append-only NAS archive remains required.
- Share retains its own source article structure and does not inherit sermon three-point outline, Full Sermon Mode, discussion or benediction requirements.
- Sermon retains Full Sermon Mode and all existing sermon-specific presentation gates.
- Any source-language-to-Chinese translation uses the existing shared fidelity state machine. No share-specific loop, reduced denominator, relaxed reviewer isolation or altered attempt/repair limits.
- TTS scripture display normalization occurs before candidate SHA freeze. Non-contiguous/ambiguous references and uncontrolled English book names fail closed; compact machine metadata remains permitted.
- Sermon Owner owns source extraction, translation fidelity, Project Bible and sermon theology. Website owns package consumer validation, rendered structure, website metadata/import/build/Git/deploy/SEO/notification.
- Historical v1.0/v1.1/v1.2 packages, `sermon-presentation/v1` readers, posts, URLs, articleIds and audit chronology remain unchanged.

## 5. Entrypoint and code consistency evidence

### Website consumer

- `python3 scripts/content_workflow.py publish-contract --help` exits 0 and exposes `--contract`, `--schema`, `--content-root`, `--mode {plan,dry-run,publish}`, `--allow-write`, and `--plan-output`.
- CLI help states `v1.3 publish is fail-closed before Stage F, regardless of --allow-write` and `--allow-write` does not override the block.
- `scripts/consume_publication_package.py` explicitly raises `v1.3 publish is disabled before Stage F; only plan and dry-run modes are permitted` for v1.3 publish mode.
- `scripts/tests/test_consume_publication_package_v13.py::V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f` passes while calling the consumer with `allow_write=True`.
- `scripts/content_workflow.py` package-bound path validates package version/content type, bound presentation artifact, package validator evidence, Share source identity and package-bound metadata; it rejects non-dry-run v1.3 workflow publish.
- Stage C direct Share importer package/source/metadata gates and legacy Ronnie fallback isolation remain in place; Stage C regression suite rerun below.

### Sermon producer

- `generate_prepublish_md.py` requires explicit v1.3 contract presentation-manifest binding.
- `build_website_publication_package.py` enforces profile-specific v1.3 archive semantics: Share `not_applicable`; Sermon cannot use `not_applicable`.
- `export_to_website_project.py` requires `--publication-package` and revalidates package, manifest, paired package and bound artifacts.
- Share uses `share_article`; Sermon uses `sermon`; the profiles are not interchangeable.

## 6. D-01..D-12 acceptance matrix — Master evidence

| ID | Result | Evidence |
|---|---|---|
| D-01 | PASS | Frozen Stage D plan matches canonical DESIGN.md authority, prerequisites and bounded write-set; no scope expansion |
| D-02 | PASS | Both projects consistently document the exact intake, fallback identity and archive differences; explicit identity wins |
| D-03 | PASS | Share article-native structure is preserved; Sermon Full Sermon Mode and sermon-only gates remain |
| D-04 | PASS | Shared fidelity state machine retained; correct candidate/fidelity/Project Bible ordering; no fidelity rules or release semantics changed |
| D-05 | PASS | TTS normalization is pre-freeze; controlled book names and non-contiguous fail-closed behavior documented; machine metadata exception retained |
| D-06 | PASS | Both projects bind `content-presentation/v1` and `website-publication-package/v1.3` with profile-specific artifacts and package references |
| D-07 | PASS | v1.3 Share/Sermon consumer is one `publish-contract` entrypoint; direct importer independently validates package/source/metadata; no bypass introduced |
| D-08 | PASS | Producer CLI and docs agree on explicit contract version, manifest, profile, archive semantics and package-bound export |
| D-09 | PASS | v1.0/v1.1/v1.2 and `sermon-presentation/v1` compatibility preserved; no historical content/package migration or rewrite |
| D-10 | PASS | v1.3 publish remains blocked even with `--allow-write`; Stage F disabled; current production routes/defaults unchanged |
| D-11 | PASS | Full and focused tests, CLI help, Python compile, Node syntax and diff checks all pass; commands/counts recorded below |
| D-12 | PASS | Exact workspaces/branches/HEAD confirmed; canonical worktrees untouched; no staging or prohibited side effects |

These are Master implementation findings for the independent Auditor to verify, not a self-issued Stage D acceptance.

## 7. Verification commands and results

### Website construction worktree

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q
  exit 0 — 269/269 PASS
python3 -m unittest scripts.tests.test_validate_content_presentation scripts.tests.test_validate_publication_package_v13 scripts.tests.test_consume_publication_package_v13 scripts.tests.test_content_workflow_v13_share scripts.tests.test_import_share_presentation scripts.tests.test_share_source_identity -q
  exit 0 — 68/68 executions PASS
python3 -m unittest scripts.tests.test_consume_publication_package scripts.tests.test_validate_publication_package scripts.tests.test_run_fixed_publication_dry_run -q
  exit 0 — 25/25 PASS
npm run check:tags
  exit 0 — 27/27 PASS
python3 -m py_compile scripts/content_workflow.py scripts/consume_publication_package.py scripts/import_shares.py scripts/import_sermons.py scripts/validate_publication_package_v13.py
  exit 0
node --check scripts/validate_content_presentation.mjs
  exit 0
python3 scripts/content_workflow.py publish-contract --help
  exit 0
python3 -m unittest scripts.tests.test_consume_publication_package_v13.V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f -v
  exit 0 — PASS, including allow_write=True negative test
git diff --check
  exit 0
```

One initial attempt to invoke the focused Stage F unit test used an incorrect unittest class name and returned a loader error; the correct exact test selector was then run and passed. This was a test-selector invocation error, not a code/test failure.

### Sermon construction worktree

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -q
  exit 0 — 59/59 PASS
python3 -m unittest scripts.tests.test_build_website_publication_package scripts.tests.test_export_to_website_contract scripts.tests.test_unified_publication_producer_stage_b scripts.tests.test_share_fidelity_loop_stage_b scripts.tests.test_unified_publication_contract_stage_a -q
  exit 0 — 35/35 PASS
python3 -m py_compile scripts/generate_prepublish_md.py scripts/build_website_publication_package.py scripts/export_to_website_project.py scripts/run_translation_fidelity_loop.py
  exit 0
git diff --check
  exit 0
```

### Contract and mirror identity

| Object | Website SHA-256 | Sermon Owner SHA-256 | Result |
|---|---|---|---|
| `content-presentation/v1` schema | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5` | byte-identical |
| `website-publication-package/v1.3` schema | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e` | byte-identical |
| `publication_contract_invariants.py` | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0` | byte-identical |
| Stage D implementation plan | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | `95e6da3471bdc8c9869f83b1949cfb4fb77113dda07b06ba287f4ca56705e93e` | byte-identical |

## 8. Workspace and side-effect evidence

| Workspace | Branch | HEAD | Final state |
|---|---|---|---|
| Website construction | `task/unified-share-sermon-publication-stage-a-20261116` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | Existing Stage A/C dirty lineage plus bounded Stage D docs/CLI-help edits; no staged files |
| Sermon construction | `task/unified-share-sermon-publication-stage-a-20261116` | `812ace500102bac54cb54cb0fa2249341118a3da` | Existing Stage A/B dirty lineage plus bounded Stage D docs edits; no staged files |
| Website canonical | `main` | `09ce7eb588a21745d0286d3eec6a890c16a26aea` | Clean; untouched |
| Sermon canonical | `master` | `812ace500102bac54cb54cb0fa2249341118a3da` | Pre-existing dirty lineage and `ahead 2` preserved; untouched |

No Git staging/commit/push/merge/reset/clean/rebase/amend. No production import, content mutation, Astro build, deploy, email/notification, dependency install/upgrade, NAS probe/read/write/archive, or Stage E synthetic E2E execution. Tests used their existing isolated temporary fixtures.

## 9. Stage boundary and handoff

- Stage A: PASS.
- Stage B: PASS / Master accepted.
- Stage C: PASS_WITH_FINDINGS / Master accepted; RF-01 residual remains disclosed.
- Stage D: implementation complete; **independent audit pending**.
- Stage E: NOT STARTED.
- Stage F: DISABLED.

Independent Auditor must freshly inspect both construction worktrees, canonical DESIGN.md, this report and the frozen plan; verify all D-01..D-12 independently; recompute hashes; inspect current scripts and test evidence; confirm no production/Git/NAS side effects; and write only `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_D_AUDIT_REPORT.md` in the Website construction worktree.

Stage D is not accepted until the separate Auditor verdict and subsequent Master acceptance. No Stage E/F authorization is implied.