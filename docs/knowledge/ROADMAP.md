# Bible Knowledge Layer Roadmap

## 1. 总目标

Bible Knowledge Layer 的目标是让 RonnieCross 当前的 Astro + Markdown 网站，在不改变读者阅读体验、不改变文章写作习惯、不迁移数据库的前提下，逐步获得更强的圣经知识组织、SEO、GEO、AI Search、结构化数据和站内搜索能力。

执行原则：

- 小步推进。
- 每阶段可独立验收。
- 每阶段可回滚。
- 先文档，后代码。
- 先构建层，后页面层。
- 先自动派生，后人工扩展。
- 不一次性重构全站。

## 2. 当前状态

当前 worktree：

```text
C:\Users\caoyi\Projects\各人网页项目-bible-knowledge
```

当前分支：

```text
feature/bible-knowledge-layer
```

当前阶段：

```text
Phase 0: 文档补强
```

## 3. Phase 0：文档补强

### 目标

把 Bible Knowledge Layer 从通用想法整理成适配当前项目的可执行技术蓝图。

### 涉及文件

```text
docs/knowledge/ARCHITECTURE.md
docs/knowledge/ROADMAP.md
```

### 必须写清楚

- 项目定位：服务 SEO / GEO / AI Search / Bible Knowledge Graph。
- 不替代现有 Markdown 文章系统。
- 不主动考虑文章数据库化。
- 不改变文章标题、摘要、正文和读者页面体验。
- 不依赖 Codex 发布。
- 不依赖 Admin 发布。
- 所有文章只要进入 `src/content/posts/`，就在 Astro build 时自动适用。
- 当前项目已有文件与能力。
- 第一阶段目标文件结构。
- JSON-LD 的安全边界。
- Admin 摘要自动生成与构建层 fallback 的关系。

### 不允许做

- 不改代码。
- 不新增 `src/lib/knowledge/`。
- 不修改页面。
- 不修改 Admin。
- 不运行大规模迁移。

### 验收标准

- `ARCHITECTURE.md` 能清楚指导后续实现。
- `ROADMAP.md` 能拆分出清晰阶段。
- Git 状态只包含文档变化。
- 没有代码变化。

## 4. Phase 1：Knowledge Core

### 目标

建立最小可用的知识层核心模块，从现有文章 frontmatter 和正文中自动派生知识信息。

### 涉及文件

新增：

```text
src/lib/knowledge/scripture.ts
src/lib/knowledge/text.ts
src/lib/knowledge/topics.ts
src/lib/knowledge/related.ts
src/lib/knowledge/posts.ts
src/lib/knowledge/schema.ts
src/lib/knowledge/index.ts
```

可能读取但尽量少改：

```text
src/data/bible.ts
src/content/config.ts
```

### 主要任务

1. `scripture.ts`
   - 复用 `src/data/bible.ts` 的书卷列表。
   - 识别 scripture 中出现的书卷。
   - 判断旧约 / 新约 / mixed / unknown。
   - 尝试解析常见章节目格式。
   - 对无法解析的复杂格式保留 raw，不抛错。

2. `text.ts`
   - 从 `search-index.json.ts` 迁移或复用 Markdown 清理逻辑。
   - 生成纯文本。
   - 统计 wordCount。
   - 计算 readingTimeMinutes。
   - 生成 fallback description。

3. `topics.ts`
   - 建立本地主题词典。
   - 根据 title、description、scripture、tags、body 推断 topics。
   - 不调用 AI，不访问外部 API。

4. `related.ts`
   - 封装相关文章打分逻辑。
   - 第一阶段至少保留现有能力：同书卷、同分类、同标签。

5. `posts.ts`
   - 提供 `buildPostKnowledge(post, allPosts)`。
   - 输出统一的 PostKnowledge 对象。

6. `schema.ts`
   - 先封装现有 JSON-LD 生成逻辑的基础函数。
   - 后续 Phase 2 再接入 Layout。

### 不允许做

- 不改变文章页视觉。
- 不改变路由。
- 不修改历史 Markdown 内容。
- 不改 Admin。
- 不引入数据库。
- 不引入外部 AI API。

### 验收标准

