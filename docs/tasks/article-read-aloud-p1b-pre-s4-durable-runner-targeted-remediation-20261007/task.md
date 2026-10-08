# Article Read-Aloud P1B-pre — S4 Durable Runner Targeted Implementation Remediation

状态：PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION / READY_FOR_FRESH_REAUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_EXECUTOR / EXECUTOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Trigger

Fresh independent implementation audit verdict:
`BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT / RETURN_TO_MASTER_CONTROL`

Primary audit:
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-independent-audit-20261007/audit.md`

Only two material implementation gaps are in scope:

1. `F-S4-IA-01` — single-worker invariant not mechanically enforced.
2. `F-S4-IA-02` — provider terminal result identity not reverse-validated against current job.

All other audited areas that passed remain closed unless the remediation itself creates a regression.

## Goal-value Gate

- GOAL_ALIGNMENT=ON_PLAN
- BLOCKER_MATERIALITY=REQUIRED
- OVERBUILDING_RISK=LOW
- OWNER_BOUNDARY=PASS
- MINIMAL_NEXT_STEP=YES
- NEXT_TASK_JUSTIFIED=YES
- decision=`PASS_MINIMAL_IMPLEMENTATION_REMEDIATION_JUSTIFIED / CONTINUE`

## Scope A — bounded execution mutual exclusion

Add the thinnest Website-local mechanical execution exclusion that guarantees:

1. At most one Website execution caller can enter any provider-POST-capable critical section at a time.
2. `worker_once()`, `execute_job()`, and `reconcile()` cannot cause concurrent provider POSTs for the same or different jobs.
3. A second worker/reconcile caller encountering an active execution owner must not call provider.speech.
4. Terminal state written by one execution path cannot be overwritten by a stale concurrent execution path.
5. Crash/restart must not infer that a prior provider side effect did not happen.
6. There must be no unsafe automatic takeover/release that could create concurrent execution after a crash.

Preferred minimal model:
- a Website-local process execution lock/claim under runtime root, using an OS/file primitive with explicit fail-closed semantics;
- no Redis/Celery/database/general lease platform;
- no multi-worker scheduler.

The implementation must explicitly define what happens if the execution lock appears stale or owner process disappears. Safety wins over availability: ambiguous ownership must block/operator-require; it must not silently reclaim and retry provider work.

If a non-expiring O_EXCL lock file is used, the remediation must provide a safe operator/manual recovery boundary rather than automatic deletion/takeover. If a kernel advisory file lock is used, prove how process death releases only the execution mutex without implying provider side effect safety; job state `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN` must remain conservative.

Do not alter authorization one-time claim semantics.

## Scope B — provider terminal result identity validation

Before any provider result may become Website terminal truth or cause artifact finalize:

1. Result must be a dict with recognized provider terminal status.
2. For syntactically valid requests that entered provider, `provider_result.request_id` must exist, be string, and exact-equal `job.request_id`.
3. PASS must require current frozen success identity fields:
   - `request_id`
   - `run_id`
   - `artifact_ref`
   - `artifact_sha256`
   - `receipt_ref`
   - provider status `PASS`
   - `failure_code` consistent with PASS contract
4. Required fields must have bounded/valid types and non-empty values where applicable.
5. BLOCKED / FAIL_CLOSED terminal results must also carry matching request_id when request identity is available from provider result contract; mismatched identity must fail-closed.
6. Any missing/mismatched/invalid provider identity:
   - Website status => `TERMINAL_FAIL_CLOSED` or operator-required fail-closed;
   - artifact finalize MUST NOT run;
   - verified artifact cache MUST NOT be created.
7. Persist enough provider result/error evidence for diagnosis, but do not persist TTS text.
8. Do not invent/repair provider identity fields on Website side.

VOICE_AI remains unchanged.

## Required regression/adversarial tests

Add tests that at minimum prove:

### Execution exclusion
- two concurrent `execute_job` calls => provider.speech call count <=1;
- `worker_once` vs `reconcile` concurrency => provider.speech call count <=1;
- PASS from first execution cannot be overwritten by second stale caller;
- second caller gets deterministic busy/blocked/no-op semantics without new identity;
- simulated process restart / lock lifecycle preserves conservative unknown semantics;
- no automatic lock takeover creates a second possible POST.

### Provider identity
- PASS with wrong request_id => TERMINAL_FAIL_CLOSED, artifact call count 0;
- PASS missing request_id => fail-closed;
- PASS missing run_id/artifact_ref/artifact_sha256/receipt_ref => fail-closed;
- PASS invalid artifact_sha256 => fail-closed;
- BLOCKED wrong request_id => fail-closed, not TERMINAL_BLOCKED for current job;
- FAIL_CLOSED wrong request_id => fail-closed for identity mismatch;
- exact matching provider PASS still succeeds;
- artifact finalize occurs only after identity validation.

### Existing regression
- all prior runner tests still pass;
- full Website Python suite passes;
- production runtime root remains absent;
- task-local temporary roots cleaned.

Preserve chronology of prior failures and any new failing attempts.

## Frozen boundaries

Do not change:
- descriptor schema/request_id derivation;
- authorization one-time claim;
- exact Render View gate;
- production runtime root;
- VOICE_AI Local HTTP V1;
- N6 exactly-once semantics;
- Website/VOICE_AI truth boundaries;
- external Owner boundaries.

## Allowed write-set

- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`
- this task package
- `docs/tasks/current.md`

Do not modify `src/`, articles, VOICE_AI, RonnieAutomation, Hermes, deployment, NAS/R2.

## Forbidden side effects

- no real Pilot claim/submit
- no real /v1/speech
- no production runtime root creation
- no LaunchAgent install/bootstrap/kickstart
- no WAV/MP3
- no external-project mutation
- no deploy/R2/NAS
- no commit/push

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-20261007/`

Write:
- `remediation.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md`.

## Verdict

Give one:
- `PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION / READY_FOR_FRESH_REAUDIT`
- `BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION / RETURN_TO_MASTER_CONTROL`

Stop after implementation + isolated verification. Do not enter activation design.
