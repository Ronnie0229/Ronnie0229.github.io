# Astro 7 升级评估草案

评估日期：2026-07-06  
状态：只读评估；未修改依赖，未执行升级

## 结论

当前不建议直接在 `main` 上运行自动升级或 `npm audit fix --force`。建议另开升级分支，把 Astro 5 → 6 与 6 → 7 视为两个可验证阶段；先建立构建与页面基线，再升级依赖、修复兼容性并完成 Cloudflare Pages Preview 回归，最后决定是否合并。

当前项目结构较简单，没有 Astro adapter、UI framework integration、Vite plugin 或自定义 Vite 配置，降低了依赖集成风险；但站点高度依赖 Markdown Content Collections、静态路由和自定义 RSS/sitemap/search-index/admin JSON，因此内容渲染与生成物回归仍是升级门禁。

## 当前环境与依赖基线

```text
package.json: astro ^5.0.0
package-lock.json: astro 5.18.2
package-lock.json: esbuild 0.27.7
npm outdated latest: astro 7.0.6
Astro 7.0.6 engines: Node >=22.12.0, npm >=9.6.5
Mac 本机: Node v26.4.0, npm 11.17.0
最近基线构建: npm run build 成功，213 pages，构建后 Git 无变化
```

本机版本满足 Astro 7 的最低 engines 条件，但 Cloudflare Pages 构建环境也必须显式核对。升级任务中应选择并固定受支持的 Node LTS 版本，避免只依赖本机 Node 26 的偶数版本行为。

## 当前 Astro 使用面

### 配置与内容层

- `astro.config.mjs` 只设置 `site` 与 `publicDir`，没有 adapter、integration、experimental flag 或 Vite 扩展。
- `src/content/config.ts` 使用 `defineCollection()` 与 `z` 定义 `posts` schema。
- 正式 Markdown 位于 `src/content/posts/`。
- 页面通过 `getCollection()` 读取文章；文章详情页还使用 `render()`。

### 页面与构建产物

- 首页、文章列表、分类、书卷、文章详情均依赖 Content Collections。
- 自定义端点包括：
  - `src/pages/rss.xml.ts`
  - `src/pages/sitemap.xml.ts`
  - `src/pages/search-index.json.ts`
  - `src/pages/admin/posts.json.ts`
  - `src/pages/deployment.json.ts`
- `src/layouts/BaseLayout.astro` 依赖 `Astro.site`、`Astro.url` 与 canonical/structured-data URL 生成。
- `src/pages/search/index.astro` 消费 `/search-index.json`。
- 邮件提醒 API `functions/api/admin/email/send-post.js` 同样消费 `/search-index.json`。

### 构建与部署

```text
npm run build -> node scripts/run_astro.mjs build
输出目录: dist/
部署平台: Cloudflare Pages
Functions: functions/
配置: wrangler.jsonc
D1 binding: COMMENTS_DB
```

当前没有 Astro Cloudflare adapter；静态站构建产物与 Pages Functions 是两层，需要分别验证，不应因 Astro build 通过就认定 Functions 与线上行为无回归。

## npm audit 风险

当前只读 audit 报告：

```text
astro: high，直接依赖
esbuild: low，Astro 间接依赖
```

`npm audit` 给出的自动修复目标是 Astro 7.0.6，属于跨 major 升级，会修改 `package.json` / `package-lock.json` 并可能触发兼容性修改。因此不执行 `npm audit fix` 或 `npm audit fix --force`；安全修复应并入独立升级任务，而不是把 audit 自动修复当作无风险补丁。

## Astro 7 重点兼容性风险

官方 v7 升级指南针对 v6 → v7；本项目当前为 v5，因此升级时还必须先审阅并完成 v6 迁移。

