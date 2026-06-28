# 当前任务

## 任务名称

移动端全屏 / 主题适配修正发布。

## 当前目标

发布已经完成的移动端显示修正：让手机端页面向下滑动时站点顶部 header 不再固定在最上方，并补充深色 / 浅色模式的浏览器主题色，使移动端顶部状态栏区域尽量跟随网站主题色。

## 背景说明

用户在手机截图中发现：

1. 网页在手机上不像全屏页面，最上方区域与网页视觉有割裂感。
2. 页面向下滑动时，顶部 Logo / 菜单区域保持不变，影响阅读体验。
3. 希望移动端自动适配深色和浅色模式。

需要注意：iPhone 顶部时间、电池等系统状态栏属于 iOS 系统区域，普通网页不能完全隐藏或真正接管；本任务目标是改善网页可控部分：主题色、安全区背景感、移动端 header 滚动行为。

## 当前已修改文件

```text
src/layouts/BaseLayout.astro
src/styles/global.css
assets/styles/global.css
```

## 已完成修改

1. 在 `src/layouts/BaseLayout.astro` 中，将单一 `theme-color` 改为深浅模式分别声明：

```html
<meta name="theme-color" content="#061625" media="(prefers-color-scheme: dark)" />
<meta name="theme-color" content="#f7f9fc" media="(prefers-color-scheme: light)" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
```

2. 在 `src/styles/global.css` 和 `assets/styles/global.css` 中，为 `html` 和 `body` 增加：

```css
min-height: 100%;
```

3. 在移动端媒体查询中，把 `.site-header` 改为：

```css
.site-header {
  position: relative;
  min-height: 68px;
}
```

这样移动端不再继承桌面端的 `position: sticky; top: 0;`，页面滑动时 header 会随内容一起滚动。

## Codex 执行要求

请 Codex 从当前工作区继续执行发布流程：

1. 先检查当前 Git 状态，确认只有以下 3 个文件处于修改状态：

```text
src/layouts/BaseLayout.astro
src/styles/global.css
assets/styles/global.css
```

以及本文件 `docs/tasks/current.md` 和 `.ai-bridge/current-plan.md` 如已写入交接计划也可能处于修改状态。

2. 不要修改 Logo / favicon / apple-touch-icon / manifest icons。品牌资产受保护，不得重绘或替换。

3. 执行构建验证：

```powershell
npm.cmd run build
```

4. 如果构建成功，提交并推送：

```powershell
git add src/layouts/BaseLayout.astro src/styles/global.css assets/styles/global.css docs/tasks/current.md .ai-bridge/current-plan.md
git commit -m "fix: improve mobile theme viewport behavior"
git push
```

5. 如果 `git push` 被拒绝，不要 force push。执行：

```powershell
git pull --rebase origin main
npm.cmd run build
git push
```

如出现冲突，停止并回报。

## 验证重点

构建成功后，发布到线上后重点检查手机端：

1. 首页和文章页在移动端可以正常滚动。
2. 向下滚动时顶部 Logo / 菜单区不再固定停留在最上方。
3. 深色模式顶部浏览器状态栏区域尽量接近深蓝背景。
4. 浅色模式顶部浏览器状态栏区域尽量接近浅白背景。
5. 不影响桌面端 header sticky 行为。
6. 不影响 Logo、favicon、文章内容、评论、搜索、RSS、sitemap。

## 未完成事项

等待 Codex 执行：

```powershell
npm.cmd run build
git add src/layouts/BaseLayout.astro src/styles/global.css assets/styles/global.css docs/tasks/current.md .ai-bridge/current-plan.md
git commit -m "fix: improve mobile theme viewport behavior"
git push
```
