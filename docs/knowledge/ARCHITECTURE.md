# Bible Knowledge Layer Architecture

## 1. 项目定位

Bible Knowledge Layer（圣经知识层）是 RonnieCross 网站的构建层能力，用来把现有 Markdown 文章在 Astro build 阶段自动转换成更清晰的圣经知识结构、SEO 结构化数据、GEO / AI Search 语义信息和站内检索索引。

它不是新的文章系统，也不是数据库化改造。

核心目标：

- 保持现有 Markdown + Astro Content Collection 文章模式。
- 保持读者看到的标题、摘要、正文和页面体验基本不变。
- 不要求作者为了 GEO 改写文章。
- 不依赖 Codex 发布流程。
- 不依赖 Admin 发布流程。
- 所有文章只要进入 `src/content/posts/`，就能在 Astro build 时自动获得知识层能力。
- 为 Google、ChatGPT、Gemini、Perplexity 等搜索 / AI 工具提供真实、结构化、可验证的页面语义。

## 2. 当前项目基础

当前项目已经具备 Bible Knowledge Layer 的基础条件：

- Astro 5 静态站。
- 文章位于 `src/content/posts/`。
- 内容 schema 位于 `src/content/config.ts`。
- 后台 Decap CMS 配置位于 `assets/admin/config.yml`。
- 后台保存钩子位于 `assets/admin/decap.js`。
- 已有圣经书卷数据位于 `src/data/bible.ts`。
- 文章页位于 `src/pages/posts/[slug].astro`。
- 站点 Layout 位于 `src/layouts/BaseLayout.astro`。
- 已有书卷页：
  - `src/pages/bible/index.astro`
  - `src/pages/bible/[book].astro`
- 已有输出索引：
  - `src/pages/search-index.json.ts`
  - `src/pages/sitemap.xml.ts`
  - `src/pages/rss.xml.ts`
- `BaseLayout.astro` 目前已经生成部分 JSON-LD：
  - `WebSite`
  - `Person`
  - `SearchAction`
  - `BlogPosting`

因此，本项目不是从零开始，而是把现有 SEO / Bible / Search / JSON-LD 逻辑收束为统一的知识层。

## 3. 非目标

本项目明确不做以下事情：

- 不把文章从 Markdown 迁移到数据库。
- 不引入新的 CMS 取代现有 Admin。
- 不强制修改历史文章标题。
- 不强制修改历史文章摘要。
- 不强制修改历史文章正文。
- 不改变现有文章 URL。
- 不为了 SEO / GEO 堆砌关键词。
- 不生成与页面内容无关的隐藏文本。
- 不生成没有页面依据的 FAQ Schema。
- 不把 Codex 作为 GEO 的必要环节。
- 不把 Admin 作为 GEO 的必要环节。

## 4. 总体数据流

所有发布入口都应该进入同一个构建层：

```text
Codex 整理发布
Admin 后台发布
本地手动编辑
GitHub 直接修改
未来其他导入方式
        ↓
src/content/posts/*.md
        ↓
Astro Content Collection
        ↓
src/lib/knowledge/
        ↓
PostKnowledge / SiteKnowledge / BibleBookKnowledge
        ↓
文章页 / 书卷页 / search-index / sitemap / RSS / JSON-LD
        ↓
最终 HTML 与静态资源
```

关键原则：GEO / Knowledge Layer 发生在 Astro build 阶段，而不是发布入口阶段。

## 5. 第一阶段建议目录

第一阶段优先新增：

```text
src/lib/knowledge/
├── scripture.ts
├── text.ts
├── topics.ts
├── related.ts
├── posts.ts
├── schema.ts
└── index.ts
```

暂时不优先建立大型 `data/knowledge/` 数据集。当前网站已经有大量文章和 frontmatter，第一阶段应先从现有内容中自动派生知识层。

## 6. 模块职责

### 6.1 `scripture.ts`

职责：解析 `scripture` 字段，并从中识别圣经书卷、旧约 / 新约、章节和经文范围。

输入示例：

```text
罗马书 8:1-11
罗马书 8:1-4, 12-17
马太福音 16:24
约翰福音 8:31-36
创世记 14:13-32:28
罗马书 8:28等
```

第一阶段目标：

