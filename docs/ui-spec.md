# UI 规范

本文件记录 RonnieCross 前台与 Admin 后台的界面样式边界，作为后续 UI 修改的入口说明。

## 样式入口规则

前台公开页面的样式入口统一维护在：
- `src/styles/tokens.css`
- `src/styles/global.css`

`src/layouts/BaseLayout.astro` 通过 Astro 源码 import 加载这两个文件，顺序必须是先 `tokens.css`，再 `global.css`。不要在前台页面继续使用 `<link rel="stylesheet" href="/styles/global.css" />`。

Admin 后台样式保持独立，入口为：
- `assets/admin/admin.css`

Admin 页面可以加载 `/styles/tokens.css` 共享变量，但不要把 Admin 的布局、表单、表格、编辑器、状态面板等样式合并进 `src/styles/global.css`。

`assets/styles/global.css` 已删除，不再作为前台样式入口维护。前台公开页面样式统一维护在 `src/styles/tokens.css` 与 `src/styles/global.css`。

样式修改前请先确认实际页面加载的 CSS 入口：
- 前台页面检查 `src/layouts/BaseLayout.astro`
- Admin 页面检查对应的 Admin HTML / Astro 文件

明确禁止：
- 不要在 Admin CSS 里修改前台文章卡片、导航、搜索页、书卷页等样式。
- 不要在 `src/styles/global.css` 里加入 Admin 编辑器、表格、图片库、评论管理、数据概览等后台样式。
- 不要同时维护两份前台 `global.css`。
