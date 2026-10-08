# Implementation — S4 Provider Evidence Semantic Persistence Closure

日期：2026-10-08

正式 verdict：`PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`

## Scope

本轮严格只收紧 Website runner 的 provider diagnostic evidence persistence：

- 保留既有 field-level bounded persistence；
- 新增 current-job-aware semantic gating；
- 新增 provider-status-aware persistence semantics；
- raw provider result 继续由 `_validate_provider_terminal_result()` 作为 terminal truth authority；
- 不修改 execution-owner、authorization claim、descriptor/request_id derivation、render gate、artifact SHA verify、runtime root、VOICE_AI/N6 ownership 或 reconcile architecture。

## Current-job-aware request identity

`_provider_result_evidence(job, provider_result)` 现在只有在以下条件全部成立时才持久化 `request_id`：

- raw value 是 string；
- 满足 frozen `REQUEST_ID_RE`；
- exact equal current `job["request_id"]`。

若 request_id 格式合法但不属于 current job：

- raw terminal validation 仍按原逻辑 fail-closed；
- durable evidence 仅最多保留 recognized raw status；
- wrong request_id 本身不持久化；
- failure_code / PASS-only success identity 也不被归属到 current job。

因此 cross-job syntactically-valid provider evidence 不会污染当前 job durable JSON。

## Status-aware field semantics

recognized terminal status only：

- `PASS`
- `BLOCKED`
- `FAIL_CLOSED`

unknown/malformed status => provider evidence `{}`；Website-local `TERMINAL_FAIL_CLOSED` + bounded local `last_error` 仍保留。

### PASS

在 request_id 已 exact match current job 后，仅允许 individually valid：

- run_id
- artifact_ref
- artifact_sha256
- receipt_ref

PASS 下任何 non-empty provider failure_code 都是 semantic-invalid：

- raw terminal validation => `PROVIDER_PASS_FAILURE_CODE_INVALID`
- evidence persistence => failure_code omitted
- artifact retrieval => 0

如果 PASS 中某一个 success identity field invalid，而其余 field individually valid：

- invalid field omitted；
- 其余 current-job/status-compatible safe fields可保留作 bounded diagnostics；
- terminal truth仍 fail-closed；
- artifact retrieval remains 0。

### BLOCKED / FAIL_CLOSED

仅在 request_id exact match current job 后允许：

- status
- request_id
- bounded valid non-empty failure_code

即使 provider 同时附带语法合法的 PASS-only：

- run_id
- artifact_ref
- artifact_sha256
- receipt_ref

这些字段也不会进入 durable evidence。

## Raw truth invariant

sanitized evidence 只用于 diagnostic persistence，不参与 terminal truth。

没有：

- truncate
- repair
- normalize
- stringify malformed identity
- sanitized-value revalidation as provider truth

因此 semantic sanitization 不可能把 invalid raw result 变成合法 terminal result。

## Long-lifecycle chronology

本 Executor 没有因普通边界扩展提前停止。

本轮 chronology：

1. semantic implementation + primary matrix 后 runner `51/51 PASS`；
2. full Website Python `112/112 PASS`；
3. 为覆盖 BLOCKED / FAIL_CLOSED wrong-but-valid request_id current-job attribution，再补两个 adversarial cases；
4. expanded runner `53/53 PASS`；
5. final full Website Python `114/114 PASS`；
6. final py_compile PASS；
7. production runtime root absent；
8. all task/test temporary roots clean；
9. full-file whitespace/EOF equivalence gate PASS；CodexPro policy要求 Git diff 使用 `show_changes` 而不是 bash `git diff`，因此未绕过工具策略执行 literal `git diff --check`。

本轮没有出现新的 product test FAIL。此前所有 PASS/BLOCKED chronology 均保留，不被本轮 closure 覆盖。

## Side effects

- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- VOICE_AI/RonnieAutomation/Hermes：NOT MODIFIED
- Website `src/` / articles：NOT MODIFIED
- R2/NAS/deploy：NOT RUN
- commit/push：NOT RUN
