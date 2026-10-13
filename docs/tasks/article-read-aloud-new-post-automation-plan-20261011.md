# 新文章发布后自动有声阅读：建设计划与启动检查（2026-10-11）

Owner：Website / 个人网页项目。状态：PLAN_RECORDED / READ_ONLY_STARTUP_CHECK / NOT_PRODUCTION_ENABLED。

## 最终目标与边界
以后新增且正式审核通过的文章，在 Website 正式发布 push 成功后异步登记一次音频生产任务；不等待本次 Cloudflare 部署终态，不阻断文章发布。复用现有 VOICE_AI_LOCAL_HTTP_V1、S4 durable job、read_aloud_workflow.py、5 分钟 thin tick、NAS WAV master、R2 64kbps MP3、Website 原生播放器。不新增调度平台、daemon 或第二套 authority。

历史文章约300篇的 batch/backfill 明确暂停；历史排版修复、文章普通更新及 audioUrl 自身更新不得自动触发新音频制作。本日单篇《腓立比书 1:20-30｜活着就是基督》（post-072eda6a5bfbe1f9）只作为 **exact-one opt-in validation candidate**，不是历史全量补录许可。

## 已决定的业务规则
1. Trigger：必须是已经通过文章/讲道正式审核、构建及 push 的新增文章发布事务；用 articleId、post路径、正文SHA、TTS Render View SHA、发布commit/transaction身份建立 stable idempotency key。不能把任意 git push、历史正文更新、手工旧文章盘点或无 audioUrl 扫描当 trigger。push 后登记失败需由受限已push发布记录对账补偿，不得扫描全站历史文章。
2. Publication Fast Lane 不变：发布文章后登记 PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY 并结束，不同步等待部署。音频可在部署过程中异步生成，只有绑定网站 audioUrl 前必须检查上一轮网站发布是否完成。
3. 统一 **previous Website release preflight**：无论准备发布文章还是音频，均核验上一轮网站写入/commit/push 的实际 Cloudflare production commit、deployment.json、目标线上身份及对应结果。文章事务验证正文、RSS、Sitemap 和原文章邮件结果；音频事务验证音频链接、播放器、R2 SHA/Range；若 pending/FAIL，则不进入下一项 Website 写动作，按可恢复状态退出。R2 MP3 单独上传不等于 Website release。检查+获取发布权必须互斥，避免两项任务同时通过同一 preflight；不得抢占未完成正式发布，不得自动篡改前次文章出版判断。
4. 音频生产：锁定合法正式 articleId/source SHA/Render View；复用现有 TTS request_id 和 UNKNOWN/reconcile/终态保护；完整 WAV 与 64kbps MP3 解码、duration、codec、SHA QC；本自动模式免逐篇人工试听，但 QC 不能冒称 HUMAN_LISTENING_PASS，机械检查不能保证发音或语义正确，异常 fail-closed。旧 Pilot 的 WAIT_HUMAN_LISTENING 和 provenance 保持历史真实，不静默升级。
5. NAS / R2 / Git：NAS append-only master+manifest：/Volumes/home/RonnieArchive/ReadAloud/articles；R2 bucket ronniecross-audio, key audio/articles/<article-id>/article.mp3；网站只为匹配正文 SHA 的现有 post 加 audioUrl，不改正文/经文/标题/日期/作者/分类/source。R2 SHA、HTTP Range 验证后受控更新 Git、触发 Cloudflare，独立记录 pending 并短时续检 live；完成并满足 repair-support/cleanup gate 后清理临时大媒体。正文版本漂移、远端分支冲突或部署仍 pending 则暂停。
6. **AUDIO_ONLY_UPDATE 严格不发送邮件通知**：生成、R2 上传、audioUrl push、重新部署、音频修复均不得发邮件，也不得调用 workflow_dispatch 发送新文章邮件。GitHub workflow 如启动必须识别只有旧文章的 audioUrl 修改，没有新增 post（diff-filter=A），安全退出；独立验证邮件实际发送数为 0。文章首次发布依旧保持原邮件规则；上次是音频发布时 preflight 不检查不存在的邮件终态。
7. Safety：授权分层。写本文档和只读检查不授权真实 TTS、NAS/R2 上传、push、部署或邮件；即便用户批准未来自动模式，也必须在 Website Owner 任务中冻结自动发布准确的 operation class / write-set / repository identity 与退出边界。不能复用普通出版的邮件权限作为音频权限。真实单篇验收与未来持续自动启用是两次明确 authority gate。

## 一次完整建设执行合同（避免细碎分发）
A. Fresh Gate：exact workspace、current owner authority、git clean/main状态、existing publish/notification workflow、latest deployed post、S4/runtime、thin tick、VOICE_AI contract；goal-aligned/no-scope-drift/no-overbuilding 记录；建设任务按 PUBLICATION_FAST_LANE + CONSTRUCTION_ISOLATION，先 mechanical worktree lane gate，隔离 branch/worktree。
B. 同一 Executor 在限定 write-set 下连续完成：push-after-new-post bounded registration、只读补偿、音频 AUTO_QC 模式、共享上次发布 preflight 与互斥、防重复、R2/NAS/Website 受控自动收口、禁邮件保护、失败后安全续跑；实施→单测→集成→局部整改→回归，不因普通可修复失败拆任务。
C. 独立 Auditor：验证新增文章/旧文更新/audioUrl 更新分母、重复触发、push/部署交错、TTS UNKNOWN、崩溃恢复、Git 冲突、NAS 未挂载、R2 失败、no-notification、旧 Pilot 兼容、无过度工程；审计不自行授权生产。
D. Fresh production gate：以 post-072eda6a5bfbe1f9 一次显式 opt-in 验证，先确认其网站 push、线上 deployment、正文身份、RSS/Sitemap、原文章 notification，随后明确授权恰好一次 TTS 真实生成与有界音频发布；现场核验 NAS/R2/site/无邮件；达到 PASS 才考虑未来持续自动触发授权。

## 启动检查结论与停止点
2026-10-11 本轮读到 canonical main...origin/main（仅为当前连接反馈；未等同于 live deployment）。
当前文档：2026-10-11 Patrick 新稿已通过 E1 91/91、网站结构验收、346 页构建；但同轮 STATUS/current 均写明 GitHub push 结果和 Cloudflare / 邮件异步终态须 fresh readback，不能预设成功。当前现存控制器 scripts/read_aloud_workflow.py 在技术 QC 后写 state=WAIT_HUMAN_LISTENING, next_action=HUMAN_LISTENING，尚无批准的 unattended release transition。
因此准确裁决：PLAN_RECORDED / ARTICLE_LOCAL_READY / PRODUCTION_RELEASE_NOT_YET_CONFIRMED / AUTOMATION_NOT_IMPLEMENTED / NO_TTS_STARTED。本轮只记录计划并进行只读检查，**不得将 status 检查等同于已触发工作流**。
下一步：通过 Website Owner 独立 construction lane 实现 A–C，再以 exact-one 用户授权进入 D。必须保留全部旧 FAIL/BLOCKED/PASS chronology。
