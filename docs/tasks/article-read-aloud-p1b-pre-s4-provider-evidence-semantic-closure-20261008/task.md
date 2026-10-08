# Article Read-Aloud P1B-pre — S4 Provider Evidence Semantic Persistence Closure

状态：PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT
日期：2026-10-08
Owner：Website / 个人网页项目

ROLE：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE_EXECUTOR / EXECUTOR`

REPORT_TO：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

LIFECYCLE：
`LONG_RUNNING_UNTIL_NEXT_AUTHORITY_BREAKPOINT`

RETURN_CONDITION：
`READY_FOR_FRESH_INDEPENDENT_AUDIT_OR_TRUE_AUTHORITY_BLOCKER`

## Why this task exists

Fresh independent re-audit verdict:

`BLOCKED_S4_PROVIDER_EVIDENCE_BOUNDED_REAUDIT / RETURN_TO_MASTER_CONTROL`

Primary audit:
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-fresh-reaudit-20261007/audit.md`

Current final residual:

provider diagnostic evidence persistence 已能过滤 oversized/malformed values，但仍会持久化“字段自身格式合法、却被 current-job/status terminal contract 判为非法”的 provider-controlled values。

Independent examples:
- wrong-but-regex-valid request_id：raw validation fail-closed / artifact=0，但 wrong request marker 仍落入 durable JSON；
- PASS + bounded nonempty failure_code：raw validation fail-closed / artifact=0，但 invalid failure_code marker 仍落入 durable JSON。

## Long-lifecycle execution rule

本 task 不得因为普通测试 FAIL、局部实现 bug、同一 write-set 内的新 edge case、或可安全定位的 regression 就提前交回。

Executor 必须在同一 authority / Owner / write-set 内连续完成：

1. 实现 semantic-aware diagnostic evidence persistence；
2. 补齐 adversarial tests；
3. 重跑 targeted + full regression；
4. 若测试暴露同一 scope 内局部缺陷，保留 FAIL chronology 后直接最小修复；
5. 重跑直到 mechanical acceptance 达标；
6. 更新正式 evidence / chronology；
7. 只有达到“需要切换 fresh independent Auditor”的断点，或出现真正需要扩大 scope/Owner/write-set/外部项目 mutation/用户授权的 blocker，才停止交回。

不得把本任务再拆成 tiny remediation 子任务。

## Exact scope

只修改 Website runner diagnostic provider evidence persistence，使其同时满足：

- field-level bounded persistence；
- current-job-aware semantics；
- provider-status-aware terminal contract semantics；
- raw provider result 继续作为 terminal truth validation authority；
- semantic-invalid provider-controlled value 不进入 durable JSON。

Do NOT change unless a regression forces a strictly local correction:
- execution-owner design；
- authorization one-time claim；
- descriptor/request_id derivation；
- exact render binding；
- artifact SHA verification；
- runtime root identity；
- VOICE_AI semantics；
- N6 exactly-once truth ownership；
- reconcile architecture；
- external Owner boundaries。

## Required semantic persistence contract

### 1. request_id

Durable provider evidence may persist `request_id` only if ALL are true:

- raw value is string；
- matches frozen `REQUEST_ID_RE`；
- exact equal current `job.request_id`。

Wrong-but-regex-valid request_id must be omitted from durable provider evidence.

It must still cause raw terminal identity validation fail-closed.

### 2. status

Persist status only if it is recognized terminal enum:

- PASS
- BLOCKED
- FAIL_CLOSED

Unknown/malformed status must be omitted from provider evidence.

Website-local job status / last_error may still record local failure classification.

### 3. failure_code

Persistence must be status-aware:

- PASS: non-empty provider failure_code is semantically invalid and MUST NOT persist；
- BLOCKED: bounded valid non-empty failure_code may persist；
- FAIL_CLOSED: bounded valid non-empty failure_code may persist；
- unknown/malformed status: provider failure_code must not be persisted as if semantically valid.

Do not truncate/repair/normalize invalid failure_code.

### 4. PASS-only success identity

These provider fields are semantically eligible for durable evidence only for raw `status=PASS` and only if individually valid:

- run_id
- artifact_ref
- artifact_sha256
- receipt_ref

For BLOCKED / FAIL_CLOSED, these PASS-only fields must not be durably preserved as trusted diagnostic identity merely because their own syntax is valid.

If raw PASS result later fails some other terminal identity contract check, only fields that are both individually valid AND semantically compatible with current job/status may be persisted; the field that triggered semantic invalidity must not be preserved.

### 5. BLOCKED / FAIL_CLOSED evidence

