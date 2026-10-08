# NEXT_HANDOFF — P1B-pre S4 Durable Runner Bounded Implementation

正式工作区：
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007`

请分发给：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_IMPLEMENTATION_EXECUTOR / EXECUTOR`

唯一 task：
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-implementation-20261007/task.md`

先读：
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-implementation-20261007/NEXT_HANDOFF.md`

严格按正式 task 执行。

本轮只实现并在隔离 test root 验证 Website S4 durable runner；不得 claim/submit 真实 Pilot，不得调用真实 /v1/speech，不得创建 production runtime root，不得安装 LaunchAgent。

## Executor return

正式 verdict：`PASS_S4_DURABLE_RUNNER_IMPLEMENTED / READY_FOR_INDEPENDENT_AUDIT`

已实现：
- Website-local deterministic descriptor/request_id；
- authorization O_EXCL one-time claim + conservative partial-claim handling；
- atomic JSON job state；
- every-possible-POST exact render binding gate；
- single worker / short submit-status-result-reconcile；
- thin VOICE_AI HTTP adapter boundary；
- artifact SHA verify + atomic local cache finalize。

验证 chronology：
- runner attempt 1：18/19，随后修正 wrong-request-id 前 runtime init 顺序；
- runner attempt 2：19/19 PASS；
- full Python attempt 1：79/80，暴露 concurrent claim visibility race；
- 最小整改后 final runner：19/19 PASS；final full Python：80/80 PASS。

Final readback：production runtime root 不存在；task-local test temp 无残留；真实 Pilot authorization 仍 `UNCLAIMED / NOT_CONSUMED`；真实 `/v1/speech` 未调用；无 LaunchAgent、无音频、无外部项目 mutation、无 commit/push。

下一步只能 fresh independent implementation audit；不得自动激活 Pilot。

Executor 已停止并交回：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`
