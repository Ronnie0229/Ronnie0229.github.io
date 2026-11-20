# Independent Audit Request — Stage C Website Consumer

You are the independent read-only auditor for Stage C of RonnieCross Share + Sermon Unified Publication Governance.

## Exact workspace

`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`

First call `open_current_workspace`, then open the exact workspace above. Confirm exact root, branch and HEAD before reading implementation.

## Authoritative inputs

Read:
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_PLAN.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/STAGE_C_IMPLEMENTATION_REPORT.md`
- `tasks/current/20261115-unified-share-sermon-publication-governance/INDEPENDENT_AUDIT_REQUEST_STAGE_C.md`
- `contracts/content-presentation-v1.schema.json`
- `contracts/website-publication-package-v1.3.schema.json`
- `scripts/publication_contract_invariants.py`
- `CONTENT_WORKFLOW.md`
- `STATUS.md`
- `docs/tasks/current.md`

Read the Owner copies in the Stage B Sermon construction workspace:
`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116`

Confirm the Stage B Re-Audit 01 report SHA-256:
`9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`

Retain the original Stage B FAIL report and Stage A audit chronology. Do not rewrite historical reports.

## Audit role and permissions

- Role: `INDEPENDENT_AUDITOR`
- Mode: read-only.
- Do not edit implementation, tests, plans, reports, STATUS, task index or schemas.
- The only authorized write path is:
  `tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_AUDIT_REPORT.md`
- No dependency installation/upgrade, build, production import, NAS access/write, notification, email, commit, push, merge or deploy.
- Do not start Stage D/E/F.
- Do not treat passing tests as a substitute for adversarial code review.

## Required audit propositions

1. **Workspace isolation**
   - Exact Website construction root/branch/HEAD.
   - Canonical Website is clean and unchanged.
   - Canonical Sermon retains its pre-existing dirty lineage and was not changed.
   - Sermon construction Stage B artifacts and accepted audit reports are unchanged.
   - No staged changes.

2. **Contract mirror and schema enforcement**
   - Website schema files and `publication_contract_invariants.py` are byte-identical to Sermon Owner copies.
   - Independently inspect `schema_definition_errors` and `validate_schema_node`; prove every keyword used by both frozen schemas is enforced, and unknown/unimplemented keywords fail closed.
   - Verify Draft 2020-12 compatibility and closed-world behavior.
   - Verify nested unknown fields and all Share/Sermon conditional constraints.

3. **Package/file identity**
   - Adversarially test package top-level and nested unknown fields, fileRef path/SHA, path escapes/symlink aliases, missing files, all five identity paths distinct, manifest/report/paired package hashes, record count/order/IDs, pair-set SHA and audit ID.
   - Verify prepublish body is byte/text-identical to bound presentation artifact after only removing the declared frontmatter separator.
   - Verify the validator never mutates package-bound files.
   - Check malformed nested report/manifest structures fail closed rather than raising uncaught exceptions.

4. **Translation/fidelity boundary**
   - Website verifies evidence/status only and does not re-adjudicate translation fidelity, Project Bible or theology.
   - Check all legal/illegal translation_status + fidelity_status combinations.
   - Verify archive semantics: Share `not_applicable`, Sermon protected archive states only.
   - Confirm Share consumer does not access NAS archive paths.

5. **Scripture/TTS**
   - Spoken Chinese references such as `罗马书1章15节`, same-chapter ranges and cross-chapter ranges pass unchanged.
   - Compact Chinese refs, discontinuous lists such as `罗马书8:28,31`, and detected English book/chapter:verse refs fail closed.
   - Check normalizer is detection-only at Website consumer; no frozen artifact rewrite or book-name guessing.

6. **Rendered structure**
   - Share profile validates H2/H3 heading identity, paragraph boundaries, list items, blockquotes, nonempty output and internal workflow residue.
   - Share is not forced into sermon-only Full Sermon Mode, three-point outline, discussion, prayer or benediction structure.
   - Sermon profile delegates to the existing sermon validator and preserves all sermon-specific hard gates.
   - Adversarially test heading/list/blockquote/paragraph loss and malformed Markdown.

7. **Share import identity**
   - Verify v1.3 Share import consumes the exact bound body artifact.
   - Verify it bypasses legacy body cleanup/formatting only for the bound v1.3 artifact.
   - Check author/date/category/slug/title/description/scripture/tags and source selector binding.
   - Test source path traversal and invalid source type.
   - Direct Share presentation import without a package must fail closed.
   - Existing legacy Share path must remain unchanged until Stage F.

8. **Sermon import compatibility**
   - Verify v1.3 Sermon uses bound package + presentation artifact + existing sermon structure gate.
   - Verify the existing v1.2 Sermon path remains operational and unchanged.

9. **Production activation boundary**
   - v1.3 consumer supports explicit plan/dry-run only before Stage F.
   - Both consumer and underlying content workflow must block v1.3 publish even when an explicit write flag is supplied.
   - No v1.3 production entrypoint/default is activated.
   - Existing Share production route and v1.2 Sermon production route remain intact.

10. **Regression**
    - Re-run full Python suite: expected 237/237 PASS; report exact actual count.
    - Re-run focused Stage C test modules (36 tests) and Share Tag Pipeline (27/27).
    - Python compile, Node syntax, `git diff --check`.
    - Check all pre-existing v1.0/v1.1/v1.2 compatibility tests.
    - Review every new test for meaningful assertions; no vacuous or mock-only claims where real code execution is required.

## Required report

Write only:
`tasks/current/20261115-unified-share-sermon-publication-governance/independent-audit/STAGE_C_AUDIT_REPORT.md`

The report must include:
- PASS / PASS_WITH_FINDINGS / PARTIAL / FAIL / BLOCKED.
- Each proposition result and evidence.
- Actual test counts and command exit codes.
- Findings with severity and exact file/line.
- Workspace identity and dirty/staged state.
- Explicit side-effect confirmation.
- SHA-256 of the report after read-back.

Stage C is not accepted until Master independently reads and accepts a formal independent PASS. Stage D remains BLOCKED until then.