For BLOCKED / FAIL_CLOSED:
- request_id must exact-match current job before persistence；
- failure_code must satisfy bounded valid semantics；
- PASS-only identity fields should be omitted from durable provider evidence unless current frozen provider contract explicitly requires them for that terminal status. Do not infer new contract fields.

### 6. Raw truth vs persisted diagnostic evidence

Critical invariant:

- `_validate_provider_terminal_result()` or equivalent terminal truth gate must evaluate the **raw provider result**；
- persistence sanitization must not mutate, normalize, repair, truncate, or otherwise convert invalid raw identity into valid terminal truth；
- sanitized evidence is diagnostic only, never provider identity authority.

### 7. Failure-path evidence

On terminal validation failure, durable job JSON may preserve only:

- Website-local `TERMINAL_FAIL_CLOSED`；
- bounded locally-generated `last_error`；
- semantically valid safe provider evidence fields under the rules above；
- no raw rejected provider-controlled marker/body.

## Required adversarial matrix

Tests must directly inspect serialized durable JSON bytes/text, not only parsed dicts.

At minimum cover:

1. wrong-but-regex-valid request_id + marker
   - raw validation fail-closed
   - artifact calls=0
   - marker absent
   - provider_result.request_id absent

2. PASS + bounded nonempty failure_code + marker
   - raw validation fail-closed
   - artifact=0
   - marker absent
   - provider_result.failure_code absent

3. BLOCKED + exact matching request_id + valid failure_code
   - persists request_id + failure_code
   - remains TERMINAL_BLOCKED

4. FAIL_CLOSED + exact matching request_id + valid failure_code
   - persists request_id + failure_code
   - remains TERMINAL_FAIL_CLOSED

5. BLOCKED/FAIL_CLOSED carrying syntactically valid PASS-only run_id/artifact_ref/artifact_sha256/receipt_ref markers
   - PASS-only markers absent from durable JSON unless frozen provider contract explicitly requires them

6. PASS with one semantically invalid field and other individually valid fields
   - invalid field marker absent
   - artifact retrieval remains 0 when terminal identity invalid
   - no invalid field survives through evidence

7. malformed/unknown status with valid-looking request_id/failure_code/success identity
   - provider-controlled fields not persisted as trusted terminal evidence
   - local fail-closed classification remains bounded

8. exact valid PASS
   - request_id/run_id/artifact_ref/artifact_sha256/receipt_ref persist
   - failure_code absent/null as contract requires
   - artifact SHA verify/finalize succeeds

9. oversized/malformed cases from prior task remain covered

10. unknown 5KB provider body/marker remains absent

## Regression / mechanical acceptance

Executor must keep iterating within this same task until all applicable checks pass or a true authority blocker occurs.

Required final checks:

- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py`
- full runner test suite
- full Website Python suite
- explicit serialized durable JSON marker-absence attacks
- execution-lock regression tests remain passing
- authorization claim regression remains passing
- render gate regression remains passing
- artifact verify regression remains passing
- `git diff --check`
- production runtime root absent
- no test temp leftovers

Preserve every intermediate FAIL/PASS chronology; later PASS does not erase earlier FAIL.

## Allowed write-set

- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`
- this task directory
- `docs/tasks/current.md`

If a strictly local test helper/fixture under `scripts/tests/` is necessary, it may be added and must be documented.

Anything outside this write-set requires STOP + Master escalation.

## Forbidden side effects

- no real Pilot claim/submit
- no real `/v1/speech`
- no production runtime root creation
- no LaunchAgent install/bootstrap/kickstart
- no WAV/MP3
- no VOICE_AI/RonnieAutomation/Hermes mutation
- no Website `src/` or article mutation
- no R2/NAS/deploy
- no commit/push

## Authority breakpoint / stop condition

Do NOT stop for ordinary implementation/test iteration.

Stop only when one of these occurs:

### A. Ready for independent audit

All mechanical acceptance passes and this task reaches:

`PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`

Then stop because a new independent Auditor context is required.

### B. True authority blocker

Use:

`BLOCKED_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE / RETURN_TO_MASTER_CONTROL`

only if continuing would require:
- expanding write-set/scope；
- changing execution architecture；
- changing VOICE_AI/provider contract；
- modifying another project；
- performing a user-gated real side effect；
- or resolving evidence conflict that cannot be safely decided inside current authority.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-semantic-closure-20261008/`

Write/update as work progresses:
- `task.md`
- `implementation.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md`.

Do not create additional remediation task directories for ordinary failures inside this scope.
