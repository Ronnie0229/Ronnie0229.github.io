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

当前主工作区：

```text
C:\Users\caoyi\Projects\各人网页项目
```

当前分支：

```text
main
```

当前阶段：

```text
Bible Knowledge Layer v1 已完成、合并 main，并已 push 到 origin/main。
```

当前提交：

```text
879d81d feat: add Bible Knowledge Layer v1
```

最近验证结果：

```text
npm.cmd run check:knowledge
Posts checked: 158
Errors: 0
Warnings: 0

npm.cmd run build
188 page(s) built
[build] Complete!

git status --short
空

git push
45c184d..879d81d main -> main
```

当前下一步不是继续开发功能，而是：

```text
Post-Deploy Verification and Worktree Cleanup
```

目标是确认发布后输出稳定，再决定是否清理临时 worktree 与 feature 分支。

## 3. Phase 0：文档补强

状态：已完成。

### 目标

把 Bible Knowledge Layer 从通用想法整理成适配当前项目的可执行技术蓝图。

### 涉及文件

```text
docs/knowledge/ARCHITECTURE.md
docs/knowledge/ROADMAP.md
```

### 验收结果

- `ARCHITECTURE.md` 已写入。
- `ROADMAP.md` 已写入。
- 后续 Phase 1 - Phase 6 已基于该路线执行完成。

## 4. Phase 1：Knowledge Core

状态：已完成。

### 目标

建立最小可用的知识层核心模块，从现有文章 frontmatter 和正文中自动派生知识信息。

### 已新增文件

```text
src/lib/knowledge/scripture.ts
src/lib/knowledge/text.ts
src/lib/knowledge/topics.ts
src/lib/knowledge/related.ts
src/lib/knowledge/posts.ts
src/lib/knowledge/schema.ts
src/lib/knowledge/index.ts
```

### 已实现能力

- 经文字段解析。
- 圣经书卷识别。
- 旧约 / 新约 / mixed / unknown 判断。
- Markdown 清理。
- fallback description 生成。
- wordCount / readingTimeMinutes 计算。
- 本地 topics 推断。
- related posts 打分。
- PostKnowledge 统一对象。
- JSON-LD 基础 builder。

## 5. Phase 2：JSON-LD 抽离

状态：已完成。

### 目标

把 `BaseLayout.astro` 中已有的结构化数据逻辑迁移到 `src/lib/knowledge/schema.ts`，降低 Layout 复杂度，并为后续扩展打基础。

### 涉及文件

```text
src/layouts/BaseLayout.astro
src/lib/knowledge/schema.ts
```

### 已实现能力

- `createWebSiteSchema`
- `createPersonSchema`
- `createBlogPostingSchema`
- `createSiteGraph`
- `createCollectionPageSchema`
- `createBibleBookPageGraph`
- `createBreadcrumbList`
- `createItemList`

### 边界

- 不生成 FAQ Schema。
- 不生成页面没有依据的隐藏内容。
- 不降低 meta / OG / Twitter / canonical 输出。

## 6. Phase 3：文章页接入 Knowledge Layer

状态：已完成。

### 目标

让文章页使用 PostKnowledge，但读者看到的页面保持不变。

### 涉及文件

```text
src/pages/posts/[slug].astro
src/lib/knowledge/related.ts
src/lib/knowledge/posts.ts
```

### 已实现能力

- 文章页接入 `buildPostKnowledge(post)`。
- `BaseLayout` 的 description 使用 `knowledge.description`。
- keywords 增加 `bibleBooks` 与 `topics`。
- 相关文章算法迁移到 `getRelatedPosts(post, posts, 3)`。
- 页面 HTML、正文、URL、留言和阅读数 DOM 保持不变。

## 7. Phase 4：书卷页、Search Index、Sitemap、RSS 接入

状态：已完成。

### 目标

让知识层不只服务文章页，也服务书卷页、站内搜索索引、sitemap 和 RSS。

### 涉及文件

```text
src/pages/bible/index.astro
src/pages/bible/[book].astro
src/pages/search-index.json.ts
src/pages/sitemap.xml.ts
src/lib/knowledge/schema.ts
```

### 已实现能力

- `/bible/` 使用 `buildPostKnowledge(post).bibleBooks` 统计书卷文章数。
- `/bible/[book]/` 使用 Knowledge Layer 的 `bibleBooks` 筛选文章。
- `search-index.json` 保留原字段并新增：
  - `bibleBooks`
  - `testament`
  - `topics`
  - `wordCount`
  - `readingTimeMinutes`
- `sitemap.xml` 保留现有 URL，并为书卷页补充基于关联文章最新日期的 `lastmod`。
- `rss.xml` 保持原结构，避免订阅兼容风险。

## 8. Phase 5：Admin 摘要自动生成与发布体验增强

状态：已完成。

### 目标

