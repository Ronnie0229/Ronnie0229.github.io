# Audit — S4 Malformed Provider Status Type-Safety Fresh Independent Audit

日期：2026-10-08

角色：`ARTICLE_READ_ALOUD_P1B_PRE_S4_MALFORMED_STATUS_TYPE_SAFETY_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_FRESH_INDEPENDENT_AUDIT / READY_FOR_ACTIVATION_DESIGN`

## 1. Independence / chronology

本轮未采用 Executor 的 PASS、`54/54`、`115/115` 或 Master fresh rerun 作为预设结论。

Chronology 保留：
- previous semantic-closure fresh independent audit：`BLOCKED_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_AUDIT`，material blocker 为 unhashable malformed status raw `TypeError`；
- malformed-status closure Executor：首次新增 matrix 后 runner `54 tests / 8 errors`，正式记录为 test-surface errors；同一 write-set 内修正 test surface 后最终 `54/54`、`115/115`；
- 本 fresh independent audit：独立 source audit + adversarial matrix + regressions 后给出本 PASS。

后续 PASS 不抹除之前 BLOCKED / intermediate error chronology。

## 2. Source-level type-safety audit

当前 runner source 已明确实现双侧 type gate：

### Evidence sanitizer

`_provider_result_evidence()`：
- 先读取 raw `status`；
- `if not isinstance(status, str): return {}`；
- 只有 string 才进入 PASS/BLOCKED/FAIL_CLOSED membership；
- 无 stringify / normalize / repair / truncate。

### Raw terminal validator

`_validate_provider_terminal_result()`：
- 先 `isinstance(provider_status, str)`；
- 非 string => bounded `RunnerError("PROVIDER_RESULT_STATUS_INVALID")`；
- unknown string => 同一 bounded error；
- raw provider result 仍直接作为 truth input；
- sanitized diagnostic evidence 没有被回灌到 terminal truth。

因此上轮 unhashable set-membership hazard 已从 source-level 闭合。

## 3. Independent malformed-status adversarial matrix

Auditor 使用独立 task-local temp roots + fake providers，不调用真实 provider。

Fresh matrix 覆盖：
- dict
- list
- nested dict/list
- numeric
- bool
- null
- tuple structured value
- unknown string

8/8 cases 均独立观察到：

- no raw Python exception escapes；
- durable Website status = `TERMINAL_FAIL_CLOSED`；
- `last_error=PROVIDER_RESULT_STATUS_INVALID`；
- provider diagnostic evidence = `{}`；
- artifact retrieval calls = 0；
- verified artifact cache absent；
- serialized durable job JSON 中 malformed status marker/body absent；
- 同一 raw provider response 附带的 run_id / artifact_ref / artifact_sha256 / receipt_ref / failure_code marker absent；
- jobs / claims / logs tested paths 中未发现这些 raw markers；
- durable fail-closed 后 execution owner absent；
- `status()` 正常返回 terminal status + last_error；
- `result()` 正常返回 terminal status + provider_result={} + artifact=null；
- terminal `reconcile()` 不再调用 provider：ready=0 / speech=0 / artifact=0。

独立 8-case malformed matrix：PASS。

## 4. Existing semantic persistence regressions

Auditor 独立 probe + fresh full runner suite 共同验证：

- exact valid PASS：PASS，artifact finalize 正常；
- exact valid BLOCKED：PASS；
- exact valid FAIL_CLOSED：PASS；
- wrong-but-regex-valid request_id：fail-closed，wrong marker absent；
- PASS nonempty failure_code：fail-closed，failure marker absent，artifact=0；
- BLOCKED PASS-only identity：PASS-only markers omitted；
- oversized 5027+ run_id：fail-closed，marker absent；
- unknown 5KB provider body：valid terminal identity不受影响，unknown body marker不持久化；
- runner suite同时覆盖 oversized/malformed artifact_ref / receipt_ref / failure_code；
- raw truth 与 sanitized diagnostic evidence 分离未回归。

未发现 semantic persistence regression。

## 5. Execution / authorization / render / artifact / reconcile regressions

Auditor 独立 probe + fresh runner suite 验证：

- authorization exact duplicate => same identity；
- same authorization changed identity => `AUTHORIZATION_IDENTITY_CONFLICT`；
- stale execution owner => `EXECUTION_BUSY_OR_STALE_LOCK`，provider speech=0，无 auto takeover；
- concurrent same-job possible POST => provider speech count=1，second caller busy；
- runner suite继续覆盖 different-job global execution exclusion；
- render SHA drift => `RENDER_SHA256_MISMATCH` before provider speech；
- runner suite继续覆盖 path escape / absolute / symlink / UTF-8 / unreadable negative gates；
- provider connection uncertainty => `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`；
- reconcile reuses exact same request_id；
- terminal reconcile no duplicate provider call；
- valid PASS artifact finalize正常；
- wrong artifact bytes => `ARTIFACT_SHA256_MISMATCH`，verified cache absent。

未发现 execution/claim/render/artifact/reconcile regression。

## 6. Fresh regression

Auditor 独立执行：

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS
- full runner suite => `54/54 PASS`
- full Website Python suite => `115/115 PASS`
- independent custom audit probe => `22/22 PASS`
- production runtime root => absent
- fresh-audit temp roots/scripts => cleaned

## 7. Hygiene / workspace

CodexPro `show_changes(include_diff=false)` fresh review完成。

Malformed-status closure declared write-set：
- runner
- runner tests
- closure task package
- `docs/tasks/current.md`

与 closure `files-changed.md` 一致。Workspace 中其它 earlier read-aloud task packages、`AGENTS.md`、`docs/task-handoff-protocol.md` 的既有变化在 Auditor 启动时已存在，不归因于本 closure。

Fresh hygiene：
- trailing whitespace scan => PASS
- EOF newline scan => PASS
- temp cleanup => PASS
- production runtime root absent

当前 CodexPro connector contract 禁止通过 bash 执行 Git diff/status inspection，故本 Auditor 未绕过 policy 执行 literal `git diff --check`。正式 task 允许在此限制下记录 connector restriction 并使用 `show_changes` + whitespace/EOF hygiene；Master 既有 literal PASS 未被本 Auditor采用为 verdict authority。

## 8. Side-effect boundary

本轮：
- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- audio：NOT GENERATED
- implementation fix：NOT PERFORMED
- Website src/article mutation：NONE
- external-project mutation：NONE
- R2/NAS/deploy：NONE
- commit/push：NOT RUN

## 9. Aggregate verdict

Aggregate material findings：**0**

Formal:

`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_FRESH_INDEPENDENT_AUDIT / READY_FOR_ACTIVATION_DESIGN`

Malformed provider status type-safety denominator 已被 fresh independent closure。

本 PASS 只表示可交回 Master 决定下一 authority；Auditor 本身不进入 activation design。

