# RonnieCross 网站有声阅读建设计划

版本：2026-10-07
Owner：Website / `个人网页项目`
当前阶段：Phase 1D CLOSED / Phase 2 in progress
状态：Pilot 1 已完成真实 TTS、人工 QC、R2、Website Player、production 上线与 NAS archival lifecycle；Phase 2 还需把真实 Pilot 扩到总计 2–3 篇并完成计划内 multi-device/browser validation。

## 1. 目标与原则

为 RonnieCross 文章增加可选“有声阅读”能力。文章阅读仍是主体验；有音频才显示播放器，无音频保持现状。音频失败不得阻塞文章正常发布。

不建设独立播客平台，不为了有声阅读重构网站，不把 TTS/音频变成文章发布 hard gate。

最终目标链路：

```text
正式文章
→ TTS Render View
→ TTS-ready 纯文本
→ VOICE_AI_LOCAL_HTTP_V1
→ WAV master
→ 音频 QC
→ FFmpeg delivery encoding
→ MP3
→ Cloudflare R2
→ article audio metadata
→ 网站播放器
```

## 2. 项目归属与工作树

有声阅读**不是 RonnieCross 根下第四个并列业务 Owner/子项目**。

RonnieCross 根当前三个业务 Owner 保持不变：

- `个人网页项目/`：Website Owner
- `讲道整理/`：Sermon Owner
- `本地讲章翻译增强项目/`：Translation Owner

有声阅读的播放器、article audio schema、Website TTS Render View consumer、音频 delivery metadata、R2 网站交付均属于 Website Owner，因此 authority 留在 `个人网页项目`。

正式建设时按 `PUBLICATION_FAST_LANE + CONSTRUCTION_ISOLATION`：

```text
个人网页项目 canonical main
→ fresh-read Website authority
→ lane_class=construction
→ 建立正式 bounded task
→ 创建 task branch
→ 创建 Owner-local bounded-stage worktree
→ 在独立 worktree 建设/验证
→ stage closure 后 audit/integrate/retire
```

不要在 RonnieCross root 新建 `有声阅读项目/` 作为第四 Owner，也不要长期占用 Website canonical tree。长期工程按 bounded stage 使用连续 worktree，不维护永久 dirty worktree。

## 3. 启动任务前 Preflight / Closure Gate

在创建第一个有声阅读 task/worktree 前，必须做一次 fresh preflight：

1. fresh-read Website `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`、`docs/branch-workflow.md`。
2. 确认 canonical root 精确为 `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`。
3. 确认 `main` 与 `origin/main` 同步、working tree clean。
4. 盘点 active/in-flight Website tasks；不得机械恢复历史 task 目录。
5. 盘点现存 worktree/branch，确认没有与本 stage 冲突的 active construction lane。
6. 运行 root/Owner 规定的 worktree lane mechanical check，留下 `lane_class=construction` evidence。
7. 检查 current-doc 与 repository truth 是否存在会影响本任务的 drift；非阻塞历史 chronology 不为了“清零”而过度整改。
8. 对标最终目标，记录 `GOAL_ALIGNED / NO_SCOPE_DRIFT / NO_OVERBUILDING`。
9. 冻结本 stage baseline HEAD、branch、允许 write-set 和停止条件。
10. 完成后才允许登记 ACTIVE construction task 并创建 bounded-stage worktree。

当前 2026-10-07 预盘点已确认 Website canonical `main == origin/main`、working tree clean，HEAD=`bb483c2`。这说明没有必须先清理的 Website dirty code。正式 task 启动时仍须重新 fresh-check，不把本次预盘点当未来永久证明。

## 4. VOICE_AI Consumer Contract

Website 只依赖：

```text
VOICE_AI_LOCAL_HTTP_V1
base=http://127.0.0.1:8765

GET  /ready
POST /v1/speech
GET  /v1/artifacts/{artifact_ref}
```

请求体严格为：

```json
{
  "text": "真正需要朗读的纯文本",
  "request_id": "稳定请求ID"
}
```

Website 不直接依赖 CosyVoice3、Python 内部 API、模型目录、reference WAV、VOICE_AI outputs 路径、PyTorch/MPS 或内部 receipt 路径。

### request_id

```text
一个明确文章版本的 TTS 操作
↔ 一个稳定 request_id
↔ 一份确定的 TTS-ready text
```

相同 `request_id + same text` 用于 replay/reconcile。发生 timeout 时不得换新 ID 重跑；必须保留同一 request_id 与同一 text。

