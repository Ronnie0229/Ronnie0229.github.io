# Current Task: Final Review and Commit Preparation

## 背景

当前 worktree：

```text
C:\Users\caoyi\Projects\各人网页项目-bible-knowledge
```

当前分支：

```text
feature/bible-knowledge-layer
```

Bible Knowledge Layer v1 已完成 Phase 0 - Phase 6：

```text
Phase 0: docs/knowledge/ARCHITECTURE.md 与 ROADMAP.md
Phase 1: src/lib/knowledge/ 核心 helper
Phase 2: JSON-LD builder 抽离到 src/lib/knowledge/schema.ts
Phase 3: 文章页接入 buildPostKnowledge
Phase 4: 书卷页、search-index、sitemap 接入 Knowledge Layer；RSS 保持兼容
Phase 5: Admin description fallback 与 articleId preSave 逻辑增强
Phase 6: scripts/check-knowledge-layer.mjs 与 check:knowledge 脚本
```

最近验证结果：

```text
npm.cmd run check:knowledge 通过
Posts checked: 158
Errors: 0
Warnings: 0

npm.cmd run build 通过
188 page(s) built
[build] Complete!
```

## 本次任务目标

最终总体验收，确认 Bible Knowledge Layer v1 可以进入提交准备阶段。

这一步不新增功能，不改业务逻辑，只做检查、整理和提交前确认。

## 本次允许操作

允许读取和检查：

```text
全部已修改文件
package.json
scripts/check-knowledge-layer.mjs
docs/knowledge/
docs/tasks/current.md
src/lib/knowledge/
src/layouts/BaseLayout.astro
src/pages/posts/[slug].astro
src/pages/bible/index.astro
src/pages/bible/[book].astro
src/pages/search-index.json.ts
src/pages/sitemap.xml.ts
assets/admin/config.yml
assets/admin/decap.js
```

允许运行：

```powershell
npm.cmd run check:knowledge
npm.cmd run build
git status --short
git diff --stat
```

## 本次不允许操作

- 不修改文章。
- 不修改前台视觉。
- 不修改 CSS。
- 不改 URL。
- 不新增功能。
- 不调用外部 API。
- 不引入数据库。
- 不部署。
- 不 push。
- 不自动提交 commit，除非用户明确要求。

## 最终验收清单

### 1. 文件范围确认

确认改动只集中在：

```text
assets/admin/config.yml
assets/admin/decap.js
docs/knowledge/
docs/tasks/current.md
package.json
scripts/check-knowledge-layer.mjs
src/lib/knowledge/
src/layouts/BaseLayout.astro
src/pages/bible/index.astro
src/pages/bible/[book].astro
src/pages/posts/[slug].astro
src/pages/search-index.json.ts
src/pages/sitemap.xml.ts
```

### 2. 禁止项确认

确认没有：

```text
src/content/posts/*.md 修改
CSS 修改
首页视觉修改
RSS 结构破坏
Admin 认证配置改动
OAuth / Cloudflare Access 改动
数据库化改造
外部 API 调用
FAQ Schema
隐藏内容
```

### 3. 构建与检查

确认：

```powershell
npm.cmd run check:knowledge
npm.cmd run build
```

都通过。

### 4. 编码检查

确认新增/修改的核心文件首行没有 UTF-8 BOM：

```text
src/lib/knowledge/*.ts
scripts/check-knowledge-layer.mjs
assets/admin/decap.js
docs/knowledge/*.md
docs/tasks/current.md
```

### 5. 提交建议

如果最终验收通过，建议分阶段提交或一次性提交。

推荐一次性提交信息：

```text
feat: add Bible Knowledge Layer v1
```

如果分阶段提交，可使用：

```text
docs: add Bible Knowledge Layer architecture
feat: add knowledge core helpers
feat: extract JSON-LD schema builders
feat: integrate article knowledge metadata
feat: extend bible pages and search index
feat: add admin description fallback
chore: add knowledge layer validation script
```

## 完成后汇报格式

完成后请汇报：

1. 最终改动范围。
2. 检查脚本结果。
3. build 结果。
4. 是否发现越界修改。
5. 是否建议提交。
6. 推荐 commit 方式。

不要部署，不要 push，等待用户确认。
