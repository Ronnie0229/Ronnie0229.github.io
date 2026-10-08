# Remediation — S4 Durable Runner Targeted Implementation Remediation

日期：2026-10-07

正式 verdict：`PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION / READY_FOR_FRESH_REAUDIT`

本轮严格只关闭 fresh independent implementation audit 的两个 material gaps：`F-S4-IA-01` 与 `F-S4-IA-02`。此前已通过的 descriptor/request_id、authorization claim、render gate、filesystem spool、N6 truth boundary 均未重开。

## F-S4-IA-01 — execution mutual exclusion

新增 runtime-root 全局 execution ownership file：`execution-owner.json`。

进入任何 possible-provider-POST non-terminal execution path 前，`execute_job()` 必须以 OS-level `O_CREAT|O_EXCL` 独占创建 execution owner。owner record 仅保存 bounded execution metadata：schema、owner marker、pid、job_id、request_id；mode=0600。

机械语义：
- 同一 runtime root 同时只允许一个 execution owner；因此 same-job 与 different-job 都不能并行 provider POST。
- `worker_once()` 最终进入 `execute_job()`；`reconcile()` 对 non-terminal job 也最终进入同一 `execute_job()`，所以没有第二 possible-POST bypass。
- second caller 发现 owner file 已存在时立即 `EXECUTION_BUSY_OR_STALE_LOCK`；不调用 provider.speech、不改 request identity、不覆盖 active owner 的 job state。
- owner 在取得 lock 后必须重新读取 job；因此 acquire 前的 stale read 不能成为 state-write authority。
- terminal fast read 保持无副作用；terminal job 不重新 POST。

### Clean release vs crash ambiguity

owner 只在两类安全情形释放自己创建的 execution owner：
1. provider 尚未进入，且当前调用已完成/阻断；
2. provider 已进入，但当前调用已把 terminal / WAITING / UNKNOWN 等状态成功 durable-persist。

若 provider 可能已进入，而随后发生未处理异常、进程死亡或 durability 无法证明，owner file 留存，不自动 unlink、不按 PID 存活性回收、不 TTL、不 lease takeover。

stale owner 的处理边界明确为 operator/manual recovery：runner 本身没有自动 recovery/delete 命令。只有在新的显式人工 authority 下，对 job state + provider/N6 evidence 完成独立核对后，才可以单独决定是否移除 stale owner。PID 不存在本身绝不证明 prior provider side effect 未发生。

这保证 crash/restart 最坏降低 availability，但不会自动获得第二 possible-POST execution right。

## F-S4-IA-02 — provider terminal identity reverse validation

任何 provider result 在成为 Website terminal truth 或触发 artifact retrieval 前，先执行 `_validate_provider_terminal_result()`。

所有 recognized terminal statuses 仅允许：`PASS` / `BLOCKED` / `FAIL_CLOSED`，并且都要求：
- provider result 是 dict；
- `request_id` 为合法 string、满足当前 request_id regex；
- `provider_result.request_id == job.request_id` exact match。

`PASS` 进一步强制当前 frozen success identity：
- request_id
- run_id：non-empty bounded string
- artifact_ref：non-empty bounded string
- artifact_sha256：exact lowercase 64-hex
- receipt_ref：non-empty bounded string
- status=`PASS`
- failure_code 只能 absent / null / empty

只有全部 identity validation PASS 后才调用 `provider.artifact()`。任何 missing/mismatch/invalid identity 直接 Website `TERMINAL_FAIL_CLOSED`，artifact call count=0，verified artifact cache 不创建。

`BLOCKED` / `FAIL_CLOSED` 也要求 exact matching request_id 与 bounded non-empty failure_code；wrong request identity 不会被误写成当前 job 的 `TERMINAL_BLOCKED`，而是 identity fail-closed。

diagnostic persistence 使用 provider evidence allowlist，仅保留 status/request_id/run_id/artifact_ref/artifact_sha256/receipt_ref/failure_code；provider 返回的其它字段（包括潜在 text）不持久化。

## Tests added

execution exclusion adversarial coverage：
- concurrent execute_job same job => speech <=1
- concurrent execute_job different jobs => global speech <=1
- worker_once vs reconcile => speech <=1
- second caller deterministic busy, no identity change
- first PASS remains terminal and is not overwritten
- stale owner file with dead-looking pid is never auto-taken-over
- UNKNOWN job + stale owner remains UNKNOWN and provider speech=0

provider identity adversarial coverage：
- PASS wrong request_id => fail-closed before artifact
- PASS missing request_id => fail-closed
- PASS missing run_id/artifact_ref/artifact_sha256/receipt_ref => fail-closed
- PASS invalid artifact SHA => fail-closed before artifact
- PASS nonempty failure_code => fail-closed
- BLOCKED wrong request_id => identity fail-closed
- FAIL_CLOSED wrong request_id => identity fail-closed
- exact matching PASS still succeeds
- untrusted provider text field not persisted

## Verification

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS
- targeted runner suite => 33/33 PASS
- full Website Python suite => 94/94 PASS
- final `PRODUCTION_ROOT_EXISTS=False`
- final targeted temp leftovers=[]

## Side-effect boundary

- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- VOICE_AI/RonnieAutomation/Hermes：NOT MODIFIED
- Website src/articles：NOT MODIFIED
- deploy/R2/NAS：NOT RUN
- commit/push：NOT RUN