# Search Console 第三阶段：Bible 书卷页 query URL 清理

更新时间：2026-07-04

## 背景

第二阶段已经把文章分类列表从 `/posts/?category=...` 改为稳定分类页，并停止在文章列表中生成 `?page=` / `?focus=`。

本阶段继续处理 Bible 书卷页中的前端状态 URL。此前 Bible 书卷页会在分页和返回定位时生成：

- `/bible/<book>/?page=2`
- `/bible/<book>/?focus=<post-slug>#post-<post-slug>`

这些 URL 本质上不是新的 canonical 页面，只是同一个书卷页的前端显示状态。为了减少 Search Console 中的重复 URL、canonical alternate 或 robots/query 相关噪音，本阶段改为不再主动生成 query URL。

## 修改内容

- Bible 书卷页分页按钮只切换前端显示，不再写入 `?page=`。
- 从 Bible 书卷页点击文章时，sessionStorage 返回地址改为纯 hash：
  - `/bible/<book>/#post-<post-slug>`
- 继续兼容旧的 `?page=` / `?focus=` 访问：
  - 如果旧 URL 带 `?focus=`，页面仍会定位到对应文章。
  - 进入页面后会用 `history.replaceState` 清理 query，只保留 pathname 和 hash。
- SEO audit 脚本加入 Bible query 代表 URL，方便部署后观察旧 URL 的最终 canonical/清理状态。

## 不在本阶段处理的内容

- 不移除 `/search/?q=...`，搜索页仍作为站内工具页处理。
- 不修改 Bible 书卷页 canonical 生成方式；canonical 仍由 `BaseLayout` 按 pathname 输出。
- 不调整 sitemap 书卷页列表，因为 sitemap 本来没有包含 Bible query URL。

## 验证要点

- `npm.cmd run build` 通过。
- `dist` 中不再出现 `searchParams.set("page"` 或 `searchParams.set("focus"`。
- Bible 书卷页仍能前端分页。
- 返回文章列表时使用 `/bible/<book>/#post-...`。
- `dist/sitemap.xml` 不包含 `/bible/.../?page=` 或 `/bible/.../?focus=`。
