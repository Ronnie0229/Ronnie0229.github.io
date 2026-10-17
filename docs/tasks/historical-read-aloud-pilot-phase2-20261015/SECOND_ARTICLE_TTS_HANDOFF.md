# Phase 2 第二篇历史文章 TTS 接力（2026-10-15）

## 已证实

- 用户授权继续第二篇生产及发布；明确采用技术 QC 后发布、用户线上试听的方式。
- 正式工作区：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`；已 fresh-read authority。
- 第一篇发布 `775d4a430fe4573430619b6a37f7359eb506b92d`，远端 Git、Cloudflare deployment、正式页面播放器身份、R2 SHA/Range 均证实通过；最后发布回执已写回 `VERIFIED`。
- 第二篇：《帖撒罗尼迦前书 4:16｜在基督里死了的人必先复活是什么意思》，文章 ID `post-0d153ce310d0eebd`。
- 第二篇当前 Git HEAD/source commit：`775d4a430fe4573430619b6a37f7359eb506b92d`。
- Render View SHA：`46523a1a5027e4b7a7792b20b30bf37d44b697ecd050464e6eeedb7074a1ab6c`；朗读文本 2178 字符。
- once-only workflow ID：`d6cd8c16f63a327ae20f7b58ac1baab1b8de2ca467ff54ca5e92f474067458f9`。
- 一次性脚本：`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/historical-pilot/post-0d153ce310d0eebd/run_tts_once.py`。
- 脚本 SHA256：`96d0e4e63487803130ecfdb45025f1e9634868486902bedf48c1f00c317147d6`。
- 脚本的 read-only preflight PASS，VOICE_AI provider READY；**尚未发起第二篇 TTS**。

## 下一个执行入口

发送到 Hermes Telegram：

```text
/expy
python3 /Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/historical-pilot/post-0d153ce310d0eebd/run_tts_once.py
```

一次性执行 `invocation_count=1`，失败也禁止盲重试；使用 Telegram 机器执行回执判断终态。

## 后续完成条件

回读 WAV 与 S4 request ID、MP3 解码/时长及基础声学 QC（人耳试听延期到线上）；NAS append-only WAV 与 manifest、R2 exact-object MP3 的远端 SHA 和正式 URL/Range 206；只向该文章增加 `audioUrl`，构建并 Git commit/push（明确授权已取得），网站发布回执写入 `PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY`，不发送订阅邮件。保留其他既有未提交文档不夹带到 commit。不得预先宣称已发布。