1. **Vite 8 / Rolldown**：项目没有自定义 Vite plugin，风险相对低，但构建脚本、资源路径、CSS 和客户端脚本仍需验证。
2. **Rust Astro compiler**：此前被容忍的未闭合标签或无效 HTML 嵌套可能报错或改变输出；所有 `.astro` 模板需通过 build，并做关键页面视觉回归。
3. **Markdown processor 变化**：Astro 7 默认使用新的 Sätteri 管线。项目虽未配置 remark/rehype plugin，但 176+ 篇 Markdown 的段落、列表、引用、经文格式、链接、HTML 和标题锚点需要抽样与自动检查。
4. **HTML 空白处理**：默认 `compressHTML: "jsx"` 可能改变相邻 inline element 的空格；导航、标签、元数据行和文章内联样式需视觉检查。
5. **Content Collections**：`src/content/config.ts`、`getCollection()`、`render()`、schema coercion 和生成类型是核心升级面；先审阅 v6 迁移要求，再确认 v7 构建结果。
6. **保留文件名**：Astro 7 将 `src/fetch.ts` / `src/fetch.js` 用于 advanced routing；当前仓库未发现该文件，但升级前应再次检查。
7. **Cloudflare Pages 环境**：确认 Preview 的 Node 版本、构建命令、输出目录、Functions、D1 binding 与 Access 行为，不在升级任务中顺带改线上配置。
8. **生成物消费者**：RSS、sitemap、search-index、admin posts JSON 与邮件提醒依赖稳定的字段、URL 和排序，必须比较升级前后输出。

官方资料：

- Astro v7 升级指南：<https://docs.astro.build/en/guides/upgrade-to/v7/>
- Astro v6 升级指南：<https://docs.astro.build/en/guides/upgrade-to/v6/>
- Astro 升级总览：<https://docs.astro.build/en/upgrade-astro/>
- Astro 7 发布说明：<https://astro.build/blog/astro-7/>

## 推荐实施策略

### Phase 0：冻结基线

- 从最新 `main` 新建专用分支，例如 `chore/astro-7-evaluation`。
- 记录当前 Node/npm、锁定版本、213 pages 和审计结果。
- 保存关键生成物的可比较摘要：页面数、文章数、RSS item 数、sitemap URL 数、search-index item 数、admin posts item 数。
- 选择首页、文章列表、文章详情、搜索、书卷、About、Admin 等页面作为截图基线。

### Phase 1：Astro 5 → 6

- 阅读官方 v6 migration guide，先处理内容层与移除项。
- 只修改升级必须的依赖和代码，不混入设计、内容或后台功能改造。
- 构建与检查全部通过后形成独立可审查节点。

### Phase 2：Astro 6 → 7

- 再按官方 v7 migration guide 升级到确认版本。
- 重点检查 Rust compiler、Markdown 输出、HTML 空白、Vite 8 与 `src/fetch.*` 保留名。
- 不自动接受 `npm audit fix --force` 产生的额外变化；逐项审阅 lockfile 与 transitive dependency diff。

### Phase 3：本地回归

必须执行：

```text
npm run build
npm run check:knowledge
npm run check:admin-save
```

必须核对：

- 构建页数和错误/警告。
- 首页、文章列表、分类、书卷、文章详情、搜索、About、订阅结果页。
- 深色/浅色、桌面/移动端、导航和 inline element 空格。
- Markdown 段落、列表、引用、链接、标题和原生 HTML 抽样。
- `/rss.xml`、`/sitemap.xml`、`/search-index.json`、`/admin/posts.json`、`/deployment.json`。
- articleId 唯一性、frontmatter schema、文章排序与 slug 稳定性。
- Admin 保存检查和邮件提醒中性链接使用的 search-index 数据。

### Phase 4：Cloudflare Preview

- 只部署预览环境，不直接替换生产。
- 核对 Pages build Node 版本、构建命令和 `dist/`。
- 验证 Pages Functions、D1 binding、Access 管理员接口、订阅/确认/退订和手动邮件 dry-run。
- 不在框架升级任务中执行真实邮件发送或 D1 migration。

### Phase 5：合并决策

只有本地和 Preview 回归通过、生成物差异已解释、audit 状态已复核后，才请求合并与生产部署授权。失败时保留升级分支并记录 blocker，不改写 `main`。

## 本次未执行

- 未运行 `npm install`、`npm update`、`npm audit fix` 或 `npm approve-builds`。
- 未修改 `package.json` 或 `package-lock.json`。
- 未升级 Astro 或其他依赖。
- 未运行构建、部署或发布。

