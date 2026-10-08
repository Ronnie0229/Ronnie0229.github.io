# Implementation — S4 Malformed Provider Status Type-Safety Closure

日期：2026-10-08

正式 verdict：`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`

## Scope

本轮严格只修 Website-local provider terminal status type-safety，未重开 execution architecture、authorization claim、descriptor/request_id derivation、render gate、artifact verification、VOICE_AI/N6 contract 或 external Owner boundary。

## Type-safe evidence sanitizer

`_provider_result_evidence(job, provider_result)` 在任何 terminal enum membership 前新增：

- `isinstance(status, str)` gate；
- 非 string status => evidence `{}`；
- 不 stringify；
- 不 normalize；
- 不 repair；
- 不 truncate；
- 不把 malformed structured value转换为合法 terminal status。

只有 string status 才进入 `PASS/BLOCKED/FAIL_CLOSED` enum membership。

## Type-safe raw terminal validator

`_validate_provider_terminal_result(job, provider_result)` 同样先执行 string type gate：

- 非 string => bounded `RunnerError("PROVIDER_RESULT_STATUS_INVALID")`；
- unknown string => 同样 bounded `PROVIDER_RESULT_STATUS_INVALID`；
- raw dict/list/nested/tuple/numeric/bool/null 不再触发 Python `TypeError`。

Raw provider result 仍直接作为 terminal truth input；没有改为验证 sanitized evidence。

## Malformed-status durable outcome

新增 matrix 覆盖：

- dict status
- list status
- nested dict/list status
- numeric status
- boolean status
- null status
- tuple structured status
- unknown string status

每个 case 都机械断言：

- Website durable status = `TERMINAL_FAIL_CLOSED`
- `last_error=PROVIDER_RESULT_STATUS_INVALID`
- `provider_result={}`
- artifact retrieval calls = 0
- malformed status marker/body 不进入 serialized durable job JSON
- provider附带 run/artifact/receipt/failure markers也不进入 durable JSON
- execution owner 在 durable fail-closed 后释放
- subsequent `status()` / `result()` 可正常读取
- terminal `reconcile()` 不调用 provider ready/speech/artifact

## Long-lifecycle chronology

本轮保留中途 FAIL chronology：

1. type-safe implementation完成；
2. py_compile PASS；
3. first runner：`54 tests / 8 errors`；
4. 8 errors 均来自新增测试误把既有 `result()` surface 当成包含 `last_error`；产品路径已实际 durable fail-closed；
5. 同一 authority/write-set 内最小修正测试：`last_error` 从正式 `status()` surface读取，`result()` 验证 terminal status/provider_result/artifact；
6. runner => `54/54 PASS`；
7. full Website Python => `115/115 PASS`；
8. 强化 nested/tuple body marker absence；
9. final py_compile PASS；
10. final runner => `54/54 PASS`；
11. final full Website Python => `115/115 PASS`；
12. production runtime root absent；temp leftovers empty；whitespace/EOF hygiene PASS。

后续 PASS 不删除第 3 步测试错误 chronology。

## Existing regression boundaries retained

最终 runner suite 继续覆盖并通过：

- exact valid PASS/BLOCKED/FAIL_CLOSED
- semantic current-job-aware request identity
- PASS invalid nonempty failure_code omission
- BLOCKED/FAIL_CLOSED PASS-only identity omission
- oversized/malformed provider evidence
- unknown 5KB provider body
- artifact SHA mismatch
- exact render binding / symlink / SHA / UTF-8
- authorization O_EXCL claim / duplicate submit
- execution mutual exclusion / stale owner
- same-id UNKNOWN reconcile
- terminal reconcile anti-duplicate

## Side effects

- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- external project mutation：NONE
- Website src/article mutation：NONE
- R2/NAS/deploy：NOT RUN
- commit/push：NOT RUN
