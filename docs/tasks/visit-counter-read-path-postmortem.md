# About 页累计访问量读取问题复盘

更新时间：2026-07-07

## 背景

Mac 移行后，第一次用 CodexPro 对个人网页项目做小范围维护时，用户发现 About 页的“本站累计访问量”长期显示“暂时无法读取”。问题是在邮件订阅通知系统完成后被注意到，但最终确认邮件订阅系统没有直接修改访问量相关代码。

相关文件：

```text
src/layouts/BaseLayout.astro
functions/api/visits.js
DEPLOY.md
docs/tasks/current.md
STATUS.md
```

## 问题现象

About 页 HTML 中的累计访问量节点初始显示：

```text
本站累计访问量：统计中…
```

当浏览器当前 session 已经记录过访问量后，页面会变成：

```text
本站累计访问量：暂时无法读取
```

## 根因

访问量前端逻辑用 `sessionStorage` 避免同一浏览器 session 内重复自增：

```text
ronniecross-visit-counted=1
```

旧逻辑中：

```text
1. 第一次访问：请求 /api/visits?increment=1，自增并返回 JSON。
2. 当前 session 已计数后：请求无参数 /api/visits，只想读取计数。
```

但此前为了处理 Search Console 4xx / 软 404，项目已规定 `/api/comments`、`/api/views`、`/api/visits` 这类接口在直接空 GET/HEAD 访问时返回 `204`，并带 `X-Robots-Tag: noindex, nofollow` 与 `Cache-Control: no-store`。

因此访问量旧前端在已计数 session 下请求无参数 `/api/visits` 时会收到 `204 No Content`，随后继续执行 `response.json()`，触发异常，最终显示“暂时无法读取”。

本质问题不是 Counter 服务不可用，也不是 D1、邮件订阅或 Cloudflare Access 配置错误，而是：

```text
前端读取计数的路径和后端 SEO 保护路径复用了同一个无参数 GET，导致接口契约冲突。
```

## 修复方式

修复原则：读取、自增、SEO 空访问三种语义必须分开。

最终约定：

```text
GET /api/visits?read=1
只读取累计访问量，返回 200 JSON，不自增。

GET /api/visits?increment=1
自增累计访问量，返回 200 JSON。

GET /api/visits
空访问，返回 204 noindex，不返回 JSON。

HEAD /api/visits
空访问，返回 204 noindex，不返回 JSON。
```

代码改动：

```text
1. src/layouts/BaseLayout.astro
   已计数 session 从请求 /api/visits 改为请求 /api/visits?read=1。

2. functions/api/visits.js
   新增 read=1 显式读取分支。
   只允许 read=1 或 increment=1 返回 JSON。
   无参数 GET / HEAD 保持 204 noindex。
```

## 验证过程

本地验证：

```text
node --check functions/api/visits.js
npm run build
npm run check:admin-save
npm run check:knowledge
git diff --check
```

线上部署后验证：

```text
1. Cloudflare Pages 确认部署到包含修复的提交。
2. /about/ HTML 确认包含 ?read=1。
3. GET /api/visits?read=1 返回 200 JSON。
4. GET /api/visits?increment=1 返回 200 JSON，且 count 增加。
5. GET /api/visits 返回 204，空响应体，带 noindex。
6. HEAD /api/visits 返回 204，带 noindex。
7. About 页在同一浏览器 session 下刷新，不再显示“暂时无法读取”。
```

已知验证记录：

```text
read：200，count=769。
increment：200，count 从 769 增加到 770。
无参数 GET：204。
HEAD：204。
```

## 曾遇到的排查误区

```text
1. 看到 About 页显示“暂时无法读取”时，容易误判为外部 counter 服务故障。
2. 因为问题在邮件订阅系统后被注意到，容易误判为订阅系统改坏了访问统计。
3. 只验证 /api/visits?increment=1 会漏掉已计数 session 的 read 路径。
4. 只验证 API 会漏掉静态 HTML 是否已经部署到最新构建。
5. Cloudflare Functions 可能已更新，但静态页面仍可能处在旧部署或旧构建，需要同时验证 HTML 内容。
```

## 以后避免类似问题的规则

1. 任何前端脚本如果要读取 API JSON，必须使用明确的查询参数或路径表达语义，不要复用“无参数 GET”。
2. 已被 SEO 规则定义为 `204 noindex` 的 API 空访问，不得再被前端当作 JSON 读取路径。
3. 对有“读取”和“写入/自增”两种语义的接口，应明确区分，例如 `read=1`、`increment=1`、`mode=counts`。
4. 修改 Cloudflare Functions 后，部署后不能只测 API，也要检查对应静态页面 HTML/JS 是否包含最新代码。
5. 涉及 sessionStorage/localStorage 的前端逻辑，至少要验证两种状态：首次访问和已存储标记后的重复访问。
6. 线上验证时要分别检查：

```text
API 成功路径
API 空访问/noindex 路径
页面 HTML 是否为最新构建
浏览器实际显示结果
```

7. 如果线上 API 已更新但页面 HTML 仍是旧代码，优先检查 Cloudflare Pages 最新部署、构建提交、静态资源哈希和页面 HTML，而不是继续改业务代码。

## CodexPro / Codex 协作经验

Mac 移行后本轮验证了 CodexPro 可以完成：

```text
读取项目文档
定位代码路径
修改源码
运行构建和检查
更新项目文档
线上只读验证
```

但本轮 Mac 侧 CodexPro 暴露给 ChatGPT 的工具仍是 `toolMode: standard`，没有直接暴露 `git_commit` / `git_push` 工具；虽然 server_config 显示 `bashMode: full`，ChatGPT 侧的 `CodexPro.bash` 仍按工具说明限制为验证命令，不应用它绕过执行 Git 写操作。

因此在 Git 能力未确认前：

```text
1. CodexPro 可负责修改、验证、写文档。
2. git commit / git push 交给本地 Codex 或用户确认后的专用 Git 工具执行。
3. 每次任务结束必须明确说明是否已提交、是否已推送、工作区是否干净。
```

如果以后要让 ChatGPT 侧 CodexPro 直接提交推送，需要在 CodexPro 服务端/管理工具中确认工具模式是否暴露 Git 写操作，并重新加载工具列表，直到能看到明确的 `git_commit` / `git_push` 工具，或工具说明明确允许 Git 写操作。

## 后续建议

访问量当前仍依赖外部 Counter API。虽然本轮线上确认该服务可用，但长期更稳妥的方案是把站点累计访问量迁移到现有 Cloudflare D1，和文章阅读数、留言数据使用同一套可控存储。迁移时要保留当前累计数作为初始值，并继续遵守本复盘中的接口语义分离规则。
