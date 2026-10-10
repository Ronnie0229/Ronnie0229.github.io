# Result — Durable Workflow Controller v0

日期：2026-10-10

## Verdict

`PASS_DURABLE_WORKFLOW_CONTROLLER_V0 / LONG_TTS_SESSION_DECOUPLING_MECHANICALLY_VERIFIED`

## Implementation

新增：
- `scripts/read_aloud_workflow.py`
- `scripts/tests/test_read_aloud_workflow.py`

接口：
- `start`
- `status`
- `tick`
- `tick-all`（供未来 5 分钟薄触发层调用）

durable workflow root：
`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/workflows`

## Mechanical verification

- initial v0 workflow tests：6/6 PASS（后续同 scope 扩展后 current=8/8 PASS）
- existing S4/S5/player regression：63/63 PASS
- py_compile：PASS
- no daemon/scheduler installed
- no new TTS generation caused by controller verification

## Real Pilot 2 readback

使用现有 Pilot 2 exact descriptor 建立 workflow：
`2acf76da2669d766c4d8fb651533267af7dc7e3876be0e2c9f053194557eb523`

S4 在 controller 接入前已经：
`TERMINAL_PASS`

controller `tick` 没有重跑 TTS，而是：
1. idempotent read/reuse exact S4 job；
2. 读取 terminal artifact；
3. 回读 cache bytes；
4. SHA-256 exact verify；
5. workflow 自动推进到 `WAV_VERIFIED`。

verified artifact：
- SHA-256：`551db6adb34d478dd40d13cdd34fe826121d42523121a63a8f5c059b6b2a2ca6`
- bytes：`58168400`
- execution owner：ABSENT
- S4 status：仍为 `TERMINAL_PASS`
- request_id：未改变
- 没有第二 generation。

## Same-scope continuation — technical QC to human gate

在 v0 long-TTS session decoupling PASS 后，同一个 Executor 按原 bounded write-set 继续接入：

```text
WAV_VERIFIED
→ technical QC
→ full WAV decode
→ 64 kbps MP3 encode
→ full MP3 decode
→ metadata/SHA persist
→ WAIT_HUMAN_LISTENING
```

新增 workflow test 后：
- workflow tests：8/8 PASS
- existing S4/S5/player regression：63/63 PASS
- py_compile：PASS

Pilot 2 real continuation：
- WAV：24 kHz / mono / pcm_f32le / full decode PASS
- WAV duration：605.92 sec
- MP3：64 kbps / 24 kHz / mono / full decode PASS
- MP3 duration：605.92 sec
- MP3 bytes：4848045
- MP3 SHA-256：`386ebaba9d467e3c9c15a7ce361e394a79809b96f3fcb67940c94cc02e22ff3c`
- MP3 absolute path：`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/delivery-cache/2acf76da2669d766c4d8fb651533267af7dc7e3876be0e2c9f053194557eb523/article-64k.mp3`

当时 workflow 首先正确停在 `WAIT_HUMAN_LISTENING`，证明 controller 能在 TTS 完成后的下一次短 tick 自动推进到真实人工断点。随后 PROJECT_OWNER 明确给出 `PROVISIONAL_PROJECT_OWNER_PASS_NO_FULL_LISTENING`，允许本 Pilot 继续完成 archive/R2/Website/live closure，并保留以后发现问题时真实执行局部修复的权利。

最终 Pilot 2 durable workflow=`COMPLETE`；NAS/R2/live/repair-support 全部验证后 cleanup gate=`CLEANUP_ELIGIBLE`，对应 DevSSD 大媒体缓存已按 exact scope 删除。

## 5-minute trigger

cadence 已冻结为每 5 分钟一次，并已在后续 activation slice 启用 LaunchAgent `com.ronniecross.read-aloud.tick`。

当前正式行为仍然只是薄触发：
`every 300s → tick-all → exit`。

Activation chronology：初版 direct-Python + external-volume WorkingDirectory/log paths 被 launchd 以 `EX_CONFIG(78)` 拒绝；未执行 workflow mutation。改为 `/bin/zsh -lc` 负责 `cd/exec`、日志移至 `~/Library/Logs/RonnieCross/` 后，launchd readback=`run interval 300 seconds`，controlled kickstart=`last exit code 0`，stdout=`[]`，stderr empty。

## Hermes disposition

Hermes future operator 不需要保持长时间命令，也不需要从聊天记忆推断进度。它只读取 durable `status`，在 `automatic_action_available=true` 时调用 `tick`，在人类/操作员 Gate 时停止。

## Next

Pilot 2 controller core path is proven through production/live closure and cleanup, and the approved thin 5-minute `tick-all` LaunchAgent is now active. Real-device iPhone/Safari/Chrome acceptance remains separate and must not be fabricated.
