# Audit — S4 Provider Evidence Bounded Persistence Fresh Independent Re-audit

日期：2026-10-08

角色：`ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_BOUNDED_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`BLOCKED_S4_PROVIDER_EVIDENCE_BOUNDED_REAUDIT / RETURN_TO_MASTER_CONTROL`

## Material residual

当前 `_provider_result_evidence()` 已能省略 oversized、malformed、unknown-key values，但 persistence gate 只按字段自身格式/长度判断，没有按当前 terminal contract / current job identity 做语义判断。

因此 raw provider result 会被 terminal truth validation 正确拒绝，但“语法上可持久化、语义上非法”的字段值仍会进入 durable job JSON。

独立攻击 1：

- provider status=`PASS`
- provider request_id=`wrong-valid-WRONG_VALID_REQUEST_MARKER`
- 该 request_id 满足 `REQUEST_ID_RE`，但不等于 current `job.request_id`
- raw terminal validation => `TERMINAL_FAIL_CLOSED`
- last_error=`PROVIDER_RESULT_REQUEST_ID_MISMATCH`
- artifact retrieval calls=`0`
- serialized durable job JSON：`WRONG_VALID_REQUEST_MARKER` **仍存在**
- persisted provider_result.request_id=`wrong-valid-WRONG_VALID_REQUEST_MARKER`

独立攻击 2：

- provider status=`PASS`
- request_id 与 current job exact match
- provider failure_code=`PASS_FAILURE_CODE_MARKER`
- 该值长度合法，但 PASS contract 明确不允许 non-empty failure_code
- raw terminal validation => `TERMINAL_FAIL_CLOSED`
- last_error=`PROVIDER_PASS_FAILURE_CODE_INVALID`
- artifact retrieval 未发生
- serialized durable job JSON：`PASS_FAILURE_CODE_MARKER` **仍存在**
- persisted provider_result.failure_code=`PASS_FAILURE_CODE_MARKER`

因此当前整改尚未满足正式 task 的要求：

- invalid raw field must be absent rather than merely bounded;
- serialized durable job JSON must not contain adversarial marker/body on invalid identity paths;
- sanitization must not be independent of the raw terminal truth semantics in a way that preserves semantically rejected provider values.

Fresh standard regression 仍为真实事实：

- py_compile：PASS
- runner：`45/45 PASS`
- full Website Python：`106/106 PASS`
- `git diff --check`：PASS
- production runtime root：absent

这些测试事实不足以关闭上述未覆盖的 semantic-invalid persistence path。

## Materiality

该 residual 仍属于最后的 provider diagnostic evidence persistence boundary，而不是新范围：

- raw identity truth 已正确 fail-closed；
- artifact gate 已正确保持 0；
- 但被 raw truth 判定为非法的 provider-controlled content 仍可通过“syntactically bounded” evidence gate durable-persist；
- 因此 durable JSON 仍不能证明“invalid provider identity values / adversarial marker completely absent”。

## Minimal remediation boundary

只需继续收紧 Website-local diagnostic evidence persistence，不需要改变 terminal truth validation、execution lock、VOICE_AI 或架构。

最小要求：

1. evidence persistence 必须结合 current job + provider status contract，而不只是字段自身 regex/length。
2. `request_id` 只有在 exact equal current `job.request_id` 时才允许持久化；wrong-but-valid request_id 必须省略。
3. `failure_code` 只有在其 provider status 语义允许时才持久化；PASS 下 non-empty failure_code 必须省略。
4. 其它 status-dependent fields 也必须只在其对应 terminal contract 语义允许时持久化。
5. 不得截断、repair、normalize 后重新解释为合法 identity。
6. 补 regression：wrong-but-regex-valid request_id marker 与 PASS bounded nonempty failure_code marker 都必须从 serialized durable job JSON 完全消失，同时 raw validation 仍 fail-closed、artifact calls=0。

本 auditor 不实施修复。

