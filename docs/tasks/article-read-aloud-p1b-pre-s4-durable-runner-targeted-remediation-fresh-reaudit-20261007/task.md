# Article Read-Aloud P1B-pre — S4 Durable Runner Targeted Remediation Fresh Independent Re-audit

状态：ACTIVE_FRESH_REAUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_FRESH_INDEPENDENT_AUDITOR / AUDITOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Audit target

只针对 independent implementation audit 的两个 material findings 做 fresh re-audit：

1. `F-S4-IA-01` — execution mutual exclusion
2. `F-S4-IA-02` — provider terminal result identity reverse validation

Primary sources:
- `docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-independent-audit-20261007/audit.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-20261007/remediation.md`
- 同 remediation package 的 verification/result/task
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`

不得采用 remediation Executor 的 PASS 或测试数字作为预设结论。

## Required independent attacks

### A. Execution mutual exclusion

Independently prove or disprove:

- any provider-POST-capable path must acquire the same runtime-root execution owner;
- same job concurrent execute => at most one provider.speech;
- different job concurrent execute => at most one provider.speech globally;
- worker_once vs reconcile => at most one provider.speech;
- second caller does not mutate active owner's job state;
- owner acquisition is O_EXCL / mechanically exclusive;
- owner record identity is bounded and cannot be silently replaced;
- owner release only occurs after a state outcome is durably persisted or before any provider entry;
- if provider may have been entered and process/state durability is ambiguous, owner remains and no automatic takeover/release occurs;
- PID death, TTL, elapsed time or process restart alone never grants a new execution right;
- stale owner + UNKNOWN job remains conservative;
- terminal state cannot be overwritten by stale concurrent caller.

Attack both thread/process-style concurrency where feasible with isolated temp roots and fake provider.

### B. Provider terminal identity validation

Independently prove or disprove:

- all PASS/BLOCKED/FAIL_CLOSED results are identity-validated before terminal persistence;
- provider_result.request_id must exact equal current job.request_id;
- PASS requires valid non-empty run_id/artifact_ref/receipt_ref and exact lowercase 64-hex artifact_sha256;
- PASS failure_code contract is enforced;
- wrong/missing/invalid identity cannot call provider.artifact;
- wrong BLOCKED/FAIL_CLOSED request_id cannot be accepted as current-job terminal truth;
- persisted provider evidence is allowlisted and cannot store arbitrary provider text/body;
- exact matching PASS still succeeds and artifact SHA verify/finalize remains correct;
- identity validation does not mutate or “repair” provider result fields.

### C. Regression / architecture safety

Confirm remediation did not regress:
- authorization one-time O_EXCL claim;
- deterministic descriptor/request_id;
- exact render binding;
- conservative same-id reconcile;
- artifact SHA verify;
- no full TTS text persistence;
- no dual-truth boundary change;
- no Redis/Celery/database/lease platform;
- no VOICE_AI semantic change.

Independently rerun relevant tests. Preserve chronology:
- pre-remediation runner 19/19 / Python 80/80 were historical true-but-insufficient facts;
- targeted remediation claims 33/33 / 94/94;
- record any new failures before final verdict.

## Scope / forbidden side effects

Audit may use only isolated temp roots and fake/stub provider.

Forbidden:
- real Pilot claim/submit
- real POST /v1/speech
- production runtime root creation
- LaunchAgent install/bootstrap/kickstart
- implementation fixes
- WAV/MP3
- VOICE_AI/RonnieAutomation/Hermes mutation
- Website src/article mutation
- R2/NAS/deploy
- commit/push

## Verdict

Give exactly one:

- `PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_FRESH_REAUDIT / READY_FOR_ACTIVATION_DESIGN`
or
- `BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_REAUDIT / RETURN_TO_MASTER_CONTROL`

If BLOCKED, report only finding + materiality + minimal remediation boundary; do not implement.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-fresh-reaudit-20261007/`

Write:
- `audit.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md` if required.

Stop and hand back to Master Control.
