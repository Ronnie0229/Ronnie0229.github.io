# 当前任务

## 当前任务状态（2026-07-03）

样式入口重构与 Admin 数据概览手机端适配修复已完成，并已推送到 `origin/main`。

本轮完成内容：

```text
1. 前台公开页面样式入口已迁移到 Astro 源码侧：
   - src/styles/tokens.css
   - src/styles/global.css
2. src/layouts/BaseLayout.astro 不再直接加载 /styles/global.css。
3. assets/styles/global.css 已删除，不再保留旧前台样式入口。
4. Admin 样式继续独立维护在 assets/admin/admin.css，不并入前台 global.css。
5. AGENTS.md、DESIGN.md、docs/ui-spec.md 已用中文记录样式入口规则。
6. Admin 数据概览页手机端溢出问题已修复：热门文章和近 30 天阅读趋势面板不再撑破手机宽度。
7. Admin CSS 版本号已更新为 stats-mobile-1，避免线上缓存旧样式。
```

相关提交：

```text
c3b5e7c fix: adapt admin stats panels on mobile
4163180 docs: document css source of truth
137894f refactor: migrate frontend css entry to src styles
```

验证结果：

```text
npm run build 通过。
线上手机端 /admin/stats.html 已确认显示正常。
未修改文章 Markdown。
未修改 data/processed。
未运行 npm audit fix。
```

后续可选清理：

```text
1. assets/styles/global.css 已在后续小任务中删除。
2. 临时 worktree 已清理：
   C:\Users\caoyi\Projects\个人网页项目-css-refactor
```

---

## 上一轮任务记录

## 任务名称

讲道整理项目与个人网页项目工作流差异整改与同步。

## 当前状态

已完成两个项目之间的内容发布工作流差异复核，并同步修正“讲道整理项目 → 个人网页项目”衔接规则。

本轮重点修正：

```text
1. 讲道发布默认必须完成 NAS 受保护归档。
2. 从讲道整理项目导入讲道时，不能只复制 posts 文件就视为完整发布。
3. 未完成 NAS 归档时，必须记录 archive_status=pending，不能在交接中写成完整完成。
4. 只有用户明确要求本次不归档时，才能记录 archive_status=skipped_by_user。
5. 讲道内容的 frontmatter date 必须使用整理发布时的日期；不得从资料文件名、正文内容或旧日期线索推断。
```

## 已修改文件

个人网页项目侧：

```text
CONTENT_WORKFLOW.md
docs/统一内容整理与发布流程.md
docs/content-publishing-error-prevention.md
skills/article-workflow.md
docs/tasks/current.md
```

讲道整理项目侧也同步修改了对应流程文档：

```text
docs/prepublish-md-metadata-quality-gate.md
docs/chinese-to-prepublish-md-workflow.md
docs/end-to-end-content-publishing-workflow.md
docs/workflow-sync-with-website-project-20260701.md
```

## 差异点与整改结果

### 1. NAS 归档规则差异

个人网页项目原本已经有正式规则：

```text
python scripts/content_workflow.py archive-sermon --folder "data/raw/教会讲道/<folder>"
```

讲道整理项目旧文档中有些地方写成“需要时 / 必要时归档”，容易被理解为可选步骤。

现已统一为：

```text
讲道内容默认必须归档到 \\RonnieNAS\share\教会讲道。
```

如果无法访问 NAS 或环境权限不足，必须记录：

```text
archive_status=pending
```

不能把发布流程写成完整完成。

### 2. 直接导出 posts 的风险

本次 2024-06-16 讲道实际走的是：

```text
讲道整理项目
→ 发布前 MD
→ export_to_website_project.py
→ 个人网页项目 src/content/posts
```

这个路径容易绕过个人网页项目 `archive-sermon`。

现已在个人网页项目文档中补充：

```text
从讲道整理项目导入讲道时，不得只把发布前 MD 或导出后的 posts 文件复制进 src/content/posts 就视为完整发布。
```

必须检查：

```text
raw/source 资料交接
processed 副本
正式 posts
articleId
build
线上验证
NAS archive_status
NAS 归档范围仅限原始文件、英文原稿文件、翻译后的中文原稿文件
```

### 3. 日期规则差异

讲道整理项目旧门禁中写过：

```text
网站 frontmatter 的 date 必须是导出/发布当天日期
```

个人网页项目已改成：

```text
讲道内容的 date 一律使用整理发布时的日期；不再判断文件名、正文内容或历史讲道日期。非讲道文章如用户明确指定发布日期，按对应内容流程处理。
```

讲道整理项目已同步该规则。

### 4. 段落与来源标记规则

两个项目已统一：

```text
正文必须保留 Markdown 段落空行。
[WD]、[SLIDE]、[MAP]、[PAGE] 等来源标记不得进入中文原稿、processed 或 posts。
```

## 当前遗留

本轮已继续同步新的 NAS 归档范围规则：归档只保留原始文件、英文原稿文件、翻译后的中文原稿文件；子目录和其他文件不归档。此前补做归档时多复制的发布前 MD、审计目录、网站 posts、processed 副本等内容由用户手动处理。

后续若再次由 CodexPro 执行归档，只能复制三类文件：原始文件、英文原稿文件、翻译后的中文原稿文件。

旧待办已取消：2024-06-16 讲道归档目录由用户手动整理。

## 验证结果

本轮只修改工作流文档，没有改动 Astro 页面、CSS、运行脚本或文章正文，因此未运行 `npm run build`。

完成前已搜索旧规则关键词，讲道整理项目中旧的“date 必须是导出/发布当天”“必要时归档”等表述已清理；个人网页项目中已加入 archive_status、不能只复制 posts 的防错规则，以及 NAS 归档只保留三类文件的范围规则。
