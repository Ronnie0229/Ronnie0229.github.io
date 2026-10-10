# Progress — Durable Workflow Controller

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| 长 TTS durable S4 job | PASS | Pilot 1/2 已证明 |
| Pilot 2 detached worker | PASS | 长运行后自然 TERMINAL_PASS |
| 调用者 session 解耦原则 | FROZEN | CodexPro/Hermes 不等待长 TTS |
| 5 分钟 tick cadence | FROZEN | 不采用 1–2 分钟 |
| start/status/tick contract | PASS | v0 已实现 |
| workflow durable JSON | PASS | real Pilot 2 workflow 已写入 runtime/workflows |
| terminal WAV artifact verify | PASS | real Pilot 2 tick 自动消费既有 S4 TERMINAL_PASS；SHA exact verify |
| technical QC | PASS | 24kHz/mono/pcm_f32le + full decode；Pilot 2 real pass |
| 64 kbps MP3 continuation | PASS | real Pilot 2 encoded/full decode/SHA recorded |
| human listening gate | PASS | controller 自动停在 WAIT_HUMAN_LISTENING，不允许自动 PASS |
| repair-support attach | PASS | v1 chunk map validator；Pilot 2 75 chunks attached |
| cleanup eligibility gate | PASS_IMPLEMENTED | 未满足 closure checks 时 NOT_ELIGIBLE |
| stale-owner auto reconcile | DEFERRED | 需单独严格验证 |
| NAS/R2/site continuation | PLANNED | human listening PASS 后再接同一 controller |
| Hermes autonomous operation | DESIGN_READY | 依赖 durable controller 完成 |
| 5-minute scheduler enable | NOT_STARTED | controller PASS 后单独启用 |
| Phase 4 business automation | DEFERRED | 不提前建设 |