当前 VOICE_AI generation concurrency=1；Website Pilot 串行调用，不假设服务端有 queue。

## 5. TTS Render View

禁止直接把 Markdown 原文提交 VOICE_AI。

```text
正式文章 Markdown
→ Website TTS Render View
→ tts-readaloud.txt
→ 人工/机械检查
→ VOICE_AI
```

原则上朗读：标题、经文、简介、正文、小标题、引用、祷告、讨论/反思、祝祷、正文结束经文。

原则上不朗读：导航、返回列表、阅读/留言计数、Tags、订阅提示、评论、URL、Markdown 控制字符、技术 metadata。

经文朗读必须由 RonnieCross / Project Bible 受控规则展开，例如：

```text
罗马书 1:15-18
→ 罗马书1章15节到18节
```

不能让 VOICE_AI 自由猜测经文缩写或重新翻译受控经文。

## 6. 长文章策略

VOICE_AI 当前整体输入硬上限为 262,144 UTF-8 bytes，中文 sentence policy 为 `ZH_SENTENCE_END_ONLY`，当前验证句级阈值 165 tokens。

已验证十几分钟级长篇生成，因此不采用“每 500 字固定切块”等粗暴拆分。Website 负责清理网页/Markdown、保留自然中文标点并避免异常无标点超长句；句级处理由 VOICE_AI frozen frontend 负责。

## 7. Voice 与生成参数

Website public consumer 只控制：

```text
text
request_id
```

不控制 voice/speaker/speed/temperature/seed/emotion/style/language/pause/model/output format/output path。Pilot 使用 VOICE_AI 当前冻结默认 voice。

## 8. WAV Master

VOICE_AI 当前返回媒体：

```text
WAV
24 kHz
mono
float32
```

下载后必须验证：

```text
downloaded WAV SHA-256 == artifact_sha256
```

验证通过后才成为 WAV master。

Delivery 编码需要重做时从同一 WAV master 重新编码，不因 MP3 参数变化重新执行 TTS。

## 9. WAV → MP3 与 QC

使用 FFmpeg。

64 kbps Pilot：

```shell
ffmpeg -i article-master.wav -ac 1 -ar 24000 -c:a libmp3lame -b:a 64k article-64k.mp3
```

96 kbps Pilot：

```shell
ffmpeg -i article-master.wav -ac 1 -ar 24000 -c:a libmp3lame -b:a 96k article-96k.mp3
```

不把 24 kHz 源无意义升采样到 44.1/48 kHz。

使用 FFprobe 检查 codec、sample_rate、channels、bitrate、duration、file_size。

人工 A/B 至少覆盖手机扬声器、耳机、Desktop，检查清晰度、齿音、高频损失、呼吸声、经文/专名发音、停顿和长时间听感。

若 64/96 kbps 无稳定可感知差异，优先 64 kbps；若 96 kbps 有明确提升，则采用 96 kbps。

## 10. Pilot 作业区

工作树中的临时作业区：

```text
tmp/
└── article-read-aloud/
    └── <article-id-or-slug>/
        ├── 00_source/
        ├── 10_render/
        ├── 20_tts/
        ├── 30_master/
        ├── 40_delivery/
        ├── 50_qc/
        └── 90_logs/
```

职责：

- `00_source/`：文章输入快照、source metadata/SHA。
- `10_render/`：`tts-readaloud.txt`、文本 SHA、render report。
- `20_tts/`：request/response、request_id、run_id、artifact_ref、artifact_sha256、receipt_ref。
- `30_master/`：已验证 WAV master。
- `40_delivery/`：64k/96k MP3 与 delivery report。
- `50_qc/`：technical QC、listening review、final selection。
- `90_logs/`：TTS/FFmpeg/FFprobe 诊断日志。

`tmp/` 仍是可清理、不提交 Git 的本地作业区；真正需要长期保留的治理证据应进入 task/evidence 文档，而不是依赖 tmp。

工作树 `artifacts/read-aloud/` 的职责冻结为**当前人工试听与局部修复工作区**，不是长期媒体库。正式 closure 后，满足 Cleanup Gate 的 WAV/MP3 应从 DevSSD 删除，避免长期占用 SSD 空间；需要后续修音时从 NAS authoritative WAV master 临时恢复。

## 11. 长期媒体生命周期

### NAS

NAS 保存 WAV archival master。

逻辑结构：

