# Verification — S4 Provider Evidence Bounded Persistence Remediation

正式 verdict：`PASS_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION / READY_FOR_FRESH_REAUDIT`

## Required invariant

- evidence built through field-level bounded persistence gates：PASS
- oversized/invalid allowlisted values not persisted verbatim：PASS
- no truncation-to-valid-identity behavior：PASS
- malformed nested/list/object values not stringified into evidence：PASS
- unknown provider body/text key omitted：PASS
- identity validation still uses raw provider result：PASS
- invalid terminal identity artifact retrieval count remains 0：PASS
- execution lock source/design unchanged by this task：PASS

## Serialized durable JSON attacks

- oversized run_id marker absent：PASS
- oversized artifact_ref marker absent：PASS
- oversized receipt_ref marker absent：PASS
- oversized BLOCKED failure_code marker absent：PASS
- oversized FAIL_CLOSED failure_code marker absent：PASS
- oversized request_id marker absent：PASS
- malformed request_id marker absent：PASS
- malformed allowlisted-value marker absent：PASS
- unknown large provider body marker absent：PASS
- invalid fields are omitted, not truncated：PASS

## Valid evidence regression

- exact valid PASS persists request_id/run_id/artifact_ref/artifact_sha256/receipt_ref and succeeds：PASS
- valid BLOCKED persists bounded request_id/failure_code and remains TERMINAL_BLOCKED：PASS
- valid FAIL_CLOSED persists bounded request_id/failure_code and remains TERMINAL_FAIL_CLOSED：PASS

## Commands

`python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS

`python3 -m unittest scripts.tests.test_read_aloud_s4_runner -v` => `45/45 PASS`

`python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` => `106/106 PASS`

`git diff --check` => PASS

Final boundary readback：`TEST_LEFTOVERS=[]`; `PRODUCTION_ROOT_EXISTS=False`.

## Chronology

- original implementation PASS retained；
- independent implementation BLOCKED retained；
- first targeted remediation PASS retained；
- fresh re-audit `F-S4-IA-01 CLOSED` / `F-S4-IA-02 evidence persistence residual BLOCKED` retained；
- current bounded-evidence remediation final targeted 45/45 PASS / full Python 106/106 PASS。

## Side effects

Pilot remains `UNCLAIMED / NOT_CONSUMED`; no real `/v1/speech`; no production runtime root; no LaunchAgent; no audio; no execution-lock redesign; no external mutation; no deploy/R2/NAS; no commit/push.