# Article Read-Aloud P1B-pre — S4 Durable Runner Fresh Independent Implementation Audit

状态：ACTIVE_FRESH_IMPLEMENTATION_AUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_FRESH_INDEPENDENT_AUDITOR / AUDITOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Audit target

Fresh independent audit of:
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`
- implementation task package
- architecture amendment + fresh re-audit authority

不得采用 Executor 的 PASS 或测试数字作为预设结论。

## Required attacks

### 1. Identity / authorization claim
- descriptor canonicalization exactness
- deterministic request_id exactness
- supplied request_id rejection before runtime mutation
- claim key truly only authorization_ref + generation_epoch
- O_EXCL mechanical exclusivity
- same binding duplicate semantics
- different identity reuse fail-closed
- partial/corrupt claim behavior
- 1-second bounded wait cannot become lease/takeover/release
- crash windows cannot create a second authorization identity

### 2. Job persistence / concurrency
- atomic temp+fsync+replace discipline
- file/directory modes
- single-worker assumption is explicit/mechanical
- submit concurrency cannot create multiple logical jobs for same authorization
- Website state does not claim provider generation truth

### 3. Render binding
- no absolute/.. escape
- symlink/rebinding resistance actually works, not merely documented
- exact bytes read once
- SHA before POST
- strict UTF-8
- same validated text object reaches provider call
- request_id re-derived before POST
- all negative paths provider speech call count=0

### 4. Provider / reconcile
- HTTP adapter sends exactly text + request_id
- readiness semantics do not mutate/start provider
- busy/not-ready does not mint identity
- connection uncertainty becomes conservative unknown state
- same-id reconcile never changes text/id/epoch
- terminal reconcile is read-only
- no hidden retry loop/new job path
- no VOICE_AI admin control

### 5. Artifact handling
- artifact_ref treated opaque
- no internal VOICE_AI path consumption
- temp download + exact SHA verify + atomic finalize
- mismatch/partial cannot become verified terminal downstream state

### 6. Runtime isolation / privacy
- production root exact constant
- tests cannot accidentally create it
- test-root injection cannot become production fallback
- root unavailable must fail-closed
- job/claim/log state does not persist full TTS text
- permissions satisfy frozen contract

### 7. Test quality / regression
Independently rerun relevant tests and inspect whether important invariants are tested rather than only self-asserted.
Preserve chronology:
- 18/19 initial runner failure
- 79/80 initial full-suite failure
- final 19/19 + 80/80

If a test gap is non-material, record it without manufacturing remediation.

## Scope / side effects

Audit may use only isolated temporary test roots and fake/stub provider.

Forbidden:
- real Pilot claim/submit
- real POST /v1/speech
- production runtime root creation
- LaunchAgent install/bootstrap/kickstart
- WAV/MP3 generation
- VOICE_AI/RonnieAutomation/Hermes mutation
- Website src/article mutation
- R2/NAS/deploy
- commit/push
- implementation fixes

## Verdict

Give exactly one:

- `PASS_S4_DURABLE_RUNNER_FRESH_INDEPENDENT_AUDIT / READY_FOR_ACTIVATION_DESIGN`
or
- `BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT / RETURN_TO_MASTER_CONTROL`

If BLOCKED, report finding/materiality/minimal remediation only; do not fix.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-independent-audit-20261007/`

Write:
- `audit.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md` if required.

Stop and hand back to Master Control.