- `npm run build` 通过。
- 新增模块可以被 TypeScript / Astro 正常解析。
- 对复杂 scripture 不报错。
- PostKnowledge 能基于现有文章生成。
- 没有页面视觉变化。

## 5. Phase 2：JSON-LD 抽离

### 目标

把 `BaseLayout.astro` 中已有的结构化数据逻辑迁移到 `src/lib/knowledge/schema.ts`，降低 Layout 复杂度，并为后续扩展打基础。

### 涉及文件

```text
src/layouts/BaseLayout.astro
src/lib/knowledge/schema.ts
src/lib/knowledge/index.ts
```

### 主要任务

- 保留现有 `WebSite`、`Person`、`SearchAction`、`BlogPosting` 能力。
- 新增或预留 `BreadcrumbList`。
- `BaseLayout.astro` 从“自己构建 JSON-LD”改为“接收或调用 schema builder”。
- 确保 meta / Open Graph / Twitter Card 不退化。

### 不允许做

- 不改变页面视觉。
- 不删除现有 SEO meta。
- 不生成页面没有依据的 FAQ。
- 不输出欺骗式隐藏内容。

### 验收标准

- `npm run build` 通过。
- 任意文章页仍有 JSON-LD。
- JSON-LD 内容不低于当前水平。
- 页面视觉不变。
- 页面 title / description / canonical 正常。

## 6. Phase 3：文章页接入 Knowledge Layer

### 目标

让文章页使用 PostKnowledge，但读者看到的页面保持不变。

### 涉及文件

```text
src/pages/posts/[slug].astro
src/lib/knowledge/posts.ts
src/lib/knowledge/related.ts
src/lib/knowledge/schema.ts
```

### 主要任务

- 在 `[slug].astro` 中构建 `knowledge = buildPostKnowledge(post, allPosts)`。
- 使用 knowledge 提供：
  - description / fallback description
  - keywords
  - bibleBooks
  - topics
  - relatedPosts
  - structuredData
- 相关文章视觉不变，但算法迁移到 `related.ts`。
- 若 frontmatter description 合格，优先使用人工 description。
- 若 description 为空或过短，使用 fallback description。

### 不允许做

- 不改变文章正文。
- 不改变标题展示。
- 不改变摘要展示样式。
- 不改变 URL。
- 不改变留言 / 阅读数功能。

### 验收标准

- `npm run build` 通过。
- 文章页可正常打开。
- 文章页视觉基本不变。
- 相关文章仍正常显示。
- 缺少 description 的文章也能生成有效 meta description。
- JSON-LD 正常。

## 7. Phase 4：书卷页、Search Index、Sitemap、RSS 接入

### 目标

让知识层不只服务文章页，也服务书卷页、站内搜索索引、sitemap 和 RSS。

### 涉及文件

```text
src/pages/bible/index.astro
src/pages/bible/[book].astro
src/pages/search-index.json.ts
src/pages/sitemap.xml.ts
src/pages/rss.xml.ts
src/lib/knowledge/*
```

### 主要任务

1. 书卷页
   - 使用 knowledge layer 判断书卷关联文章。
   - 后续为书卷页输出 `CollectionPage`、`ItemList`、`BreadcrumbList`。
   - 不改变 `/bible/` 和 `/bible/[book]/` URL。

2. Search Index
   - 在现有字段上新增：
     - bibleBooks
     - testament
     - topics
     - wordCount
     - readingTimeMinutes
   - 第一阶段只生成数据，不一定改搜索 UI。

3. Sitemap
   - 保持现有 URL。
   - 文章页继续输出。
   - 书卷页继续输出。
   - 可选：书卷页 lastmod 使用该书卷下最新文章日期。

4. RSS
   - 保持兼容。
   - 不破坏订阅。
   - 可选添加 category / tags / scripture。

### 不允许做

- 不破坏 RSS 格式。
- 不删除现有 sitemap URL。
- 不改公开 URL。
- 不大改搜索 UI。

### 验收标准

- `npm run build` 通过。
- `/search-index.json` 输出新增知识字段。
- `/sitemap.xml` 仍包含文章页和书卷页。
- `/rss.xml` 正常。
- `/bible/` 和 `/bible/[book]/` 正常。

## 8. Phase 5：Admin 摘要自动生成与发布体验增强

