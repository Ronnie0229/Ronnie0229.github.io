# PROJECT_DECISIONS.md

本文件记录 RonnieCross 项目的关键决策和背后理由。多个 ChatGPT / Codex 账号接手时，除了知道“怎么做”，也要知道“为什么这样做”。

## 1. 为什么使用 Astro

RonnieCross 是文字内容为主的个人文章网站，核心需求是长文阅读、静态生成、SEO、低成本部署和长期可维护。Astro 适合内容型静态站点，可以把 Markdown / Content Collections 与组件化页面结合起来，避免使用过重的全栈框架。

决策：继续以 Astro 作为主框架，除非未来出现明确且重大的迁移理由。

## 2. 为什么使用 Cloudflare Pages

项目目标包括免费、境外服务器、中国大陆无需翻墙可访问、静态站部署方便。Cloudflare Pages 适合静态网站，并且当前项目已经包含 `wrangler.jsonc`、Functions 和后台接口相关结构。

决策：Cloudflare Pages 是默认部署平台；部署、后台和边缘函数相关规则写入 `DEPLOY.md` 和 `docs/网站后台使用与配置.md`。

## 3. 为什么把项目记忆写进仓库

多个 ChatGPT / Codex 账号不能共享完整聊天记忆。若项目规则只存在于某个账号的历史对话里，切换账号、换电脑或暂停数月后都会造成上下文丢失。

决策：项目事实、当前状态、流程、设计、内容规则、部署规则、交接记录全部写入仓库文档。`AGENTS.md`、`STATUS.md`、`docs/tasks/current.md` 是接手项目的最高频入口。

## 4. 为什么不按账号分工

早期曾考虑 A 账号负责开发、B 账号负责文章。但长期来看，最稳妥的方式是让任何账号都可以接手全部项目，只要它按文档读取上下文并遵守任务边界。

决策：不以账号命名分支，不把权限固定给某个账号。所有账号按任务类型工作，分支名使用 `task/<task-name>-YYYYMMDD`。

## 5. 为什么保留原始资料和中间稿

项目内容包括分享、讲道、翻译稿和公众号文章。很多资料一旦覆盖或删除，无法可靠还原。讲道和翻译类内容尤其需要保留原始 PDF、提取稿、中文整理稿和发布稿之间的链路。

决策：`data/raw/` 保护原始资料，`data/processed/` 保留整理中间稿，正式文章进入 `src/content/posts/`。NAS 归档区只新增和读取，不移动、不删除、不覆盖。

## 6. 为什么设计方向是深蓝、白底、金色点缀

网站定位是信仰随笔、圣经学习、长文阅读，不是企业官网、科技博客或图片社区。用户已经确认深色版为深蓝圣经学习氛围，浅色版为白底深蓝阅读风格，少量金色点缀用于温暖感和视觉识别。

决策：设计修改必须参考 `DESIGN.md`、`docs/ui-spec.md` 和 `风格重新设计素材/ronniecross_astro_design_spec.md`。不要把主视觉改成绿色田园风、强科技感或大量缩略图卡片风。

## 7. 为什么内容表达要保持忠实又温和

项目内容包含信仰文章、讲道整理、翻译稿和公众号发布稿。翻译任务必须忠实原文；公开发布文章则需要语气温和、可读、适合公众平台阅读。

决策：翻译任务以忠实为最高优先级，文章整理任务以保留神学核心和提升中文可读性为目标。具体规则见 `CONTENT_WORKFLOW.md`、`docs/content-style.md` 和 `skills/article-workflow.md`。

## 8. 为什么每次任务都要更新 current.md

账号切换的最大风险不是代码，而是“下一个账号不知道上一个账号做到哪里”。

决策：`docs/tasks/current.md` 是唯一接力棒。任何账号结束任务前必须更新它，说明完成内容、修改文件、验证情况、未完成事项和下一步。

## 9. 为什么尽量减少 Codex 后续工作量

ChatGPT 更适合先规划、整理项目规则和生成高层文档；Codex 更适合按明确文档执行代码修改、批量落盘、运行验证和提交。为了避免 Codex 在缺上下文时自由发挥，本项目尽量把规则写清楚，再让 Codex 执行小而明确的任务。

决策：能由当前账号明确写入的文档直接写入；需要本地命令、构建验证、批量检查或后续落盘时，才通过 bridge / `.ai-bridge/current-plan.md` 交给 Codex。

## 决策：GitHub 作为代码事实来源

网站代码以 GitHub 仓库为正式来源。本机 `C:\Users\caoyi\Projects\个人网页项目` 是日常开发工作区，NAS 用于资料归档、历史保留和原始材料存放。

不把 NAS 作为日常 Git、Node、Astro 或文件监听工作区，主要是为了减少 SMB 网络文件系统带来的慢、卡、监听异常和路径差异问题。需要跨 Windows/macOS 迁移时，优先重新 clone GitHub 仓库，再按文档恢复资料入口和归档路径。

## 2026-10-08 — Read-aloud runtime lives in RonnieCross DevSSD project domain

- Website read-aloud persistent runtime state no longer uses `~/Library/Application Support/RonnieCross/read-aloud`.
- Current runtime authority is `/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud`.
- Runtime state stays outside Git worktrees so jobs/claims/locks/cache survive worktree changes and do not pollute version control.
- Human-review Pilot audio belongs in the active worktree under `artifacts/read-aloud/`; it is local/untracked, not a production media publication location.
- This is a storage-layout decision only; S4 exactly-once/request_id/UNKNOWN/reconcile/provider semantics are unchanged.

