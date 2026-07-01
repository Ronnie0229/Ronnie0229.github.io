# AGENTS.md

## 项目总入口

任何 ChatGPT / Codex 账号接手本项目时，必须先阅读本文件。

本项目不依赖任何单个账号的聊天记忆。项目事实、当前状态、设计规范、内容流程、部署流程和交接记录，都以仓库内文档为准。

## 项目定位

- 本仓库是 RonnieCross 个人文章网站的唯一正式代码仓库。
- 网站开发、设计、内容整理、SEO、部署、后台配置和维护都在本仓库完成。
- 正式本地仓库路径：`C:\Users\caoyi\Projects\个人网页项目`。
- 日常开发应使用本机 SSD 上的 Git 工作副本，不要直接在 NAS 目录运行 Git、Node、Astro、Codex 或文件监听。
- GitHub 是代码和正式网站内容的长期事实来源。

## 新账号必读顺序

新账号进入项目后，先按顺序阅读：

1. `AGENTS.md`
2. `PROJECT.md`
3. `PROJECT_DECISIONS.md`
4. `STATUS.md`
5. `RUNBOOK.md`
6. `docs/account-switching.md`
7. `docs/task-handoff-protocol.md`
8. `docs/context-engineering.md`
9. `docs/tasks/current.md`

按任务类型继续阅读：

- 设计 / 前端 / 主题：`DESIGN.md`、`docs/ui-spec.md`、`风格重新设计素材/ronniecross_astro_design_spec.md`
- 内容 / 文章 / 讲道 / 分享：`CONTENT_WORKFLOW.md`、`docs/统一内容整理与发布流程.md`、`docs/content-style.md`、`docs/content-publishing-error-prevention.md`、`skills/article-workflow.md`
- SEO：`SEO.md`、`src/pages/sitemap.xml.ts`、`src/pages/rss.xml.ts`、`src/pages/search-index.json.ts`
- 部署 / 后台：`DEPLOY.md`、`docs/网站后台使用与配置.md`、`wrangler.jsonc`、`functions/`
- Git / worktree / 多账号协作：`docs/branch-workflow.md`、`docs/account-switching.md`
- 历史交接记忆：`docs/codex-handoff-memory.md`

## 全账号通用工作原则

1. 不要依赖账号自身的聊天记忆；先读取仓库文档。
2. 修改前先确认 `STATUS.md` 和 `docs/tasks/current.md`。
3. 不要在不清楚当前任务的情况下大规模改代码。
4. 不要直接在 NAS 上运行 Git、Node、Astro、Codex 或文件监听。
5. 不要删除、移动、覆盖未知文件。
6. 不要覆盖 `data/raw/` 中的原始资料。
7. 不要移动、删除、覆盖 `\\RonnieNAS\share` 中的受保护归档资料。
8. 每次任务结束前，更新 `docs/tasks/current.md`，说明完成内容、修改文件、未完成事项和下一步。
9. 影响全局状态时，同时更新 `STATUS.md`。
10. 新增流程或规则时，写入对应文档，而不是只留在聊天记录里。
11. 遇到文档冲突时，以当前仓库状态、`AGENTS.md`、`STATUS.md`、`docs/tasks/current.md` 为优先。
12. 任何本地修改开始前，必须先同步线上最新状态，尤其是用户可能通过 Admin 后台发布过文章时；默认先执行 `git pull --rebase origin main`，确认本地不落后远端后再修改、构建、提交和推送。
13. Logo、favicon、apple-touch-icon、manifest icons 都属于受保护品牌资产；未经用户明确确认，不得 AI 重绘、临时新建、替换或重新设计，只能使用用户已确认的正式 Logo 文件，或从正式 Logo 等比例裁切/缩放生成尺寸版本，不得改变设计。
14. Markdown 文档中的多行命令、路径、日志和文件列表必须使用标准三反引号代码块；代码块开头可以标注 text、shell 或 powershell，结尾单独一行关闭，避免单反引号或转义字符造成格式损坏。
15. 项目文档类修改请求默认直接写入仓库文件；用户说“当前任务文档”时，默认指 `docs/tasks/current.md`。除非用户明确要求“只给我看看，不要改文件”，否则不要只把文档内容留在聊天里。
16. 给 Codex 写执行任务时，任务内容必须明确要求 Codex 在完成构建、提交、push 或其他执行动作后，更新 `docs/tasks/current.md` 的任务完成状态，记录构建结果、提交哈希、push 结果、修改文件、未完成事项和需要用户验证的内容。

## Codex 输出控制

```text
Process_narration=false
```

所有 ChatGPT / Codex 账号在本项目执行任务时，默认关闭过程叙述和规划步骤输出。

- 不输出“我正在分析……”“我准备这样做……”等过程性说明。
- 不展示内部推理、长篇计划或逐步思考过程。
- 任务清楚时直接执行，不反复请求确认。
- 完成后只汇报：实际修改内容、涉及文件、验证结果、剩余问题和下一步建议。
- 如任务存在高风险、大范围重构、删除/覆盖文件、部署发布或资料不可逆变更，仍需先明确说明风险并等待确认。

