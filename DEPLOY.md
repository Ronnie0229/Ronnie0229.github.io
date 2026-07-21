# DEPLOY.md

本文件是 RonnieCross 部署和线上维护的项目级入口。后台使用细节见 `docs/网站后台使用与配置.md`。

## 部署平台

默认部署平台：Cloudflare Pages。

项目中与部署相关的文件和目录：

- `wrangler.jsonc`
- `functions/`
- `assets/robots.txt`
- `assets/site.webmanifest`
- `src/pages/deployment.json.ts`
- `scripts/migrations/`
- `docs/网站后台使用与配置.md`

## 本地构建

部署前必须至少确认构建：

```shell
npm run build
```

构建输出目录：

```text
dist/
```

如果只修改纯文档，可以不运行构建，但必须在 `docs/tasks/current.md` 写明原因。

## 本地预览

```shell
npm run preview
```

默认本地开发地址：

```text
http://127.0.0.1:4321
```

## Cloudflare Functions

项目包含 `functions/` 目录，可能用于评论、浏览量、访问统计或后台接口。

修改 Functions 前必须检查：

- 是否影响现有 API 路径。
- 是否需要 D1 数据库或环境变量。
- 是否需要执行 `scripts/migrations/`。
- 是否影响后台页面。
- 是否影响静态站构建。

### API 空访问与前端读取路径

`/api/comments`、`/api/views`、`/api/visits` 等接口的无参数 GET / HEAD 可用于 Search Console / crawler / 误访问处理，默认应返回 `204`，并带 `X-Robots-Tag: noindex, nofollow` 与 `Cache-Control: no-store`。不要让前端把这些无参数 API 空访问当作 JSON 读取路径。

有读取和写入两种语义的接口必须显式区分路径或参数。例如站点累计访问量使用：

```text
GET /api/visits?read=1       只读取累计访问量，返回 200 JSON，不自增。
GET /api/visits?increment=1  自增累计访问量，返回 200 JSON。
GET /api/visits              空访问，返回 204 noindex。
HEAD /api/visits             空访问，返回 204 noindex。
```

相关复盘见：`docs/tasks/visit-counter-read-path-postmortem.md`。

## 后台相关

后台入口见 README 和 `docs/网站后台使用与配置.md`。

与后台有关的目录：

- `assets/admin/`
- `src/pages/admin/`
- `functions/admin/`
- `functions/_lib/`

修改后台时，应同时检查：

- 登录 / 权限逻辑。
- API 返回格式。
- 前端后台页面是否仍能加载。
- Cloudflare 环境变量和 D1 绑定是否仍一致。

## 部署前检查

- [ ] `npm run build` 通过。
- [ ] 本次修改文件范围符合任务目标。
- [ ] 没有把 `node_modules/`、`.astro/`、`dist/` 提交进 Git。
- [ ] 没有提交敏感信息、token、密码或本地环境变量。
- [ ] 如果修改内容，文章页面能正常生成。
- [ ] 如果修改 SEO，sitemap / RSS / search-index 能正常生成。
- [ ] 如果修改 Functions，确认后台和 API 影响范围。
- [ ] 如果修改前端读取 API 的脚本，确认首次访问和 sessionStorage/localStorage 已存在两种状态。
- [ ] 已更新 `docs/tasks/current.md`。

## 部署后检查

部署完成后必须同时验证“HTTP可访问”和“目标正文真实存在”。Cloudflare Pages在未知路由上可能仍返回首页HTML和HTTP 200，因此仅检查状态码不能证明文章已经上线。

文章发布后优先运行：

```shell
python3 scripts/verify_publication_release.py \
  --url "https://ronniecross.com/posts/<slug>/" \
  --expect "<文章标题>" \
  --expect "<作者或核心正文>" \
  --run-id <GitHub Actions运行编号>
```

然后检查：

- 首页是否能打开。
- 最新文章是否出现。
- 文章详情页是否能打开，而且页面包含标题、作者/经文和正文关键字。
- 搜索、分类、标签等入口是否正常。
- RSS 是否正常。
- Sitemap 是否正常。
- 后台入口是否仍可访问。
- 浏览器控制台是否有明显错误。
- 如果修改了 Functions 或前端 API 调用，确认 API 成功路径、API 空访问/noindex 路径、对应页面 HTML/JS 最新构建和浏览器实际显示结果都正确。
- 如果修改了 About 页累计访问量，确认 `/about/` HTML 包含 `?read=1`，且 read、increment、无参数 GET、HEAD 四条路径行为符合本文件约定。

## 回滚原则

如果部署后发现问题：

1. 先确认是否为缓存、网络或 Cloudflare 边缘延迟。
2. 如果是代码问题，优先回滚到上一个稳定 commit。
3. 不要在 main 上连续热修多个不确定修改。
4. 回滚或热修后，必须更新 `STATUS.md` 和 `docs/tasks/current.md`。

## 不要做的事

- 不要把本地 `.env`、token、密钥写进文档或代码。
- 不要在不理解 Functions / D1 的情况下删除后台相关目录。
- 不要为了 SEO 把后台、API 或测试页暴露给搜索引擎。
- 不要直接修改 Cloudflare 线上配置后不记录到项目文档。

## 文档任务与部署边界

普通文档维护任务只允许运行 `npm run build` 做本地验证，不执行部署，也不推送代码。

以下命令只有在用户明确授权上线时才允许执行：

```shell
git push origin main
npx wrangler pages deploy dist --project-name ronniecross --branch main
```

本项目是Cloudflare Pages项目，不要使用`wrangler deploy`；该命令用于Worker入口或Worker assets部署，会在本项目中产生错误提示，甚至在配置变化后造成错误部署目标。通常应优先依赖Git推送触发的Cloudflare Pages自动部署。只有自动部署异常、且当前环境具备`CLOUDFLARE_API_TOKEN`时，才使用上面的`wrangler pages deploy`手动部署。

涉及 Cloudflare Pages、Functions、D1 或 `wrangler.jsonc` 的改动时，要先说明影响范围，再执行构建和线上验证。文档任务默认不得修改 `functions/`、`wrangler.jsonc` 或 Cloudflare 配置。
