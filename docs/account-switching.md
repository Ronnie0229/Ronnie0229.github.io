# 多账号切换说明

## 目标

这个项目可以被不同 Codex 账号、不同电脑或不同对话继续维护。换账号时，不靠“上一个对话记得什么”，而是靠仓库里的文档快速恢复上下文。

## 正式工作目录

当前 Windows 本机正式开发目录：

```text
C:\Users\caoyi\Projects\各人网页项目
```

旧桌面目录 `C:\Users\caoyi\Desktop\Codex\这人网页项目` 只作为跳转目录保留。收到网站开发、分享整理、讲道发布、文档维护任务时，都应先切换到正式工作目录。

## 新账号接手时先读什么

建议按这个顺序阅读：

| 顺序 | 文件 | 作用 |
| --- | --- | --- |
| 1 | `AGENTS.md` | 项目入口规则，包含路径、禁区、常用命令和协作边界。 |
| 2 | `STATUS.md` | 当前状态、最近验证结果、未完成事项。 |
| 3 | `docs/tasks/current.md` | 当前这一轮任务的目标、范围、验收和构建结果。 |
| 4 | `docs/task-handoff-protocol.md` | 每次任务开始前读什么、结束后更新什么。 |
| 5 | `docs/context-engineering.md` | 新对话拆分、上下文压缩、会话预算和临时文件管理规则。 |
| 6 | `PROJECT.md` | 项目定位、技术栈、目录职责和源码来源。 |
| 7 | `PROJECT_DECISIONS.md` | 已确认的长期决策，避免反复讨论。 |
| 8 | `RUNBOOK.md` | 日常开发、内容发布、排查问题的操作手册。 |

## 不同任务继续读什么

| 任务类型 | 继续阅读 |
| --- | --- |
| 网站界面、组件、样式 | `DESIGN.md`、`风格重新设计素材/ronniecross_astro_design_spec.md` |
| 分享资料或讲道资料整理发布 | `CONTENT_WORKFLOW.md`、`docs/统一内容整理与发布流程.md`、`skills/article-workflow.md` |
| SEO、标题、描述、分类、文章元数据 | `SEO.md`、`src/content/config.ts` |
| 构建、预览、上线验证 | `DEPLOY.md`、`RUNBOOK.md` |
| Git 分支和提交习惯 | `docs/branch-workflow.md` |
| 当前任务执行状态 | `docs/tasks/current.md`、`.ai-bridge/agent-status.md` |

## 换账号前检查清单

1. 运行 `git status --short`，确认有哪些未提交文件。
2. 按照 `docs/task-handoff-protocol.md` 的结束流程，把当前任务进度写入 `STATUS.md` 和 `docs/tasks/current.md`。
3. 如果任务跨对话交接，把执行摘要写入 `.ai-bridge/agent-status.md`。
4. 不要把临时输出、密钥、账号信息、构建缓存写进文档。
5. 不要用旧桌面目录继续做正式开发。
6. 在交接说明里写清楚下一个账号应该先做什么。

## 新账号开始前检查清单

1. 确认当前目录是 `C:\Users\caoyi\Projects\各人网页项目`。
2. 运行 `git status --short`，先识别已有改动，不能随意回滚。
3. 先读 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`、`docs/task-handoff-protocol.md`、`docs/context-engineering.md`。
4. 只在任务允许的范围内修改文件。
5. 涉及上线时，先确认用户是否明确允许部署和推送。

## 受保护目录

普通文档任务不得修改这些位置：

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

如果某个任务确实需要改这些位置，必须由用户明确说明，并在执行前解释影响。

## 账号切换时最容易出错的地方

1. 把旧桌面目录当成正式仓库继续改。
2. 只看对话历史，不看仓库文档。
3. 在没有确认的情况下推送、部署或清理文件。
4. 在 NAS 路径上跑 Node、Astro、Git、文件监听，导致慢或状态混乱。
5. 忽略已有未提交改动，误以为工作区是干净的。

## 成功标志

换账号后，只要新账号能在不读取旧对话全文的情况下，通过这些文档说清楚下面几件事，就说明交接成功：

1. 正式开发目录在哪里。
2. 当前任务做到哪一步。
3. 哪些目录不能碰。
4. 构建、预览、发布分别怎么做。
5. 分享资料和讲道资料分别从哪里进入、如何归档和发布。