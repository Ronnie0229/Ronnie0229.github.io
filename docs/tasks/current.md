# 当前任务

## 任务名称

移动端前台全屏适配修正：构建、提交并发布。

## 当前目标

把已经完成的前台移动端全屏适配修正发布到 GitHub main，触发 Cloudflare Pages 自动部署。目标是让前台手机页面更接近 admin 页面的全屏适配效果：页面背景从最外层铺满，顶部浏览器 / iOS 状态栏区域尽量跟随当前网站主题，手机端 header 不 sticky 固定，并且深浅模式切换时同步更新浏览器主题色。

## 背景

用户发现 admin 页面在手机上已经接近想要的全屏效果，而前台页面仍有问题：

1. 手机顶部系统状态栏下方区域没有很好地和网页背景融为一体。
2. 切换深浅模式时，顶部浏览器 / iOS 状态栏区域没有稳定跟随网站主题。
3. 前台移动端需要参考 admin 页面逻辑做全屏适配。

检查 admin 页面后确认其移动端全屏感主要来自：

```text
html / body 负责整屏背景
shell 只负责内容宽度和 padding
没有 sticky header
移动端 shell 接近全屏显示
```

## 当前代码状态

当前工作区已有未提交修改，预期修改文件为：

```text
src/layouts/BaseLayout.astro
src/styles/global.css
assets/styles/global.css
docs/tasks/current.md
```

`.ai-bridge/current-plan.md` 也会作为给 Codex 的临时执行计划更新，但它可能被 `.gitignore` 忽略，不要求提交。

## 已完成的代码修改

### 1. `src/layouts/BaseLayout.astro`

已将 viewport 改为支持移动端安全区覆盖：

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
```

已将 `theme-color` 改为动态 meta：

```html
<meta name="theme-color" id="theme-color" content="#061625" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
```

已在页面初始化脚本中加入主题色同步逻辑：

```js
const setThemeColor = (theme) => {
  const themeColor = document.querySelector('meta[name="theme-color"]');
  themeColor?.setAttribute("content", theme === "dark" ? "#061625" : "#f7f9fc");
};
```

已在主题初始化时调用 `setThemeColor(theme)`。

已在 `applyTheme()` 中调用 `setThemeColor(theme)`，使用户点击右上角深浅模式切换按钮时，浏览器顶部 theme-color 也同步变化。

Logo / favicon / apple-touch-icon 没有修改。

### 2. `src/styles/global.css` 与 `assets/styles/global.css`

两份样式已同步修改。

`html` / `body` 已增加 `width: 100%`，并继续保持 `min-height: 100%`，让最外层负责整屏背景。

移动端 `.site-shell` 已调整为更接近 admin 的布局逻辑：

```css
@media (max-width: 760px) {
  .site-shell {
    width: min(100%, 1180px);
    max-width: none;
    min-height: 100dvh;
    padding: 0 14px;
  }

  .site-header {
    position: relative;
    min-height: 68px;
  }
}
```

这表示：

```text
html / body 负责铺满整屏背景
site-shell 负责移动端内容边距
site-header 在移动端不 sticky
桌面端仍保留原 sticky header 行为
```

## Codex 执行任务

请 Codex 从当前工作区继续执行到发布完成。

### 步骤 1：确认状态

在项目根目录执行：

```powershell
git status
```

预期看到修改文件主要为：

```text
src/layouts/BaseLayout.astro
src/styles/global.css
assets/styles/global.css
docs/tasks/current.md
```

如果 `.ai-bridge/current-plan.md` 显示为修改或未跟踪，通常可以忽略，因为它可能被 `.gitignore` 忽略，不要求提交。

### 步骤 2：构建验证

必须使用 Windows PowerShell 兼容命令：

```powershell
npm.cmd run build
```

不要使用：

```powershell
npm run build
```

因为 PowerShell 可能会因 `npm.ps1` Execution Policy 阻止执行。

### 步骤 3：提交

构建成功后执行：

```powershell
git add src/layouts/BaseLayout.astro src/styles/global.css assets/styles/global.css docs/tasks/current.md
git commit -m "fix: align mobile viewport with admin layout"
```

### 步骤 4：推送发布

提交成功后执行：

```powershell
git push
```

推送成功后，Cloudflare Pages 会自动部署。

### 步骤 5：如果 push 被拒绝

如果出现 `fetch first` 或远端领先，不要 force push。执行：

```powershell
git pull --rebase origin main
npm.cmd run build
git push
```

如果 rebase 出现冲突，停止并回报，不要继续乱改。

## 严格限制

1. 不要修改 Logo / favicon / apple-touch-icon / manifest icons。
2. 品牌资产受保护，不得 AI 重绘、临时新建、替换或重新设计。
3. 不要修改文章内容。
4. 不要修改 admin 功能文件。
5. 不要使用 `git push --force`。
6. 不要直接运行 `npm run build`，使用 `npm.cmd run build`。

## 发布后验证重点

发布后用手机端检查：

1. 首页移动端背景是否从屏幕最上方开始铺满。
2. 文章页移动端背景是否从屏幕最上方开始铺满。
3. 深色模式下，顶部浏览器 / iOS 状态栏区域是否尽量接近深蓝背景 `#061625`。
4. 浅色模式下，顶部浏览器 / iOS 状态栏区域是否尽量接近浅白背景 `#f7f9fc`。
5. 点击右上角深浅模式切换按钮后，顶部浏览器区域是否随主题变化。
6. 手机端向下滚动时，前台 Logo / 菜单区不再固定在顶部。
7. 桌面端 header sticky 行为不受影响。
8. Logo / favicon 没有变化。

## 完成后回报格式

Codex 完成后请回报：

```text
构建结果：成功 / 失败
提交哈希：xxxxx
push 结果：成功 / 失败
修改文件：...
需要用户验证的线上项目：...
```

## 未完成事项

等待 Codex 执行以下发布流程：

```powershell
git status
npm.cmd run build
git add src/layouts/BaseLayout.astro src/styles/global.css assets/styles/global.css docs/tasks/current.md
git commit -m "fix: align mobile viewport with admin layout"
git push
```
