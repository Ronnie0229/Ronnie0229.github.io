# 当前任务

## 任务名称

上下文工程规则补充。

## 当前目标

把不同任务是否新开对话、如何精简上下文、如何避免长会话污染、如何把重要信息写回仓库文档的规则，补充到项目文档体系中。

## 本任务范围

已修改：

```text
AGENTS.md
STATUS.md
docs/account-switching.md
docs/branch-workflow.md
docs/context-engineering.md
docs/task-handoff-protocol.md
docs/tasks/current.md
```

未修改：

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

## 已完成

1. 更新 `AGENTS.md`：
   - 将 `docs/context-engineering.md` 加入新账号必读文档。
   - 新增上下文工程章节。
2. 新增 `docs/context-engineering.md`：
   - 记录目标和基本原则。
   - 记录各类任务对应的必读文档。
   - 记录新开对话判断规则。
   - 记录 Conversation Budget。
   - 记录 Context Compression。
   - 记录对话、分支、worktree 对应关系。
   - 记录临时文件和调试产物管理。
   - 记录新对话启动和结束 Checklist。
3. 更新 `docs/task-handoff-protocol.md`：
   - 将 `docs/context-engineering.md` 加入一级必读文件。
   - 新增“何时新开对话”。
   - 新增会话预算和上下文压缩规则。
4. 更新 `docs/branch-workflow.md`：
   - 新增“对话、分支、Worktree 的对应关系”。
5. 更新 `docs/account-switching.md`：
   - 将 `docs/context-engineering.md` 加入新账号接手必读顺序。
   - 将 `docs/context-engineering.md` 加入新账号开始前检查清单。
6. 更新 `STATUS.md` 和本文件完成交接。

## 验证结果

本轮只修改 Markdown 流程文档，没有修改网站源码、内容文章、脚本或构建配置，因此未运行 `npm.cmd run build`。

已使用 `git diff` 检查当前改动范围。

## 当前状态

文档规则已写入，准备随本轮收尾提交入库并推送。

## 下一步

1. 后续任何新对话都应先读取 `docs/context-engineering.md`，再按任务类型读取专项文档。
2. 可另开任务讨论是否新增 `PROJECT_MEMORY.md`，用于记录长期项目记忆和设计、技术取舍原因。
3. `.ai-bridge/` 是既有未跟踪目录，本轮不纳入提交。
