# 当前任务

## 任务名称

内容整理发布防重复错误整改。

## 当前目标

复盘上次讲道整理发布中出现的所有流程问题，分析原因，形成固定整改方案，并写入仓库流程文档和记忆更新说明，避免后续不同 Codex 账号重复踩坑、重复消耗额度。

## 本任务范围

允许修改：

```text
CONTENT_WORKFLOW.md
skills/article-workflow.md
docs/codex-handoff-memory.md
docs/content-style.md
docs/task-handoff-protocol.md
docs/content-publishing-error-prevention.md
STATUS.md
docs/tasks/current.md
C:\Users\caoyi\.codex\memories\extensions\ad_hoc\notes\*.md
```

不处理：

```text
AGENTS.md          # 本轮开始前已有未提交修改，不触碰
.ai-bridge/        # 既有未跟踪目录，不触碰
src/content/posts/ # 本轮不改文章正文
scripts/           # 本轮只写流程，不改脚本
```

## 已完成

1. 读取并复盘 `STATUS.md`、`docs/tasks/current.md`、`docs/content-style.md`、`CONTENT_WORKFLOW.md`、`skills/article-workflow.md`、`docs/codex-handoff-memory.md`。
2. 梳理上次讲道发布问题：
   - 双语 PDF 普通提取会混排、错序、截断。
   - 机器提取稿 `*.extracted.txt` 不能直接作为最终翻译源。
   - 翻译任务容易被整理文章习惯带偏成摘要或主题整理。
   - 自动摘要 `description` 会截断。
   - 自动经文识别可能丢节数。
   - 中文 slug 不稳定，URL 可能不清晰。
   - 重命名后 `articleId` 可能失效或变空。
   - 讲道导入脚本会重写旧讲道文章。
   - Astro 本地缓存会导致新文章不出现或 Duplicate id 警告。
   - GitHub Pages 默认域名不能替代正式域名验证。
   - 内容提交后还需要单独更新交接文件。
3. 新增 `docs/content-publishing-error-prevention.md`，写入问题、原因、整改和发布前强制检查清单。
4. 更新 `CONTENT_WORKFLOW.md`、`skills/article-workflow.md`、`docs/codex-handoff-memory.md`、`docs/content-style.md`、`docs/task-handoff-protocol.md`，把防错清单纳入固定流程。
5. 写入 Codex 记忆更新 note：`C:\Users\caoyi\.codex\memories\extensions\ad_hoc\notes\2026-06-22-ronniecross-publishing-error-prevention.md`。
6. 更新 `STATUS.md` 和本文件完成交接。

## 本轮不运行构建的原因

本轮只修改 Markdown 流程文档和记忆 note，不修改网站文章、页面组件、脚本或构建配置。无需运行 `npm.cmd run build`。

## 当前状态

待最终提交前检查。已知本轮开始前存在：

```text
 M AGENTS.md
?? .ai-bridge/
```

本轮不触碰这两项。

## 交接注意

1. 下一个账号处理分享或讲道时，除常规流程文档外，必须读取 `docs/content-publishing-error-prevention.md`。
2. 以后不要再把 PDF 机器提取稿直接当作翻译源，不要再接受截断的 description，不要再跳过 diff 检查。
3. 如果用户要求进一步自动化，优先改造 `scripts/import_sermons.py`，让它支持只导入指定讲道 folder，并自动生成完整 description 和稳定英文 slug。