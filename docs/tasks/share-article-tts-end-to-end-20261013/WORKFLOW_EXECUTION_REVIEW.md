# 分享文章 → TTS → NAS/R2 → 网站音频发布：2026-10-13 真实执行复盘

- 记录日期：2026-10-14（Asia/Tokyo）；本文件只记录证据与流程，不重放任何执行。
- 项目：RonnieCross / 个人网页项目。
- 本次样本：《如何荣耀神并永远以祂为乐？》（原始 PDF：`How Do We Glorify God and Enjoy Him Forever.pdf`）。
- Article ID：`post-c313198e37dddf21`。
- 结论：本次文章发布、Telegram 唯一 TTS、NAS WAV 主档、R2 MP3、网站音频绑定均执行成功；截至本次 fresh read，workflow/intake 为 `COMPLETE`，音频发布 receipt 为 `VERIFIED`。保留过程中的先前 BLOCKED/恢复记录，后续 PASS 不覆盖旧事实。

## 1. 运行对象与不可混淆的身份

| 对象 | 本次冻结身份 |
| --- | --- |
| NAS 收件源 | `/Volumes/DevSSD/RonnieWork/RonnieCross/NAS/分享收件/How Do We Glorify God and Enjoy Him Forever.pdf`（ingest 后移入 raw） |
| 原 PDF SHA-256 | `02bfc20c28bab941c77b8abeb3da2f6f70414b67cf3ef3199f6e93388ad1bf8a` |
| raw PDF / 中文源稿 | `data/raw/分享/How Do We Glorify God and Enjoy Him Forever.pdf`；`data/raw/分享/How Do We Glorify God and Enjoy Him Forever_中文.txt` |
| 正式文章 | `src/content/posts/2026-10-13-如何荣耀神并永远以祂为乐.md` |
| 首次文章发布 commit | `f19503d6164b039826b3dc80285d2727b93cf6e5` |
| 冻结文章 SHA-256 | `816735b84ce0c0b85ab2a2733293ffe0f7382c1dae13622de94cbd531578135d` |
| TTS render SHA-256 | `e884e60b6ac86c2e5770e0da534c7beffc6d5e038c929ac66e8e2bc46575c498`（3,070 字符） |
| intake ID | `c59a87c2083f01b5540fc1530afcdeebc255d07a46fd2385288721a842311b74` |
| S4 workflow/job ID | `99bac02b17e2338fe78201edf52296dfcc9e9686d20192d4d7315cc96bb27a4d` |
| TTS request ID | `rc-readaloud-v1:99bac02b17e2338fe78201edf52296dfcc9e9686d20192d4d7315cc96bb27a4d` |
| Telegram TTS script | `/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/telegram-tasks/post-c313198e37dddf21/run_tts_once.py` |
| Script SHA-256 | `b6e506791a1e8c80c77cfdabd02ea76b4163d1c601643cfad917f553272db51c` |
| 音频绑定 commit | `67a68298a21c05ab27befd2b39c2a722a67bd851` |
| R2 正式 URL | `https://audio.ronniecross.com/audio/articles/post-c313198e37dddf21/article.mp3` |

说明：原始 PDF 和中文原稿位于 raw，受现有 Git ignore 保护，不在文章发布 commit 中；不能将“已归档在 raw”误写为“已 Git 追踪”。首次文章发布的日期字段为 `2026-10-13`，按当次正式结果保存，不以本次复盘日期改写文章。

## 2. 从收件到文章发布的事件顺序

1. 打开 **exact** 正式网站工作区 `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`；fresh-read AGENTS、PROJECT_DECISIONS、STATUS、当前任务和统一内容流程；`npm run sync` 成功，Git 与 `origin/main` 对齐。
2. 检查正式 NAS 分享收件，找到唯一业务 PDF（4 页）；按 SHA 校验后进入 `data/raw/分享/`。通过 PDF 正文而非文件名识别文章主题；保留 Westminster Shorter Catechism 的历史背景、圣经论据、应用段落及基督论结尾。
3. 生成完整中文稿，不摘要化；保留三个主体分区与段落逻辑。将直接经文引述对照正式 Project Bible CUVMPS Rv2（本地受控 TSV），避免模型自行编造标准经文。分享文章由网站流程治理，不冒充讲道项目 E1 审核通过。
4. `publish share --dry-run` PASS；正式导入后内容镜像检查 `606/606` PASS、Knowledge Layer `303` 篇 `0 errors / 0 warnings`、Astro `347` 页构建 PASS。文章含 `articleId`，分类灵命成长，主要经文元数据哥林多前书 10:31／诗篇 16:11。
5. 精确 Git write-set 检查后正常 commit/push：`f19503d6164b039826b3dc80285d2727b93cf6e5`。记文章发布 `PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY`，**不等待本次 Cloudflare 和邮件异步终态**。
6. intake 以真实文章新增 Git push interval `3d3ce7a..f19503d` 登记，并冻结文章 blob、Render View 文本、SHA 和单篇任务身份。

