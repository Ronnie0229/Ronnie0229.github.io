# Sermon Content → Website Rendering 最小绑定（C-min）

状态：`CURRENT / STRUCTURE_V2_HARD_GATE`

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

2026-09-13 incident 后补充两条机械约束：

- 连续两个以上 `1）/2）/3）` 这类中文视觉编号，或同一行内出现多个此类编号，不能作为最终 Website Markdown；它们必须先规范成标准 Markdown list，否则 presentation Gate fail-closed。
- 公开讲道的小组分享标题统一为 `小组分享`；`小组分享（WAKACHIAI）`、仅 `WAKACHIAI` 或其他仍保留 `WAKACHIAI` 的小组分享 H2/H3 不能进入公开页面。该项只是 Website display normalization，不修改讲道 Owner 的正式翻译稿或 fidelity verdict。

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

Current success terminal：`SERMON_PRESENTATION_STRUCTURE_PASS`。

Current failure terminal：`SERMON_PRESENTATION_STRUCTURE_FAIL`。

Current success completion ceiling：`publication_structure_ready`；failure ceiling：`publication_structure_blocked`。

Gate 除既有 production residue / scripture label / TOC / list / small-group checks 外，必须同时检查：`paragraph_collapse_guard`、`rendered_block_density`、`heading_render_integrity`，并输出 rendered paragraph/heading/list/blockquote/text-char/content-block metrics。像 2026-10-04《前方弯道》事故中“4091 字 / 1 paragraph / 0 H2”的形态必须 deterministic fail-closed。

输出仍保留 `legacy_mechanical_status=MECHANICAL_PRESENTATION_PASS|FAIL` 仅用于历史 chronology/兼容；该字段不再是 publication acceptance authority。Current publication 只能采信 `SERMON_PRESENTATION_STRUCTURE_PASS + publication_structure_ready`。

该结构 PASS 仍不能替代 fidelity/semantic PASS、Project Bible/CUV exactness、完整 reader-quality/aesthetic 判断、build/deploy/live technical PASS；但它是 sermon Website publish 前不可缺少的结构硬门。

## 7.1 正式强制执行位置（2026-10-18）

**先检查、再发布；不得依赖发布后的网页试听或人工发现问题代替发布前检查。**

1. Sermon Owner 在发布前生成 Markdown，完成独立 fidelity + Project Bible Gate，并产出 sermon-presentation/v1 的 frozen-text 顺序与 SHA 身份 PASS。此后 Website 只能检查呈现结构，不能改写或重新判断 E1。
2. Website `scripts/consume_publication_package.py` 的 sermon `dry-run` 和 `publish` 调用现有 `scripts/validate_sermon_presentation.mjs`；绑定 `prepublish.path + prepublish.sha256 + metadata.batch_id`，必须收到 `SERMON_PRESENTATION_STRUCTURE_PASS`、`publication_structure_ready` 和当前 Markdown/rendered HTML SHA 证据，才允许进入导入流程。命中缺证据、SHA drift、validator/renderer failure、标题/列表/段落 FAIL 均 fail-closed，`plan` 只可用于只读计划，不代表发布准入。
3. `scripts/content_workflow.py publish sermon` 直接入口也执行同一来源的结构校验，禁止绕过 package consumer 直接写入。结构检查在任何 Website post 写入、Astro build、Git commit/push 或部署触发**之前**。
4. 结构专项必检查：三并列要点的编号、层级、来源段落与经文范围和显式答案不能消失；多个并列要点必须采用统一 Markdown heading/list/block，不能以混合 H2/普通文本或中文视觉编号伪装；四项理由、小组分享要按语义正确列表化；经文出处、引语、结束语及荣耀颂不能因渲染折叠丢失。**内容语义一致性的人工判定及 frozen fidelity 记录仍归 Sermon Owner**，Website 机械 Gate 不可声称已代替语义审查。
5. 只采信与**本次正式候选 SHA** 绑定的 gate terminal；任何旧稿、旧 HTML、旧截图、历史 PASS 或仅仅 build PASS 都不能代替。发布后仍做 live/手机端/RSS/Sitemap/notification 验证，但这些是额外验收，不是允许先发布的理由。
6. 记录 PASS/FAIL/BLOCKED chronology。发现排版 FAIL，先最小修改 presentation 层，重新验证受控正文 exact identity 和整个 rendered gate；未达 PASS 不得继续正式发布，不引入新服务、平台或后台任务。


## 8. Current implementation anchors

本 binding 的 current facts 来自：

- `src/pages/posts/[slug].astro`：`render(post)`、H2/H3 filter、`<ol>` TOC、frontmatter title/H1、scripture metadata display、`<Content />`；
- `src/styles/global.css`：`.article-toc ol`、`.article-content p`、H2/H3 current article styles；
- `CONTENT_WORKFLOW.md` / `docs/content-style.md`：单换行不等于公开页面独立 paragraph 的现有 Owner rule；
- Website runtime dependency `@astrojs/markdown-remark`：B-min 使用与 Astro 同源 Markdown processor 做同一 candidate 的 rendered block probe。
