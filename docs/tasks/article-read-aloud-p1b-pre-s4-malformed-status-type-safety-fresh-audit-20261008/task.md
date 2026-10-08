# Article Read-Aloud P1B-pre — S4 Malformed Provider Status Type-Safety Fresh Independent Audit

状态：ACTIVE_FRESH_INDEPENDENT_AUDIT
日期：2026-10-08
Owner：Website / 个人网页项目

ROLE：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_MALFORMED_STATUS_TYPE_SAFETY_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

REPORT_TO：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

LIFECYCLE：
`ONE_INDEPENDENT_AUDIT_TO_VERDICT`

RETURN_CONDITION：
`AUDIT_COMPLETE_OR_TRUE_BLOCKER`

## Audit target

Fresh independent audit of the malformed provider status type-safety closure.

Primary implementation:
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`

Primary evidence:
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-fresh-audit-20261008/audit.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-malformed-status-type-safety-closure-20261008/task.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-malformed-status-type-safety-closure-20261008/implementation.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-malformed-status-type-safety-closure-20261008/verification.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-malformed-status-type-safety-closure-20261008/result.md`

Do NOT adopt Executor PASS, 54/54, 115/115, or Master rerun as presumed conclusion.

## Independence rule

Auditor may:
- read source/tests/task evidence;
- use isolated temp roots and fake/stub providers;
- run adversarial probes;
- inspect serialized durable JSON;
- rerun full regression/hygiene.

Auditor must NOT:
- implement fixes;
- modify runner/tests;
- claim/submit Pilot;
- call real /v1/speech;
- create production runtime root;
- install LaunchAgent;
- commit/push;
- enter activation design.

If findings exist, aggregate all material findings before returning. Do not stop after the first small issue unless continuing would be unsafe.

## Core denominator

The closure claims malformed/non-string provider status never escapes as raw Python implementation exception and always forms bounded terminal fail-closed behavior.

Auditor must independently prove or disprove:

### A. Type-safe sanitizer

For raw provider_result.status values:
- dict
- list
- nested dict/list
- numeric
- bool
- null
- tuple/structured non-string if fake provider path permits
- unknown string

Require:
- sanitizer itself never raises raw Python exception;
- non-string / unknown status does not preserve provider-controlled terminal evidence;
- no stringify/normalize/repair/truncate.

### B. Type-safe raw validator

For same matrix require:
- no raw TypeError/KeyError escapes;
- bounded local classification:
  - Website durable status = TERMINAL_FAIL_CLOSED
  - last_error = PROVIDER_RESULT_STATUS_INVALID
- raw provider result remains truth input;
- sanitized evidence is never used as truth substitute.

### C. Durable evidence / privacy

For every malformed-status case:
- provider_result diagnostic evidence = {};
- malformed status marker/body absent from serialized durable JSON;
- any accompanying run_id/artifact_ref/artifact_sha256/receipt_ref/failure_code marker absent;
- no raw provider response dump appears elsewhere in tested job/claim/log paths.

### D. Artifact / execution lifecycle

For every malformed-status case:
- artifact retrieval=0;
- verified artifact cache absent;
- execution owner released only after durable fail-closed is persisted;
- subsequent status() read is normal;
- subsequent result() read is normal terminal result;
- terminal reconcile does not call ready/speech/artifact again.

### E. Existing semantic persistence regression

Fresh-check:
- exact valid PASS / BLOCKED / FAIL_CLOSED
- current-job-aware request identity
- wrong-but-regex-valid request_id marker absence
- PASS nonempty failure_code omission
- BLOCKED / FAIL_CLOSED PASS-only identity omission
- oversized 5027+ run_id
- oversized/malformed artifact_ref/receipt_ref/failure_code
- unknown 5KB provider body
- raw truth vs sanitized evidence separation

### F. Execution / claim / render / reconcile regression

Fresh-check:
- global O_EXCL execution owner
- stale owner conservative behavior
- same/different job concurrent possible-POST exclusion
- authorization O_EXCL claim
- duplicate same identity
- changed identity conflict
- exact render binding / symlink / SHA / UTF-8 fail-closed
- same-id UNKNOWN reconcile
- terminal reconcile anti-duplicate
- artifact SHA mismatch no verified cache
- exact valid PASS artifact finalize

## Required regression / hygiene

Independently run:
- py_compile
- full runner suite
- full Website Python suite
- literal `git diff --check` if allowed by current connector policy; otherwise record connector restriction and independently perform show_changes + whitespace/EOF hygiene, without adopting Master’s literal PASS as audit authority
- production runtime root absence
- temp-root cleanup

Preserve chronology:
- previous semantic-closure audit BLOCKED on unhashable status;
- malformed-status long-lifecycle Executor first runner 54 tests / 8 test-surface errors;
- corrected final 54/54, 115/115;
- this fresh independent verdict.

## Verdict

Give exactly one:

### PASS

`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_FRESH_INDEPENDENT_AUDIT / READY_FOR_ACTIVATION_DESIGN`

Only if:
- malformed-status type-safety is independently closed;
- no new material blocker is found;
- relevant regressions/hygiene pass.

### BLOCKED

`BLOCKED_S4_MALFORMED_STATUS_TYPE_SAFETY_AUDIT / RETURN_TO_MASTER_CONTROL`

If BLOCKED:
- aggregate all material findings;
- state evidence/materiality/minimal remediation;
- do not implement fixes.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-malformed-status-type-safety-fresh-audit-20261008/`

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
