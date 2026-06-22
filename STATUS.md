# 项目状态

最后更新：2026-06-22 09:30:00 +09:00

## 当前结论

已完成“内容整理发布防重复错误”整改：把 2026-06-21 Patrick 讲道发布中暴露的问题整理成固定防错清单，并写入仓库流程文档、交接记忆文档和 Codex 记忆更新 note，方便不同账号切换时直接读取执行。

正式开发目录：

```text
C:\Users\caoyi\Projects\各人网页项目
```

旧桌面目录 `C:\Users\caoyi\Desktop\Codex\这人网页项目` 只作为跳转目录保留。NAS 只作为收件、原始资料和受保护归档位置，不在 NAS 上运行 Git、Node 或 Astro。

## 本轮已完成

1. 复盘上次讲道整理发布流程中出现的问题：PDF 提取错序/截断、翻译可能摘要化、description 截断、经文字段不完整、中文 slug 不稳定、articleId 可能失效、导入脚本重写旧文、Astro 缓存、线上验证域名选择、交接记录不足。
2. 新增 `docs/content-publishing-error-prevention.md`，作为分享/讲道发布前强制执行的防错清单。
3. 更新 `CONTENT_WORKFLOW.md`，加入发布防错清单入口和核心风险摘要。
4. 更新 `skills/article-workflow.md`，让另一个 Codex 账号读取 skill 时能看到防错要求。
5. 更新 `docs/codex-handoff-memory.md`，把防错清单加入项目级交接记忆。
6. 更新 `docs/content-style.md`，补充网站发布 metadata 质量要求。
7. 更新 `docs/task-handoff-protocol.md`，让内容类任务启动检查包含防错清单。
8. 写入 Codex 记忆更新 note：`C:\Users\caoyi\.codex\memories\extensions\ad_hoc\notes\2026-06-22-ronniecross-publishing-error-prevention.md`。

## 本轮整改重点

- `*.extracted.txt` 只能作为机器提取辅助，不能直接作为翻译或发布源。
- 双语 PDF 必须确认翻译源语言，并检查源语言底稿是否漏页尾、漏例子、漏经文引用或错序。
- 讲道翻译必须逐句忠实完整，不允许用摘要、提纲、主题整理或灵修改写替代翻译。
- 发布前必须人工核对 `description`、`scripture`、title、speaker/author、slug、source、`articleId`。
- 讲道导入后必须检查 diff，排除旧讲道文章被批量重写带来的无关改动。
- 新文章不出现在构建产物或出现 Duplicate id 时，先确认源文件唯一，再清理 `.astro` 本地缓存重建。
- 线上验证优先使用正式域名 `https://ronniecross.com/`。

## 当前工作边界

本轮没有处理既有未跟踪目录：

```text
?? .ai-bridge/
```

`AGENTS.md` 在本轮开始前已经有未提交修改；本轮没有修改该文件。

## 后续建议

1. 后续所有“分享/讲道/整理发布”任务，启动检查必须读取 `docs/content-publishing-error-prevention.md`。
2. 如果要进一步减少人工修正，可单独开任务改进 `scripts/import_sermons.py`：只导入指定 folder、生成完整 description、识别完整经文范围、稳定 slug、避免重写旧文。