```text
RonnieArchive/ReadAloud/articles/
└── YYYY-MM-DD_<title>_<articleId>/
    ├── master/
    │   └── YYYY-MM-DD_<title>_master.wav
    └── metadata/
        ├── audio-manifest.json
        └── repair-support.json
```

Phase 1D 已 fresh-verify 并冻结正式长期资产根为 `/Volumes/home/RonnieArchive/ReadAloud/articles`。目录采用人类友好的 `YYYY-MM-DD_<title>_<articleId>`；WAV 采用 `YYYY-MM-DD_<title>_master.wav`。`articleId` 仍作为稳定机器身份保留在目录名后缀及 manifest 中。

每篇正式 archive 还必须长期保留 `metadata/repair-support.json`。第一版至少记录 generation/request/render/WAV identity、voice/model/speed，以及 acoustic chunk 的 `chunk_index + start/end frame + start/end time`。current VOICE_AI public contract 不提供 exact phrase↔chunk alignment，因此 Website 不得猜测或伪造；实际修复采用“听到的时间点 → acoustic chunk”定位。未来若要按文本自动定位，必须由 VOICE_AI 正式接口提供 provider-owned alignment evidence。


## 11.1 DevSSD Cleanup Gate 与后续局部修复

正式媒体生命周期完成后，DevSSD 不承担长期 WAV/MP3 保存职责。只有以下条件全部满足，workflow 才能标记 `CLEANUP_ELIGIBLE`：

- 人工整篇试听 PASS；
- NAS final WAV 写入并 readback SHA/bytes exact PASS；
- R2 final MP3 full readback SHA/bytes exact PASS；
- R2 Content-Type/Range PASS；
- Website binding/build/deploy/live verify PASS；
- repair-support metadata complete 且已进入长期归档；
- 无开放 pronunciation/chunk repair。

进入 `CLEANUP_ELIGIBLE` 后，允许删除：
- worktree `artifacts/read-aloud/` 中该文章 WAV/MP3；
- runtime `artifact-cache` / `delivery-cache` 中该 workflow 的大媒体缓存。

不得删除：jobs/claims/workflows JSON、Render View、task/evidence、repair-support metadata、NAS master/manifest、R2 delivery。

清理后若发现一句发音错误：从 NAS master 恢复 → 用 chunk map 定位 → 只重新生成目标片段 → splice/rebuild → 人工试听目标片段及接缝 → 新 WAV 归档 → MP3 重编码并原 R2 key 替换 → remote verify → 再次 cleanup。不得因为本地缓存已删除而默认整篇重生成。

### Cloudflare R2

R2 保存 Website delivery MP3：

```text
audio/
└── articles/
    └── <article-id-or-slug>/
        └── article.mp3
```

### Website Git

Git 不保存 WAV/MP3，只保存网站代码、文章、audio metadata 与必要治理/验证证据。

职责固定为：

```text
NAS = WAV 母版真源
R2  = MP3 网站播放副本
Git = 网站代码、文章和音频指针
```

## 12. Website MVP

Pilot 通过后增加 optional schema，初始建议：

```yaml
audio:
  url: "https://audio.example.com/articles/.../article.mp3"
  duration: "15:32"
```

第一版不增加 voice、codec、bitrate、sampleRate、fileSize、transcript、waveform、chapters。

新增 `src/components/ArticleAudioPlayer.astro`，第一版使用浏览器原生：

```html
<audio controls preload="metadata">
```

`post.data.audio` 存在才渲染；不存在则完全保持现状。播放器位于 article header 信息结束后、正文开始前。

## 13. 第一版明确不做

- 全历史文章批量生成
- Podcast feed / Spotify / Apple Podcasts
- 逐字高亮或正文/音频同步
- 章节时间轴、waveform、音频数据库
- 复杂自定义播放器
- 多 voice selector / emotion/style
- 自动批量 TTS
- Opus 正式 delivery
- WAV 上传 R2
- WAV/MP3 进入 Git
- TTS 自动生成后未经人工 QC 直接发布
- 音频成为文章发布 hard gate
- 为本功能建立第四个 RonnieCross Owner 或第二套通用媒体平台

## 14. 分阶段建设

### Phase 0 — Construction Intake / Worktree

- fresh preflight/closure check
- lane_class=construction
- 建立正式 bounded task
- 创建 task branch
- 创建 Owner-local bounded-stage worktree
- 冻结 baseline/write-set/stop condition

不生成正式音频、不上传 R2、不部署。

