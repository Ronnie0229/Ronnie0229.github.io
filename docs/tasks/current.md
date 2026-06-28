# 当前任务：Phase 8 PR 创建与合并前检查

## 任务状态

Phase 8 的本地实现、构建验证、视觉验收和远端分支 push 已完成。

```text
当前工作树：C:\Users\caoyi\Projects\各人网页项目-phase8-admin
当前分支：phase8/admin-stabilization
远端分支：origin/phase8/admin-stabilization
当前提交哈希：dcc5b76
push 状态：已 push
merge 状态：未合并 main
force push：未使用
工作树状态：干净
```

GitHub 返回的 PR 创建地址：

```text
https://github.com/Ronnie0229/Ronnie0229.github.io/pull/new/phase8/admin-stabilization
```

PR 标题：

```text
Phase 8: Admin stabilization and theme alignment
```

---

## Phase 8 完成内容

### 1. 文章标签显示修正

- Admin 发布的新文章即使 `tags: []`，前台也会显示 `category` 分类标签。
- `PostCard.astro` 现在合并 `tags` 与 `category`，并自动去重。
- 已确认：
  - 2026/06/27 文章显示 `分享`、`灵命成长`。
  - 2026/06/14 文章没有重复显示两个 `灵命成长`。

### 2. Admin 标签输入体验增强

- Admin 编辑器新增常用标签快捷按钮。
- 正式发布时，如果 tags 为空，会给出提醒。
- 保存草稿不受影响。

### 3. Admin 页面风格统一

- `/admin/`、`/admin/index.html`、`/admin/editor.html`、`/admin/comments.html`、`/admin/stats.html` 已统一视觉风格。
- Admin 页面接入当前前台网站设计 token。
- 顶部栏使用正式网站同款普通 header 风格：无大圆角边框、无卡片背景、无 box-shadow。
- 桌面端导航为正式网站同款文字链接 + 金色下划线。
- 手机端导航已折叠为 hamburger 下拉菜单。
- Admin 支持深浅模式切换，使用 `ronniecross-theme`。
- Admin hero 标题区使用正式网站同款背景图。
- Admin hero 区域加入现有正式 Logo，文案在 Logo 下方左对齐。
- Admin body 背景改为纯色，不再使用渐变或放射光。
- 未 AI 重绘、未替换 Logo、favicon、apple-touch-icon 或 manifest icons。

### 4. `/admin/` 路由修正

- 已修正本地 `/admin/` 404。
- `/admin/` 与 `/admin/index.html` 均可打开。

---

## 构建与本地验证结果

最近一次验证：

```text
npm.cmd run build 成功
生成页面：191 pages
输出：[build] Complete!
```

本地检查均返回 200：

```text
http://localhost:4321/admin/
http://localhost:4321/admin/index.html
http://localhost:4321/admin/editor.html
http://localhost:4321/admin/comments.html
http://localhost:4321/admin/stats.html
```

已知未验证项：

- 未实际登录 GitHub OAuth 验证线上保存、发布、删除、上传图片、留言管理和统计后台真实账号操作。
- 这属于线上账号/权限验证，不是本地代码构建问题。

---

## PR 正文建议

创建 PR 时正文建议使用：

```md
## Summary

Phase 8 focuses on stabilizing Admin-published article metadata display and aligning the Admin interface with the current public site design.

## Changes

- Show category badges for admin-published posts when tags are empty
- Deduplicate tags and category badges
- Add common tag shortcuts and empty-tag publish reminder in Admin editor
- Fix `/admin/` local route
- Align Admin desktop header with public site header style
- Add Admin dark/light mode toggle using `ronniecross-theme`
- Add hero Logo and left-aligned hero copy to Admin title sections
- Use solid Admin body background matching current site theme
- Add mobile hamburger dropdown navigation for Admin pages
- Keep existing GitHub OAuth, article save/publish/delete, image upload, comments, and stats data flow unchanged

## Verification

- `npm.cmd run build` passed
- Generated 191 pages
- Checked:
  - `/`
  - `/posts/`
  - `/admin/`
  - `/admin/index.html`
  - `/admin/editor.html`
  - `/admin/comments.html`
  - `/admin/stats.html`

## Notes

- Not merged into `main` yet
- No force push used
- Logo and brand assets were not replaced or redrawn
```

---

## 合并前最后检查

在 GitHub PR 页面重点确认：

### 1. 预期修改范围

PR 主要应包含以下文件附近的变更：

```text
src/components/PostCard.astro
assets/admin/admin.css
assets/admin/index.html
assets/admin/editor.html
assets/admin/editor.js
assets/admin/comments.html
assets/admin/stats.html
assets/admin/theme.js
src/pages/admin/index.astro
docs/tasks/current.md
```

### 2. 不应误改的范围

确认没有误改：

```text
assets/images/
favicon
apple-touch-icon
site.webmanifest
文章正文大批量内容
GitHub OAuth / Admin API 核心逻辑
```

### 3. 合并原则

- 如果 GitHub checks 通过，PR diff 无异常，用户确认视觉效果满意，可以 merge。
- 不要使用 `git push --force`。
- 不要在未确认 diff 前直接本地合并 main。

---

## PR 合并后的本地同步步骤

PR 合并到 `main` 后，在主工作区执行：

```powershell
cd C:\Users\caoyi\Projects\各人网页项目

git pull --rebase origin main
```

线上部署完成后，确认以下页面：

```text
https://ronniecross.com/
https://ronniecross.com/posts/
https://ronniecross.com/admin/
https://ronniecross.com/admin/editor.html
https://ronniecross.com/admin/comments.html
https://ronniecross.com/admin/stats.html
```

确认线上无问题后，再清理 worktree：

```powershell
cd C:\Users\caoyi\Projects\各人网页项目

git worktree remove ..\各人网页项目-phase8-admin
git branch -d phase8/admin-stabilization
```

如果 GitHub 没有自动删除远端分支，可在确认线上正常后执行：

```powershell
git push origin --delete phase8/admin-stabilization
```

建议等线上 `/admin/`、`/admin/editor.html` 正常后再清理本地与远端分支。

---

## 交给 Codex 的下一步任务

下一位 Codex 只需要协助用户完成：

1. 创建 PR。
2. 检查 PR diff。
3. 如用户确认，合并 PR。
4. 合并后同步 main。
5. 线上验证完成后，清理 Phase 8 worktree 与分支。

不要继续修改 Phase 8 代码，除非用户发现新的视觉或功能问题。