## CodexPro 低噪音模式

所有 ChatGPT 对话中调用 CodexPro 操作本项目时，默认采用低噪音模式：

1. 不要展开完整目录树，除非任务确实需要。
2. 不要输出大段文件内容。
3. 不要输出大段 diff；查看改动时优先使用 `show_changes(include_diff=false)`。
4. 只在必要时调用工具，避免反复读取、扫描或验证。
5. 最后只给用户总结和需要确认的事项。
6. 中间不要要求用户确认无关的 CSP、工具卡片、嵌入 UI 或过程信息，除非真的需要用户做决定。

## Context Engineering（上下文工程）

本项目不把 Codex 对话当作长期记忆。长期事实、长期规则、当前状态、设计决策、内容流程、SEO 规则和部署流程必须写入仓库文档；Codex 对话只作为单次任务工作区。

基本原则：

1. 一个 Codex 对话只处理一个明确任务或一个连续 Feature。
2. 任务完成后，应更新 `STATUS.md` 和 `docs/tasks/current.md`，再结束该对话。
3. 不要在同一个长对话中连续处理 UI、SEO、内容发布、部署、Bug 修复等无关任务。
4. 当任务类型明显切换时，应新开 Codex 对话，而不是继续旧对话。
5. 新对话开始后，必须先读取 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`、`docs/context-engineering.md` 和对应专项文档恢复上下文。
6. 如果对话出现重复规划、反复 patch、忘记约定、修改范围扩大或上下文混乱，应先整理交接文档，再开启新对话继续。
7. 临时文件、调试产物、废弃代码和无关日志不得留在仓库中污染后续上下文。

详细规则见 `docs/context-engineering.md`。

## 任务生命周期

任何账号执行任务时，统一遵守 `docs/task-handoff-protocol.md`。

简化流程：请先按照 `AGENTS.md` 和 `docs/task-handoff-protocol.md` 完成启动检查，然后执行任务。完成后更新 `STATUS.md` 和 `docs/tasks/current.md`，再进行交接。

任务开始前必须确认：

- 已读取 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`、`docs/account-switching.md`、`docs/task-handoff-protocol.md`。
- 已根据任务类型读取对应专项文档。
- 已确认当前 Git 状态和允许修改范围。
- 已确认是否存在切换账号带来的新状态、新警告或未完成事项。

任务结束后必须更新：

- `STATUS.md`：记录项目状态、构建结果、已知警告和后续建议。
- `docs/tasks/current.md`：记录当前任务进度、修改文件、未完成事项和下一步。

如果产生新的长期规则，还要同步更新对应规范文档，例如 `DESIGN.md`、`CONTENT_WORKFLOW.md`、`SEO.md`、`DEPLOY.md` 或 `docs/branch-workflow.md`。

## 内容入口和资料位置

- 分享收件目录：`\\RonnieNAS\tmp\分享`
- 讲道收件目录：`\\RonnieNAS\tmp\讲道`
- 分享原始资料：`data/raw/分享/`
- 讲道原始资料：`data/raw/教会讲道/`
- `data/raw/` 是原始资料留存区，发布后默认保留；归档是复制到受保护归档区，不代表删除本目录。
- 分享中间稿：`data/processed/整理后的分享文章/`
- 讲道中间稿：`data/processed/整理后的讲道文章/`
- 整理后的中间稿 Markdown 文件名默认使用中文，保留 `YYYY-MM-DD-经文-中文标题.md` 或现有中文命名风格；不要把 processed 中间稿批量改成英文 slug。
- 正式网站文章：`src/content/posts/`
- 整理报告：`docs/内容整理报告/`
- 网站正文必须保留 Markdown 段落空行；单换行在前台不会形成独立段落。
- `[WD]`、`[SLIDE]`、`[MAP]`、`[PAGE]` 等讲稿/投影片来源标记不得进入中文原稿、processed 或正式 posts。
- 讲道内容的 frontmatter `date` 一律使用整理发布时的日期，不从原始文件名、讲道内容、历史讲道日期或用户旧日期线索推断；补录旧讲道也按整理发布当天进入网站时间线。普通非讲道文章如用户明确指定发布日期，仍按对应内容流程处理。

## 基本命令

安装依赖：

```shell
npm install
```

本地开发：

```shell
npm run dev
```

构建验证：

```powershell
npm.cmd run build
```

Windows PowerShell 下不要直接使用 `npm run build`，否则可能因 `npm.ps1` 被 Execution Policy 阻止而失败。需要运行 npm 脚本时，优先使用 `npm.cmd ...`，例如 `npm.cmd run build`。

预览构建结果：

```shell
npm run preview
```

同步远端：

```shell
npm run sync
```

## 交接规则

任何账号在结束当前工作前，都必须检查：

- 当前分支和 Git 状态是否清楚。
- 是否更新了 `docs/tasks/current.md`。
- 是否说明了已经完成什么、还没完成什么、下一步是什么。
- 是否说明了修改过哪些文件。
- 是否运行过必要验证；如果没有，写明原因。

`docs/tasks/current.md` 是多个账号之间的接力棒。不要只把交接信息留在聊天里。

