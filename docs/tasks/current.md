# 当前任务

## 任务名称

2026-06-21 Patrick 讲道整理与发布。

## 当前目标

将讲道收件目录中的 Patrick 讲道 PDF 按统一讲道流程处理：入库、提取、忠实中文翻译、受保护归档、生成网站文章、构建、推送、线上验证，并完成任务交接。

## 本任务范围

允许修改：

```text
data/processed/整理后的讲道文章/
src/content/posts/
docs/内容整理报告/讲道文章目录.csv
STATUS.md
docs/tasks/current.md
```

允许操作：

```text
\\RonnieNAS\tmp\讲道         # 收件目录，处理后移动新 PDF
\\RonnieNAS\share\教会讲道   # 受保护归档，只新增和读取
```

禁止操作：

```text
删除、移动、覆盖 \\RonnieNAS\share 中既有文件
在 NAS 上运行 Git、Node、Astro 或文件监听
触碰无关的 .ai-bridge/ 未跟踪目录
```

## 已完成

1. 完成启动检查，读取 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`、`docs/account-switching.md`、`docs/task-handoff-protocol.md`、`CONTENT_WORKFLOW.md`、`SEO.md`、`docs/统一内容整理与发布流程.md`、`docs/content-style.md`、`skills/article-workflow.md`、`docs/codex-handoff-memory.md`。
2. 检查 `\\RonnieNAS\tmp\讲道`，确认新 PDF：`[TF] Romans 15_1-13 Gospel Harmony - Google Docs.pdf`。
3. 入库到 `data/raw/教会讲道/20260621罗马书15章1-13节福音带来的和谐_Patrick/` 并生成提取稿。
4. 以英文稿为翻译源完成逐句忠实中文翻译，生成 `罗马书15章1-13节福音带来的和谐_中文.txt`。
5. 归档到 `\\RonnieNAS\share\教会讲道\20260621罗马书15章1-13节福音带来的和谐_Patrick`，脚本校验通过：2 个文件，670467 字节。
6. 生成网站文章：`src/content/posts/2026-06-21-romans-15-1-13-gospel-harmony.md`。
7. 生成 processed 文章：`data/processed/整理后的讲道文章/2026-06-21-romans-15-1-13-gospel-harmony.md`。
8. 更新讲道目录报告：`docs/内容整理报告/讲道文章目录.csv`。
9. 修正本篇摘要、经文、slug 和 articleId。
10. 构建成功，推送提交 `d695f66`。
11. 正式域名线上验证成功。

## 构建结果

命令：

```powershell
npm.cmd run build
```

结果：成功。

关键输出：

```text
[build] 188 page(s) built in 7.37s
[build] Complete!
```

说明：构建前曾因 Astro 本地缓存导致新文件显示异常；已清理 `.astro` 并重建，最终无 Duplicate id 警告。

## 发布结果

提交：

```text
d695f66 Publish Patrick sermon on Romans 15
```

线上 URL：

```text
https://ronniecross.com/posts/2026-06-21-romans-15-1-13-gospel-harmony/
```

验证：HTTP 200，标题、讲员、经文、摘要和正文关键内容均存在。

## 受保护目录检查

归档只新增了本次讲道目录，未移动、删除或覆盖 `\\RonnieNAS\share` 中既有文件。

## 当前状态

任务已完成。当前仓库只剩既有未跟踪目录：

```text
?? .ai-bridge/
```

## 交接注意

1. 后续讲道翻译必须继续按 `docs/content-style.md` 的 Translation Fidelity 执行：逐句忠实翻译，不用摘要、提纲或主题整理替代翻译。
2. 运行讲道导入脚本后要检查旧讲道 diff；本轮导入脚本曾临时重写 2026-06-14 旧讲道，已恢复到任务开始前状态。
3. 如新文章未出现在构建产物中，优先清理 `.astro` 本地缓存后重建。