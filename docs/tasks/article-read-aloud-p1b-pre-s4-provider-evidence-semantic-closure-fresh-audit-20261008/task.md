# Article Read-Aloud P1B-pre — S4 Provider Evidence Semantic Closure Fresh Independent Audit

状态：ACTIVE_FRESH_INDEPENDENT_AUDIT
日期：2026-10-08
Owner：Website / 个人网页项目

ROLE：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

REPORT_TO：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

LIFECYCLE：
`ONE_INDEPENDENT_AUDIT_TO_VERDICT`

RETURN_CONDITION：
`AUDIT_COMPLETE_OR_TRUE_BLOCKER`

## Audit target

Fresh independent audit of the current S4 durable runner after semantic persistence closure.

Primary implementation:
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`

Primary authority/evidence:
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-fresh-reaudit-20261007/audit.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-20261008/task.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-20261008/implementation.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-20261008/verification.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-20261008/result.md`

Do NOT adopt Executor PASS, 53/53, 114/114, or Master rerun as a presumed conclusion.

## Independence rule

This is a fresh Auditor role.

Auditor may:
- read source/tests/task evidence;
- run isolated test roots;
- use fake/stub providers;
- run adversarial probes;
- rerun regression;
- inspect serialized durable JSON;
- inspect Git diff/status/hygiene.

Auditor must NOT:
- implement fixes;
- modify runner/tests;
- claim/submit Pilot;
- call real /v1/speech;
- create production runtime root;
- install LaunchAgent;
- commit/push;
- enter activation design.

If findings exist, aggregate all material findings into one audit result before returning. Do not stop after the first small issue unless continuing would be unsafe.

## Core audit denominator

The current closure claims that durable provider diagnostic evidence is simultaneously:

1. field-bounded;
2. current-job-aware;
3. terminal-status-aware;
4. raw-truth-preserving;
5. free of rejected provider-controlled content on invalid identity paths.

Auditor must independently prove or disprove those claims.

## Required attack matrix

### A. Current-job-aware request identity

Attack PASS / BLOCKED / FAIL_CLOSED independently with:

- exact matching request_id;
- wrong-but-regex-valid request_id;
- oversized request_id;
- malformed request_id;
- object/list/nested request_id.

For wrong/malformed cases require:
- raw terminal validation fails closed;
- artifact retrieval=0 where applicable;
- wrong request marker absent from serialized durable JSON;
- provider_result.request_id omitted;
- no failure_code or success identity from wrong job is incorrectly attributed to current job.

### B. Terminal-status-aware failure_code

Attack:

- PASS + absent/null/empty failure_code;
- PASS + bounded nonempty failure_code marker;
- PASS + oversized failure_code;
- BLOCKED + valid bounded failure_code;
- BLOCKED + missing/empty/oversized/malformed failure_code;
- FAIL_CLOSED same matrix.

Require:
- PASS nonempty failure_code never persists;
- valid BLOCKED/FAIL_CLOSED failure_code persists only when current request_id matches;
- invalid/malformed failure_code marker absent;
- raw truth still fail-closes correctly.

### C. Status-dependent success identity

Fields:
- run_id
- artifact_ref
- artifact_sha256
- receipt_ref

Attack:

- exact valid PASS;
- PASS with one invalid field and other fields valid;
- BLOCKED carrying fully valid-looking PASS-only identity markers;
- FAIL_CLOSED carrying fully valid-looking PASS-only identity markers;
- unknown/malformed status carrying valid-looking request/failure/success identity.

Require:
- PASS-only fields persist only when status semantics allow them;
- BLOCKED/FAIL_CLOSED do not persist PASS-only identity;
- unknown/malformed status does not preserve provider-controlled terminal evidence;
- invalid field marker absent from serialized durable JSON;
- semantic sanitization does not repair/truncate/reinterpret provider truth.

### D. Raw truth authority

Directly inspect control flow and prove:

- terminal truth validation consumes raw provider result;
- diagnostic sanitizer output is never fed back into truth validation;
- no normalize/truncate/stringify/repair path creates a legal identity from an illegal provider value;
- no sanitized evidence can authorize artifact retrieval or terminal PASS.

### E. Artifact boundary

Attack:
- invalid request identity with otherwise valid artifact fields;
- invalid PASS failure_code with valid artifact fields;
- invalid success identity field;
- correct PASS with wrong artifact bytes/hash.

Require:
- invalid terminal identity => artifact retrieval 0;
- artifact mismatch cannot become verified;
- valid PASS still completes exact SHA verify/finalize;
- no stale or cross-job artifact attribution.

### F. Prior residual regression

Re-run/adversarially verify prior closed paths:
- oversized 5027+ run_id marker absent;
- oversized artifact_ref marker absent;
- oversized receipt_ref marker absent;
- oversized BLOCKED/FAIL_CLOSED failure_code marker absent;
- malformed allowlisted nested/list/object marker absent;
- unknown >=5KB provider body marker absent.

### G. Execution / exactly-once safety regression

Fresh-check that semantic closure did not regress:
- global O_EXCL execution owner;
- same/different job concurrent possible-POST exclusion;
- stale/ambiguous owner no auto takeover;
- UNKNOWN remains conservative;
- authorization one-time O_EXCL claim;
- same authorization different identity fail-closed;
- no second request_id/epoch creation;
- exact render binding before every possible POST;
- same-id reconcile semantics;
- terminal reconcile no duplicate provider call.

### H. Persistence privacy / boundedness

Inspect serialized durable JSON directly:
- no TTS body/provider body/unknown large payload survives invalid paths;
- locally generated last_error remains bounded;
- provider evidence size remains bounded by field rules;
- no full raw provider response dump exists elsewhere in job/claim/log path under this runner.

### I. Diff / workspace hygiene

Fresh-run:
- py_compile
- runner suite
- full Website Python suite
- literal `git diff --check`
- inspect current changed files / write-set
- production runtime root absent
- temp roots clean

Note explicitly:
Master fresh rerun before this audit already observed 53/53, 114/114 and literal `git diff --check` PASS, but Auditor must rerun independently and not treat those as verdict authority.

## Scope discipline

Already closed architecture areas must not be reopened merely for preference or redesign.

Do not propose:
- Redis
- Celery
- database
- generic lease platform
- VOICE_AI async V2
- RonnieAutomation/Hermes worker
- multi-worker scheduler

Only report a new material finding if independently evidenced and relevant to current frozen denominator.

## Chronology requirement

Preserve full chronology in audit report:
- original implementation PASS;
- independent implementation audit BLOCKED;
- execution/identity targeted remediation PASS;
- targeted re-audit residual BLOCKED;
- bounded evidence remediation PASS;
- bounded evidence fresh re-audit BLOCKED;
- semantic closure Executor PASS;
- this fresh independent audit verdict.

Later PASS must not erase prior BLOCKED history.

## Verdict

Give exactly one:

### PASS

`PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_FRESH_INDEPENDENT_AUDIT / READY_FOR_ACTIVATION_DESIGN`

Only if:
- semantic persistence denominator is independently closed;
- no new material implementation blocker found;
- regression/hygiene checks pass.

### BLOCKED

`BLOCKED_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_AUDIT / RETURN_TO_MASTER_CONTROL`

If BLOCKED:
- aggregate all material findings;
- state evidence, materiality, and minimal remediation boundary;
- do NOT implement fixes.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-fresh-audit-20261008/`

Write:
- `audit.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md` if required.

Stop and return to:
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

Do not enter activation design in this Auditor task.
