# AGENTS.md

## 项目总入口

任何 ChatGPT / Codex 账号接手本项目时，必须先阅读本文件。

本项目不依赖任何单个账号的聊天记忆。项目事实、当前状态、设计规范、内容流程、部署流程和交接记录，都以仓库内文档为准。

## 项目定位

- 本仓库是 RonnieCross 个人文章网站的唯一正式代码仓库。
- 网站开发、设计、内容整理、SEO、部署、后台配置和维护都在本仓库完成。
- 正式本地仓库路径：`C:\Users\caoyi\Projects\各人网页项目`。
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
7. `docs/tasks/current.md`

按任务类型继续阅读：

- 设计 / 前端 / 主题：`DESIGN.md`、`docs/ui-spec.md`、`风格重新设计素材/ronniecross_astro_design_spec.md`
- 内容 / 文章 / 讲道 / 分享：`CONTENT_WORKFLOW.md`、`docs/统一内容整理与发布流程.md`、`docs/content-style.md`、`skills/article-workflow.md`
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
12. Markdown 文档中的多行命令、路径、日志和文件列表必须使用标准三反引号代码块；代码块开头可以标注 text、shell 或 powershell，结尾单独一行关闭，避免单反引号或转义字符造成格式损坏。

## 内容入口和资料位置

- 分享收件目录：`\\RonnieNAS\tmp\分享`
- 讲道收件目录：`\\RonnieNAS\tmp\讲道`
- 分享原始资料：`data/raw/分享/`
- 讲道原始资料：`data/raw/教会讲道/`
- 分享中间稿：`data/processed/整理后的分享文章/`
- 讲道中间稿：`data/processed/整理后的讲道文章/`
- 正式网站文章：`src/content/posts/`
- 整理报告：`docs/内容整理报告/`

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

```shell
npm run build
```

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