本次收件脚本还有一个非阻断缺陷：`inspect/ingest share` 把隐藏 Finder 文件 `.DS_Store` 算作业务文件并移动。该文件已按同 SHA 无覆盖地放回原收件目录；未纳入 Git 提交。该缺陷应独立做最小修复，不能把它解释为新文章源。

## 3. Telegram 仅负责一次性 TTS

- 脚本、manifest、render text、单篇 intake 在 RonnieCross 正式运行时准备并验证；脚本 preflight 校验 article ID、源 commit/SHA、render SHA、脚本 SHA、无历史 claim/result、无现存同文章 S4 job，生成时使用固定 `request_id`。
- 用户通过 Hermes Telegram **只执行一次**：

```text
/expy
python3 /Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/telegram-tasks/post-c313198e37dddf21/run_tts_once.py
```

- 实际 Telegram machine：`execution_id=run-20261013T144705-78562255`，`terminal=true`，`exit_code=0`，`invocation_count=1`，`automatic_retry=0`，`safe_to_retry=false`，脚本 SHA 与 manifest 一致，stdout `PASS`。
- 不能只依赖 stdout：已 fresh-read `telegram-tasks/post-c313198e37dddf21/result.json` 的 `TTS_TERMINAL_PASS`、S4 job `TERMINAL_PASS`、WAV 实体和 SHA。
- WAV：72,821,840 bytes，SHA-256 `75a3205c84636cdb0226dcf52759cc3551d28bb71f30c6ac79b324c577eb48d9`。
- 后续由 RonnieCross 接管；Telegram 不负责 NAS 写入、R2 上传、网站更新、Git push、订阅邮件。出现 UNKNOWN 不得再发第二次 `/expy`；应使用原 execution ID 查状态，按原 request ID 做受控只读/人工 reconciliation。

## 4. 自动技术 QC 与媒体交付

- S4 状态进入 `AUDIO_READY_PENDING_PUBLICATION_GATE`；`AUTO_TECHNICAL_QC: PASS` 的**准确依据仅为** WAV/MP3 全解码、codec/采样率/通道/时长，非人耳音质判定。
- WAV 为 `pcm_f32le / 24 kHz / mono`；MP3 为 `64 kbps / 24 kHz / mono`；时长 758.56 秒（约 12 分 39 秒）；MP3 6,069,165 bytes，SHA-256 `c274db251bbeb5bfee2633e2bb89facd1d9b6040fa7c6a871a2304b9d16c9f74`。
- NAS `/Volumes/home/RonnieArchive/ReadAloud/articles/` 挂载验证后，WAV 以 append-only 存入 `2026-10-13_如何荣耀神并永远以祂为乐？_post-c313198e37dddf21/master/`，附 manifest；SHA 与源 WAV 一致。
- **首次 R2 上传出现 BLOCKED**：`R2_UPLOADED_NOT_VERIFIED`，原因是对象上传后公开的 canonical URL 仍返回 Cloudflare 缓存的旧 HTTP 404。
- 恢复过程禁止第二次上传：R2 `wrangler r2 object get --remote` 下载后比对 6,069,165 bytes 与 SHA 精确一致；加 cache-busting query 的公开请求 HTTP 200、Range 206；随后 canonical URL HTTP 200、完整 SHA 和 Range 206 通过，才记 `r2_delivery.verified=true`。
- 保存 `runtime/read-aloud/exact-one-media/post-c313198e37dddf21/r2-remote-readback.json` 和一次性 claims。**这次成功恢复不等于源码已支持通用自动恢复**；今后应做最小、只读、安全的缓存误判恢复，不得自动重传。

## 5. 网站发布前上次文章的核验与音频发布

