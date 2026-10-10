# Article Read-Aloud Phase 2 — Repeatability Pilot 2

日期：2026-10-10
Owner：Website / 个人网页项目
LIFECYCLE：LONG_RUNNING_UNTIL_NEXT_REAL_AUTHORITY_BREAKPOINT

## Goal

完成原总计划 Phase 2 的最小重复性验证，不扩建架构：

- 在已完成 Pilot 1 的基础上增加 exactly one 第二篇真实文章，使 Pilot 总数达到 2；
- 复用现有 Render View / S4 runner / VOICE_AI_LOCAL_HTTP_V1 / 64 kbps delivery / RonnieArchive / R2 / native player；
- 做机械 QC、归档、R2、frontmatter binding、build/production verification；
- 完成可由当前执行环境真实验证的 Desktop/HTTP/Range 项；
- iPhone/Safari 的真实设备播放不得伪造；若无法由当前环境验证，停在唯一 human/device breakpoint。

## User authorization

PROJECT_OWNER 当前明确指令：`继续推进并完成`。

该指令是在 Phase 1D 已闭合、下一步被明确陈述为“Phase 2：再做 1–2 篇真实文章，把总 Pilot 数做到 2–3 篇，并完成正式的 Desktop / iPhone / Safari / Chrome 播放验证”后给出。

本任务将其绑定为：

- authorization_ref=`article-read-aloud-phase2-repeatability-user-authorization-20261010-a1`
- generation_epoch=`phase2-pilot2-20261010-a1`
- exactly one new Pilot 2 generation
- article_id=`post-fa05168ade9ea9b8`

不授权第三篇、批量生成、通用自动化或 Phase 4。

## 2026-10-10 Architecture correction — durable workflow foundation

PROJECT_OWNER 明确要求同时考虑：
- 超长 TTS 完成后应能自动识别并继续后续作业；
- 当前 CodexPro 单次命令时限不应成为正确性前提；
- 最终整套作业要可交给 Hermes 本地模型独立完成；
- 本地薄触发层 cadence 冻结为每 5 分钟一次，不采用 1–2 分钟。

因此本任务允许在不扩建业务自动化的前提下增加最小 durable workflow controller。它只负责 `start/status/tick`、持久状态和长 TTS 完成检测；真正自动批量/无人审核发布仍属于 Phase 4。

## Pilot 2 selection

Source:
`src/content/posts/2026-08-06-camel-through-eye-of-needle.md`

Identity:
- articleId=`post-fa05168ade9ea9b8`
- title=`骆驼穿过针眼是什么意思`
- date=`2026-08-06`
- scripture=`马太福音 19:23-26`
- source SHA-256=`5e635131fb5f892fdf662256cb5907fae154111493f78aa7bccb284c3d7581dc`

Why:
- already-published real article;
- moderate length;
- no existing audioUrl;
- title itself is spoken-natural rather than a numeric scripture title;
- representative normal article, while remaining small enough for repeatability validation.

## Render View

`tts-readaloud.txt`

- title preserved exactly;
- frontmatter main scripture normalized only to `马太福音19章23节到26节`;
- body wording/order preserved;
- Markdown heading / blockquote presentation markers removed, content retained;
- no body scripture retranslation or replacement.

Frozen render:
- SHA-256=`5c92d640795b98840c7bf62ee4e6c488727127997750da22caa28cb8988574b7`
- bytes=7124

## Allowed side effects in this task

Bounded to Pilot 2:
- submit exactly one S4 job;
- invoke existing one-shot worker exactly as needed for that job;
- same-id reconcile/operator resolution only if required by existing S4 semantics and supported by authoritative provider evidence;
- retrieve/verify WAV;
- create 64 kbps MP3;
- append-only archive under `/Volumes/home/RonnieArchive/ReadAloud/articles`;
- upload exactly Pilot 2 MP3 to existing R2 bucket/path pattern;
- bind Pilot 2 article audioUrl;
- run tests/build;
- production publication/deploy necessary to make Pilot 2 live;
- update task/status/plan evidence;
- implement and mechanically verify the minimal durable workflow controller foundation needed to decouple long TTS from CodexPro/Hermes session lifetime.

## Not allowed

- new daemon/scheduler/runtime framework beyond the approved minimal durable controller; actual 5-minute scheduler installation/enablement remains a separate activation step;
- batch/backfill;
- third Pilot generation;
- generalized pronunciation engine;
- auto-regeneration after audible QC issues;
- changing VOICE_AI model/voice;
- changing article body for TTS convenience;
- pretending iPhone/Safari real-device verification passed when it has not.

## Current execution state — 2026-10-10

- Pilot 2 S4 job=`2acf76da2669d766c4d8fb651533267af7dc7e3876be0e2c9f053194557eb523`
- TTS=`TERMINAL_PASS`
- artifact SHA=`551db6adb34d478dd40d13cdd34fe826121d42523121a63a8f5c059b6b2a2ca6`
- durable workflow controller v0=`PASS`
- human listening disposition=`PROVISIONAL_PROJECT_OWNER_PASS_NO_FULL_LISTENING`；PROJECT_OWNER 允许先发布并以后续真实 repair path 验证可修复性
- technical QC + 64 kbps MP3 continuation=`PASS`
- Pilot 2 MP3 SHA=`386ebaba9d467e3c9c15a7ce361e394a79809b96f3fcb67940c94cc02e22ff3c`
- current real breakpoint=`HUMAN_LISTENING`
- 5-minute scheduler cadence frozen but not yet enabled.
- repair-support v1 attached：75 acoustic chunks / 14542080 total frames；exact text↔chunk alignment NOT_AVAILABLE。
- cleanup gate implemented；Pilot 2 current cleanup=`NOT_ELIGIBLE` until human/NAS/R2/live closure。

## Stop condition

PASS:
`PASS_PHASE2_REPEATABILITY_PILOT2_MACHINE_SCOPE / READY_FOR_FINAL_HUMAN_DEVICE_ACCEPTANCE`

or, if all required real-device acceptance is actually available and passes:

`PASS_PHASE2_REPEATABILITY_COMPLETE / READY_FOR_PHASE3_FORMALIZATION`

BLOCKED:
preserve exact failure chronology and do not expand scope.
