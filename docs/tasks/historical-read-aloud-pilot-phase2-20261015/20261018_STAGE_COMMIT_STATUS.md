# 历史文章有声阅读阶段归档｜2026-10-18

本文件为截至 2026-10-18 的事实快照，保留此前 Phase 0/0.5/1/Pilot 的原始 FAIL/BLOCKED/PASS 记录，不覆盖其时间序列。今天仅归档文档，不生产新音频、不改网站文章、不触发通知。

## 已发生的生产发布

- 第一篇 `post-d6033867e9b33cc1`：《以利亚与撒勒法寡妇：信靠神的供应》，音频绑定已在 `775d4a430fe4573430619b6a37f7359eb506b92d` 独立 commit/push；其上一轮网站部署和播放器已在第二篇启动前验证。
- 第二篇 `post-0d153ce310d0eebd`：《在基督里死了的人必先复活是什么意思》，音频绑定已在 `7ebd1c87e538011bebea04793208c1f36b6c7f97` 独立 commit/push；生产时通过 WAV/MP3 QC、NAS WAV、R2 对象及正式 URL 验证。
- 当前 Git HEAD 为 `7ebd1c87e538011bebea04793208c1f36b6c7f97`；当前最新 website-publication receipt 是第二篇 `PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY`。这不是部署失败：下一次网站正式发布前必须 fresh 检查部署 commit、页面播放器、MP3 SHA/Range 206，满足条件再将 receipt 设为 VERIFIED。
- S4 workflow 文件仍显示 `AUDIO_READY_PENDING_PUBLICATION_GATE`；该生成工作流状态没有同步代表后续独立发布步骤。因此不能用此字段否定两篇 Git 发布，也不能凭 Git 发布推断已通过今天的线上部署核验。

## 后续处理范围

- 首批五篇 Pilot 已生成并推送前两篇的 `audioUrl`，第三至第五篇尚无本阶段生产发布证据。后续逐篇开展，用户采用技术 QC 后发布、线上试听；不得把 human listening 写为 PASS。
- 先前因 NAS 归档远端超时、R2 正式 URL 暂时 404 的 BLOCKED 状态属真实发生过的历史事件；后续分别获得 NAS verified 和 R2 正式 URL 可用证据，但不删旧记录。
- 早期要求原文/E1/reviewed 的资格结论不构成历史文章 TTS-only 硬门，以 Phase 1 TTS-only 重新盘点为准。
- `docs/tasks/share-article-tts-end-to-end-20261013/` 与现有 `docs/tasks/current.md` dirty 归属另一复盘事项，本次不纳入 Git 暂存或提交；不能为清理工作树而丢弃。
