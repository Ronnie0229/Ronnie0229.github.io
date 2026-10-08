# Verification — S4 Durable Runner Fresh Independent Implementation Audit

## Verdict

`BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT / RETURN_TO_MASTER_CONTROL`

## Fresh regression

- `python3 -m unittest scripts.tests.test_read_aloud_s4_runner -v` -> `19/19 PASS`
- `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` -> `80/80 PASS`
- production root after rerun -> `False`

Chronology preserved:
- historical initial runner=`18/19`
- historical initial full-suite=`79/80`
- Executor final=`19/19 + 80/80`
- Auditor fresh rerun=`19/19 + 80/80`
- independent adversarial attacks below still expose material uncovered gaps.

## Material attack 1 — concurrent execution

Isolated fake-provider attack on same job with two concurrent `execute_job()` callers:

- `SPEECH_CALLS=2`
- both paths entered provider speech

Second attack with PASS + simulated `HTTP_DUPLICATE_IN_FLIGHT`:

- first path=`TERMINAL_PASS`
- second path=`TERMINAL_BLOCKED`
- final persisted Website state=`TERMINAL_BLOCKED / HTTP_DUPLICATE_IN_FLIGHT`

Result: frozen single-worker invariant is not mechanically enforced; Website state can be overwritten by a concurrent stale/duplicate caller.

## Material attack 2 — wrong provider request identity

Fake provider received correct request but returned:
- status=`PASS`
- request_id=`WRONG-ID`
- valid artifact bytes/SHA

Runner persisted:
- `TERMINAL_PASS`
- job request_id != provider_result request_id

Result: provider terminal result identity is not re-bound/validated against the current Website job.

## Source confirmation

- no `provider_result.get("request_id")` validation exists in runner
- no worker lock/flock/execution exclusive-claim exists
- O_EXCL is currently used only for authorization claim creation

## Side effects

- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- VOICE_AI/RonnieAutomation/Hermes mutation：NONE
- Website src/article mutation：NONE
- R2/NAS/deploy：NONE
- implementation remediation：NOT PERFORMED
- commit/push：NOT RUN

