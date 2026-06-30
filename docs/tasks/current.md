# 当前任务

## 任务名称

发布正式深色背景 favicon 修正。

## 当前目标

把已经完成并构建通过的 favicon 修正提交并推送到 GitHub `main`，触发 Cloudflare Pages 自动部署。目标是让 Google 搜索结果和浏览器标签页使用网站已有的正式深色背景 Logo，而不是透明背景 Logo。

## 问题背景

Google 搜索结果中当前网站图标显示为透明背景白色字母和金色十字架，在深色搜索结果界面中不清楚。

原因是 favicon / apple-touch-icon 之前指向透明背景 Logo：

```text
/images/ronniecross-logo-theme-dark-transparent.png
```

## 当前已完成修改

已修改文件：

```text
src/layouts/BaseLayout.astro
```

现在应指向网站已有的正式深色背景 Logo：

```html
<link rel="icon" type="image/jpeg" href="/images/ronniecross-logo-theme-dark.jpg" />
<link rel="apple-touch-icon" href="/images/ronniecross-logo-theme-dark.jpg" />
```

对应现有资产：

```text
assets/images/ronniecross-logo-theme-dark.jpg
```

不要新建或重绘任何 Logo。

## 已完成验证

ChatGPT 已运行：

```powershell
npm.cmd run build
```

结果成功：

```text
194 page(s) built in 88.26s
[build] Complete!
```

## 当前状态

已完成。

发布记录：

```text
构建结果：成功，ChatGPT 已执行 npm.cmd run build，194 page(s) built in 88.26s，[build] Complete!
提交哈希：518a1ac
push 结果：成功，已推送到 origin/main
修改文件：src/layouts/BaseLayout.astro, docs/tasks/current.md
需要用户验证：Google Search Console 对 https://ronniecross.com/ 请求重新编入索引
```

执行记录：

```powershell
git status
git add src/layouts/BaseLayout.astro
git commit -m "fix: use official dark logo favicon"
git push origin main
```

## 严格限制

1. 不要新建、重绘、替换或重新设计任何 Logo / favicon。
2. 不要修改 `assets/images/` 中的图片文件。
3. 不要修改 `assets/site.webmanifest`。
4. 不要修改文章内容、Admin 功能文件、Cloudflare 配置或脚本。
5. 不要使用 `git push --force`。

## 发布后用户需要做的事

部署完成后，用户需要在 Google Search Console 对首页执行：

```text
https://ronniecross.com/
```

流程：

```text
网址检查 → 测试实际网址 → 请求编入索引
```

Google 搜索结果 favicon 不会立即刷新，可能需要数天或更久。
