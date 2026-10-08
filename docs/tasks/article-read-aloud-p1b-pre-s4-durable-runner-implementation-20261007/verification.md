# Verification — P1B-pre S4 Durable Runner

正式 verdict：`PASS_S4_DURABLE_RUNNER_IMPLEMENTED / READY_FOR_INDEPENDENT_AUDIT`

## Mechanical acceptance

- Pilot descriptor SHA/request_id exact fixture：PASS
- request_id regex compatibility：PASS
- first submit one claim/job：PASS
- exact duplicate returns same job：PASS
- 8-way concurrent duplicate -> one claim identity：PASS
- same authorization + changed article/operation/render/voice identity：fail-closed PASS
- corrupt/partial claim：fail-closed, no auto-release PASS
- simulated restart preserves claim：PASS
- render exact bytes：PASS
- render SHA mismatch -> speech calls 0：PASS
- missing / absolute / `..` escape / symlink / decode failure / unreadable -> speech calls 0：PASS
- verify-once/send exact text object：PASS
- READY -> PASS fake lifecycle：PASS
- provider not-ready -> WAITING, no new identity/post：PASS
- lost response -> UNKNOWN, same-id reconcile：PASS
- terminal reconcile no provider re-call：PASS
- artifact SHA pass path：covered by PASS lifecycle
- artifact mismatch -> fail-closed/no verified cache：PASS
- status/result read-only：PASS
- permissions root/subdirs 0700, state files 0600：PASS
- full TTS text absent from job/claim persisted state：PASS
- production root never created：PASS
- task-local temporary test roots cleaned：PASS

## Commands

`python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` -> PASS

`python3 -m unittest scripts.tests.test_read_aloud_s4_runner -v` -> final 19/19 PASS

`python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` -> final 80/80 PASS

Final readback：`TEST_LEFTOVERS=[]`; `PRODUCTION_ROOT_EXISTS=False`.

## Chronology

- Attempt 1 runner suite: 18/19, failure on runtime-dir creation ordering before wrong-request-id rejection.
- Attempt 2 runner suite after minimal ordering fix: 19/19 PASS.
- Attempt 1 full Python suite: 79/80, failure exposed claim visibility race during concurrent duplicate submit.
- Final after bounded claim-completion wait: runner 19/19 PASS; full Python 80/80 PASS.

## Forbidden side effects readback

real Pilot authorization remains UNCLAIMED / NOT_CONSUMED; no real provider POST; no production runtime root; no LaunchAgent; no audio; no external-project mutation; no commit/push.