- 识别书卷名。
- 判断旧约 / 新约。
- 尽量解析常见章节和节范围。
- 对复杂格式保留原始字符串，不报错。

输出建议：

```ts
interface ScriptureKnowledge {
  raw: string;
  books: string[];
  testament: "old" | "new" | "mixed" | "unknown";
  references: ScriptureReference[];
}
```

### 6.2 `text.ts`

职责：处理 Markdown 正文纯文本。

功能：

- 清理 Markdown 语法。
- 去除代码块、链接、图片语法、HTML 标签。
- 统计中文字数 / 粗略字数。
- 计算阅读时间。
- 生成 fallback description。

Admin 后台可以在 `preSave` 层自动填充摘要，但构建层仍然必须能生成 fallback description。这样即使 Admin 没填、Codex 没填、本地手动漏填，页面也不会缺少 description。

### 6.3 `topics.ts`

职责：根据 title、description、scripture、tags、body 进行主题推断。

第一阶段不要调用 AI，也不要接外部 API。使用可审查的本地词典规则。

示例：

```ts
const TOPIC_RULES = {
  恩典: ["恩典", "白白", "礼物", "赦免"],
  信心: ["信心", "相信", "信靠"],
  十字架: ["十字架", "舍己", "跟随"],
  自由: ["自由", "释放", "捆绑"],
  祷告: ["祷告", "代祷", "祈求"]
};
```

### 6.4 `related.ts`

职责：统一相关文章打分逻辑。

当前文章页已经有 relatedPosts 逻辑，第一阶段应迁移到统一模块，并保持视觉输出基本不变。

推荐打分：

```text
同一圣经书卷 +100
同一经文章节 +80
同一主题 +50
同一分类 +20
同一标签 +10
日期接近 +5
```

第一阶段只要能替代现有“同书卷 / 同分类 / 同标签”的逻辑即可，不必一次实现所有权重。

### 6.5 `posts.ts`

职责：生成文章知识对象。

建议核心函数：

```ts
buildPostKnowledge(post, allPosts)
```

输出建议：

```ts
interface PostKnowledge {
  slug: string;
  articleId: string;
  title: string;
  description: string;
  fallbackDescription: string;
  date: Date;
  author: string;
  category: string;
  tags: string[];
  scripture: string;
  scriptureKnowledge: ScriptureKnowledge;
  bibleBooks: string[];
  testament: "old" | "new" | "mixed" | "unknown";
  topics: string[];
  wordCount: number;
  readingTimeMinutes: number;
  relatedPosts: unknown[];
}
```

### 6.6 `schema.ts`

职责：集中生成 JSON-LD。

当前 `BaseLayout.astro` 中的结构化数据应逐步迁移到本模块。

第一阶段至少支持：

- `WebSite`
- `Person`
- `SearchAction`
- `BlogPosting`
- `BreadcrumbList`

后续可选：

- `CollectionPage`
- `ItemList`
- `DefinedTerm`
- `Thing`

重要限制：JSON-LD 必须真实反映页面内容，不做欺骗式隐藏内容，不生成没有页面依据的 FAQ。

### 6.7 `index.ts`

职责：统一导出知识层 API，减少页面直接依赖内部模块。

## 7. 页面接入策略

### 7.1 `BaseLayout.astro`

当前问题：`BaseLayout.astro` 同时负责页面结构、导航、主题切换、访问统计和 JSON-LD 生成。

目标：

- 保持页面视觉不变。
- 保持现有 meta / Open Graph / Twitter Card 输出。
- 把 JSON-LD 构建逻辑逐步抽离到 `src/lib/knowledge/schema.ts`。
- `BaseLayout.astro` 只负责接收结构化数据并输出。

### 7.2 `src/pages/posts/[slug].astro`

目标：

- 使用 `buildPostKnowledge(post, allPosts)`。
- 文章视觉结构不变。
- 相关文章逻辑来自 `related.ts`。
- keywords / description / readingTime / wordCount / JSON-LD 由知识层提供。
- 如果 frontmatter description 正常，优先使用人工 description。
- 如果 description 为空或过短，使用构建层 fallback description。

### 7.3 `src/pages/bible/index.astro` 与 `src/pages/bible/[book].astro`

目标：

- 继续作为圣经书卷索引页。
- 使用知识层判断每个书卷关联的文章。
- 后续为书卷页输出 `CollectionPage`、`ItemList`、`BreadcrumbList`。
- 不改变现有 URL。

