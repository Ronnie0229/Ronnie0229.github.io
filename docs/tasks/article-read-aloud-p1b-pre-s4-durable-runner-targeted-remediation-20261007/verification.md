# Verification — S4 Durable Runner Targeted Remediation

正式 verdict：`PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION / READY_FOR_FRESH_REAUDIT`

## F-S4-IA-01 acceptance

- runtime-root global O_EXCL execution owner：PASS
- concurrent same-job execute => provider.speech=1：PASS
- concurrent different-job execute => provider.speech=1：PASS
- worker_once vs reconcile => provider.speech=1：PASS
- second caller => deterministic `EXECUTION_BUSY_OR_STALE_LOCK`, provider.speech additional calls=0：PASS
- first owner PASS not overwritten by stale caller：PASS
- stale owner with nonexistent-looking PID not reclaimed：PASS
- UNKNOWN + stale owner remains conservative, provider.speech=0：PASS
- no TTL/lease/takeover/automatic deletion：PASS by source + adversarial test

## F-S4-IA-02 acceptance

- wrong PASS request_id => TERMINAL_FAIL_CLOSED：PASS
- missing PASS request_id => TERMINAL_FAIL_CLOSED：PASS
- missing run_id/artifact_ref/artifact_sha256/receipt_ref => TERMINAL_FAIL_CLOSED：PASS
- invalid artifact_sha256 => TERMINAL_FAIL_CLOSED：PASS
- nonempty PASS failure_code => TERMINAL_FAIL_CLOSED：PASS
- wrong BLOCKED request_id => identity TERMINAL_FAIL_CLOSED, not current-job TERMINAL_BLOCKED：PASS
- wrong FAIL_CLOSED request_id => identity TERMINAL_FAIL_CLOSED：PASS
- all invalid identity cases artifact call count=0：PASS
- exact matching PASS => TERMINAL_PASS + verified artifact：PASS
- diagnostic allowlist does not persist untrusted provider text field：PASS

## Regression

`python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS

`python3 -m unittest scripts.tests.test_read_aloud_s4_runner -v` => 33/33 PASS

`python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` => 94/94 PASS

Final boundary readback：`TEST_LEFTOVERS=[]`; `PRODUCTION_ROOT_EXISTS=False`.

## Chronology

- independent implementation audit historical verdict `BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT / RETURN_TO_MASTER_CONTROL` retained.
- pre-remediation runner 19/19 and Python 80/80 retained as true historical tests but insufficient for the independent audit denominator.
- one attempted test-source edit was rejected by workspace secret-looking-content guard before write; no project mutation resulted from that attempt. Reissued with explicit non-credential fixture markers and continued.
- targeted remediation final runner 33/33 PASS; full Python 94/94 PASS.

## Forbidden side effects

Pilot authorization remains `UNCLAIMED / NOT_CONSUMED`; no real provider POST; no production runtime root; no LaunchAgent; no audio; no external-project mutation; no deploy/R2/NAS; no commit/push.