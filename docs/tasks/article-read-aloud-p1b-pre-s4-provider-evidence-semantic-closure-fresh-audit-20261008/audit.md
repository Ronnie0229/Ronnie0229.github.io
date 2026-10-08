# Audit — S4 Provider Evidence Semantic Closure Fresh Independent Audit

日期：2026-10-08

角色：`ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`BLOCKED_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_AUDIT / RETURN_TO_MASTER_CONTROL`

## 1. Independence / chronology

本轮未采用以下任何结论作为预设：
- semantic closure Executor `PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE`；
- Executor `53/53`、`114/114`；
- Master fresh rerun。

Chronology 永久保留：
1. original durable runner implementation：PASS reported；
2. fresh independent implementation audit：`BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT`；
3. execution/identity targeted remediation：PASS reported；
4. targeted fresh re-audit：execution exclusion CLOSED，但 evidence residual BLOCKED；
5. bounded evidence remediation：PASS reported；
6. bounded evidence fresh re-audit：`BLOCKED_S4_PROVIDER_EVIDENCE_BOUNDED_REAUDIT`；
7. semantic closure Executor：`PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`；
8. 本 fresh independent audit：本文件 verdict。

后续 PASS/BLOCKED 不抹除之前 chronology。

## 2. Source-level audit

当前 semantic closure 的主要结构成立：

- `_provider_result_evidence(job, provider_result)` 已变为 current-job-aware：
  - request_id 只有 string + frozen regex + exact current job match 才进入 evidence；
  - wrong-but-valid request_id 不带入 failure_code / PASS-only identity。
- persistence 已 terminal-status-aware：
  - PASS 不持久化 nonempty failure_code；
  - BLOCKED / FAIL_CLOSED 只持久化 status + matching request_id + bounded failure_code；
  - BLOCKED / FAIL_CLOSED 不持久化 PASS-only run_id / artifact_ref / artifact_sha256 / receipt_ref；
  - unknown recognized-outside-string status 返回空 evidence。
- raw truth 与 diagnostic evidence 仍分离：
  - `_apply_provider_result()` 生成 evidence 后，仍把 raw `provider_result` 直接传入 `_validate_provider_terminal_result()`；
  - sanitizer output 没有被送回 terminal truth validation；
  - artifact finalize 只发生在 raw terminal validation 通过后；
  - evidence 不授权 terminal PASS 或 artifact retrieval。

但是 source-level audit 同时发现一个 malformed-status safety hole：

`_provider_result_evidence()` 当前使用：

`if status not in {"PASS", "BLOCKED", "FAIL_CLOSED"}:`

`_validate_provider_terminal_result()` 同样使用 set-membership。

当 raw provider status 是 unhashable malformed value（例如 dict / list）时，Python set membership 会直接抛 `TypeError`，而不是形成 bounded `RunnerError("PROVIDER_RESULT_STATUS_INVALID")`。

这违反正式 denominator 对 malformed status 的要求。

## 3. Independent current-job / terminal-status matrix

Auditor 使用 task-local isolated runtime roots + fake providers，自建独立 matrix，不调用真实 provider。

独立 matrix 覆盖：
- exact valid PASS / BLOCKED / FAIL_CLOSED；
- PASS / BLOCKED / FAIL_CLOSED wrong-but-regex-valid request_id；
- oversized / object request_id；
- PASS bounded nonempty failure_code；
- PASS oversized failure_code；
- BLOCKED / FAIL_CLOSED missing / empty / oversized / malformed failure_code；
- BLOCKED / FAIL_CLOSED 携带 valid-looking PASS-only identity；
- unknown string status；
- malformed dict/list status；
- PASS invalid run_id / artifact_ref / artifact_sha256 / receipt_ref；
- unknown 5KB provider body。

除 malformed unhashable status 外，其余独立 matrix 均符合 frozen contract。

### Current-job-aware request identity

PASS / BLOCKED / FAIL_CLOSED wrong-but-valid request_id：
- raw terminal validation => `TERMINAL_FAIL_CLOSED`；
- artifact retrieval=0；
- wrong request marker 不进入 serialized durable JSON；
- provider_result.request_id 省略；
- wrong-job failure_code / success identity 不被归属当前 job。

PASS/BLOCKED/FAIL_CLOSED exact matching request identity 的合法 evidence 正常保留。

### Terminal-status-aware failure_code

- PASS absent/null/empty：合法；
- PASS bounded nonempty / oversized failure_code：raw fail-closed，failure_code marker 不持久化，artifact=0；
- BLOCKED valid bounded failure_code：`TERMINAL_BLOCKED`，request_id + failure_code 持久化；
- FAIL_CLOSED valid bounded failure_code：`TERMINAL_FAIL_CLOSED`，request_id + failure_code 持久化；
- BLOCKED / FAIL_CLOSED missing/empty/oversized/malformed failure_code：raw fail-closed；invalid marker 不持久化。

### Status-dependent success identity

- exact valid PASS：success identity 全部持久化，artifact finalize 成功；
- PASS 任一 invalid success field：raw fail-closed；invalid field marker absent；artifact=0；
- BLOCKED / FAIL_CLOSED 携带 valid-looking PASS-only identity：PASS-only markers 均 absent；
- unknown string status：provider_result evidence 空，local fail-closed classification bounded。

## 4. Material finding — malformed unhashable status escapes fail-closed contract

### Independent reproduction

Auditor 分别注入：

`status={"nested":"DICT_STATUS_MARK"}`

与：

`status=["LIST_STATUS_MARK"]`

两条路径均观察到：

- `execute_job()` 抛出 raw Python `TypeError`：
  - dict：`TypeError: unhashable type: 'dict'`
  - list：`TypeError: unhashable type: 'list'`
- Website job durable state 保持：
  - `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`
- `provider_result` 未形成 bounded diagnostic evidence；
- artifact retrieval=0；
- malformed marker 未进入 durable JSON；
- execution owner 保留。

### Why material

这不是 marker persistence 泄漏，但它仍直接违反本轮正式 attack denominator：

对 malformed status 要求：
- raw terminal validation fail-closes correctly；
- unknown/malformed status 不保留 provider-controlled terminal evidence；
- local fail-closed classification remains bounded。

当前实现对 hashable unknown string status满足该要求，但对 unhashable dict/list status不满足：
- sanitizer 自身先异常；
- raw validator也具有同样 unhashable membership hazard；
- Website 没有 durable `TERMINAL_FAIL_CLOSED / PROVIDER_RESULT_STATUS_INVALID`；
- runner 暴露 Python implementation exception；
- owner 被保守留存，后续需要 operator handling。

Execution owner 保留本身是安全的，但它不能替代 malformed provider response 的 bounded terminal classification。

### Minimal remediation boundary

仅需 Website-local、同一函数范围内的最小类型安全修复：

1. 在 evidence sanitizer 中，status membership 前显式要求 `isinstance(status, str)`；否则 evidence={}。
2. 在 raw terminal validator 中，同样先做 string/type gate，再做 enum membership；malformed/unhashable status 必须转为 bounded `RunnerError("PROVIDER_RESULT_STATUS_INVALID")`。
3. 保持 raw provider result 作为 truth authority；不要先 stringify/normalize/repair status。
4. malformed dict/list/nested status 必须：
   - Website => `TERMINAL_FAIL_CLOSED`
   - last_error => `PROVIDER_RESULT_STATUS_INVALID`
   - provider_result evidence => `{}`
   - artifact retrieval=0
   - serialized durable JSON 不含 marker/body
   - execution owner 在 durable fail-closed 后可按既有 clean-release语义释放。
5. 增加 dict/list malformed status serialized durable JSON regressions。

无需修改 execution architecture、claim、render、VOICE_AI、N6、queue/platform。

本 Auditor 不实施修复。

## 5. Artifact boundary

Independent attacks confirmed：

- wrong request identity + otherwise valid artifact identity => artifact retrieval=0；
- PASS invalid failure_code + valid artifact identity => artifact retrieval=0；
- invalid PASS success identity field => artifact retrieval=0；
- valid PASS => artifact retrieval=1，exact SHA verify/finalize成功；
- correct PASS identity + wrong artifact bytes => `TERMINAL_FAIL_CLOSED / ARTIFACT_SHA256_MISMATCH`，verified cache不存在。

未发现 stale/cross-job artifact attribution。

## 6. Prior residual regression

Independent re-check passed：

- 5027+ run_id marker：durable jobs/claims/logs 中 marker absent；
- oversized artifact_ref / receipt_ref：marker absent；
- oversized BLOCKED / FAIL_CLOSED failure_code：marker absent；
- malformed allowlisted nested/list/object：marker absent；
- unknown >=5KB provider body：marker absent；
- no raw provider response dump observed in job/claim/log path under tested invalid flow。

Locally generated `last_error` remains fixed bounded codes on handled validation paths。

## 7. Execution / claim / render / reconcile regression

Auditor independently probed, in addition to full runner suite：

- authorization exact duplicate => same request/job identity, one claim；
- same authorization changed identity => `AUTHORIZATION_IDENTITY_CONFLICT`；
- stale/dead-looking execution owner => `EXECUTION_BUSY_OR_STALE_LOCK`, provider speech=0, no auto takeover；
- concurrent same-job possible POST => provider speech count=1；second caller busy；first PASS preserved；
- render drift => `RENDER_SHA256_MISMATCH` before provider speech；
- connection uncertainty => `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`；
- reconcile reuses exact same request_id；
- terminal reconcile does not issue another provider call；
- artifact SHA mismatch cannot become verified。

No regression found in these previously closed boundaries.

## 8. Fresh regression

Auditor independently ran：

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS
- runner suite => `53/53 PASS`
- full Website Python suite => `114/114 PASS`
- production runtime root => absent
- task-local Auditor temp roots/scripts => cleaned

The existing suites do not cover unhashable dict/list status, so 53/53 and 114/114 are true regression facts but do not close this material finding.

## 9. Diff / workspace hygiene

CodexPro `show_changes(include_diff=false)` fresh review completed：
- semantic closure task’s declared write-set remains runner/tests/task package/current.md；
- workspace also contains pre-existing modified `AGENTS.md` and `docs/task-handoff-protocol.md` plus earlier read-aloud task packages; these were already present at Auditor start and are not claimed by semantic closure Executor’s files-changed record；
- no new source/article/deploy/external-project mutation observed from this Auditor task；
- semantic closure source/task files trailing-whitespace scan：PASS；
- EOF newline scan：PASS。

### literal git diff --check limitation

本 Auditor task 要求 literal `git diff --check`。当前 CodexPro connector contract explicitly requires Git diff/status inspection through `show_changes` and forbids using bash for Git diff commands，因此 Auditor did not bypass tool policy to execute literal command.

Master current evidence says it had previously observed literal `git diff --check PASS`，但本 Auditor does not adopt that as independent verdict authority.

This verification limitation is recorded, but the overall verdict is already BLOCKED by the independently reproduced product finding above.

## 10. Side-effect boundary

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

## 11. Aggregate verdict

Formal:

`BLOCKED_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_AUDIT / RETURN_TO_MASTER_CONTROL`

Aggregate material findings count：**1**

- malformed unhashable raw provider status (dict/list) causes unbounded Python `TypeError` before bounded terminal fail-closed classification.

其余本轮 required matrices/regressions 未发现第二个 material blocker。

当前不得进入 activation design。

