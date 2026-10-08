# Article Read-Aloud P1B-pre — S4 Malformed Provider Status Type-Safety Closure

状态：PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT
日期：2026-10-08
Owner：Website / 个人网页项目

ROLE：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_MALFORMED_STATUS_TYPE_SAFETY_CLOSURE_EXECUTOR / EXECUTOR`

REPORT_TO：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

LIFECYCLE：
`LONG_RUNNING_UNTIL_NEXT_AUTHORITY_BREAKPOINT`

RETURN_CONDITION：
`READY_FOR_FRESH_INDEPENDENT_AUDIT_OR_TRUE_AUTHORITY_BLOCKER`

## Trigger

Fresh independent audit verdict:

`BLOCKED_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_AUDIT / RETURN_TO_MASTER_CONTROL`

Primary audit:
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-fresh-audit-20261008/audit.md`

Aggregate material findings count: 1.

唯一 material blocker：

malformed unhashable provider `status`（dict/list/nested values）在 evidence sanitizer 与 raw terminal validator 的 enum membership 处可直接抛 Python `TypeError`，导致 Website job 保持 `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`，而不是形成 bounded：

- `TERMINAL_FAIL_CLOSED`
- `last_error=PROVIDER_RESULT_STATUS_INVALID`
- provider evidence `{}`
- artifact retrieval=0

其余 current-job-aware / status-aware persistence、artifact boundary、execution owner、authorization claim、render、reconcile、prior residual regressions 均已被该 Auditor 独立验证通过。

## Long-lifecycle rule

本 task 不得因为普通 test FAIL、局部 bug、同一 write-set 内的新 malformed-status edge case 或可安全定位的 regression 提前交回。

Executor 必须在同一 authority/write-set 内连续完成：

1. type-safe status gating implementation；
2. sanitizer + raw validator 双侧 closure；
3. dict/list/nested/malformed status adversarial tests；
4. serialized durable JSON marker-absence validation；
5. artifact gate validation；
6. runner targeted/full suite；
7. full Website Python suite；
8. existing execution/claim/render/reconcile/artifact regressions；
9. py_compile / hygiene / runtime-root absence / temp cleanup；
10. 若同 scope 内暴露局部 bug，保留 chronology 后直接最小修复并重跑。

只在下一个真正 authority breakpoint 停止。

## Exact remediation boundary

只修 Website-local provider terminal status type-safety。

### A. Evidence sanitizer

在任何 terminal enum membership 前：

- 必须先明确 `isinstance(status, str)`；
- 非 string status => evidence `{}`；
- 不 stringify；
- 不 normalize；
- 不 repair；
- 不 truncate；
- 不把 malformed provider value转成合法 status。

### B. Raw terminal validator

在任何 terminal enum membership 前：

- 必须先明确 `isinstance(status, str)`；
- 非 string status => raise bounded `RunnerError("PROVIDER_RESULT_STATUS_INVALID")`；
- unknown string status => 同样 bounded `PROVIDER_RESULT_STATUS_INVALID`；
- 禁止 raw Python `TypeError`、`KeyError` 或其它 implementation exception逃出正式 fail-closed path。

### C. Required durable outcome for malformed status

对 dict/list/nested/object malformed status，必须证明：

- Website durable status => `TERMINAL_FAIL_CLOSED`
- last_error => `PROVIDER_RESULT_STATUS_INVALID`
- provider_result diagnostic evidence => `{}`
- artifact retrieval calls => 0
- serialized durable job JSON 不含 malformed marker/body
- execution owner 在 durable fail-closed 后按现有 safe clean-release 语义释放
- subsequent status/result reads 正常
- terminal reconcile 不再触发 provider POST

### D. No regression to existing raw-truth boundary

Raw provider result 仍直接进入 terminal truth validation。

Do NOT:
- validate sanitized evidence instead of raw result；
- stringify malformed status；
- map dict/list to a string；
- silently coerce unknown status；
- alter current job identity rules；
- alter failure_code semantics；
- alter PASS-only identity semantics。

## Required adversarial matrix

至少新增并独立验证：

1. `status={"nested":"DICT_STATUS_MARK"}`
2. `status=["LIST_STATUS_MARK"]`
3. nested dict/list mixtures containing unique marker/body
4. numeric status
5. boolean status
6. null status
7. tuple-like / non-string structured value if representable in fake provider path
8. unknown string status

For each malformed/non-terminal enum case require:

- raw validation => bounded `PROVIDER_RESULT_STATUS_INVALID`
- durable Website status => `TERMINAL_FAIL_CLOSED`
- artifact calls=0
- provider_result evidence empty
- marker absent from serialized durable JSON
- no raw Python implementation exception escapes
- execution owner safely released after durable fail-closed
- terminal reconcile does not re-enter provider

## Regression matrix

Must keep passing:

- exact valid PASS
- exact valid BLOCKED
- exact valid FAIL_CLOSED
- wrong-but-regex-valid request_id
- PASS invalid nonempty failure_code
- BLOCKED / FAIL_CLOSED PASS-only identity omission
- oversized 5027+ run_id
- oversized artifact_ref / receipt_ref
- oversized/malformed failure_code
- unknown 5KB provider body
- artifact SHA mismatch
- exact render binding / symlink / SHA / UTF-8
- authorization O_EXCL claim / duplicate submit
- execution mutual exclusion / stale owner
- same-id UNKNOWN reconcile
- terminal reconcile no duplicate call

## Mechanical acceptance

Keep iterating in THIS SAME TASK until all applicable checks pass or a true authority blocker occurs.

Required final checks:

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py`
- full runner suite
- full Website Python suite
- explicit malformed-status adversarial matrix
- serialized durable JSON marker absence
- artifact call-count assertions
- execution owner release assertions
- `git diff --check` when permitted by current connector policy; if connector forbids literal bash git diff, record policy and use show_changes + whitespace/EOF equivalence, leaving literal rerun to fresh Auditor
- production runtime root absent
- temp roots/scripts clean

Preserve all intermediate FAIL/PASS chronology.

## Allowed write-set

- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`
- this task directory
- `docs/tasks/current.md`

A strictly local helper/fixture under `scripts/tests/` may be added only if necessary and documented.

Anything outside this write-set => STOP + Master escalation.

## Forbidden

- no real Pilot claim/submit
- no real `/v1/speech`
- no production runtime root creation
- no LaunchAgent install/bootstrap/kickstart
- no WAV/MP3
- no execution architecture redesign
- no VOICE_AI/N6 change
- no external-project mutation
- no Website `src/` or article mutation
- no R2/NAS/deploy
- no commit/push

## Authority breakpoint / stop condition

Do NOT stop for ordinary test iteration.

Stop only when:

### A. Ready for fresh independent audit

All mechanical acceptance passes and verdict is:

`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`

Then stop because a fresh independent Auditor context is required.

### B. True blocker

Use:

`BLOCKED_S4_MALFORMED_STATUS_TYPE_SAFETY_CLOSURE / RETURN_TO_MASTER_CONTROL`

only if continuing requires:
- expanding write-set/scope；
- changing execution architecture；
- changing VOICE_AI/provider contract；
- modifying another project；
- user-gated real side effect；
- or resolving evidence conflict outside current authority.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-malformed-status-type-safety-closure-20261008/`

Write/update:
- `task.md`
- `implementation.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md`.

Do not create additional tiny remediation task directories for ordinary failures inside this scope.
