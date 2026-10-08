# Activation Checklist — Exactly One Controlled Article Pilot

此清单仅供**未来获得明确真实授权后**执行。本 S5 未执行任何 production activation/Pilot generation。

## Authorization gates

在执行真实动作前必须同时区分并确认：
1. minimal Website activation authorization；
2. exactly one frozen Pilot generation authorization；
3. commit/push authorization（若未来需要，与本 Pilot generation分开）；
4. deploy/publication authorization（当前不包含）。

## Minimal authorized sequence

1. Fresh verify 当前 code/task authority，确认 S4/S5测试仍通过。
2. 确认 Pilot descriptor/article/render SHA/request_id仍是冻结对象，authorization仍 `UNCLAIMED / NOT_CONSUMED`。
3. 检查 frozen production root：
   `/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`
   - 若不存在，只能在已获 activation authorization 后由现有 runner创建；
   - root/subdirs预期0700、files 0600。
4. 在**尚未 submit Pilot**时可先做一次 idle one-shot activation验证：
   ```text
   cd /Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007
   python3 scripts/read_aloud_s4_runner.py worker-once
   ```
   预期：无 job时输出 `null`，不得发生 provider POST。
5. 明确确认 exactly-one Pilot generation authorization后，才允许用冻结 descriptor执行 submit；不得生成新 request_id/generation epoch。
6. 只执行一次：
   ```text
   python3 scripts/read_aloud_s4_runner.py worker-once
   ```
7. 使用 `status` / `result` 读取 bounded durable evidence。
8. 若 terminal：停止，不再次 POST。
9. 若 `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`：不要创建新 request_id，不自动清 owner；只按现有 same-id reconcile contract处理。
10. 若 execution owner存在/看似 stale：不要 PID/TTL reclaim；停止并按 operator/manual authority处理。
11. 检查 stdout/durable state不得包含 full TTS text。
12. one-shot返回后即视为 Website worker已停止；不要再启动下一轮 invocation，保留 jobs/claims/execution owner/evidence。
13. 然后才进入 WAV QC / MP3对比 /人工听感等 Pilot业务验收；不自动建设长期平台。

## Pilot-first stop

第一篇真实可播放文章完成前，不建设 feed/highlight/general queue/platform。
