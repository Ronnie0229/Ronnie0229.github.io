# Result — P1B-pre Long-running TTS Architecture Redecision

状态：PASS_MINIMAL_ARCHITECTURE_SELECTED

选定最小架构为 Website Owner-local S4 durable consumer runner，而不是修改 VOICE_AI，也不是把当前 Pilot 强行接入 RonnieAutomation/Hermes。VOICE_AI Local HTTP V1 保持同步、loopback、exactly-once semantics 不变；Website S4 增加最薄 filesystem job spool、短时 submit/status/result/reconcile surface，以及未来由 macOS launchd 监督的 single worker。worker 才持有长时间同步 HTTP call，CodexPro/Hermes/future automation 都只作为短时 caller。

N6 继续是唯一 generation exactly-once authority。timeout、disconnect、worker restart 只允许同一 exact text + 同一 stable request_id reconcile；不得自动生成新 ID、清 state 或重新生成。

不引入 Redis/Celery/database、distributed queue、VOICE_AI async V2、Hermes-specific worker 或 RonnieAutomation TTS integration。

当前 Pilot exactly-one generation authorization 保持未消耗。本轮没有调用 TTS、没有生成音频、没有修改外部项目或 Website 业务代码，也没有 commit/push。

下一步只能由 Master Control 决定是否建立 Website Owner-local bounded S4 implementation task；本执行者在 architecture redecision 后停止。