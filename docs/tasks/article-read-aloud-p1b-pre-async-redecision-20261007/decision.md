# Decision — P1B-pre Long-running TTS Architecture Redecision

日期：2026-10-07

正式 verdict：PASS_MINIMAL_ARCHITECTURE_SELECTED

## Owner / architecture decision

选择：Website Owner 的 S4 consumer adapter/orchestration 增加最小 durable execution layer；VOICE_AI Local HTTP V1 保持不变。

- VOICE_AI 继续拥有 text→speech、N6 request state、exactly-once、run/artifact identity、artifact retrieval 与 TTS failure semantics。
- Website S4 拥有 article/render provenance、generation authorization、stable request_id derivation、job submit/status/result/reconcile 与 downstream artifact handling。
- CodexPro、Hermes Telegram、未来 Website automation 都只做短时 caller/observer，不持有长任务生命周期。
- 长时同步 POST /v1/speech 由 Website-side durable single worker 持有。

## 为什么不修改 VOICE_AI V1

VOICE_AI current authority 已冻结：HTTP V1 是 loopback、同步 generation；V1 明确不包含 queue/job scheduler、Redis/Celery/database；exactly-once authority 只属于 N6 persisted request state。将 submit/status/result 做成新的 VOICE_AI async API 会扩大 provider contract，并复制/干扰 N6 state machine，不是当前最小方案。

## 外部执行层复用判断

RonnieAutomation 确实拥有 orchestration/task lifecycle/idempotency/fail-closed 能力，但 current authority 没有已授权的 TTS worker surface，且明确把 VOICE_AI/TTS 排除在当前 critical path。把当前 Pilot 接入会新增跨项目 authority、contract、runtime qualification 与 audit 链，属于不必要复杂化。

Hermes 可作为未来 caller/observer；其当前 authority 与历史 Telegram 窄例外都不能把它升级为唯一 durable worker。

因此当前不复用 RonnieAutomation/Hermes 作为 worker；只复用已验证的 macOS launchd 作为未来进程监督原语。不得修改 VOICE_AI S2 LaunchAgent identity。

## Minimal S4 durable execution model

仅两个逻辑组件：

1. S4 control adapter：submit / status / result / reconcile。
2. single durable worker：读取 Website-owned durable job record，调用现有同步 VOICE_AI HTTP V1，将终态 identity 写回 job record。

持久化选择：Website-owned filesystem job spool + atomic JSON state。runtime state root 必须由后续 implementation task 冻结为 Website-owned local application state，位于 Git repo 与 NAS 之外。每个 logical job 一个 immutable identity + mutable atomic state；temp file + atomic rename。默认只保存 identity/hash/status，不在日志复制全文。

未来进程监督选择 macOS launchd，但本轮不安装任何 LaunchAgent。

## Minimal V1 job contract

submit 至少绑定 operation_id、article_id、render_ref、render_sha256、request_id、voice_contract_id=VOICE_AI_LOCAL_HTTP_V1、exact generation authorization reference/epoch。重复提交同一 immutable identity 返回 existing job；identity conflict fail-closed；submit 快速返回，不等待 TTS。

status 只读 Website job state，不伪造 VOICE_AI 内部状态。最小状态：QUEUED、WAITING_PROVIDER_READY、CALL_IN_PROGRESS_OR_RESULT_UNKNOWN、TERMINAL_PASS、TERMINAL_BLOCKED、TERMINAL_FAIL_CLOSED。

result 仅在 terminal 时返回 request_id、provider status/failure_code、run_id、artifact_ref、artifact_sha256、receipt_ref、replay/reconcile evidence 与 downstream retrieval verification state。

reconcile 只能使用同一个 exact text + 同一个 request_id。禁止 mint 新 request_id、清理 VOICE_AI lock/state、扫描 internal output 猜 PASS、按 elapsed time 自动 regenerate。

## Stable request_id

Website 使用 deterministic derivation，不使用随机 retry ID。推荐形式：rc-readaloud-v1:<sha256(canonical_operation_descriptor)>。

canonical descriptor 至少包含 articleId、exact Render View SHA-256、explicit generation epoch/authorization identity、VOICE_AI contract id。该格式满足 current request_id regex，且小于 128 chars。

同一 logical generation 永远得到同一 request_id。未来若用户明确授权重新生成，必须先形成新的 explicit generation epoch，不能因 timeout/busy/disconnect/worker restart 自动产生新 epoch。

## Crash / busy / disconnect reconcile

worker 在 POST 前必须先持久化 exact request identity，并进入 CALL_IN_PROGRESS_OR_RESULT_UNKNOWN。

恢复时：
1. 不生成新 request_id。
2. 检查 /ready。
3. provider busy/not-ready 时等待，不提交其它 identity。
4. provider 可接受请求后，用同一 text + 同一 request_id 再 POST。
5. 如果 N6 已 terminal，得到 exact replay，generation delta=0。
6. 如果 N6 返回 unknown/in-progress/blocking，保持 BLOCKED/Owner resolution，绝不自动 regenerate。

这样 Website job state 只负责 orchestration；N6 仍是唯一 generation exactly-once truth。

## Artifact / privacy

只有 terminal PASS 后才使用 opaque artifact_ref 调用现有 artifact retrieval，并验证返回 bytes SHA-256 等于 artifact_sha256。Website downstream copy/rename 必须保留 request_id/run_id/artifact provenance。不得直接消费 VOICE_AI internal outputs path。

job/log 默认只保留 hash、articleId、bounded local ref、provider identity/status；不通过 Hermes/Telegram 把完整 TTS 正文当 durable job storage。

## Caller model

CodexPro、Hermes、future Website automation 只做短时 submit/status/result/reconcile。它们不等待长 generation，不持有 worker PID，不用 nohup & 冒充 durable architecture。

## Current Pilot route

GENERATION_AUTHORIZATION_NOT_CONSUMED 保持成立。

当前 frozen Pilot：articleId=post-32d30724d859c99c；Render View SHA-256=5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a。

合法下一路径：先由 Website Owner 建立并验证最小 S4 durable runner/control adapter；冻结 Pilot operation_id + generation_epoch + deterministic request_id；把现有 exactly-one authorization 绑定该 exact job identity；short submit 一次；worker 执行同步 HTTP；caller 后续只查 status/result；PASS 后 artifact retrieval + SHA verify；任何 timeout/crash 只用相同 request_id reconcile；整个 lineage 必须证明只有一个 VOICE_AI generation identity。

不得为赶 Pilot 退回 CodexPro 长连接、nohup、Hermes 人工启动或随机 request_id retry。

## Overbuilding exclusions

当前不建设 VOICE_AI async V2/provider status endpoint、Redis/Celery/database、distributed queue、generic cross-project automation platform、RonnieAutomation TTS integration、Hermes-specific worker、remote exposure、multiple workers、cancellation/priority queue、scheduled publication、R2/NAS lifecycle 或 automatic publication。

## Gate

- GOAL_ALIGNMENT=ON_PLAN
- BLOCKER_MATERIALITY=REQUIRED
- OVERBUILDING_RISK=LOW
- OWNER_BOUNDARY=PASS
- MINIMAL_NEXT_STEP=YES
- NEXT_TASK_JUSTIFIED=YES

Final: PASS_MINIMAL_ARCHITECTURE_SELECTED

下一阶段如继续，只应建立 Website Owner-local bounded implementation task，实施并验证最小 S4 filesystem-spool + single launchd-supervised worker + short submit/status/result/reconcile surface；本轮不得实现。