### 7.4 `src/pages/search-index.json.ts`

目标：

在现有字段基础上增加知识字段：

```json
{
  "bibleBooks": ["罗马书"],
  "testament": "new",
  "topics": ["恩典", "信心"],
  "wordCount": 3200,
  "readingTimeMinutes": 8
}
```

第一阶段只生成数据，不一定马上改变搜索 UI。

### 7.5 `src/pages/sitemap.xml.ts`

目标：

- 保持现有 sitemap 输出。
- 文章页继续包含在 sitemap。
- 书卷页继续包含在 sitemap。
- 后续可把书卷页 `lastmod` 设置为该书卷下最新文章日期。

### 7.6 `src/pages/rss.xml.ts`

目标：

- 保持 RSS 稳定。
- 不破坏订阅。
- 后续可选加入 category / tags / scripture 信息。

## 8. Admin 发布体验

当前 Admin 使用 Decap CMS，配置在 `assets/admin/config.yml`，保存钩子在 `assets/admin/decap.js`。

目标：

- Admin 继续写入 Markdown。
- Admin 不需要理解 GEO。
- Admin 新建文章时，如果 `description` 为空、太短或是占位文本，可以在 `preSave` 中根据正文自动填入摘取式摘要。
- 自动摘要应优先使用稳定规则，不默认调用 AI。
- 构建层仍然必须提供 fallback description，避免绕过 Admin 时失效。

推荐规则：

```text
description 为空
或少于 20 个中文字符
或等于“待补充”“简介”“摘要”等占位词
→ 从正文清理 Markdown 后截取 120-160 个中文字符
→ 尽量在句号、问号、叹号处截断
```

## 9. SEO / GEO / AI Search 原则

Bible Knowledge Layer 服务 SEO / GEO / AI Search，但不牺牲文章真实性。

允许：

- meta description fallback。
- JSON-LD 描述真实页面内容。
- `BlogPosting`、`BreadcrumbList`、`CollectionPage`、`ItemList`。
- 从正文、标题、经文、标签中派生 topics。
- 为站内搜索生成更丰富的 JSON 索引。

不允许：

- 给 AI 写隐藏 prompt。
- 用 `display:none` 塞与正文无关的关键词。
- 生成页面没有依据的 FAQ Schema。
- 用结构化数据声明页面没有表达的内容。
- 为了 GEO 改坏文章阅读体验。

## 10. 验证原则

每个阶段都必须可独立验证、可回滚。

基础验证：

```text
npm run build
```

如果 CodexPro 的 bash / WSL 环境无法运行 build，可以由本机 PowerShell 手动运行。

后续建议新增：

```text
scripts/check-knowledge-layer.mjs
```

检查：

- 非草稿文章是否有 title。
- 非草稿文章是否有 date。
- description 是否有人工值或 fallback。
- scripture 是否至少能识别书卷。
- JSON-LD 是否能正常 stringify。
- search-index 是否包含知识字段。
- sitemap 是否仍包含文章页和书卷页。

## 11. 长期方向

长期目标不是把网站变成复杂 CMS，而是让当前 Markdown 静态站逐渐拥有知识网站能力。

最终形态：

```text
文章内容：Markdown
发布入口：Codex / Admin / Git
构建引擎：Astro
知识层：src/lib/knowledge
互动数据：Cloudflare D1（评论、阅读数）
输出：HTML / JSON-LD / RSS / sitemap / search-index
```

这条路线保留当前项目的简单性，同时提高 SEO、GEO、AI Search 与站内知识组织能力。

## Phase 7-3 Topic Vocabulary

Phase 7-3 expands the Knowledge topics layer without changing Markdown / MDX frontmatter.

Source of truth:
```text
src/lib/knowledge/topics.ts
```

Each topic uses this structure:
```ts
interface KnowledgeTopic {
  id: string;
  zh: string;
  en: string;
  aliases: string[];
  description: string;
}
```

Runtime behavior:
```text
- inferTopics() still returns zh topic names, so existing search and Bible pages keep working.
- TOPIC_RULES remains exported for compatibility.
- Topic inference uses title, description, scripture, tags, and cleaned body text.
- The vocabulary is intentionally curated; it should not force-retag posts or rewrite article content.
```
