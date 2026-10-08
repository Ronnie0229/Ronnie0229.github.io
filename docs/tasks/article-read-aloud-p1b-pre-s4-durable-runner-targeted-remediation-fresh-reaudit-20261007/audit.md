# Audit — S4 Durable Runner Targeted Remediation Fresh Independent Re-audit

日期：2026-10-07

角色：`ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_REAUDIT / RETURN_TO_MASTER_CONTROL`

## 1. Independent basis

本轮未采用 remediation Executor 的 `PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION` 或其 33/33、94/94 数字作为预设结论。

Fresh-read / fresh-check：
- 原 fresh independent implementation audit 的两个 material findings；
- targeted remediation task / remediation / verification / result；
- 当前 `scripts/read_aloud_s4_runner.py`；
- 当前 `scripts/tests/test_read_aloud_s4_runner.py`；
- isolated task-local fake/stub provider adversarial executions。

本轮严格只复核：
1. `F-S4-IA-01` execution mutual exclusion；
2. `F-S4-IA-02` provider terminal result identity reverse validation；
以及整改是否对既有架构边界引入 material regression。

## 2. Regression fresh rerun

独立重跑：

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` -> PASS
- targeted runner suite -> `33/33 PASS`
- full Website Python suite -> `94/94 PASS`
- production runtime root -> absent

Chronology 保留：
- pre-remediation runner `19/19 PASS` / Python `80/80 PASS` 是历史真实但不足的事实；
- remediation Executor 报告 `33/33 PASS` / `94/94 PASS`；
- Auditor fresh rerun 同样得到 `33/33 PASS` / `94/94 PASS`；
- 本轮一个 evidence attack 首次审计命令因 auditor 自身引用错误（NameError）未完成，不是 product failure；修正命令后重跑得到下面 material finding。

## 3. F-S4-IA-01 — execution mutual exclusion

结论：

`PASS / ORIGINAL MATERIAL FINDING CLOSED`

### Source-level mechanics

当前 implementation：
- runtime-root 全局 `execution-owner.json`；
- acquisition 使用 OS-level `O_CREAT|O_EXCL`；
- owner 记录 bounded execution metadata；
- same root 同时只能存在一个 owner；
- non-terminal `execute_job()` 在执行 provider-capable logic 前获取 owner，并在获取后重新读取 job；
- `worker_once()` 与 non-terminal `reconcile()` 最终都进入同一 `execute_job()`；
- terminal fast-path 不触发 provider；
- active/stale owner 不按 PID、TTL、elapsed time 自动 reclaim；
- owner ambiguity => `EXECUTION_BUSY_OR_STALE_LOCK`；
- unexpected exception after provider entry leaves owner in place。

### Independent thread/process attacks

现有 targeted tests fresh rerun 已验证：
- same-job concurrent execute -> speech <= 1；
- different-job concurrent execute -> global speech <= 1；
- worker_once vs reconcile -> speech <= 1；
- stale owner不自动 takeover；
- UNKNOWN + stale owner保持保守。

Auditor 另做 process-style fork attack：
- first process successfully entered provider；
- second process hit `EXECUTION_BUSY_OR_STALE_LOCK`；
- `COUNT_BEFORE_RELEASE=1`
- `FINAL_COUNT=1`
- first process exit=0；
- final Website state=`TERMINAL_PASS`。

### Crash / ambiguous provider-side-effect attack

Auditor 注入：
- provider.speech 已返回 PASS identity；
- artifact retrieval 随后抛出未处理 RuntimeError。

结果：
- execution owner 仍存在；
- job state 保持 `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`；
- 后续 reconcile => `EXECUTION_BUSY_OR_STALE_LOCK`；
- 没有自动 release/takeover/re-POST。

因此原 `F-S4-IA-01` 已被当前 remediation 机械关闭。

## 4. F-S4-IA-02 — provider terminal identity reverse validation

结论：

`BLOCKED / PARTIALLY CLOSED, MATERIAL EVIDENCE-PERSISTENCE GAP REMAINS`

### What is correctly fixed

当前 implementation 已做到：
- recognized terminal status only：PASS / BLOCKED / FAIL_CLOSED；
- provider result request_id 必须是合法 string 并 exact equal current `job.request_id`；
- PASS 要求 bounded non-empty run_id / artifact_ref / receipt_ref；
- PASS artifact_sha256 必须 exact lowercase 64-hex；
- PASS non-empty failure_code 被拒绝；
- BLOCKED / FAIL_CLOSED 要求 matching request_id + bounded non-empty failure_code；
- invalid identity 在 artifact retrieval 前进入 `TERMINAL_FAIL_CLOSED`；
- wrong/missing identity 不会调用 `provider.artifact()`；
- exact matching PASS 仍能完成 artifact SHA verify/finalize；
- evidence keys 使用 allowlist，不直接保存 provider 的未知 `text` key。

这些部分均通过 fresh suite 与源码核对。

### Remaining material finding — invalid allowlisted values are persisted before validation

`_apply_provider_result()` 当前顺序：

1. 先调用 `_provider_result_evidence(provider_result)`；
2. evidence 直接复制 allowlisted key 的原始值；
3. 然后才调用 `_validate_provider_terminal_result()`；
4. 若 validation 失败，仍把先前复制的原始 evidence 写入 durable job JSON。

因此“key allowlist”并不等于“bounded evidence”。

### Independent attack evidence

Auditor 使用 isolated fake provider 返回：
- `status=PASS`
- correct current request_id
- `run_id` = 一个 5027 字符的 `UNTRUSTED_PROVIDER_PAYLOAD_...`
- 其他 PASS identity field 合法

结果：
- Website status 正确变为 `TERMINAL_FAIL_CLOSED`
- last_error=`PROVIDER_PASS_RUN_ID_INVALID`
- artifact retrieval 被阻止
- **但完整 5027-character invalid run_id 被写入 persisted provider_result**
- `PERSISTED_MARKER=True`
- `PERSISTED_RUN_ID_LEN=5027`

因此 remediation 文档声称的：

“diagnostic persistence 使用 provider evidence allowlist…provider 返回的其它字段（包括潜在 text）不持久化”

只保护了 unknown keys；没有保护 allowlisted keys 的值。任意 provider body/text 可以被塞进 run_id / artifact_ref / receipt_ref / request_id / failure_code 等 allowlisted field，在 validation failure 路径中原样持久化。

### Materiality

这违反本 fresh re-audit 的明确 denominator：

`persisted provider evidence is allowlisted and cannot store arbitrary provider text/body`

风险包括：
- full/partial TTS text 或其它大 payload 可通过 malformed identity field 被 durable job state 保存；
- 绕过既有“jobs/logs 不持久化 full TTS text”的 privacy boundary；
- malformed provider response 可造成 durable state size amplification；
- fail-closed identity validation 本身成立，但诊断持久化在 validation failure path 泄漏了未信任内容。

该问题属于原 `F-S4-IA-02` 的残余，不是新的无关范围扩张。

## 5. Minimal remediation boundary

不得扩大架构。

只需 Website runner 做最小 evidence sanitization/bounding：

1. provider evidence 必须在 durable persistence 前按字段独立做类型/长度/格式 gating；
2. invalid/oversized identity field 不得原样持久化；
3. validation failure 时仅保存 bounded safe diagnostic metadata，例如 status（若合法）、failure classification、本地 validation error code，以及经过长度上限验证的 identity field；
4. 不得把 arbitrary provider string 截断后当作“合法 identity”使用；sanitized diagnostic 与 identity truth 必须区分；
5. 补定向 test：oversized/malformed allowlisted field 中包含 marker/body 时，durable job JSON 不包含 marker，且 artifact call=0。

无需修改 VOICE_AI；无需修改 execution-owner 方案；无需 Redis/Celery/database/lease platform。

## 6. Architecture regression check

未发现 remediation 对以下已关闭边界引入 material regression：
- deterministic descriptor/request_id；
- authorization one-time O_EXCL claim；
- exact render binding；
- conservative same-id reconcile；
- artifact SHA verify；
- N6 provider exactly-once truth ownership；
- Website authorization/job orchestration truth boundary；
- anti-overbuilding；
- external project ownership。

## 7. Verdict

Formal:

`BLOCKED_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_REAUDIT / RETURN_TO_MASTER_CONTROL`

`F-S4-IA-01` 可独立关闭。

`F-S4-IA-02` 的 terminal identity rejection 与 artifact gating 已基本关闭，但 persisted provider evidence 仍能保存 arbitrary oversized content，因此尚未达到 fresh re-audit denominator。

当前不得进入 activation design。

