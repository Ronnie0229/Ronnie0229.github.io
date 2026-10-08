# Article Read-Aloud P1B-pre — Long-running TTS Execution Architecture Redecision

状态：PASS_MINIMAL_ARCHITECTURE_SELECTED / RETURN_TO_MASTER_CONTROL
日期：2026-10-07
Owner：Website / 个人网页项目
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Trigger / chronology

1. Phase 1A 已闭合并 push：`359ebc3ccd9fb48ad9caa2a0f00a08545ec95173`。
2. 用户随后授权 frozen Pilot exactly one VOICE_AI generation。
3. Master 建立过直接同步 P1B draft，但用户在执行前指出 CodexPro 有执行时间上限，长 TTS 不应绑定 CodexPro 单次调用。
4. 用户明确确认：旧 P1B 提示词没有执行。
5. 因此：`GENERATION_AUTHORIZATION_NOT_CONSUMED`；没有 POST、没有 WAV、没有未知 generation。
6. 用户批准重新分发任务，先解决长期无人值守执行路径。

## Problem

当前 `VOICE_AI_LOCAL_HTTP_V1 POST /v1/speech` 为同步长请求。VOICE_AI daemon 本身长期运行，但 consumer HTTP call 生命周期仍与长 generation 绑定。CodexPro/tool timeout、会话断开或 shell 生命周期会造成结果不确定；让用户每次经 Telegram/Hermes 人工启动又不能满足未来自动化目标。

正式 blocker：
`LONG_RUNNING_TTS_CALLER_LIFECYCLE_COUPLING`

## Goal

只做 architecture/authority redecision，确定最小、长期可复用、可无人值守的 long-running TTS submission/execution/status/retrieval 边界。

必须回答：

1. 该能力应属于 Website Owner 的 S4 consumer adapter/orchestration，还是 VOICE_AI 通用 contract/runtime，或已有 RonnieAutomation/Hermes 能力可直接复用。
2. 是否能在不改变 `VOICE_AI_LOCAL_HTTP_V1` frozen semantics 的前提下，以 consumer-side detached worker/job record 解耦 caller lifetime。
3. 最小 V1 contract：submit/status/result/reconcile；stable request_id；exactly-once；crash/restart；busy；artifact retrieval；privacy。
4. 进程监督应复用 macOS launchd、现有 durable runner 或其它已有正式能力；不得因“异步”默认引入 Redis/Celery/database。
5. CodexPro、Hermes Telegram、未来 Website automation 分别如何成为 caller，而不成为 worker lifecycle owner。
6. 当前 exactly-one Pilot 如何在新架构下执行，并证明一次授权只产生一个 generation identity。
7. 哪些能力现在不需要建设，明确 overbuilding exclusions。

## Mandatory fresh-read

Website:
- `AGENTS.md`
- `docs/tasks/article-read-aloud-construction-plan-20261007.md`
- P1A closure package
- 本 task

VOICE_AI（只读）：
- `/Volumes/DevSSD/RonnieWork/语音模型/AGENTS.md`
- `START_HERE.md`
- `VOICE_AI_CURRENT_MASTER_PLAN.md`
- `PROJECT_STATUS.md`
- S1 HTTP V1 current contract
- S2 daemon current closure/architecture
- 与 S3/S4 consumer integration 相关的 current frozen design

如判断 RonnieAutomation/Hermes 有可复用执行能力，只允许 read-only fresh-read 其 current authority/接口证据；不得修改外部项目。

## Decision principles

- 优先复用，最小新增。
- Website business orchestration 不得侵入 VOICE_AI Owner。
- VOICE_AI 不得接管 Website article/storage/publish logic。
- 不为了一个 Pilot 建通用 distributed job platform。
- 不允许依赖 CodexPro 长时间保持连接。
- 不允许要求用户长期手工通过 Telegram/Hermes 执行。
- Hermes 可以是 caller/observer，不应成为唯一 worker。
- exactly-once identity 必须继续由 frozen request_id 语义约束。
- 如果 consumer-side detached process 无法安全满足 crash/reconcile，则必须明确指出，不得用 `nohup &` 冒充 durable architecture。

## Deliverables

仅写：
- `docs/tasks/article-read-aloud-p1b-pre-async-redecision-20261007/decision.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`
- 必要时更新 `docs/tasks/current.md`

不得写实现代码。

## Forbidden

- 不得 POST `/v1/speech`
- 不得生成 WAV/MP3
- 不得修改 VOICE_AI
- 不得修改 RonnieAutomation/Hermes
- 不得修改 Website src/文章
- 不得 install daemon/LaunchAgent
- 不得 R2/NAS/deploy
- 不得 commit/push
- 不得进入 implementation
- 不得消耗用户 exactly-one generation authorization

## Stop

给出一个明确 verdict：
- `PASS_MINIMAL_ARCHITECTURE_SELECTED`
或
- `BLOCKED_NEEDS_OWNER_REDECISION`

然后停止并交回 Master Control。
