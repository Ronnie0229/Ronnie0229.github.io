# Audit — P1B-pre Fresh Independent Architecture Audit

日期：2026-10-07

角色：`ARTICLE_READ_ALOUD_P1B_PRE_ASYNC_ARCHITECTURE_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`BLOCKED_ARCHITECTURE_GAP / RETURN_TO_MASTER_CONTROL`

## 1. Independent basis

本审核未采用上一 Executor 的 `PASS_MINIMAL_ARCHITECTURE_SELECTED` 作为预设结论。已 fresh-read Website 当前 authority、P1A closure、P1B-pre redecision package，并只读核对 VOICE_AI current S1/S2/S4 frozen contract 与 N6 exactly-once/replay semantics。另做最小只读复核：RonnieAutomation current authority 明确 VOICE_AI/TTS 不在当前 critical path；Hermes current authority没有当前 durable TTS lifecycle owner 权限。因此“不把 worker 放进 RonnieAutomation/Hermes”方向没有被 current authority 推翻。

## 2. What passes

以下架构方向本身成立，不构成 blocker：

- Owner boundary：durable runner/control adapter 属于 Website S4；VOICE_AI 继续只拥有 text->speech、request state/exactly-once、run/artifact identity/retrieval 与 TTS failure semantics。
- N6 remains the only generation exactly-once truth；Website job state 只能描述 orchestration，不得声称替代 N6 generation truth。
- stable request_id + exact text replay 与 VOICE_AI frozen contract一致；timeout/disconnect/worker restart 不得 mint 新 request_id。
- crash window 在 provider 已接收请求之后可由 same request_id + exact text replay/fail-closed semantics 保守处理；N6 terminal PASS replay 不产生第二 generation。
- artifact retrieval 可以在 Website 侧做临时文件下载、完整 SHA-256 verify 后再进入 downstream terminal state；不得消费 VOICE_AI internal output path。
- single worker + filesystem spool 是当前规模下合理最小方案；无需 Redis/Celery/database/distributed queue/VOICE_AI async V2。
- launchd 可以作为 Website worker 的 process supervision 原语，但不得获得 VOICE_AI daemon admin authority，也不得把 worker restart解释为 regeneration authority。
- runtime state root 必须在 Git/NAS 外、Website-owned；exact path/owner/permissions 应在 implementation task 写代码前冻结。

## 3. Blocking finding A — generation authorization lacks a single-use atomic claim

### Finding

Redecision 要求 job descriptor 包含 `exact generation authorization reference/epoch`，并规定同一 immutable identity 的重复 submit 返回 existing job；但没有规定：

**同一个 authorization reference/epoch 只能原子地绑定到一个 immutable logical generation identity。**

当前 deterministic request_id descriptor 同时包含 article/render/auth identity。如果两个 caller 使用同一个 authorization epoch，却改变 article/render/operation descriptor，就会得到两个不同 request_id。VOICE_AI N6 只能保证“每个 request_id + exact text 最多消费一次 generation right”，不能证明 Website 的“一次用户 generation authorization”没有被两个不同 request_id 各消费一次。

这不是 N6 缺陷，而是 Website Owner 的 authorization-consumption contract 尚未封口。

### Materiality

本 Pilot 明确只有 exactly-one generation authorization。若没有 Website-side single-use claim，重复/并发 submit 或 caller bug 可以合法构造第二 logical generation identity，因此不能证明“一次授权只产生一个 generation identity”。

### Minimal remediation boundary

不需要数据库、Redis、lease 或跨项目平台。只需在 bounded implementation authority 前冻结：

1. `authorization_ref/epoch -> immutable job identity/request_id` 为 one-to-one binding。
2. 首次 submit 必须在任何 provider POST 前原子占用该 authorization。
3. exact same binding 的重复 submit 返回 existing job。
4. 同一 authorization 指向任何不同 operation/article/render/request_id 时必须 fail-closed，且不得 POST。
5. 该 claim 必须对并发短时 caller 有机械排他性。最小实现可以是 Website-local atomic exclusive-create / bounded file lock；single worker 本身不能替代 submit-side claim atomicity。
6. generation authorization 只有在 exact job identity 已冻结后才能被标记为 bound；不得由 worker timeout/restart 创建新 epoch。

## 4. Blocking finding B — render_ref drift is not explicitly fail-closed before POST

### Finding

Redecision 已把 `render_ref + render_sha256` 放入 immutable descriptor，并要求 reconcile 使用 same exact text + same request_id，但没有明确规定 worker 在真正读取 `render_ref` 后、每次可能进入 provider POST 前，必须机械验证读取到的 exact bytes SHA-256 与冻结 `render_sha256` 一致。

如果 job record 只保存 ref/hash而不复制全文，这是合理的 privacy/minimal design；但 ref 指向的文件在 submit 后可能被改写、替换、消失或路径重绑定。若 worker直接读取当前 ref 内容并首次 POST，N6 会把该 request_id 绑定到“当前实际文本”，而 Website descriptor/request_id 却声称绑定旧 Render View SHA，形成 provenance corruption。

### Materiality

这会破坏 frozen Render View provenance，并且可能在第一次 provider invocation 时就把错误文本永久绑定到 stable request_id。之后 N6 的 exactly-once 反而会忠实保护这个错误 binding，无法由 Website 自动修复。

### Minimal remediation boundary

不复制全文进 job JSON即可解决：

1. 每次 worker准备进行可能触发 provider invocation 的 POST 前，读取 bounded `render_ref` 的 exact bytes。
2. 计算 SHA-256，必须等于 job immutable `render_sha256`；missing/unreadable/mismatch 一律 Website-side `TERMINAL_FAIL_CLOSED` 或等价不可自动重试状态，且 provider POST=0。
3. POST body 必须使用刚完成 SHA 验证的同一 bytes/string instance，不得 verify 一个对象、发送另一个重新读取对象。
4. reconcile 若只是读取 Website terminal state，不需重新读全文；只有准备再次发起 same-id POST 时才重新执行 exact render binding check。
5. job/log 继续只保留 bounded ref/hash/status，不需要把完整文章复制到 durable spool。

## 5. Persistence / concurrency disposition

`atomic JSON + single worker` 可以继续作为最小设计，但需要区分两类并发：

- execution concurrency：single worker 足够，不需要 lease/worker pool；
- submit/authorization concurrency：需要最小原子排他机制，至少保证 job identity create 与 authorization one-time claim 不会在两个短时 caller 间竞态。

因此不建议引入通用 lease/claim-token system；只需要 Website-local、bounded、可机械验证的 atomic create/lock discipline。

## 6. Crash-window review

- job persisted、POST 前 crash：PASS if recovery重新验证 render SHA，并使用同一 request_id；此时尚未 provider side effect。
- POST 已进入 provider、response 未收到：PASS under current S1/N6 semantics；不得新 ID，只允许 same-id recovery。若 in-flight/unknown，保持 BLOCKED/fail-closed。
- provider PASS、Website 未持久化 terminal result：PASS；same-id exact-text replay应返回同一 terminal identity，generation delta=0。
- artifact 下载中断：PASS if partial bytes只写 temp，不标 terminal；重新 GET opaque artifact_ref 后完整 SHA verify再原子落盘。
- worker restart：PASS as process recovery only；不得控制/重启/清理 VOICE_AI state。provider not-ready/busy 时等待；任何 N6 unknown/in-progress/fail-closed保持阻断。
- host restart：Website worker supervision可以自动恢复自身，但不得把 host restart解释为 generation retry authority。VOICE_AI host reboot persistence仍未正式证明，因此 provider unavailable时只能等待/阻断，不得自修 provider。

## 7. Anti-overbuilding

当前 blocker 均可在 Website S4 内以很薄的 immutable descriptor + atomic filesystem discipline 解决。没有证据要求 Redis、Celery、database、distributed queue、VOICE_AI async V2、RonnieAutomation TTS integration、Hermes worker、multi-worker、remote exposure或通用 automation platform。

## 8. Verdict

现有 `PASS_MINIMAL_ARCHITECTURE_SELECTED` 的方向正确，但尚不足以直接作为 bounded implementation authority，因为 authorization single-use 与 render-ref exact binding 两个关键首次提交前 Gate 未冻结。

Formal:

`BLOCKED_ARCHITECTURE_GAP / RETURN_TO_MASTER_CONTROL`

允许的最小后续仅是 Master Control 对上述两个 Website-local contract gap 做 architecture amendment/redecision；不得在本审核会话实施。