### Phase 1A — TTS Render View Pilot

选择 1 篇约 10–20 分钟真实文章，冻结文章版本，生成并审核第一份 `tts-readaloud.txt`。

### Phase 1B — VOICE_AI Pilot

```text
GET /ready
→ stable request_id
→ POST /v1/speech
→ PASS
→ artifact_ref
→ 下载 WAV
→ SHA-256 verify
→ WAV master
```

### Phase 1C — Delivery A/B

同一 WAV master 生成 64/96 kbps MP3，FFprobe + 人工试听，冻结正式 delivery bitrate。

### Phase 1D — 媒体生命周期 Pilot

验证 WAV → NAS、MP3 → R2、metadata → Git；冻结命名、manifest、NAS archive path 与 R2 object path。

### Phase 2 — Website MVP + Durable Workflow Foundation

实现 optional audio schema、ArticleAudioPlayer、`[slug].astro` conditional render 与基本 CSS，只给 2–3 篇 Pilot 文章启用。验证 Desktop/iPhone/Safari/Chrome、播放/暂停/seek、加载和 R2 Range Request。

Phase 2 同时加入一个最小可靠性基础：**durable workflow controller**。原因不是提前做业务自动化，而是长时间 TTS 已证明会超过 CodexPro / Hermes 单次调用生命周期。任何可能超过调用者生命周期的步骤，都不得把“调用者仍然在线”作为正确性前提。

最小接口冻结为：

```text
start
status
tick
```

workflow current truth 存在 RonnieCross runtime，而不是聊天上下文。长 TTS 由现有 S4 durable job + detached one-shot worker 执行；后续 controller 通过 job terminal state 自动识别完成并继续。未来薄触发层固定为每 5 分钟调用一次 `tick`，每次调用完成一次当前合法推进后立即退出，不建设常驻业务 daemon。

### Phase 3 — 正式功能与 Workflow Freeze

冻结 TTS Render View rules、媒体 lifecycle、R2 bucket/custom domain、音频命名、QC gate、文章/audio 状态模型，以及 durable workflow state/next-action contract。音频始终 optional。

Phase 3 前必须证明：
- CodexPro/Hermes session 可在 TTS 运行期间退出，不影响 job 完成；
- 下一次 `tick` 可仅凭 durable state 继续；
- human QC / device QC / authorization Gate 机械可停；
- UNKNOWN 不会被误判为成功或触发第二 generation；
- Hermes 不需要依赖聊天记忆判断 workflow 进度。

### Phase 4 — Business Automation

Phase 4 保留真正的业务自动化，仍不得提前扩大：

```text
文章定稿
→ 自动创建有声阅读 workflow
→ TTS Render View
→ VOICE_AI
→ WAV
→ QC
→ FFmpeg
→ MP3
→ NAS
→ R2
→ audio metadata
→ Website
```

Phase 2/3 的 durable controller 只是可靠性基础，不等于自动批量生成、历史 backfill 或无人审核自动发布。

始终保持 `TTS failure != article publication failure`。

## 15. 全体建设进度

