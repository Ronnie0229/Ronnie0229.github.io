# NEXT_HANDOFF — S4 Durable Runner Targeted Implementation Remediation

正式工作区：
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007`

请分发给：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_TARGETED_REMEDIATION_EXECUTOR / EXECUTOR`

唯一 task：
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-20261007/task.md`

先读：
`docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-20261007/NEXT_HANDOFF.md`

严格按正式 task 执行。

本轮只修复 independent implementation audit 的两个 material gaps：execution mutual exclusion 与 provider terminal result identity validation。

不得 claim/submit 真实 Pilot，不得调用真实 /v1/speech，不得创建 production runtime root，不得安装 LaunchAgent，不得 commit/push。

## Executor return

正式 verdict：`PASS_S4_DURABLE_RUNNER_TARGETED_REMEDIATION / READY_FOR_FRESH_REAUDIT`

已关闭：
- `F-S4-IA-01`：runtime-root global O_EXCL execution owner 机械保证同一时刻最多一个 possible-POST execution caller；same/different job、worker_once/reconcile 并发均 provider.speech<=1；stale/crash owner 不自动 takeover/release。
- `F-S4-IA-02`：provider terminal result 在 terminal truth / artifact finalize 前强制 exact request_id reverse binding 与 PASS frozen success identity validation；wrong/missing/invalid identity fail-closed 且 artifact call=0。

验证：runner 33/33 PASS；全仓 Python 94/94 PASS；production runtime root absent；task-local temp 无残留。

Pilot authorization 仍 `UNCLAIMED / NOT_CONSUMED`；未真实 `/v1/speech`、未安装 LaunchAgent、未生成音频、未修改外部项目、未 deploy/R2/NAS、未 commit/push。

下一步只能 fresh independent re-audit 本 targeted remediation；不得进入 activation design。

Executor 已停止并交回：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`
