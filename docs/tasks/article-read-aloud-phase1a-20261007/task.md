# Article Read-Aloud Phase 1A — TTS Render View Pilot

状态：PHASE1A_TTS_RENDER_VIEW_VERIFIED_PENDING_MASTER_CLOSURE
日期：2026-10-07
Owner：Website / 个人网页项目
lane_class：construction

## 最终目标

用一篇真实正式文章验证 Website 能从 canonical Markdown 生成 fidelity-preserving、适合 VOICE_AI 的纯文本 Render View。Phase 1A 只验证文本，不调用真实 TTS。

## Pilot source

- articleId：`post-32d30724d859c99c`
- title：`基督徒不应该做计划吗？`
- source path：`src/content/posts/2026-10-06-does-james-4-say-not-to-make-plans.md`
- source SHA-256：`14dcd20d98b1b644a6613d4f54813b065842af3b221d8347c8713d20957c7398`
- source baseline：construction branch `ef1f8a8d85ab62d278f7eddc6d540943fe0d1b74`
- selection reason：长度适中；包含主经文、正文引用、多个经文 reference、问答式段落；最新正式发布，便于人工核对。
- source mutation：禁止。Phase 1A 不修改正式文章。

## Render View v0 rules

### Include

1. 文章标题。
2. 主经文 reference，转换为可朗读形式。
3. 正文全部 proposition，保持原顺序。
4. 正文中的问题、引语、经文引语、结束语全部保留。
5. 正文中仅用于视觉呈现的 Markdown 标记应去除，但语义文本必须保留。

### Exclude

1. YAML frontmatter 中除标题/主经文之外的 metadata。
2. 日期、publishedAt、tags、category、author、reviewed、source、articleId。
3. 网站导航、阅读统计、评论、订阅、URL、播放器 UI 等非文章正文。
4. Markdown 控制符本身。

### Scripture speech normalization

只做 deterministic display/speech normalization，不改经文译文：

- `雅各书 4:13-17` → `雅各书4章13节到17节`
- `箴言16章1节` 等已经是 spoken form 的保持不变。
- reference normalization 只改变 reference 表达，不自由改写经文正文。
- 多 reference、跨章 reference 或不能确定的形式必须 fail-closed/记录，不得猜。

### Fidelity invariants

- 不删除 proposition。
- 不概括、不润色、不重新翻译。
- 不删除问题、祷告、引语归属、结尾。
- 不改变段落顺序。
- 标点只允许为 TTS 可读性做不改变命题的机械处理。
- 任何受控经文正文保持 source 原文；Phase 1A 不自行替换成另一译本。

## Deliverables

在 `docs/tasks/article-read-aloud-phase1a-20261007/` 生成：

- `tts-readaloud.txt`
- `render-report.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

可增加 task-local manifest，但不得新增通用平台/registry。

## Verification

至少验证：

1. source SHA 与冻结值一致。
2. frontmatter 非朗读 metadata 未进入 Render View。
3. 标题、主经文和正文完整。
4. 正文段落顺序一致。
5. source 中每个正文 paragraph 都能在 Render View 中建立对应关系；若机械 normalization 使 exact match 不成立，必须在 report 中列明。
6. 经文 reference normalization 有显式记录。
7. Render View 不含 Markdown/YAML 控制结构。
8. UTF-8 byte size 小于 VOICE_AI 262,144 bytes。
9. 不调用 `/v1/speech`。

## Write-set

只允许：

- `docs/tasks/article-read-aloud-phase1a-20261007/`
- 必要的 `docs/tasks/current.md` 状态更新。

禁止修改 `src/`、正式文章、schema、播放器、scripts、R2、NAS、VOICE_AI。

## 停止条件

完成首份 Render View + verification 后停止，交回 `ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`。不得进入 Phase 1B，不得调用真实 TTS。
