# 当前任务

## 任务名称

手机导航与文章元信息修复收尾。

## 当前状态

已收尾，暂停继续追修 iPhone/Safari 顶部状态栏完全融合问题。

本轮已经完成并发布的相关提交：

```text
28ce9a3 refine article metadata displays
4bd66fb fix iOS light status bar viewport
```

当前 `main` 与 `origin/main` 已同步到：

```text
4bd66fb fix iOS light status bar viewport
```

## 已完成内容

### 1. 文章元信息显示修复

已完成：

```text
首页文章卡片：日期 + 阅读 X 分钟
全部文章页：日期 + 阅读 X 分钟
文章详情页：日期 + 阅读 X 分钟
书卷详情页：日期 + 阅读 X 分钟
搜索结果页：日期 + 分类 + 阅读 X 分钟
Admin 文章列表：发布日期 · 阅读 X 分钟 · 分类
```

已去掉前台列表中重复显示的经文标签，避免标题中已有经文时再次重复。

浅色模式下 `阅读 X 分钟` 已修复为普通元信息文本，不再显示为蓝色胶囊；普通主题标签仍保持胶囊样式。

### 2. 手机端导航修复

已恢复手机端固定导航栏。

当前做法是在手机端使用 fixed header，并给页面外层补顶部间距，避免导航遮挡正文。

### 3. iPhone/Safari 顶部状态栏尝试修复

已尝试并发布：

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

即撤回前台普通页面的 `viewport-fit=cover`，目标是恢复修改全屏适配前的旧行为。

构建通过并已发布：

```text
npm.cmd run build
194 page(s) built
Build Complete
提交：4bd66fb fix iOS light status bar viewport
```

## 当前遗留问题

用户反馈：iPhone/Safari 浅色模式最顶部状态栏区域仍未达到期望效果。

当前决定：

```text
不再继续在本轮任务中追修该问题。
```

原因：

1. 该问题已经多轮尝试，继续小修 CSS/meta 容易反复试错。
2. iPhone/Safari 顶部状态栏涉及普通 Safari、PWA、viewport、安全区、浏览器 UI 等边界，不能仅靠 `npm run build` 验证。
3. 当前网站核心功能和主要视觉问题已修复；继续处理应单独开任务，先做可控区域确认和真机验证方案。

## 后续如需重启该问题

必须单独开任务，任务名称建议：

```text
iOS Safari 顶部状态栏与 safe-area 专项排查
```

专项任务开始前必须先确认：

1. 用户是在普通 Safari 打开，还是添加到主屏幕的 PWA 模式。
2. 问题只发生在浅色模式，还是深色模式也有异常。
3. 是否只发生在书卷页，还是所有页面都有。
4. 是否与 Safari 地址栏位置、无痕模式、刷新缓存有关。
5. 是否需要重新引入 `viewport-fit=cover`，以及是否要配套 `safe-area-inset-top` 专项设计。

不要在普通样式修复任务中顺手修改：

```text
viewport-fit
safe-area-inset-top
apple-mobile-web-app-status-bar-style
theme-color
```

除非任务目标就是 iOS safe-area 专项。

## 收尾结论

本轮任务的可交付部分已经完成：

```text
文章元信息修复：完成
阅读时间样式修复：完成
Admin 列表元信息修复：完成
手机固定导航：完成
iPhone/Safari 顶部状态栏完全融合：暂停，不再继续追修
构建状态：通过
远端状态：已推送 main
```

## 接手提醒

1. 新任务开始前先读取 `STATUS.md` 和本文件。
2. 目前不要继续围绕 iPhone 状态栏做零散 CSS/meta 尝试。
3. 后续优先做已经计划好的样式入口重构，解决 `src/styles/global.css` 与 `assets/styles/global.css` 双入口混乱问题。
4. 不要提交 `.ai-bridge` 文件。
