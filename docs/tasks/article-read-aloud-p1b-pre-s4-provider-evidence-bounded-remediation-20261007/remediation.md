# Remediation — S4 Provider Evidence Bounded Persistence

日期：2026-10-07

正式 verdict：`PASS_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION / READY_FOR_FRESH_REAUDIT`

本轮只修复 fresh independent re-audit 唯一 residual：provider diagnostic evidence 在 validation failure path 可能把 invalid / oversized allowlisted raw values 原样 durable-persist。`F-S4-IA-01 execution mutual exclusion` 已独立 CLOSED，本轮未修改 execution-lock 设计。

## Minimal implementation

仅收紧 `scripts/read_aloud_s4_runner.py::_provider_result_evidence()`。

该函数现在把 provider result 全部视为 untrusted input，并在 durable persistence 前逐字段执行独立 persistence gate：
- `status`：仅 `PASS` / `BLOCKED` / `FAIL_CLOSED` recognized enum 才持久化；
- `request_id`：仅 string 且满足 frozen `REQUEST_ID_RE` 才持久化；
- `run_id` / `artifact_ref` / `receipt_ref`：仅 non-empty string 且 `<= MAX_PROVIDER_ID_LENGTH` 才持久化；
- `artifact_sha256`：仅 exact lowercase 64-hex 才持久化；
- `failure_code`：仅 non-empty string 且 `<= MAX_FAILURE_CODE_LENGTH` 才持久化；
- unknown provider keys：不持久化。

非法、超长或 malformed value 直接省略，不截断、不 stringify、不 repair，也绝不把截断后的值重新解释成合法 identity。

原 terminal identity truth validation 未改变：`_validate_provider_terminal_result()` 仍以 raw provider result 判定是否可成为 Website terminal truth；因此 evidence omission 不会把非法 raw identity 变成合法 identity。

validation failure 时 durable job 只保留：
- locally generated bounded `last_error`；
- individually passed persistence gate 的 safe provider evidence；
- Website-local status/artifact fields。

## Artifact invariant

provider terminal identity validation failure 仍发生在 artifact retrieval/finalize 前。新增 adversarial tests 证明 oversized/malformed request/identity values 均 `artifact_calls=0`。

## Adversarial persistence verification

新增 tests 直接读取 serialized durable job JSON，而非只比较 parsed dict：
- oversized run_id + unique body marker：TERMINAL_FAIL_CLOSED；artifact=0；marker absent；run_id key absent；
- oversized artifact_ref + marker：marker absent；artifact_ref key absent；
- oversized receipt_ref + marker：marker absent；receipt_ref key absent；
- oversized BLOCKED failure_code + marker：marker absent；failure_code key absent；
- oversized FAIL_CLOSED failure_code + marker：marker absent；failure_code key absent；
- oversized request_id + marker：marker absent；raw request_id omitted；
- malformed request_id object + marker：marker absent；raw request_id omitted；
- malformed allowlisted run_id/artifact_ref/artifact_sha256/receipt_ref/failure_code values containing marker：all omitted；
- unknown provider key containing 5000-byte body + marker：key/body absent；
- exact valid PASS：bounded success identity still persists and artifact succeeds；
- exact valid BLOCKED / FAIL_CLOSED：bounded request_id + failure_code persist as intended，unknown body absent。

## Regression

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS
- runner suite => `45/45 PASS`
- full Website Python suite => `106/106 PASS`
- `git diff --check` => PASS
- final `PRODUCTION_ROOT_EXISTS=False`
- final `TEST_LEFTOVERS=[]`

## Chronology preserved

1. original bounded implementation：PASS reported；
2. independent implementation audit：`BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT`；
3. first targeted remediation：PASS reported；
4. fresh targeted re-audit：`F-S4-IA-01 PASS/CLOSED`；`F-S4-IA-02 PARTIALLY CLOSED`，5027-character invalid run_id proved raw diagnostic persistence residual；overall `BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_REAUDIT`；
5. current narrow remediation：bounded field-level evidence persistence implemented；45/45 targeted + 106/106 full Python PASS。

## Forbidden side effects

- execution lock redesign：NOT DONE
- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- VOICE_AI/RonnieAutomation/Hermes：NOT MODIFIED
- Website src/articles：NOT MODIFIED
- R2/NAS/deploy：NOT RUN
- commit/push：NOT RUN