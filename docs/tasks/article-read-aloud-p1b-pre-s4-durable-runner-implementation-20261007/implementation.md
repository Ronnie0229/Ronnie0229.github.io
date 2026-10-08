# Implementation — P1B-pre S4 Durable Runner

日期：2026-10-07

正式 verdict：`PASS_S4_DURABLE_RUNNER_IMPLEMENTED / READY_FOR_INDEPENDENT_AUDIT`

## Implemented surface

- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`

实现保持 Website Owner-local、filesystem-spool、single-worker、short caller surface；未新增 web server、Redis、Celery、database、distributed queue 或 VOICE_AI async API。

CLI / function surface：
- submit
- status
- result
- reconcile
- worker-once

production root 常量精确冻结为 `/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`。本任务所有运行测试均通过 task-local temporary test root 注入；production root 没有创建。

## Identity / authorization claim

实现 exact descriptor schema `ronniecross-readaloud-generation-operation/v1` 与 frozen canonical JSON serialization。request_id 固定为 `rc-readaloud-v1:` + descriptor SHA-256。

submit 在任何 claim/runtime mutation 前先验证 supplied request_id 与 deterministic request_id 一致。authorization claim key 只由 authorization_ref + generation_epoch 决定，并通过 OS-level O_CREAT|O_EXCL 创建。

existing exact claim + exact descriptor/request_id 返回 existing logical job；identity drift/corrupt claim fail-closed。claim 不支持 delete/retry、TTL、lease takeover、timeout release、auto new epoch。

并发实现细节：O_EXCL pathname 会先于 claim body fsync 完成而可见，因此 exact duplicate caller 在 existing claim 暂时无法解析时只进行 bounded short wait，等待同一个 claim 完成；它从不删除、替换、接管或释放 claim。若 1 秒内仍不完整，保持 `AUTHORIZATION_CLAIM_CORRUPT` fail-closed。这保留 frozen crash invariant，并消除合法并发 duplicate 的瞬时误判。

## Durable job state

states：QUEUED / WAITING_PROVIDER_READY / CALL_IN_PROGRESS_OR_RESULT_UNKNOWN / TERMINAL_PASS / TERMINAL_BLOCKED / TERMINAL_FAIL_CLOSED。

JSON state 使用 temp file + fsync + atomic replace；runtime root/subdirs 0700，files 0600。job/claim 不持久化完整 TTS text。

Website job state 只表示 orchestration；provider generation truth 仍来自 VOICE_AI result/N6。

## Exact render binding

任何可能 provider POST 前均通过 descriptor-relative bounded path walk 读取 Render View：
- absolute path / `..` 拒绝；
- root 与每一级目录/leaf 使用 O_NOFOLLOW descriptor-relative open；
- leaf 必须 regular file；
- exact bytes 只读一次；
- exact SHA-256 必须匹配 frozen render_sha256；
- strict UTF-8 decode；
- 不 trim/normalize/rewrite；
- provider speech 直接使用刚验证的 text object；
- request_id 再次从 descriptor derive 并 exact compare。

任何 failure 均在 provider speech 之前进入 Website fail-closed，speech call count=0。

## Provider boundary

`HttpVoiceProvider` 只封装：
- GET `/ready`
- POST `/v1/speech` exact `{text,request_id}`
- GET opaque artifact_ref

本任务没有实例化该 adapter 去调用真实 `/v1/speech`。所有 execution/reconcile tests 使用 FakeProvider dependency injection。

## Reconcile / artifact

provider busy/not-ready 仅进入 WAITING_PROVIDER_READY；lost response 保持 CALL_IN_PROGRESS_OR_RESULT_UNKNOWN。reconcile 不生成新 request_id/epoch，复用同一 descriptor；若需要再次 POST，会重新执行 exact render gate。

terminal job 的 reconcile 是纯读取，不再调用 provider。

PASS artifact 先读取 fake provider bytes、校验 artifact_sha256，再 temp+fsync+atomic finalize 到 test artifact-cache；mismatch 不产生 verified cache。

## Verification chronology

1. 初次 runner 专项：18/19 PASS；唯一 FAIL 是 wrong supplied request_id 已 fail-closed，但 runtime subdirs 因 validate 顺序提前创建。实现最小调整：纯 identity validation 移到 ensure_runtime_root 前。
2. 修正后专项：19/19 PASS。
3. 首次全量 Python 回归：79/80 PASS；唯一 FAIL 暴露 O_EXCL claim pathname visibility race，exact duplicate caller 可能读取到尚未写完的同一 claim。
4. 最小修正：existing claim 仅 bounded wait for durable completion；不 release/takeover/delete。
5. 最终专项：19/19 PASS。
6. 最终全量 Python：80/80 PASS。

历史 FAIL chronology 保留，不被最终 PASS 覆盖。

## Side-effect boundary

- real Pilot claim/submit：NOT RUN
- real `/v1/speech`：NOT RUN
- production runtime root：NOT CREATED
- LaunchAgent：NOT INSTALLED
- WAV/MP3：NOT GENERATED
- VOICE_AI/RonnieAutomation/Hermes：NOT MODIFIED
- Website src/articles：NOT MODIFIED
- commit/push：NOT RUN