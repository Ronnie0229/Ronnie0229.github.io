# Audit — S4 Durable Runner Fresh Independent Implementation Audit

日期：2026-10-07

角色：`ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT / RETURN_TO_MASTER_CONTROL`

## 1. Independent basis

本轮未采用 implementation Executor 的 `PASS_S4_DURABLE_RUNNER_IMPLEMENTED` 或其测试数字作为预设结论。

Fresh-read / fresh-check：
- implementation task package；
- architecture amendment 与其 fresh independent re-audit；
- `scripts/read_aloud_s4_runner.py`；
- `scripts/tests/test_read_aloud_s4_runner.py`；
- VOICE_AI current S1/S4/N6 identity contract（read-only）；
- isolated fake-provider adversarial executions。

标准测试已 fresh rerun：
- runner suite：`19/19 PASS`
- Website Python suite：`80/80 PASS`

这些 PASS 作为 chronology 保留，但下面两个 material implementation finding 未被现有测试覆盖。

## 2. Finding F-S4-IA-01 — single-worker invariant 未被机械执行

### Finding

冻结架构要求 execution concurrency=`single worker`，正式 audit task 也要求“single-worker assumption is explicit/mechanical”。

当前 implementation 中：
- `worker_once()` 仅扫描第一个 non-terminal job 后直接调用 `execute_job()`；
- `execute_job()` 自身没有 process/thread/job execution claim、exclusive lock 或等价机械排他；
- `reconcile()` 也可直接再次进入 `execute_job()`；
- source 中没有 worker lock / flock / execution O_EXCL 等机制。

因此两个并发 worker/reconcile caller 可同时读取同一 non-terminal job、同时把它写为 `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`，然后同时调用 `provider.speech(text, same_request_id)`。

### Independent attack evidence

在 task-local isolated test root + fake provider 下并发执行同一 job：

`SPEECH_CALLS 2`

两个 execution path 均实际进入 provider speech。

进一步模拟 VOICE_AI current same-id in-flight 行为：
- 第一个 invocation 返回 PASS；
- 第二个 invocation 返回 `BLOCKED / HTTP_DUPLICATE_IN_FLIGHT`；
- 最终 Website persisted state 被后到的 BLOCKED 覆盖为：

`TERMINAL_BLOCKED / HTTP_DUPLICATE_IN_FLIGHT`

即 provider generation 已成功产生 PASS，但 Website orchestration truth 可以被并发 duplicate 的 transport BLOCKED 覆盖为 terminal blocked。

### Materiality

这不是“provider 会不会重复真正生成音频”的问题；N6 exactly-once 仍可阻止第二 generation。

material 风险在 Website durable runner：
- 违反 frozen single-worker architecture；
- 同一 logical job 可产生并发 provider POST；
- Website terminal state 存在 last-writer-wins corruption；
- 一个真实 PASS 可被 duplicate-in-flight BLOCKED 覆盖；
- 后续 activation 若只依赖“LaunchAgent 通常单实例”而没有 implementation-level机械约束，则不能证明 durable orchestration truth。

### Minimal remediation boundary

只需 Website-local 最小 execution exclusion，不需要 Redis/Celery/database/lease platform。

允许 Master 选择例如：
- runtime-root 内一个 non-expiring single-worker O_EXCL ownership/lock primitive；
- 或 per-job atomic execution claim，只允许一个 caller 进入 possible-POST section。

必须满足：
1. 同一时刻仅一个 Website execution caller 可以进入 provider POST critical section；
2. second worker/reconcile 不得并发 POST；
3. crash 后不得通过不安全自动 takeover 推断 prior provider side effect 未发生；
4. terminal state 不得被 stale concurrent caller 覆盖。

本 auditor 不实施。

## 3. Finding F-S4-IA-02 — provider terminal result identity 未反向绑定 Website job

### Finding

VOICE_AI frozen success identity 是：

`request_id + run_id + artifact_ref + artifact_sha256 + receipt_ref`

并且 terminal result schema 中 `request_id` 是 caller request identity。

当前 `_apply_provider_result()` 只读取：
- `status`
- artifact fields（PASS 时）

但没有验证：
- `provider_result.request_id == job.request_id`
- terminal result required identity/schema fields 是否与当前 request/job一致。

Source search 对 `provider_result.get("request_id")` 返回无匹配。

### Independent attack evidence

隔离 fake provider 接收正确 Website request_id，但返回：

`request_id = WRONG-ID`

同时返回可通过 SHA 校验的 artifact。

runner 实际结果：

- Website job request_id = 正确 deterministic request_id
- provider_result.request_id = `WRONG-ID`
- persisted Website status = `TERMINAL_PASS`

说明当前 runner 会接受与自身 logical job 不同 request identity 的 provider PASS。

### Materiality

这破坏 frozen provenance / dual-truth boundary：
- Website 不能证明其 terminal PASS 属于本 job 的 exact provider request identity；
- artifact 即使 SHA 正确，也可能属于另一 request/run；
- reconcile 或 transport bug 返回 stale/wrong result 时，Website 会把它绑定进当前 job；
- 后续 downstream provenance 会把错误 VOICE_AI identity 当作当前文章 TTS 成果。

### Minimal remediation boundary

在任何 provider terminal result 被持久化为 Website terminal truth前，最小验证：

1. result 必须是 frozen VOICE_AI terminal result shape；
2. syntactically valid current request 下，`provider_result.request_id` 必须 exact equal `job.request_id`；
3. PASS 必须具备 required success identity fields，类型与格式合法；
4. identity mismatch / missing required field => Website `TERMINAL_FAIL_CLOSED` 或 operator-required fail-closed；
5. mismatch result 不得 finalize artifact 为 verified downstream result。

不需要修改 VOICE_AI。

## 4. Other audited areas

以下攻击未发现新的 material blocker：

- descriptor canonicalization / deterministic request_id：符合 frozen rule；
- wrong supplied request_id 在 runtime mutation 前被拒绝；
- authorization claim key 只由 authorization_ref + generation_epoch决定；
- O_EXCL claim exclusivity、same-binding duplicate、different identity conflict、partial/corrupt claim fail-closed：方向成立；
- bounded 1-second wait 不 delete/release/takeover claim；
- job JSON 使用 temp + fsync + replace；
- render path 使用 descriptor-relative open + O_NOFOLLOW，absolute/.. / symlink ambiguity fail-closed；
- exact render bytes -> SHA -> strict UTF-8 -> same validated text object 到 provider call；
- render negative paths provider speech call count=0；
- readiness 不执行 provider admin/start；
- connection uncertainty进入 `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`；
- terminal reconcile 本身 read-only；
- artifact_ref 作为 opaque ref 使用；
- artifact bytes SHA verify 后才 atomic finalize；
- job/claim 不持久化 full TTS text；
- production root constant精确，fresh test后仍不存在；
- 本轮没有真实 provider POST、Pilot claim/submit、LaunchAgent 或外部项目 mutation。

## 5. Test-quality disposition

现有 19 个 runner tests 能覆盖大量 frozen invariants，但没有覆盖：
- concurrent execution / reconcile against same job；
- provider terminal result request_id mismatch。

因此 `19/19 PASS` 与 `80/80 PASS` 都是真实测试事实，但不足以满足本 independent audit denominator。

## 6. Verdict

Formal:

`BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION_AUDIT / RETURN_TO_MASTER_CONTROL`

当前不应进入 activation design。Master Control 若决定继续，只需对上述两个 Website-local material gaps 做最小 targeted remediation + fresh re-audit；不得借机扩大到 generic queue/lease/platform 或修改 VOICE_AI。