### 目标

改善 Admin 后台新建文章体验：摘要为空或过短时，保存前自动从正文生成摘取式摘要。同时保留构建层 fallback，保证绕过 Admin 的发布方式也安全。

### 涉及文件

```text
assets/admin/decap.js
assets/admin/config.yml
src/lib/knowledge/text.ts
```

### 主要任务

- 在 `assets/admin/decap.js` 的 `preSave` 中扩展逻辑。
- 保留现有 articleId 自动生成。
- 新增 description 检查：
  - 空值。
  - 过短。
  - 占位文本。
- 根据 body 清理 Markdown 后截取 120-160 字。
- 尽量在标点处截断。
- `assets/admin/config.yml` 中可补充 description / scripture / tags 的提示文字。

### 不允许做

- 不默认调用 AI。
- 不覆盖用户认真填写的摘要。
- 不改变后台认证流程。
- 不改变 GitHub OAuth / Cloudflare Access。
- 不改变文章存储位置。

### 验收标准

- 新建文章 description 为空时，保存可自动补充摘要。
- 已有合理 description 不被覆盖。
- articleId 自动生成仍正常。
- Admin 配置仍能被 Decap CMS 读取。
- `npm run build` 通过。

## 9. Phase 6：验证脚本与回归检查

### 目标

为 Bible Knowledge Layer 增加自动检查脚本，避免以后文章增多或功能扩展后出现隐性错误。

### 涉及文件

新增：

```text
scripts/check-knowledge-layer.mjs
```

可能修改：

```text
package.json
README.md
SEO.md
docs/knowledge/ARCHITECTURE.md
docs/knowledge/ROADMAP.md
```

### 主要任务

- 检查非草稿文章是否有 title / date。
- 检查 description 是否有人工值或 fallback。
- 检查 scripture 是否至少能识别书卷。
- 检查 PostKnowledge 生成不报错。
- 检查 JSON-LD 可 stringify。
- 检查 search-index 字段完整。
- 可选新增 npm script：

```json
{
  "scripts": {
    "check:knowledge": "node scripts/check-knowledge-layer.mjs"
  }
}
```

### 不允许做

- 不让检查脚本自动修改文章。
- 不在检查脚本中调用外部 API。
- 不把复杂规则一次性设为 hard fail。

### 验收标准

- `npm run build` 通过。
- `npm run check:knowledge` 通过或输出清晰警告。
- 文档说明如何处理检查结果。

## 10. 推荐执行顺序

建议严格按以下顺序推进：

```text
Phase 0 文档补强
  ↓
Phase 1 Knowledge Core
  ↓
Phase 2 JSON-LD 抽离
  ↓
Phase 3 文章页接入
  ↓
Phase 4 书卷页 / search-index / sitemap / RSS 接入
  ↓
Phase 5 Admin 摘要自动生成
  ↓
Phase 6 验证脚本与回归检查
```

不要跳过 Phase 1 直接改页面。不要先做 Admin。不要先做大规模数据迁移。

## 11. 每次交给 Codex 的任务格式

每次给 Codex 派发任务时，建议使用以下格式：

```text
当前 worktree：
C:\Users\caoyi\Projects\各人网页项目-bible-knowledge

当前阶段：Phase X

本次只允许修改：
- 文件 A
- 文件 B

本次不允许：
- 不改文章正文
- 不改页面视觉
- 不改 URL
- 不引入数据库
- 不调用外部 API

完成后必须：
- 说明改了什么
- 运行 npm run build（如果当前环境可运行）
- 不提交，等待验收
```

## 12. 合并策略

建议每个 Phase 独立 commit。

推荐 commit 粒度：

```text
Phase 0: docs for Bible Knowledge Layer
Phase 1: add knowledge core helpers
Phase 2: extract structured data builders
Phase 3: integrate post knowledge layer
Phase 4: extend bible/search/sitemap/rss outputs
Phase 5: enhance admin description fallback
Phase 6: add knowledge validation script
```

合并回 main 前必须确认：

- `npm run build` 通过。
- 页面视觉没有非预期变化。
- Admin 仍能使用。
- sitemap / RSS / search-index 正常。
- 没有修改历史文章正文。
