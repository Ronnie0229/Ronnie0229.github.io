# 项目状态

最后更新：2026-06-26 +09:00

## 当前结论

已完成“Context Engineering / 上下文工程规则”补充：把 Codex 长会话精简、新对话判断、会话预算、上下文压缩、对话/分支/worktree 对应关系、临时文件管理等规则写入仓库文档。

正式开发目录：

```text
C:\Users\caoyi\Projects\各人网页项目
```

旧桌面目录 `C:\Users\caoyi\Desktop\Codex\这人网页项目` 只作为跳转目录保留。NAS 只作为收件、原始资料和受保护归档位置，不在 NAS 上运行 Git、Node 或 Astro。

## 本轮已完成

1. 更新 `AGENTS.md`：
   - 将 `docs/context-engineering.md` 加入新账号必读顺序。
   - 新增 `Context Engineering（上下文工程）` 章节，明确一个 Codex 对话只处理一个明确任务，长期规则必须写入仓库文档。
2. 新增 `docs/context-engineering.md`：
   - 记录上下文工程目标、基本原则、任务类型对应的必读文档、新开对话判断、会话预算、上下文压缩、对话/分支/worktree 对应关系、临时文件管理、新对话启动 Checklist 和结束对话 Checklist。
3. 更新 `docs/task-handoff-protocol.md`：
   - 将 `docs/context-engineering.md` 加入一级必读文件。
   - 新增“何时新开对话”。
   - 新增 Conversation Budget 和 Context Compression 规则。
4. 更新 `docs/branch-workflow.md`：
   - 新增“对话、分支、Worktree 的对应关系”。
5. 更新 `docs/account-switching.md`：
   - 将 `docs/context-engineering.md` 加入新账号接手必读顺序和新账号开始前检查清单。
6. 更新 `docs/tasks/current.md` 完成本轮交接。

## 当前工作边界

本轮只修改流程和规范文档，没有修改网站源码、内容文章、脚本、部署配置或后台代码。

修改范围：

```text
AGENTS.md
STATUS.md
docs/account-switching.md
docs/branch-workflow.md
docs/context-engineering.md
docs/task-handoff-protocol.md
docs/tasks/current.md
```

## 验证结果

本轮为纯 Markdown 文档更新，未修改网站源码、Astro 内容、脚本或构建配置，因此未运行 `npm.cmd run build`。

已通过 `git diff` 检查当前改动范围。

## 已知注意事项

1. 后续新开 Codex 对话时，应把 `docs/context-engineering.md` 作为一级必读文档。
2. 以后不要在同一个长对话中混合 UI、SEO、内容发布、部署、后台、Bug 修复等无关任务。
3. 任务结束前必须把重要上下文压缩回 `STATUS.md` 和 `docs/tasks/current.md`，必要时同步写入专项规范文档。
4. `.ai-bridge/` 是既有未跟踪目录，本轮不纳入提交。