## 2026-10-09 — Read-aloud media lifecycle storage freeze

- NAS archival root is frozen as `/Volumes/home/RonnieArchive/ReadAloud/articles`.
- Per-article NAS layout is human-readable: `/Volumes/home/RonnieArchive/ReadAloud/articles/YYYY-MM-DD_<title>_<articleId>/master/YYYY-MM-DD_<title>_master.wav` plus `metadata/audio-manifest.json`. The title/date lead for human browsing; `articleId` remains in the directory suffix and manifest as the stable machine identity.
- The manifest schema for the Pilot is `ronniecross-readaloud-audio-manifest/v1`. The first accepted Pilot is archived under `2026-10-06_基督徒不应该做计划吗_post-32d30724d859c99c`.
- R2 delivery remains bucket `ronniecross-audio`, object key pattern `audio/articles/<article-id>/article.mp3`, custom domain `audio.ronniecross.com`.
- Storage roles are now proven in the real Pilot: NAS = WAV archival master + manifest; R2 = MP3 Website delivery; Git = code/article pointer/governance evidence only.
- NAS archive is append-only for new article objects; existing archive contents are not silently overwritten. Chronology: an initial Pilot copy was mistakenly placed under `/Volumes/share/网站有声阅读`; after PROJECT_OWNER rejected that root and approved `/Volumes/home/RonnieArchive`, the final WAV was verified at the new human-readable path and the mistaken Pilot-only copy was removed.

## 2026-10-10 — Read-aloud durable workflow control / Hermes-ready execution

- Long-running TTS must not depend on CodexPro, ChatGPT, Hermes, or any shell session remaining alive.
- The existing S4 durable job remains the TTS execution truth; a new Website-owned durable workflow controller provides short `start / status / tick` operations around it.
- Future local trigger cadence is frozen at once every 5 minutes. The trigger is intentionally thin: invoke `tick`, then exit. It must not contain business logic or become a second workflow authority.
- Workflow current truth lives under `/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/workflows`, outside Git worktrees. Models/tools are interchangeable operators, not state authorities.
- Durable workflow control is reclassified as Phase 2/3 reliability foundation, not Phase 4 business automation. Phase 4 still owns automatic article triggering, historical batch/backfill, and unattended production publication.
- Human listening/device acceptance and explicit authorization boundaries remain hard stops. UNKNOWN/stale-owner states cannot be guessed or converted into a new generation.
- Initial v0 first proved automatic continuation through verified WAV. In the same bounded task it was then extended, after mechanical tests, through technical QC and 64 kbps MP3 encoding to the hard `WAIT_HUMAN_LISTENING` gate. NAS/R2/Website transitions remain after human acceptance. No daemon/Redis/Celery/database is introduced.

## 2026-10-10 — Read-aloud DevSSD cleanup + repair-support policy

- Active worktree `artifacts/read-aloud/` is a temporary human-listening/repair workspace, not a long-term media store.
- Runtime `artifact-cache` / `delivery-cache` are temporary media caches; jobs/claims/workflows/logs remain durable small-state evidence.
- After human listening PASS + NAS exact archive verification + R2 exact/read-range verification + Website live verification + complete repair-support metadata + no open repair, workflow becomes `CLEANUP_ELIGIBLE`.
- `CLEANUP_ELIGIBLE` permits deletion of the article's DevSSD WAV/MP3 copies from worktree/runtime caches, but never deletes durable JSON/evidence, Render View, NAS master/manifest, repair-support metadata, or R2 delivery.
- Post-cleanup pronunciation repair restores the authoritative WAV from NAS, uses the acoustic chunk/time map to locate the target region, regenerates only the target fragment, splices/rebuilds, re-verifies, re-archives, replaces the same R2 object key, then becomes cleanup-eligible again.
- Current repair-support v1 records acoustic chunk frame/time boundaries and generation identity. Current VOICE_AI public contract does not expose exact text-to-chunk alignment, so Website must not infer or fabricate phrase↔chunk mapping.

## 2026-10-10 — Read-aloud first-stage formal closure

- PROJECT_OWNER adopted the independent audit conclusion and authorized formal stage closure.
- Formal verdict: `PASS_FIRST_STAGE_GOAL_ACHIEVED / STOP_ENGINEERING_EXPANSION / SHIFT_TO_REAL_USAGE`.
- The first engineering stage is closed. Existing controller + 5-minute thin trigger + NAS/R2/site lifecycle are sufficient for current goals.
- Default operating mode is now `REAL_USAGE / MAINTENANCE / ISSUE_DRIVEN_REPAIR`.
- Real iPhone/Safari/Chrome device acceptance and a future real targeted pronunciation repair remain non-blocking follow-up items; neither justifies continued framework expansion.
- Do not add a new task platform, scheduler/monitor/watchdog layer, general Agent orchestration platform, second Hermes-specific Website runtime, generalized audio editor, historical batch backfill, or unattended publication unless a later explicit business goal or observed production defect requires it.
- Pilot 2 keeps `PROVISIONAL_PROJECT_OWNER_PASS_NO_FULL_LISTENING`; stage closure must not rewrite it as completed full listening.
