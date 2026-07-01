# 当前任务

## 任务名称

个人网页项目发布工作流规范同步更新。

## 当前状态

已完成个人网页项目侧的内容发布规范同步，重点补齐本次讲道发布后发现的三个长期规则：

```text
1. 网站正文必须保留 Markdown 段落空行，避免前台合并成一整段。
2. [WD]、[SLIDE]、[MAP]、[PAGE] 等讲稿/投影片来源标记不得进入中文原稿、processed 或正式 posts。
3. 补录旧讲道、旧文章或用户明确指定发布日期时，frontmatter date 必须保留用户确认日期，不得被导出日覆盖。
```

## 已修改文件

```text
AGENTS.md
CONTENT_WORKFLOW.md
docs/统一内容整理与发布流程.md
docs/content-style.md
docs/content-publishing-error-prevention.md
skills/article-workflow.md
docs/tasks/current.md
```

## 已完成内容

### 1. 项目入口文档更新

`AGENTS.md` 已把 `docs/content-publishing-error-prevention.md` 加入内容/文章/讲道/分享任务的必读文档。

同时在内容入口和资料位置中补充：

```text
- 正文必须保留 Markdown 段落空行。
- 讲稿/投影片来源标记不得进入最终正文。
- 用户指定旧发布日期时，date 不得被导出日覆盖。
```

### 2. 内容发布入口规范更新

`CONTENT_WORKFLOW.md` 已新增“正文 Markdown 规范”，明确：

```text
- 段落之间必须保留空行。
- Admin 编辑区能看到换行，不代表前台会分段。
- [WD]、[SLIDE]、[slide]、[SLIDE - ...]、[TIMELINE SLIDE - ...]、[MAP]、[PAGE ...] 等标记必须清理。
- 清理必须覆盖中文原稿合并、发布前 Markdown 生成、导出到网站三个阶段。
```

同时把旧规则“date 必须是实际发布当天”修正为：

```text
date 默认使用实际发布当天；但补录旧讲道、旧文章或用户明确指定发布日期时，必须使用用户确认的发布日期，不能被导出当天、文件修改时间或脚本运行日期覆盖。
```

### 3. 统一发布流程更新

`docs/统一内容整理与发布流程.md` 已新增“正文与日期质量门”，把段落空行、来源标记清理、指定日期保留写入正式流程。

### 4. 内容风格规范更新

`docs/content-style.md` 已在 Paragraph Formatting 和 Quality Checklist 中补充网站 Markdown 要求：

```text
- 网站 Markdown 段落之间保留空行。
- 不要在压缩翻译草稿时删除所有空行。
- 清理讲稿/投影片标记。
- 发布后检查正文是否正常分段、是否无来源标记残留。
```

### 5. 防错清单更新

`docs/content-publishing-error-prevention.md` 已新增三项防错：

```text
9. 正文段落空行不能被压扁
10. 讲稿/投影片标记不得进入正文
11. 旧讲道补录日期不得被导出日期覆盖
```

并把这三项加入“发布前强制检查”。

### 6. Article Workflow skill 更新

`skills/article-workflow.md` 已加入对应规则，确保另一个 Codex 账号处理内容发布时也会读取并执行这些检查。

## 验证结果

本轮只修改 Markdown 文档，没有改动网站运行代码、Astro 页面、CSS 或脚本，因此未运行 `npm run build`。

已检查工作区改动范围，当前只包含上述文档修改。

## 下一步

如需把这些规范正式保存到远端，需要单独提交并推送本次文档修改。