改善 Admin 后台新建文章体验：摘要为空或过短时，保存前自动从正文生成摘取式摘要。同时保留构建层 fallback，保证绕过 Admin 的发布方式也安全。

### 涉及文件

```text
assets/admin/decap.js
assets/admin/config.yml
```

### 已实现能力

- `preSave` 中保留 articleId 自动生成。
- 同一个 `preSave` listener 中处理 articleId 与 description fallback。
- description 为空、少于 20 字或占位文本时，从 body 自动生成摘要。
- 用户认真填写的 description 不会被覆盖。
- `config.yml` 中 description 字段增加中文提示。

### 边界

- 不调用 AI。
- 不访问外部 API。
- 不改变 GitHub OAuth / Cloudflare Access。
- 不改变文章存储位置。

## 9. Phase 6：验证脚本与回归检查

状态：已完成。

### 目标

为 Bible Knowledge Layer 增加自动检查脚本，避免以后文章增多或功能扩展后出现隐性错误。

### 涉及文件

```text
scripts/check-knowledge-layer.mjs
package.json
```

### 已实现能力

新增 npm script：

```json
{
  "scripts": {
    "check:knowledge": "node scripts/check-knowledge-layer.mjs"
  }
}
```

检查脚本会验证：

- 非草稿文章是否有 title / date。
- description 或 fallback 是否可用。
- scripture 是否可识别书卷。
- PostKnowledge 生成是否报错。
- topics / wordCount / readingTimeMinutes 是否正常。
- JSON-LD 基础结构是否可 stringify。
- Admin `preSave` 是否仍只有一个 listener。
- Admin 是否仍包含 articleId 与 description fallback 逻辑。

当前结果：

```text
Posts checked: 158
Errors: 0
Warnings: 0
```

## 10. 当前下一步：发布后验证与 worktree 清理准备

状态：待执行。

### 目标

在不开发新功能、不修改前台视觉、不部署、不 push 的前提下，确认 main 合并后的本地与构建输出稳定，并准备清理临时 worktree 的手顺。

### 建议任务文件

```text
docs/tasks/current.md
```

当前任务标题：

```text
Post-Deploy Verification and Worktree Cleanup
```

### Codex 本次应做

- 确认当前分支是 `main`。
- 确认 `git status --short` 为空或只包含本次文档更新。
- 运行 `npm.cmd run check:knowledge`。
- 运行 `npm.cmd run build`。
- 检查关键构建产物：
  - `dist/index.html`
  - `dist/search-index.json`
  - `dist/sitemap.xml`
  - `dist/rss.xml`
  - `dist/bible/index.html`
- 读取 `git worktree list`，确认 feature worktree 仍存在。
- 给出是否可以清理 worktree 的建议。

### Codex 本次不应做

- 不修改文章。
- 不修改前台页面。
- 不修改 CSS。
- 不修改 Knowledge Layer 代码。
- 不新增功能。
- 不部署。
- 不 push。
- 不删除 worktree。
- 不删除 feature 分支。
- 不自动 commit。

## 11. 后续可能的 Phase 7：搜索 UI 增强

状态：暂不执行。

只有在发布后验证稳定、worktree 清理完成后，再考虑 Phase 7。

可能方向：

- 利用 `search-index.json` 新增字段，在站内搜索 UI 中增加按书卷 / 主题筛选。
- 在搜索结果中显示阅读时间、书卷、主题。
- 为 `/bible/[book]/` 接入更明确的 CollectionPage JSON-LD 输出。
- 添加简单的知识统计页面，例如按书卷、主题、年份浏览。

Phase 7 的边界：

- 仍不修改历史文章正文。
- 仍不改变文章 URL。
- 仍不引入数据库。
- 仍不调用外部 AI API。
- 搜索 UI 改动必须单独开分支或 worktree。

## 12. 每次交给 Codex 的任务格式

每次给 Codex 派发任务时，建议使用以下格式：

```text
当前 worktree：
C:\Users\caoyi\Projects\各人网页项目

当前阶段：Post-Deploy Verification and Worktree Cleanup

本次只允许修改：
- docs/tasks/current.md
- docs/knowledge/ROADMAP.md
- docs/knowledge/POST_DEPLOY_CHECK.md（如需要）

本次不允许：
- 不改文章正文
- 不改页面视觉
- 不改 URL
- 不引入数据库
- 不调用外部 API
- 不部署
- 不 push
- 不删除 worktree

完成后必须：
- 说明检查结果
- 运行 npm.cmd run check:knowledge
- 运行 npm.cmd run build
- 不提交，等待验收
```

## 13. 清理策略

确认线上部署正常后，可以清理临时 worktree 与 feature 分支：

```powershell
cd C:\Users\caoyi\Projects\各人网页项目
git worktree list
git worktree remove C:\Users\caoyi\Projects\各人网页项目-bible-knowledge
git branch -d feature/bible-knowledge-layer
```

如果 `git worktree remove` 提示目录不干净，不要强制删除，先检查并汇报。
