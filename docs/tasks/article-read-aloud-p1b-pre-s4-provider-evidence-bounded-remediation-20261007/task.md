# Article Read-Aloud P1B-pre — S4 Durable Runner Provider Evidence Bounded Persistence Remediation

状态：PASS_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION / READY_FOR_FRESH_REAUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION_EXECUTOR / EXECUTOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Trigger

Fresh independent re-audit verdict:
`BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_REAUDIT / RETURN_TO_MASTER_CONTROL`

Primary finding:
- `F-S4-IA-01 execution mutual exclusion` = PASS / CLOSED
- `F-S4-IA-02 provider terminal identity validation` = PARTIALLY CLOSED
- sole residual = invalid/oversized allowlisted provider identity values can still be copied into durable diagnostic evidence before validation.

Primary audit:
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-fresh-reaudit-20261007/audit.md`

## Goal-value Gate

- GOAL_ALIGNMENT=ON_PLAN
- BLOCKER_MATERIALITY=REQUIRED
- OVERBUILDING_RISK=VERY_LOW
- OWNER_BOUNDARY=PASS
- MINIMAL_NEXT_STEP=YES
- NEXT_TASK_JUSTIFIED=YES
- decision=`PASS_NARROW_REMEDIATION_JUSTIFIED / CONTINUE`

## Exact remediation scope

Only change provider diagnostic evidence persistence so that **untrusted provider values are mechanically bounded/sanitized before durable write**.

Do NOT change:
- execution-owner design;
- descriptor/request_id derivation;
- authorization claim;
- render gate;
- provider identity truth rules;
- artifact verification;
- runtime-root architecture;
- VOICE_AI;
- reconcile semantics except if strictly necessary to preserve this evidence invariant.

## Required invariant

A provider result may contain arbitrary/untrusted values. Durable Website job state must never store arbitrary provider body/text merely because it was placed under an allowlisted key.

Therefore:

1. Durable provider evidence must be built **after or through field-level validation/sanitization**, not by blindly copying raw allowlisted values.
2. Each persisted field must have an explicit safe rule:
   - status: only recognized bounded enum;
   - request_id: only if valid current request-id syntax and bounded length;
   - run_id: only if bounded valid string;
   - artifact_ref: only if bounded valid string;
   - artifact_sha256: only exact lowercase 64-hex;
   - receipt_ref: only bounded valid string;
   - failure_code: only bounded valid string.
3. Invalid/oversized values must NOT be persisted verbatim.
4. Do not truncate arbitrary provider string and then treat it as a valid identity.
5. On validation failure, persist only bounded local diagnostic facts sufficient for debugging, e.g.:
   - recognized status if safe;
   - local validation error code in `last_error`;
   - optionally a boolean/field-name classification such as `invalid_field`, if bounded and locally generated;
   - only provider identity fields that individually passed their safe persistence gate.
6. The durable JSON must never contain the adversarial marker/body placed inside oversized/malformed allowlisted fields.
7. Artifact retrieval remains forbidden whenever terminal identity validation fails.

## Recommended implementation pattern

Prefer one of these minimal patterns:

- make `_provider_result_evidence()` itself validate/bound each field before including it; or
- validate provider terminal result first and build full evidence only after PASS validation, while a separate failure-evidence builder emits bounded local diagnostics.

Do not create a generic sanitizer framework.

## Required adversarial tests

Add at minimum:

1. PASS with oversized run_id containing a unique marker/body:
   - Website => TERMINAL_FAIL_CLOSED
   - artifact call count = 0
   - durable job JSON does NOT contain marker
   - persisted run_id absent or safely omitted
2. Oversized artifact_ref containing marker => marker absent from durable job
3. Oversized receipt_ref containing marker => marker absent
4. Oversized failure_code for BLOCKED/FAIL_CLOSED => marker absent
5. malformed/oversized request_id => raw value absent from durable job
6. unknown provider key containing large text remains absent
7. exact valid PASS still persists the expected bounded identity evidence and succeeds
8. valid BLOCKED/FAIL_CLOSED still persist bounded safe diagnostic evidence as intended

Independently inspect serialized job JSON bytes/string, not only parsed dict equality, to prove marker absence.

## Regression

Must rerun:
- runner suite
- full Website Python suite
- py_compile
- production runtime root absence
- temp-root cleanup
- git diff --check

Preserve full chronology:
- original implementation PASS
- independent implementation BLOCKED
- first targeted remediation PASS
- fresh re-audit: F-S4-IA-01 CLOSED, F-S4-IA-02 residual evidence-persistence BLOCKED
- this remediation results

## Allowed write-set

Only:
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`
- this task package
- `docs/tasks/current.md`

## Forbidden

- no real Pilot claim/submit
- no real /v1/speech
- no production runtime root creation
- no LaunchAgent install/bootstrap/kickstart
- no WAV/MP3
- no execution-lock redesign
- no VOICE_AI/RonnieAutomation/Hermes mutation
- no Website src/article mutation
- no R2/NAS/deploy
- no commit/push

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-remediation-20261007/`

Write:
- `remediation.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md`.

## Verdict

Give one:
- `PASS_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION / READY_FOR_FRESH_REAUDIT`
- `BLOCKED_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION / RETURN_TO_MASTER_CONTROL`

Stop after implementation + isolated verification. Do not enter activation design.
