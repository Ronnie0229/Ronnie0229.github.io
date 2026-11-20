# Stage E — Synthetic End-to-End Acceptance Plan

- Task: `20261115-unified-share-sermon-publication-governance`
- Stage: E — Synthetic end-to-end acceptance
- Status: `FROZEN / EXECUTION_COMPLETE_PENDING_INDEPENDENT_AUDIT`
- Date: 2026-11-19
- Website construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Sermon construction workspace (read-only evidence source): `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`
- Canonical design authority: Sermon Owner `tasks/current/20261115-unified-share-sermon-publication-governance/DESIGN.md`, SHA-256 `dbf7f7116323ed65b2e6b463e0a32aac0bbcbebdf817ff45fff33ef8e09eed7f`
- Prerequisites: Stage A PASS; Stage B PASS / Master accepted; Stage C PASS_WITH_FINDINGS / Master accepted; Stage D PASS_WITH_FINDINGS / Master accepted.

## 1. Goal and boundaries

Verify the already implemented Share/Sermon v1.3 producer-consumer contract using synthetic fixtures and read-only plan/dry-run execution. Stage E validates that the two existing implementations interoperate; it is not a new implementation or production cutover.

The only content types are synthetic Share and Sermon fixtures. Use the existing Stage B producer, Stage C consumer, existing renderers, validators and tests. Do not create a parallel validator, state machine, service, registry or framework.

## 2. Frozen acceptance matrix

| ID | Mandatory proposition | Required evidence |
|---|---|---|
| E-01 | Share producer path | Generic presentation identity, v1.3 package generation, Share metadata/profile and archive semantics validated using synthetic Share fixtures |
| E-02 | Sermon producer path | Generic presentation identity, v1.3 package generation, Sermon profile and protected archive-state semantics validated using synthetic Sermon fixtures |
| E-03 | Consumer interoperability | Website v1.3 validator accepts valid producer-shaped packages and rejects SHA drift, missing identity, wrong profile/type, unsupported fields and path escape |
| E-04 | Rendered structure | Share article profile passes without sermon-only outline requirements; Sermon profile retains the existing Full Sermon Mode structural gate; source and rendered HTML evidence are SHA-bound |
| E-05 | Scripture display | TTS-friendly Chinese references pass; compact/English/discontinuous references fail closed; normalization does not rewrite machine metadata |
| E-06 | Archive branch | Share accepts only `not_applicable` and has no archive-path operation; Sermon rejects `not_applicable` and accepts only controlled archive states; pending states are not represented as completed archive |
| E-07 | Fidelity and legacy | Existing common fidelity state-machine tests preserve Attempt 01–03 / repair 01–03, max-audit terminal and reject Attempt 04; v1.0/v1.1/v1.2 compatibility tests remain green |
| E-08 | Workflow safety | v1.3 plan/dry-run is read-only; v1.3 publish is blocked before Stage F even with `--allow-write`; direct Share/Sermon bypasses remain fail-closed |
| E-09 | Chronology and side effects | No production import/content write, NAS access, build, deploy, email/notification, dependency change or Git history operation; pre-existing worktree lineage preserved |

Overall acceptance: all mandatory propositions must have reproducible evidence. A test using mocks/stubs must be described as such and cannot be represented as a real importer execution. Any missing evidence is BLOCKED; any reproducible mandatory failure is FAIL. Non-blocking residuals must be explicitly recorded without expanding the frozen threat model.

## 3. Execution approach

1. Reconfirm the exact Website and Sermon construction worktrees and canonical comparison roots; preserve all pre-existing dirty/untracked files.
2. Run the Sermon Owner's synthetic Stage A/B producer, fidelity, package-builder and export-gate suites. These are read-only against repository content; tests create disposable temporary fixtures.
3. Run Website consumer schema/identity, Share/Sermon workflow, import boundary, rendering and legacy compatibility suites.
4. Run the full relevant Python regression suites in both construction worktrees, the relevant Node structural tests, schema Draft 2020-12 validation in the isolated offline environment, CLI help and `git diff --check`.
5. Run the v1.3 negative production-mode test with `--allow-write`; it must fail closed. Do not run an actual import or any write-capable publication command.
6. Record exact commands, exit codes, counts, any mock/stub boundaries, SHA identities and residual findings in the Stage E report.

## 4. Explicit exclusions

- No Stage F enablement; no v1.3 non-dry-run.
- No production import, raw/processed/posts mutation, historical content rewrite or real article.
- No NAS probe/read/write/archive.
- No Astro production build.
- No deployment, GitHub Actions/workflow dispatch, email, notification or subscription action.
- No dependency install/upgrade.
- No Git staging, commit, push, merge, reset, clean, rebase or amend.
- No writes to either canonical worktree.
- No changes to frozen schemas, package contracts, Project Bible, fidelity rules, sermon theology or Stage D frozen plan.
- No changes to Sermon construction source/tests/task files; it is a read-only producer evidence source for this Website-owned acceptance run.

## 5. Deliverables and stop point

- Stage E execution report in this Website construction task directory.
- Website `STATUS.md`, `docs/tasks/current.md` and task `TASK_INDEX.md` updated with the actual result and preserved chronology.
- Independent audit request and designated Auditor report path, authored only after implementation/execution evidence is frozen.
- Stop after returning the read-only independent audit handoff. Stage F remains disabled and requires separate explicit authorization after independent Stage E acceptance.

## 6. Goal / scope / overbuilding check

- Goal alignment: synthetic Share/Sermon interoperability is the explicit prerequisite to any future v1.3 production enablement.
- Scope: Website consumer owns this acceptance execution; Sermon is read-only evidence source. No cross-owner implementation change is planned.
- Overbuilding: reuse existing producer, consumer, schema, renderers and tests; add no infrastructure or duplicate business logic.
- Disposition: `GOAL_ALIGNED / NO_SCOPE_DRIFT / NO_OVERBUILDING`.
