# Branch Workflow

本文件说明 RonnieCross 项目的分支、任务目录和多账号协作规则。

## 核心原则

- `main` 只保存稳定状态。
- 分支按任务命名，不按账号命名。
- 任何账号接手前都要先阅读 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`。
- 任务结束前必须更新 `docs/tasks/current.md`。
- 不清楚当前状态时，不要做会覆盖、丢弃或删除现有工作的操作。

## 分支命名

推荐格式：

```text
task/<task-name>-YYYYMMDD
```

示例：

```text
task/account-switching-system-20260620
task/theme-redesign-20260620
task/article-import-romans-20260620
task/seo-cleanup-20260620
task/deploy-fix-20260620
```

避免使用：

```text
a-dev
b-content
my-test
new-branch
```

原因：账号名和随意命名不能说明任务，不利于下一个账号接手。

## 开始任务前

- 确认当前分支。
- 确认是否有未提交修改。
- 确认任务是否已有 `docs/tasks/current.md` 记录。
- 从稳定主线开始创建任务分支。

## 任务过程中

- 每次只围绕当前任务修改。
- 不把无关文件混入同一个任务。
- 阶段性完成后提交小而清楚的 commit。
- 如果任务方向变化，更新 `docs/tasks/current.md`。

## 合并前

- 检查当前分支是否对应当前任务。
- 检查修改文件范围是否符合任务目标。
- 运行必要验证，通常是 `npm run build`。
- 确认 `docs/tasks/current.md` 已写明完成情况。

## Worktree 使用建议

多个任务并行时，推荐按任务创建 worktree，而不是在同一个目录频繁切换分支。

示例目录：

```text
C:\Users\caoyi\Projects\各人网页项目\
C:\Users\caoyi\Projects\各人网页项目-theme-redesign\
C:\Users\caoyi\Projects\各人网页项目-docs\
```

注意：

- worktree 目录应位于本机 SSD。
- 不要在 NAS 上创建 worktree。
- 每个 worktree 只做一个任务。
- 任务结束后再清理对应 worktree。

## 对话、分支、Worktree 的对应关系

推荐关系：

```text
一个任务 = 一个 Codex 对话 = 一个任务分支
大型或并行任务 = 一个独立 worktree
```

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

不要在同一个分支、同一个 worktree 或同一个对话中混合多个无关任务。

## 多账号切换检查

新账号接手时检查：

- 当前分支是否对应当前任务。
- 是否有未提交修改。
- 是否有 `.ai-bridge/current-plan.md` 正在被另一个 agent 使用。
- `docs/tasks/current.md` 是否描述了当前工作。

## 冲突处理

遇到冲突时：

1. 不要盲目选择某一边。
2. 先判断冲突文件属于内容、样式、配置还是文档。
3. 以当前任务目标和项目文档为准。
4. 解决后运行必要验证。
5. 在 `docs/tasks/current.md` 记录冲突文件和处理方式。

## 禁止事项

- 不要在不了解状态时使用会丢弃本地修改的操作。
- 不要删除其他任务分支或任务目录。
- 不要在 `main` 上做大规模功能开发。
- 不要提交本地缓存、构建产物或依赖目录。
- 不要只在聊天中交接，必须写入 `docs/tasks/current.md`。

## 文档任务如何提交

文档整改类任务应先确认改动只包含文档和允许的 `.ai-bridge` 记录文件。提交前建议检查：

```powershell
git status --short
git diff -- AGENTS.md PROJECT.md PROJECT_DECISIONS.md STATUS.md RUNBOOK.md DESIGN.md CONTENT_WORKFLOW.md SEO.md DEPLOY.md docs/account-switching.md docs/branch-workflow.md docs/tasks/current.md
```

如果任务没有明确授权推送，只能本地提交或等待用户确认，不执行 `git push`。