- 上次文章发布 commit `f19503d` 的线上部署 commit、目标标题/页面、RSS/Sitemap 已核实。
- GitHub 对应通知 workflow run `38352057156`：push 触发、`completed/success`；job `115146439566` 和 `Wait for deployment and send email` 步骤成功。仓库发送脚本在 `failedCount>0` 的重试耗尽后会抛错，不应把作业成功写成失败。
- **证据限制必须保留**：GitHub 未认证的日志接口 403，公开 API 不能独立给出发送摘要的具体 `recipientCount`；本次以“push 身份 + workflow/job 成功 + 发送脚本退出条件”形成受限的替代证据。回执 `notification_terminal=PASS` 的 provenance 保存在 `website-publication/article-notification-public-api-evidence-f19503d.json`，同时标记 `NOT_OBSERVABLE_FROM_PUBLIC_API`，不得编造收件人数，也不得声称已取得原始发送日志。
- 媒体就绪且前轮 `VERIFIED` 后，目标文章**仅新增一行 `audioUrl`**。`npm run build` 347 页 PASS；精确 Git `-z` 路径核验确保无中文转义误判；commit/push `67a68298a21c05ab27befd2b39c2a722a67bd851`，仅 1 文件 1 行增加；音频更新禁止新文章邮件。
- 完成 `PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY` 回执后当轮合法收口，**不等待本轮 Cloudflare 部署**。截至 2026-10-14 本次 fresh read，workflow/intake 均为 `COMPLETE`、`website_live.verified=true`、`open_repairs=0`，网站 release receipt 已是 `VERIFIED`；这是发布后额外取得的终态，而不是应当等待的本轮前置条件。

## 6. 固定的后续工作流与硬门

`分享收件只读 inspect → SHA 入 raw → 英文原稿完整中文整理与经文门 → dry-run → mirrors/knowledge/build → 文章精确 commit/push → 当轮 PENDING 收口 → 单篇 intake + immutable Git blob/Render View/SHA → Telegram /expy 唯一 TTS → machine/result/WAV 双证据 → AUTO_TECHNICAL_QC（技术层） → NAS WAV append-only → R2 MP3 exact object + 公开完整/Range 校验 → **音频发布前核验上一篇文章** → 仅新增 audioUrl/build/commit/push/零新文章通知 → 音频 PENDING 收口 → 下一次任何发布前核验上一轮`。

- 文章与音频正常已授权的 commit/push 包含在同次发布授权内，无须每次另问；不得扩大到其他代码、force push、额外批量任务或未授权部署动作。
- 收口与后续验证分离：本次发布成功只要求精确 commit/push 和 pending receipt；上次发布的线上身份、RSS/Sitemap、通知/媒体结果，在**下一次文章或音频发布前**验证；失败、PENDING、UNKNOWN 必须 fail-closed。
- 运行时状态必须以正式文件 fresh read 为准，不能用聊天中的旧 PASS 代替当前事实；`FAIL/BLOCKED → 后续恢复 PASS` 保留原始 chronology。
- WAV/MP3 技术 QC PASS 不等于音质好听。Patrick 曾报告约 1:36 啸音，证明未来音质检查应聚焦可听缺陷，但本轮不得因此擅自增加全局训练、通用调度/监控或假造人工试听。
- 下一次最小整改候选：过滤 Finder `.DS_Store` 的分享 ingest；R2 stale-404 只读恢复；中文 Git 文件名安全的 `-z` 核验；前轮通知证据可观察性。分别建最小任务，不以本复盘直接授权业务代码、NAS/R2 重做、通知补发或 Git push。

## 7. 正式现场证据索引

- 工作区 `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目` 的 Git `f19503d`、`67a6829`。
- `runtime/read-aloud/new-post-intake/c59a87c2083f01b5540fc1530afcdeebc255d07a46fd2385288721a842311b74.json`。
- `runtime/read-aloud/workflows/99bac02b17e2338fe78201edf52296dfcc9e9686d20192d4d7315cc96bb27a4d.json`。
- `runtime/read-aloud/jobs/99bac02b17e2338fe78201edf52296dfcc9e9686d20192d4d7315cc96bb27a4d.json`。
- `runtime/read-aloud/telegram-tasks/post-c313198e37dddf21/{task_manifest.json,result.json,tts_once.claim.json,run_tts_once.py}`。
- `runtime/read-aloud/exact-one-media/post-c313198e37dddf21/` claims 及 R2 readback evidence。
- `runtime/read-aloud/website-publication/last_website_release.json` 与 `article-notification-public-api-evidence-f19503d.json`。
- NAS audio-manifest 与 R2 canonical URL，以文件 SHA 和生产线上真实回读为准。

## 8. 本复盘操作边界

本文档只做历史事实记录、未来 SOP 说明及缺陷分级。它不是新的生产执行授权，也不改写正式 authority；若与后续 AGENTS/PROJECT_DECISIONS/当前任务及生产状态冲突，先 fresh-read 当前 authority，再决定。**本轮不执行 TTS、NAS、R2、文章发布、邮件、构建、Git commit 或 push。**