| 建设项目 | 状态 | 说明 |
| --- | --- | --- |
| 总体架构 | 已完成 | 有声阅读作为 Website optional capability |
| Website 现场核验 | 已完成 | Astro 统一文章入口适合低侵入接入 |
| VOICE_AI HTTP 接口 | 已完成 | V1 consumer contract 已确认 |
| TTS 调用边界 | 已完成 | Website 只走 localhost HTTP |
| request_id 原则 | 已完成 | exactly-once/replay 语义已明确 |
| 长文章策略 | 已完成 | 不做固定字符粗暴切块 |
| WAV 格式 | 已确认 | 24 kHz / mono / float32 |
| MP3 工具 | 已确认 | FFmpeg |
| MP3 QC 工具 | 已确认 | FFprobe |
| Pilot bitrate | 已确认 | 64k / 96k A/B |
| Pilot 作业区 | 已设计 | source/render/tts/master/delivery/qc/log |
| WAV 长期职责 | 已决定 | NAS archival master |
| MP3 长期职责 | 已决定 | R2 delivery |
| Git 媒体策略 | 已决定 | 不存 WAV/MP3 |
| 项目归属 | 已决定 | Website Owner，不建立第四 Owner |
| Construction isolation | 已决定 | bounded-stage worktree |
| 启动前预盘点 | 已完成一次 | 2026-10-07 Website main clean/synced；正式 task 前须重跑 |
| 正式 construction task | 已完成 | Phase 0 已闭合 |
| task branch/worktree | 已完成 | construction worktree 已实际使用 |
| TTS Render View 详细规则 | 已完成 | Phase 1A 已闭合 |
| 第一篇 Pilot | 已完成 | post-32d30724d859c99c |
| 第一次真实 TTS | 已完成 | Phase 1B exactly-one real generation |
| WAV master | 已完成 | final accepted repaired v2 WAV |
| 64k/96k MP3 | 已完成 | Phase 1C |
| 人工 A/B | 已完成 | 64k accepted，96k rejected as unnecessary |
| 正式 bitrate | 已冻结 | 64 kbps |
| NAS/R2 lifecycle | 已完成 | Phase 1D：NAS master+manifest / R2 delivery |
| Website audio schema/player | 已完成 | optional audioUrl + native player |
| 正式上线 | 已完成首篇 | Pilot 1 production + human verify PASS |
| Phase 2 Pilot 数量 | 2/2–3 | Pilot 2 production/archive/site/cleanup scope 已闭合；human listening 为 provisional PASS |
| Phase 2 长 TTS session 解耦 | 已证明 | Pilot 2 detached worker 长运行后自然 TERMINAL_PASS；调用者不需保持长 shell session |
| Durable workflow controller v0 | 已实现/验证 | `start/status/tick/attach-repair-support`；8/8 tests PASS；Pilot 2 已完成到 production/live/cleanup |
| Repair-support / chunk map | 已实现 Pilot 2 | 75 acoustic chunks；frame total=14542080；不伪造 text alignment |
| DevSSD Cleanup Gate | 已实现规则/机械 gate | human/NAS/R2/live/repair-support/no-open-repair 全部 PASS 才 CLEANUP_ELIGIBLE |
| Pilot 2 cleanup | PASS_COMPLETE | `CLEANUP_ELIGIBLE` 后已删除 DevSSD worktree/runtime 大媒体副本；NAS/R2/metadata 保留 |
| Post-cleanup repair restore drill | PASS | NAS exact WAV restore + acoustic chunk 10 localization/decode；无已知缺陷所以未做真实 TTS/splice |
| 5 分钟薄触发 cadence | PASS_ACTIVE | LaunchAgent `com.ronniecross.read-aloud.tick`；300s；launchd controlled run exit 0 |
| Phase 2 多端验证 | 保留项 / 非阻塞 | 机器/live HTTP 已通过；真实 iPhone/Safari/Chrome 设备矩阵未闭合，不伪造 PASS |
| Hermes 独立执行兼容 | 已满足当前目标 | Hermes/CodexPro 都只做短调用；durable files 才是 current truth；不再建设专用第二 runtime |
| 第一阶段工程建设 | FORMALLY_CLOSED | `PASS_FIRST_STAGE_GOAL_ACHIEVED / STOP_ENGINEERING_EXPANSION / SHIFT_TO_REAL_USAGE` |
| Phase 3 进一步工程冻结/扩展 | 暂不启动 | 当前能力已足够真实使用；仅在真实问题或新业务目标出现时重开 |
| Phase 4 Business Automation | 暂缓 | 自动触发/批量/backfill/无人审核发布继续禁止提前启动 |

## 16. 当前下一步

第一阶段工程建设于 2026-10-10 正式收口：

`PASS_FIRST_STAGE_GOAL_ACHIEVED / STOP_ENGINEERING_EXPANSION / SHIFT_TO_REAL_USAGE`

当前默认模式不再是继续 construction，而是：

```text
REAL_USAGE
→ MAINTENANCE
→ ISSUE_DRIVEN_REPAIR（只有真实问题出现时）
```

现有能力保持运行：两篇真实 Pilot、durable workflow controller、300s `tick-all`、NAS WAV archive、R2 MP3 delivery、Website player、cleanup gate、repair restore path。

非阻塞保留项只有：
- 未来有时间时完成真实 iPhone / Safari / Chrome 播放/暂停/seek/长时间播放矩阵；
- 以后若真实发现发音问题，再执行 targeted fragment regeneration + splice，以实际问题验证修复链最后一段。

不得把上述保留项解释为继续建设通用平台的理由。任何可能超过调用者生命周期的动作继续遵守 durable + resumable 原则；CodexPro/Hermes 不保持长会话等待。自动触发、全历史 backfill、无人审核发布继续属于未授权 Phase 4。
