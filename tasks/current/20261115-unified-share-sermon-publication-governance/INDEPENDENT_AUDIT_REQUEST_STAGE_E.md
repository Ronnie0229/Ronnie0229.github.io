# Independent Audit Request — Stage E Synthetic End-to-End Acceptance

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR` (not Master; read-only audit)
- Date: 2026-11-19
- Exact primary workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Primary workspace ID expected: `ws_36904a3d8e03f8682750de45`
- Read-only producer evidence workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Canonical Website comparison root: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- Canonical Sermon comparison root: `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`

## 1. Mandatory workspace procedure

1. Call `open_current_workspace`.
2. Open the exact primary Website construction workspace above; if root differs, switch immediately.
3. Open the Sermon construction, Website canonical and Sermon canonical comparison workspaces. Do not write to any of them.
4. Fresh-read the authority and evidence below. Do not rely on prior chat or Master summaries as evidence.
5. Confirm branch, HEAD, staged/unstaged/untracked state before and after audit.

## 2. Fresh-read authority and evidence

Read in Website construction:
- `AGENTS.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_E_ACCEPTANCE_PLAN.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_E_EXECUTION_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_D_IMPLEMENTATION_PLAN.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/TASK_INDEX.md`
- `scripts/consume_publication_package.py`
- `scripts/tests/test_stage_e_synthetic_e2e.py`
- `scripts/tests/test_validate_publication_package_v13.py`
- `scripts/tests/test_consume_publication_package_v13.py`
- `scripts/tests/test_content_workflow_v13_share.py`
- `scripts/tests/test_import_share_presentation.py`
- `scripts/tests/test_import_sermon_source_identity.py`
- `scripts/validate_content_presentation.mjs`
- `scripts/validate_publication_package_v13.py`
- Website schema mirrors and the relevant archive/scripture fixtures.

Read in Sermon construction (read-only):
- `AGENTS.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/DESIGN.md`
- `scripts/validate_content_presentation_artifact.py`
- `scripts/build_website_publication_package.py`
- `scripts/publication_contract_invariants.py`
- `scripts/translation_fidelity_orchestration_lib.py`
- `scripts/tests/test_unified_publication_producer_stage_b.py`
- `scripts/tests/test_share_fidelity_loop_stage_b.py`
- `scripts/tests/test_export_to_website_contract.py`
- `tests/test_scripture_reference_normalizer.py`
- relevant producer package/fidelity/archive fixtures.

Also fresh-read the Website canonical current dirty status. At Master completion it showed four modified files:
`AGENTS.md`, `STATUS.md`, `docs/task-handoff-protocol.md`, `docs/tasks/current.md`.
These were not changed by this Stage E execution and must not be attributed without evidence. Sermon canonical had 41 porcelain entries at completion. Preserve all current lineage.

## 3. Frozen acceptance denominator

The frozen Stage E plan defines E-01 through E-09. Do not edit the plan or change its denominator.

| ID | Proposition to audit |
|---|---|
| E-01 | Actual Share producer paired-presentation validation and v1.3 package builder; correct Share profile/metadata/archive semantics |
| E-02 | Actual Sermon producer paired-presentation validation and v1.3 package builder; correct Sermon profile/archive semantics |
| E-03 | Website consumer accepts valid Share/Sermon packages and rejects SHA drift, missing identity, profile/type mismatch, unknown fields and path escape |
| E-04 | Share and Sermon rendered structure checks use body-only artifacts; prepublish metadata remains SHA-bound; rendered HTML evidence SHA matches bound artifact SHA |
| E-05 | TTS-friendly Chinese scripture references pass; compact/English/discontinuous forms fail closed; normalization does not corrupt machine metadata |
| E-06 | Share `archive_status=not_applicable` and no NAS archive path; Sermon archive states remain distinct and invalid cross-profile states fail |
| E-07 | Shared fidelity Attempt 01–03 / repair 01–03 / terminal and max-audit rules; Attempt 04 blocked; v1.0/v1.1/v1.2 compatibility preserved |
| E-08 | Plan/dry-run read-only; v1.3 publish blocked before Stage F even with `--allow-write`; direct importer/workflow bypasses remain fail-closed |
| E-09 | Chronology, worktree boundaries, side-effect exclusions and completeness of synthetic end-to-end evidence |

## 4. Critical audit focus — E-F01 and its remediation

Master's first synthetic integrated run:
- Share synthetic producer-to-consumer passed.
- Sermon failed at `heading_render_integrity`, source headings=2 vs rendered headings=3.
- Root cause: Website consumer sent metadata-bearing prepublish Markdown (frontmatter + body) to the Sermon public-body structure gate.

Master changed `scripts/consume_publication_package.py`:
- Verify prepublish path/SHA.
- Resolve the package-bound body-only artifact and verify `presentation.artifact_sha256`.
- Pass the body-only artifact to the renderer.
- Compare renderer evidence source SHA to the artifact SHA.
- Package validator still binds prepublish body exactly to the artifact.

Independently determine whether this is the correct bounded fix and whether it introduces any bypass:
- prepublish SHA remains enforced;
- artifact path stays content-root constrained;
- artifact SHA is bound to the package and verified immediately before rendering;
- profile/status/completion ceiling/rendered SHA checks remain;
- Share and Sermon renderers are not conflated;
- caller-provided paths cannot replace package-bound artifact identity.

Do not accept E-F01 closure solely from the test author's assertions. Inspect implementation and rerun the synthetic test.

## 5. Important evidence limitation — final workflow dispatch stub

`scripts/tests/test_stage_e_synthetic_e2e.py`:
- Creates temporary synthetic Share and Sermon roots.
- Uses actual Sermon paired package builder utility.
- Executes actual generic presentation artifact validator.
- Executes actual Website Publication Package v1.3 builder.
- Executes actual Website consumer validation and body-only Node rendering.
- Builds the actual dry-run import command and checks read-only/metadata/archive/SHA evidence.
- **The final workflow subprocess is a synthetic stub**, not the real importer. Master explicitly records this limitation and does not claim a real importer execution.

Separately, Website existing regression suites exercise importer source identity, package-bound author/metadata, direct bypass, and dry-run behavior. Independently inspect whether these separate tests sufficiently satisfy the frozen Stage E acceptance denominator. If the final stub boundary leaves a mandatory gap, return BLOCKED or PASS_WITH_FINDINGS as appropriate; do not silently re-label the stub as a real importer run and do not expand scope by running a real production import.

## 6. Re-run verification (read-only)

At minimum:
- `python3 -m unittest scripts.tests.test_stage_e_synthetic_e2e`
- `python3 -m unittest discover -s scripts/tests -p 'test_*.py'` in Website construction
- `python3 -m unittest scripts.tests.test_consume_publication_package_v13.V13PackageImportCommandTests.test_v13_publish_mode_is_disabled_until_stage_f`
- `node --test scripts/tests/test_sermon_presentation_gate.mjs`
- `npm run check:tags`
- `python3 -m unittest discover -s scripts/tests -p 'test_*.py'` in Sermon construction
- `python3 -m unittest tests.test_scripture_reference_normalizer` in Sermon construction
- `uv run --isolated --no-project --offline --with jsonschema==4.26.0 -- python tasks/current/20261115-unified-share-sermon-publication-governance/validate_draft202012_stage_a.py`
- `git diff --check` in both construction worktrees
- Python compile / Node syntax checks for changed Website files.

You may run additional narrowly relevant read-only tests. Do not install/upgrade dependencies or run Astro production build.

## 7. Fixed chronology and safety checks

Verify:
- Original Stage D FAIL and Re-Audit 01 FAIL remain in history.
- Stage D Master accepted `PASS_WITH_FINDINGS` remains the current accepted state.
- Stage E plan frozen; report records initial E-F01 FAIL followed by bounded remediation and final tests.
- Stage E has not been prematurely accepted by Master.
- Stage F remains DISABLED; v1.3 non-dry-run remains blocked; `--allow-write` cannot override it.
- Current production routes/defaults remain unchanged.
- No NAS, production import/write, build, deploy, email/notification, dependency change or Git history operation occurred.
- No writes to Sermon construction or either canonical root.
- Website canonical four modified files are observed only; do not modify or attribute them.
- No Stage F execution or recommendation to enable production as part of this audit.

## 8. Auditor verdict and allowed write

Return one verdict:
- `PASS`
- `PASS_WITH_FINDINGS`
- `FAIL`
- `BLOCKED`

Assess E-01..E-09 individually, report any finding IDs, and explicitly state whether E-F01 is closed. Clearly distinguish actual producer/consumer execution, test stubs/mocks, and direct importer tests. Include commands, counts, worktree identities, side-effect attestations, residuals and SHA-256.

**The only permitted write in this audit is:**
`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_E_AUDIT_REPORT.md`

Do not modify source, tests, plans, implementation report, status, task index, contracts, canonical worktrees, or any other file. After writing, read the report back, calculate/verify SHA-256, and stop. Return the verdict to Master. Do not accept Stage E, begin Stage F, or execute production operations.
