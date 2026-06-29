# 任务交接协议

## 目标

本文件规定每一次 ChatGPT / Codex 账号执行任务前和任务结束后的固定流程。

目的不是增加流程负担，而是确保不同账号、不同对话、不同电脑在接手 RonnieCross 项目时，都能从仓库文档恢复上下文，不依赖任何单个账号的聊天记忆。

## 一句话流程

每次执行任务时，请先按照 `AGENTS.md` 和 `docs/task-handoff-protocol.md` 完成启动检查，然后执行任务。完成后更新 `STATUS.md` 和 `docs/tasks/current.md`，再进行交接。给 Codex 写任务时，必须把“完成后更新 `docs/tasks/current.md` 的任务完成状态”写入执行要求。

## 任务开始前：一级必读

任何任务开始前，都必须先阅读以下文件：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
docs/account-switching.md
docs/task-handoff-protocol.md
docs/context-engineering.md
```

### 每个文件的作用

| 文件 | 作用 |
| --- | --- |
| `AGENTS.md` | 项目总入口、通用规则、禁区和基本命令。 |
| `STATUS.md` | 当前项目状态、最近构建结果、已知警告和后续建议。 |
| `docs/tasks/current.md` | 当前任务接力棒，记录上一轮做到哪里、哪些还没做。 |
| `docs/account-switching.md` | 多账号切换规则、接手流程和常见风险。 |
| `docs/task-handoff-protocol.md` | 本文件，规定每次任务的启动和结束流程。 |
| `docs/context-engineering.md` | Codex 对话拆分、上下文压缩、会话预算和临时文件管理规则。 |

## 任务开始前：按任务类型继续阅读

### 网站开发、组件、样式、主题

继续阅读：

```text
PROJECT.md
PROJECT_DECISIONS.md
RUNBOOK.md
DESIGN.md
docs/branch-workflow.md
```

如果涉及现有主题重设计素材，还要阅读：

```text
风格重新设计素材/ronniecross_astro_design_spec.md
```

### 文章整理、讲道整理、分享资料发布

继续阅读：

```text
CONTENT_WORKFLOW.md
SEO.md
docs/统一内容整理与发布流程.md
docs/content-style.md
skills/article-workflow.md
```

### SEO、文章元信息、站点地图、RSS、搜索索引

继续阅读：

```text
SEO.md
src/content/config.ts
src/pages/sitemap.xml.ts
src/pages/rss.xml.ts
src/pages/search-index.json.ts
```

### 部署、上线、后台配置

继续阅读：

```text
DEPLOY.md
RUNBOOK.md
docs/网站后台使用与配置.md
wrangler.jsonc
functions/
```

### Git、worktree、跨账号协作

继续阅读：

```text
docs/branch-workflow.md
docs/account-switching.md
```

## 启动检查清单

开始任何任务前，先确认：

1. 当前目录是正式仓库：`C:\Users\caoyi\Projects\个人网页项目`。
2. 已读取一级必读文件。
3. 已根据任务类型读取对应专项文档。
4. 已查看 `docs/tasks/current.md`，确认上一轮交接事项。
5. 已查看 `STATUS.md`，确认最近构建状态和已知警告。
6. 已检查 Git 状态，不能误以为工作区干净。
7. 已同步线上最新状态：开始任何本地修改前，默认先执行 `git pull --rebase origin main`，尤其是用户可能通过 Admin 后台发布过文章时，必须先把远端最新文章和代码同步到本地。
8. 已明确本次任务允许修改哪些文件。
9. 已明确本次任务禁止修改哪些文件。
10. 如果任务涉及部署、推送、删除、覆盖、移动资料，必须先得到用户明确许可。

## 默认受保护范围

除非任务明确要求，否则不要修改：

```text
src/
functions/
assets/
scripts/
src/content/posts/
data/raw/
data/processed/
wrangler.jsonc
```

如果确实需要修改这些范围，必须在执行前说明原因、影响和验证方式。

## 何时新开对话

建议新开对话的情况：

1. 当前任务已经完成，准备开始另一个不同类型任务。
2. 对话已经很长，出现重复规划、忘记约定、反复修改、修改范围扩大的迹象。
3. 任务从一个领域切换到另一个领域，例如从 UI 切换到内容发布、从 SEO 切换到部署。
4. 上一个任务产生大量 diff、日志、构建错误或调试过程，可能污染后续上下文。
5. 需要另一个账号接手同一项目的新任务。

可以继续同一个对话的情况：

1. 仍在处理同一个任务的连续步骤。
2. 正在修复刚才同一任务产生的构建错误。
3. 当前对话上下文仍然清晰，且没有切换任务类型。
4. 修改范围仍然保持在本次任务允许范围内。

原则：一个对话对应一个任务，不把整个项目塞进一个长对话。

## 任务执行中规则

1. 不要依赖账号记忆，以仓库文档为准。
2. 不要扩大任务范围。
3. 不要删除未知文件。
4. 不要覆盖原始资料。
5. 不要在 NAS 路径运行 Git、Node、Astro、Codex 或文件监听。
6. 文档中多行命令、路径、日志和文件列表必须使用标准三反引号代码块。
7. PowerShell 环境下构建优先使用 `npm.cmd run build`。
8. 如果发现新警告、新风险或文档冲突，先记录到 `STATUS.md` 和 `docs/tasks/current.md`。
9. 项目文档类请求默认直接写入项目文件；用户说“当前任务文档”时，默认指 `docs/tasks/current.md`。除非用户明确要求“只给我看看，不要改文件”，否则不要只在聊天里生成 Markdown。当前会话具备写入能力时，不需要用户每次显式指定 CodexPro。

## Conversation Budget（会话预算）

如果出现以下任意情况，应考虑结束当前对话，先完成交接记录，再开启新对话继续：

1. 已完成一个完整 Feature、PR 或阶段性任务。
2. 已进行了大量 Debug 或多轮修改。
3. 已明显开始讨论新的主题。
4. 对话中包含大量已经无关的日志、diff 或临时方案。
5. Codex 开始重复规划、忘记前提或扩大修改范围。

## Context Compression（上下文压缩）

结束一个对话前，不要把重要信息只留在聊天中。必须把可复用信息压缩回仓库文档：

1. 当前状态、验证结果、已知警告写入 `STATUS.md`。
2. 本轮目标、修改文件、未完成事项和下一步写入 `docs/tasks/current.md`。
3. 长期技术或流程决策写入 `PROJECT_DECISIONS.md`。
4. 设计变化写入 `DESIGN.md`。
5. SEO / GEO 变化写入 `SEO.md` 或对应新增规范文档。
6. 内容整理流程变化写入 `CONTENT_WORKFLOW.md`、`docs/content-style.md` 或 `skills/article-workflow.md`。
7. 部署流程变化写入 `DEPLOY.md` 或 `RUNBOOK.md`。

## 任务结束后：必须更新的文件

每次任务结束前，至少更新：

```text
STATUS.md
docs/tasks/current.md
```

如果任务产生新的长期规则，还要更新对应文档：

| 新增内容 | 应更新文件 |
| --- | --- |
| 通用入口规则 | `AGENTS.md` |
| 项目状态、构建结果、已知风险 | `STATUS.md` |
| 当前任务进度、下一步、修改文件 | `docs/tasks/current.md` |
| 多账号切换规则 | `docs/account-switching.md` |
| 任务启动/结束规则 | `docs/task-handoff-protocol.md` |
| 设计规则 | `DESIGN.md` |
| 内容整理规则 | `CONTENT_WORKFLOW.md` |
| SEO 规则 | `SEO.md` |
| 部署规则 | `DEPLOY.md` |
| Git / worktree 规则 | `docs/branch-workflow.md` |
| 长期技术和流程决策 | `PROJECT_DECISIONS.md` |

## STATUS.md 更新要求

任务结束时，`STATUS.md` 至少记录：

1. 本次完成了什么。
2. 是否运行构建或其他验证。
3. 验证结果是否成功。
4. 新增或仍存在的警告。
5. 未处理事项和原因。
6. 是否有需要用户确认的事项。

## docs/tasks/current.md 更新要求

给 Codex 写执行任务时，必须在任务中明确要求 Codex 完成后更新 `docs/tasks/current.md` 的任务完成状态。不能只让 Codex 构建、提交、push 后结束；它还应把完成情况回写到当前任务文档。

任务结束时，`docs/tasks/current.md` 至少记录：

1. 任务名称。
2. 当前目标。
3. 本次允许和禁止修改范围。
4. 已完成事项。
5. 构建或验证结果。
6. 修改文件列表。
7. 未完成事项。
8. 下一个账号应该做什么。
9. 需要人工确认的事项。
10. 如果任务由 Codex 执行，还要记录 Codex 是否已完成任务、构建结果、提交哈希、push 结果，以及线上验证是否仍需用户手动确认。

## 构建验证要求

涉及文档以外的代码、样式、内容或配置时，默认需要运行：

```powershell
npm.cmd run build
```

纯文档任务也建议运行构建，但如果当前工具无法执行，可以记录原因，并由用户本地运行后把结果补回 `STATUS.md` 和 `docs/tasks/current.md`。

## 交接成功标准

一个新账号不看旧聊天记录，只阅读仓库文档后，应能说清楚：

1. 项目正式目录在哪里。
2. 当前任务做到哪一步。
3. 最近一次构建是否成功。
4. 当前有哪些已知警告。
5. 哪些目录是默认禁止修改的。
6. 本次任务下一步是什么。
7. 完成后要更新哪些交接文件。

如果做不到，说明交接文档还需要补充。
