# 历史文章 TTS Phase 2 — 首批五篇 Pilot 启动与单篇交接

状态：**PHASE2_APPROVED / FIRST_ARTICLE_READY_FOR_SINGLE_TELEGRAM_EXECUTION / TTS_NOT_YET_DISPATCHED**。

- 本次用户明确批准首批五篇历史文章 TTS Pilot。与历史全量 backfill 分开；不得自动触发 299 篇，五篇逐篇执行、QC、NAS/R2、网站绑定。
- 正式工作区：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`；本轮 fresh-read AGENTS、PROJECT_DECISIONS、STATUS、docs/tasks/current.md、统一内容整理与发布流程，以及 Phase 1 TTS-only 报告。
- 既有原封不动 dirty 文档保留；当前网站 Git HEAD：`67a68298a21c05ab27befd2b39c2a722a67bd851`。上一轮正式音频 release receipt `VERIFIED`。
- **本轮只完成第一篇生成任务的冻结和脚本准备，尚未运行合成、NAS/R2、网站 Git 发布。**
- 生产顺序：① Ronnie《以利亚与撒勒法寡妇：信靠神的供应》；② Ronnie《在基督里死了的人必先复活是什么意思》；③ Akira《信仰的殿堂：挪亚》；④ Grayson《信仰的殿堂：雅各》；⑤ Nathan《没有道路时的信心》。
- 五篇只执行 TTS-only；原英文、E1、reviewed 标记不在 TTS 资格门范围。每一篇仍需检验真实音质和音频生成证据。
- 第一篇 Article ID `post-d6033867e9b33cc1`；文章路径 `src/content/posts/2026-07-12-列王纪上-17-1-24-以利亚与撒勒法寡妇-信靠神的供应.md`。
- 第一篇 post SHA `3e89df59c2812ccc129c3954b2ed6fa802083b722a60e6c315279ad4df977c73`；render SHA `d736091f42749fd37c5563f9163895e60934819e22d4d01aa41915fff0a5f144`；Render View 2160 字。
- TTS 唯一 workflow ID `8d9ecd9bd27beb7316d5f5bdfbfae7de8b10f7a44d6c1708e1916928643e8571`；preflight PASS、provider READY；正式启动必须由用户在 Telegram 调用。
- 精确脚本：`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/historical-pilot/post-d6033867e9b33cc1/run_tts_once.py`；SHA-256 `2af7f0a01c82dbaa9c4c5e1c95045fd1ec6ea7e79fe212aa130c02151122a521`。脚本只负责单篇 TTS、S4 WAV 和 durable 证据，不执行媒体发布。
- Telegram 原样执行：`/expy` 换行后 `python3 /Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/historical-pilot/post-d6033867e9b33cc1/run_tts_once.py`。一次性执行 `invocation_count=1`，不得重跑；长时间运行由原执行 ID 使用 `/exst` 查询。
- 完成后提供 Telegram machine 终态、script SHA、result 与 S4 artifact；RonnieCross 先核对 WAV SHA 和 MP3 解码，增加 Pilot 人工试听/啸音检查，然后按现有 NAS append-only/R2 exact-object/前次发布核验/单篇 audioUrl 网站发布合同交付。每篇完成再开始下一篇。
- 失败保持 FAIL/BLOCKED 原状并只读恢复，不自动重试 TTS、不重传已有媒体、不覆盖已完成工件。
