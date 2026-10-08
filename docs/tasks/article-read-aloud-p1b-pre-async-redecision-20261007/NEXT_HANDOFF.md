# NEXT_HANDOFF — P1B-pre Long-running TTS Architecture Redecision

正式工作区：
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007`

角色：
`ARTICLE_READ_ALOUD_P1B_PRE_ASYNC_ARCHITECTURE_REDECISION_EXECUTOR / EXECUTOR`

先 fresh-read：
`docs/tasks/article-read-aloud-p1b-pre-async-redecision-20261007/task.md`

本轮只做 architecture/authority redecision。不得调用真实 TTS，不得实现代码，不得修改 VOICE_AI/RonnieAutomation/Hermes，不得生成 WAV/MP3。

特别注意：用户已经确认旧 P1B 提示词没有执行，所以 exactly-one generation authorization 尚未消耗。本轮执行后仍保持 `GENERATION_AUTHORIZATION_NOT_CONSUMED`。

## Executor return

- verdict：`PASS_MINIMAL_ARCHITECTURE_SELECTED`
- selected owner：Website S4 consumer adapter/orchestration
- provider：VOICE_AI Local HTTP V1 保持不变
- long-running lifecycle：future Website-owned single durable worker；caller 只做短时 submit/status/result/reconcile
- persistence：filesystem spool + atomic JSON；无 Redis/Celery/database
- supervision：future bounded Website LaunchAgent/launchd，当前未安装
- exactly-once：N6 保持唯一 generation authority；reconcile 永远复用同一 exact text + stable request_id
- external projects：RonnieAutomation/Hermes 仅做 read-only reuse assessment；当前不选为 worker
- Pilot generation：未执行，authorization 未消耗
- side effects：无 TTS、无 WAV/MP3、无 runtime/code/external-project mutation、无 commit/push

Executor 已停止并交回：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`
