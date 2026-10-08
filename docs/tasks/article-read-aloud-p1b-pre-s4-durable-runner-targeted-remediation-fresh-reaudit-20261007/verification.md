# Verification — S4 Durable Runner Targeted Remediation Fresh Independent Re-audit

## Verdict

`BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_REAUDIT / RETURN_TO_MASTER_CONTROL`

## Fresh standard verification

- py_compile：PASS
- targeted runner suite：`33/33 PASS`
- full Website Python suite：`94/94 PASS`
- production runtime root：absent

## F-S4-IA-01 independent verification

### Thread-level paths

Fresh targeted suite confirms:
- same job concurrent execute -> at most one provider speech
- different jobs -> global at most one provider speech
- worker_once vs reconcile -> at most one provider speech
- stale lock not auto-taken-over
- UNKNOWN + stale owner remains conservative

### Process-style attack

Observed:
- `FIRST_ENTERED=True`
- `COUNT_BEFORE_RELEASE=1`
- second process exit=1 due `EXECUTION_BUSY_OR_STALE_LOCK`
- `FINAL_COUNT=1`
- first process exit=0
- final status=`TERMINAL_PASS`

Disposition: `F-S4-IA-01 PASS / CLOSED`.

### Crash ambiguity attack

Injected artifact transport RuntimeError after provider entry:
- first error=`RuntimeError`
- execution owner remains=true
- job=`CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`
- next reconcile=`EXECUTION_BUSY_OR_STALE_LOCK`

Disposition: no automatic takeover/release; PASS.

## F-S4-IA-02 independent verification

### Correctly enforced

- wrong PASS request_id -> fail-closed before artifact
- missing PASS request_id -> fail-closed
- missing PASS success identity -> fail-closed
- invalid artifact_sha256 -> fail-closed
- PASS non-empty failure_code -> fail-closed
- wrong BLOCKED / FAIL_CLOSED request_id -> identity fail-closed
- exact matching PASS -> terminal PASS + verified artifact
- unknown provider `text` key itself is not persisted

### Material uncovered failure

Attack:
- correct request_id
- PASS
- run_id = 5027-character untrusted marker/body
- other required PASS fields valid

Observed:
- `STATUS=TERMINAL_FAIL_CLOSED`
- `ERROR=PROVIDER_PASS_RUN_ID_INVALID`
- artifact prevented=true
- `PERSISTED_MARKER=True`
- `PERSISTED_RUN_ID_LEN=5027`

Root cause:
`_provider_result_evidence()` copies raw allowlisted values before `_validate_provider_terminal_result()`; validation failure then persists those raw values.

Disposition:
`F-S4-IA-02 BLOCKED / evidence persistence not bounded`.

## Chronology

- historical implementation audit: BLOCKED
- pre-remediation tests: 19/19 + 80/80
- remediation Executor claim: 33/33 + 94/94
- Auditor fresh rerun: 33/33 + 94/94
- one auditor evidence command initially failed from an auditor-side NameError; corrected rerun produced the material persistence finding above

## Side effects

- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- implementation fix：NOT PERFORMED
- VOICE_AI/RonnieAutomation/Hermes mutation：NONE
- Website src/article mutation：NONE
- R2/NAS/deploy：NONE
- commit/push：NOT RUN

