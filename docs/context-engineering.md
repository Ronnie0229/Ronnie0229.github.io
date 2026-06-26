# Context Engineering 上下文工程

## 目的

减少 Codex 长会话带来的上下文污染，让每个账号、每个对话、每个 worktree 都只携带当前任务真正需要的信息。

本项目不把聊天记录当作长期记忆。长期事实、长期规则、当前状态、设计决策、内容流程、SEO 规则和部署流程必须写入仓库文档；Codex 对话只作为单次任务工作区。

## 基本原则

1. 长期记忆写入仓库文档，不依赖账号聊天记忆。
2. 一个 Codex 对话只处理一个明确任务，或一个连续 Feature。
3. 任务完成后，必须更新 `STATUS.md` 和 `docs/tasks/current.md`。
4. 任务类型明显切换时，应新开对话。
5. 大型或并行任务使用独立分支，必要时使用独立 worktree。
6. 临时文件、调试产物、废弃代码和无关日志不得长期留在仓库中。
7. 不要在同一个对话里混合 UI、内容发布、SEO、部署、后台、Bug 修复等无关任务。
8. 如果对话出现重复规划、反复修改、忘记约定、修改范围扩大或上下文混乱，应先整理交接文档，再开启新对话继续。

## 项目文档写入默认规则

当用户提出项目文档类请求时，默认直接写入项目文件，而不是只在聊天里生成 Markdown。

适用说法包括：

```text
更新当前任务
写入当前任务
整理当前任务
写入项目文档
更新 STATUS
更新 AGENTS
```

执行规则：

1. 用户说“当前任务文档”时，默认指 `docs/tasks/current.md`。
2. 只要用户没有明确说“只给我看看，不要改文件”，项目文档类修改请求默认落盘到仓库文件。
3. 当前会话具备写入能力时，应主动写入文件，不要求用户每次显式指定 CodexPro。
4. 如果只是讨论草稿、方案比较或用户明确要求不要落盘，才只在聊天中输出内容。
5. 文档落盘后，按任务需要同步更新 `STATUS.md` 和 `docs/tasks/current.md`。
## 按任务类型读取文档

### UI / 主题 / 前端

必读：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
docs/context-engineering.md
DESIGN.md
docs/branch-workflow.md
```

适用范围：

- 首页、文章页、组件和布局。
- 深浅色主题。
- CSS 变量、响应式、视觉层级、阴影和圆角。
- 视觉回归和浏览器验证。

### 内容整理 / 文章发布

必读：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
docs/context-engineering.md
CONTENT_WORKFLOW.md
docs/统一内容整理与发布流程.md
docs/content-style.md
docs/content-publishing-error-prevention.md
skills/article-workflow.md
SEO.md
```

适用范围：

- 分享资料整理。
- 讲道资料翻译整理。
- Markdown 正式文章生成。
- frontmatter、description、scripture、slug、articleId 检查。

### SEO / GEO

必读：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
docs/context-engineering.md
SEO.md
src/content/config.ts
src/pages/sitemap.xml.ts
src/pages/rss.xml.ts
src/pages/search-index.json.ts
```

适用范围：

- 标题、描述、分类、标签、canonical。
- sitemap、RSS、搜索索引。
- 面向搜索引擎和 AI 摘要系统的结构化信息。

### 部署 / 后台 / Cloudflare

必读：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
docs/context-engineering.md
DEPLOY.md
RUNBOOK.md
docs/轻量后台使用与配置.md
wrangler.jsonc
functions/
```

适用范围：

- 构建失败排查。
- Cloudflare Pages / Functions 配置。
- 后台 API。
- 部署和线上验证。

### Bug 修复

必读：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
docs/context-engineering.md
RUNBOOK.md
```

再根据 Bug 所属范围继续读取专项文档。

Bug 修复对话应尽量短。修完、验证、记录后，不要在同一个对话里继续开展新功能。

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

## Conversation Budget 会话预算

如果出现以下任意情况，应考虑结束当前对话，先完成交接记录，再开启新对话继续：

1. 已完成一个完整 Feature。
2. 已完成一次 PR 或一次可提交任务。
3. 已进行了大量 Debug。
4. 已经过多轮修改。
5. 已明显开始讨论新的主题。
6. 对话中已经积累大量与下一步无关的信息。

结束对话不是丢失上下文，而是把上下文压缩回仓库文档。

## Context Compression 上下文压缩

结束一个对话前，不要把重要信息只留在聊天中。必须把可复用信息压缩回仓库文档：

1. `STATUS.md`：当前状态、验证结果、已知警告、后续建议。
2. `docs/tasks/current.md`：本轮目标、范围和禁止修改范围、已完成事项、修改文件、未完成事项、下一步。
3. `PROJECT_DECISIONS.md`：长期技术和流程决策。
4. `DESIGN.md`：设计系统、UI 规则、主题视觉变化。
5. `SEO.md`：SEO / GEO / metadata / sitemap / RSS 相关变化。
6. `CONTENT_WORKFLOW.md`：内容整理和发布流程变化。
7. `DEPLOY.md` 或 `RUNBOOK.md`：部署、构建、后台运维变化。
8. `docs/branch-workflow.md`：分支、worktree、多账号协作规则变化。

## 对话、分支、Worktree 的对应关系

推荐关系：

```text
一个任务 = 一个 Codex 对话 = 一个任务分支
大型或并行任务 = 一个独立 worktree
```

不要在同一个对话、同一个分支或同一个 worktree 中混合多个无关任务。

示例：

```text
UI 主题重设计：
- 对话：theme-redesign
- 分支：task/theme-redesign-YYYYMMDD
- Worktree：各人网页项目-theme-redesign

文章整理发布：
- 对话：article-publishing
- 分支：task/article-publishing-YYYYMMDD
- Worktree：通常可使用正式目录，除非与开发任务并行

SEO 改造：
- 对话：seo-engine
- 分支：task/seo-engine-YYYYMMDD
- Worktree：各人网页项目-seo
```

## 临时文件和调试产物管理

Codex 执行任务时不得长期保留无意义中间产物。

允许短期使用：

```text
tmp/
logs/
```

任务结束前必须处理：

1. 无用临时文件应删除。
2. 有保留价值的日志应整理成简洁结论，写入 `STATUS.md` 或 `docs/tasks/current.md`。
3. 不要提交构建产物、缓存、依赖目录、浏览器 profile、测试截图等无说明产物。
4. 不要新增 `old`、`backup`、`new2`、`final-final` 等缺少说明的文件。
5. 如果必须保留临时文件，应在 `docs/tasks/current.md` 说明原因和清理时机。

## 新对话启动 Checklist

新开 Codex 对话后，先确认：

1. 当前目录是正式仓库或正确 worktree。
2. 已读取 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`。
3. 已读取本文件 `docs/context-engineering.md`。
4. 已根据任务类型读取专项文档。
5. 已确认当前任务允许修改和禁止修改的范围。
6. 已确认是否需要新分支或独立 worktree。
7. 已确认不依赖旧聊天记忆也能执行当前任务。

## 结束对话 Checklist

结束当前对话前，必须确认：

1. 已完成任务，或已经形成明确交接点。
2. 已记录实际修改文件。
3. 已运行必要验证；如果没有验证，已写明原因。
4. 已更新 `STATUS.md`。
5. 已更新 `docs/tasks/current.md`。
6. 已将长期规则写入对应规范文档。
7. 已删除或说明临时文件。
8. 已写清下一个账号或新对话应该从哪里开始。
