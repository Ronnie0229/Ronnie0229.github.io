# NEXT_HANDOFF — S4 Provider Evidence Bounded Persistence Remediation

正式工作区：
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007`

请分发给：
`ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION_EXECUTOR / EXECUTOR`

唯一 task：
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-remediation-20261007/task.md`

先读：
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-remediation-20261007/NEXT_HANDOFF.md`

严格按正式 task 执行。

本轮唯一整改目标：
provider diagnostic evidence 必须在 durable persistence 前完成 bounded validation/sanitization，非法或超长 allowlisted values 不得原样落盘。

不得修改 execution lock 设计。
不得 claim/submit 真实 Pilot。
不得调用真实 /v1/speech。
不得创建 production runtime root。
不得安装 LaunchAgent。
不得 commit/push。

## Executor return

正式 verdict：`PASS_S4_PROVIDER_EVIDENCE_BOUNDED_REMEDIATION / READY_FOR_FRESH_REAUDIT`

已完成：
- `_provider_result_evidence()` 改为逐字段 bounded persistence gate；非法/超长/malformed values 直接省略，不截断、不 stringify、不 repair；
- terminal identity truth validation 继续使用 raw provider result，未改变 provider identity truth rules；
- oversized/malformed run_id、artifact_ref、receipt_ref、failure_code、request_id 以及 unknown large provider body 均通过 serialized durable JSON marker-absence 测试；
- identity validation failure 路径 artifact retrieval 继续为 0；
- valid PASS/BLOCKED/FAIL_CLOSED bounded evidence persistence 保持正常；
- execution lock 设计未修改。

验证：runner 45/45 PASS；全仓 Python 106/106 PASS；`git diff --check` PASS；production runtime root absent；task-local temp 无残留。

Pilot authorization 仍 `UNCLAIMED / NOT_CONSUMED`；未真实 `/v1/speech`、未安装 LaunchAgent、未生成音频、未修改外部项目、未 deploy/R2/NAS、未 commit/push。

下一步只能 fresh independent re-audit 本 bounded evidence remediation；不得进入 activation design。

Executor 已停止并交回：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`
