# Article Read-Aloud — Local Asset Cleanup Gate + Repair Support

日期：2026-10-10
Owner：Website / 个人网页项目
状态：PASS_FOUNDATION / PILOT2_WAIT_HUMAN_LISTENING

## Goal

把 PROJECT_OWNER 已批准的三条规则正式落地：

1. 工作树 `artifacts/read-aloud/` 只作为当前人工试听/局部修复工作区，不承担长期资产保存；
2. 正式 WAV 已归档 NAS、MP3 已进入 R2、Website/live 验证完成且 repair-support metadata 完整后，DevSSD 上 WAV/MP3 大文件进入 `CLEANUP_ELIGIBLE` 并删除；
3. 长期保存 repair-support metadata，优先保存 acoustic chunk map，使后续发现单句发音错误时可从 NAS authoritative WAV master 恢复并做局部修复，而不是重新生成整篇。

## Storage roles after this correction

```text
active worktree/artifacts/read-aloud
= human listening + temporary repair workspace

runtime/read-aloud
= durable job/workflow state + temporary provider/delivery cache

/Volumes/home/RonnieArchive/ReadAloud
= authoritative long-term WAV master + manifest + repair-support metadata

Cloudflare R2
= authoritative Website delivery MP3
```

## Cleanup Gate

只有同时满足以下条件才允许删除 DevSSD WAV/MP3：

- human listening PASS；
- final WAV 已写入 NAS formal archive；
- NAS readback SHA/bytes exact PASS；
- final MP3 已写入 R2；
- R2 full readback SHA/bytes exact PASS；
- HTTP Range/Content-Type PASS；
- Website audio binding/build/deploy/live verify PASS；
- repair-support metadata 已形成并随正式归档长期保留；
- 当前没有未完成 pronunciation/chunk repair；
- workflow 明确标记 `CLEANUP_ELIGIBLE`。

删除范围只包括可恢复的大媒体临时副本：
- worktree WAV/MP3；
- runtime artifact-cache/delivery-cache 中对应 workflow 的 WAV/MP3。

不得随 cleanup 删除：
- jobs/claims/workflows JSON；
- task/evidence；
- Render View；
- repair-support metadata；
- NAS master/manifest；
- R2 delivery。

## Repair after cleanup

```text
NAS authoritative WAV master
→ 临时恢复到 DevSSD
→ 根据时间点/chunk map 定位 chunk
→ 只重新生成目标片段
→ splice/rebuild final WAV
→ 人工检查目标片段 + 前后接缝
→ 新 WAV 写回 NAS（保留版本/repair chronology）
→ 从新 WAV 重编码 MP3
→ 原 R2 object key 原位替换
→ remote SHA/Range verify
→ 再次 CLEANUP_ELIGIBLE
```

不得因为本地缓存已删除而自动重新生成整篇 TTS。

## Chunk map boundary

当前 VOICE_AI receipt 提供每个 acoustic chunk 的 frame count/QC，但 public HTTP contract 不提供 exact text-to-chunk alignment。

因此 Website 当前长期保存：
- chunk_index；
- start_frame/end_frame；
- start_sec/end_sec；
- chunk frames；
- provider run/request/render identity；
- final WAV SHA；
- model/voice/speed identity；
- provider QC finding。

这足以按“用户听到的时间点 → exact acoustic chunk”定位后续局部修复。

不得伪称存在 exact phrase↔chunk 对齐。若未来需要全自动按文本定位 chunk，应由 VOICE_AI 正式接口提供受控 alignment evidence，而不是 Website 复制/猜测 provider segmentation。

## Pilot 2

当前 Pilot 2 仍为 `WAIT_HUMAN_LISTENING`，因此：
- cleanup_status=`NOT_ELIGIBLE`
- 不删除任何当前 WAV/MP3；
- 已从 VOICE_AI current receipt 只读提取 75 个 acoustic chunk 的 frame evidence，形成 task-local repair-support candidate；
- 人工 PASS 后继续 NAS/R2/site closure，再由 cleanup gate 裁决。
