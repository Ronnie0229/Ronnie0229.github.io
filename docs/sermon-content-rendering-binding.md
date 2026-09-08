# Sermon Content → Website Rendering 最小绑定（C-min）

状态：`OWNER_CANDIDATE / PENDING_INDEPENDENT_AUDIT`

Owner：`个人网页项目`

本文件只冻结 2026-09-06 sermon presentation incident 直接需要的 current rendering truth；不修改 renderer/CSS/layout/route/deployment，也不建立通用 Markdown framework。

## 1. 当前 TOC policy / behavior

当前文章页 `src/pages/posts/[slug].astro` 使用 `render(post)` 取得 `headings`，并把 depth=2 或 depth=3 的 heading 全部放入 `tableOfContents`。只要存在 H2/H3，页面就渲染 `<nav class="article-toc"><ol>...</ol></nav>`。当前实现没有 sermon-only TOC disable 开关。

因此本 C-min 只记录 current behavior；不在本任务中取消或修改 TOC。

## 2. H2/H3 与自动编号 interaction

TOC 使用 `<ol>`，浏览器会自动显示列表序号；链接文字直接使用 heading.text。若正文 heading 自己写成 `## 1. 属于基督`，目录视觉上会形成“自动序号 + heading 自带序号”的重复编号风险，例如 `1. 1. 属于基督`。

当前避免方式：用于 sermon publication candidate 的 H2/H3 不自行带 `1.` / `2.` 等阿拉伯数字前缀。B-min Gate 对该已知风险做 deterministic fail-closed 检查。

## 3. title / H1 / body heading 职责边界

文章页面 H1 来自 frontmatter `title`，由 `<h1>{displayTitle}</h1>` 渲染。正文 `<Content />` 在 `.article-content` 内单独渲染 Markdown body。

因此：

- frontmatter `title` 负责页面主标题/H1；
- body H2/H3 负责正文 major sections，并进入当前自动 TOC；
- 不应为了重复页面主标题而机械在 body 再添加等价 H1/H2；若原稿存在有业务意义的正文题头，应按内容 Owner authority 判断，不由 renderer 猜测。

## 4. 普通单换行与 rendered block boundary

当前 Astro Markdown 使用标准 Markdown paragraph semantics。普通文本的单换行不会形成新的 `<p>`；只有明确块级 Markdown 结构（例如空行分隔的段落、列表 item、heading 等）才稳定生成独立 rendered block。

这与现有 `CONTENT_WORKFLOW.md`、`docs/content-style.md` 记录一致：Admin/source 中“看起来换行”不能证明公开页面已分段。

## 5. key points / discussion items 的稳定 syntax

对 A-min 认定为“语义上必须逐项呈现”的 key points、提纲要点、小组讨论/Reflection/Discussion Questions，当前最薄稳定约定是使用标准 Markdown list：

```markdown
## 三个重点

1. 第一项
2. 第二项
3. 第三项
```

或：

```markdown
## 小组讨论

- 问题一
- 问题二
```

当前 Astro renderer 会把它们渲染为 `<ol>/<ul>`，每项为独立 `<li>` block。B-min 不只检查 source list marker，还用 Website 当前 `@astrojs/markdown-remark` processor 渲染同一 source candidate，并验证对应 section 的 rendered HTML 中存在匹配数量的独立 `<li>`。

## 6. scripture metadata 与正文 scripture display

frontmatter `scripture` 是网站 metadata；文章页会把它格式化并用 `toSpokenScriptureDisplay()` 转为 TTS 友好显示，渲染在 `<p class="article-scripture">`。

正文内的经文引用 label 属于 Markdown body 内容，不由上述 metadata 渲染自动补全全角冒号。因此 A-min 要求正文 scripture label 自身以 `：` 结束；B-min 只机械检查 label 形态，不重新判定 CUV 经文正文 exactness。

## 7. B-min Gate locator / interface

稳定 locator：

`scripts/validate_sermon_presentation.mjs`

调用：

```shell
node scripts/validate_sermon_presentation.mjs --source <single-sermon-candidate.md> --candidate-id <stable-id>
```

可选：

```shell
--rendered-output <path>
```

输入：单篇 sermon publication candidate Markdown + caller 提供的 candidate id。

Gate 自己从该同一 source 生成 rendered HTML，因此 source evidence 与 rendered evidence 绑定到同一 candidate；输出 JSON 同时记录 source SHA-256、rendered HTML SHA-256、检查结果与 completion ceiling。

成功 terminal：`MECHANICAL_PRESENTATION_PASS`。

失败 terminal：`MECHANICAL_PRESENTATION_FAIL`。

固定 completion ceiling：`incident_proven_mechanical_checks_only_not_full_reader_quality_or_aesthetic_pass`。

该 PASS 不能替代 fidelity/semantic PASS、Project Bible/CUV exactness、完整 reader-quality/aesthetic 判断、build/deploy/live technical PASS。

## 8. Current implementation anchors

本 binding 的 current facts 来自：

- `src/pages/posts/[slug].astro`：`render(post)`、H2/H3 filter、`<ol>` TOC、frontmatter title/H1、scripture metadata display、`<Content />`；
- `src/styles/global.css`：`.article-toc ol`、`.article-content p`、H2/H3 current article styles；
- `CONTENT_WORKFLOW.md` / `docs/content-style.md`：单换行不等于公开页面独立 paragraph 的现有 Owner rule；
- Website runtime dependency `@astrojs/markdown-remark`：B-min 使用与 Astro 同源 Markdown processor 做同一 candidate 的 rendered block probe。
