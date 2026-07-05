# 样式结构重构计划

整理日期：2026-07-06  
资料来源：`C:\Users\caoyi\Desktop\codex++` 导出的 Codex Markdown 会话备份，以及当前仓库 `AGENTS.md`、`DESIGN.md` 中的样式入口规则。本文只记录计划，不修改样式代码。

## 背景

历史会话中多次出现样式入口、前台/Admin 分层、`global.css` 双入口和 tokens 管理问题。当前仓库已经明确：前台公开页面样式入口不应分散维护，Admin 后台样式也不应混入前台全局样式。

## 当前已知入口

```text
前台 token：src/styles/tokens.css
前台全局：src/styles/global.css
前台加载：src/layouts/BaseLayout.astro 通过 Astro import 加载
Admin 样式：assets/admin/admin.css
```

历史路径 `assets/styles/global.css` 已不应作为前台样式入口维护。

## 目标结构

目标不是一次性大重构，而是逐步把样式职责分清：

```text
src/styles/tokens.css       颜色、字体、间距、圆角、阴影、主题变量
src/styles/base.css         reset、body、链接、排版基础（待确认是否拆出）
src/styles/components.css   前台通用组件，如按钮、卡片、标签（待确认是否拆出）
src/styles/layout.css       前台布局，如 shell、sidebar、main、footer（待确认是否拆出）
src/styles/pages.css        页面级样式，如首页、文章列表、搜索页（待确认是否拆出）
assets/admin/admin.css      Admin 后台独立样式
```

是否真正拆出 `base.css`、`components.css`、`layout.css`、`pages.css`，需要后续任务结合现有 CSS 规模和构建入口确认；当前只作为重构方向。

## 分阶段计划

### Phase 0：只读审计

- 确认 `BaseLayout.astro` 当前加载哪些 CSS。
- 搜索是否还有 `<link rel="stylesheet" href="/styles/global.css">` 旧入口。
- 搜索 `assets/styles/global.css` 是否仍被引用。
- 列出 Admin 页面实际加载的 CSS。

### Phase 1：前台入口收敛

- 保持 `tokens.css` 先于 `global.css`。
- 移除或标记废弃的旧前台 CSS 引用。
- 不改 Admin 样式。
- 验证首页、文章页、文章列表、搜索页、书卷页。

### Phase 2：变量与基础层整理

- 把颜色、字体、间距、圆角、阴影集中到 token。
- 保持深色/浅色主题行为不变。
- 不改变视觉方向，只减少重复和混乱。

### Phase 3：前台组件/布局拆分（待确认）

- 如 CSS 已经难维护，再拆 `base.css`、`components.css`、`layout.css`、`pages.css`。
- 每次只移动一类样式，并做页面截图或 build 验证。

### Phase 4：Admin 独立维护

- Admin 可读取共享 token，但后台布局、编辑器、表单、表格、状态卡等继续放在 Admin 样式中。
- 不把 Admin 的复杂界面规则并回前台 `global.css`。

## 风险

- CSS 移动容易造成视觉回退，尤其是深浅色主题、移动端、文章正文宽度和 Admin 编辑器。
- 同名 class 如果同时被前台和 Admin 使用，拆分前必须确认 DOM 作用范围。
- 构建通过不代表视觉正确，必要时需要浏览器截图验证。

## 验证清单

后续真正修改样式时至少验证：

```text
npm.cmd run build
首页
文章列表页
文章详情页
搜索页 / Bible query 相关页
Admin 登录后主要编辑界面（如任务范围包含 Admin）
移动端宽度
深色 / 浅色主题
```

## 本次状态

本次只创建计划文档，没有修改任何 CSS、Astro、脚本或文章内容。
