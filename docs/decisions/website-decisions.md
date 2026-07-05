# 网站继承决策记录

整理日期：2026-07-06  
资料来源：`C:\Users\caoyi\Desktop\codex++` 导出的 Codex Markdown 会话备份，以及当前仓库已有项目文档。本文提炼稳定决策，不保存隐藏 reasoning、系统/开发者提示、token 或 auth 信息。

## 1. Astro 继续作为主框架

RonnieCross 是内容型网站，核心是 Markdown 长文、静态生成、SEO、低维护成本和部署稳定性。Astro 与当前目录结构、Content Collections、Cloudflare Pages 部署方式已经匹配。

决策：继续使用 Astro；除非出现明确迁移理由，不切换框架。

## 2. GitHub 是代码事实来源

本机正式目录是日常开发工作区，GitHub 是代码和正式内容的长期事实来源。NAS 只作为资料收件、归档和历史副本，不作为日常 Node/Git 工作区。

决策：Windows 或 Mac 接手时都从 GitHub 同步；不要在 NAS 上运行 Git、Node、Astro、Codex 或文件监听。

## 3. 内容使用 Markdown，正式文章放在 src/content/posts

历史导出会话显示，项目从早期个人主页开始就选择 Markdown 管理文章，后续大量讲道和分享文章也沿用这个方向。

决策：正式发布文章继续进入：

```text
src/content/posts/
```

原始资料和中间稿保留在 `data/raw/`、`data/processed/` 或讲道整理项目对应目录，不把来源链路压扁成单个正式 Markdown。

## 4. 设计方向保持“安静、圆润、长文阅读”

已确认的视觉方向：

- 深色：深蓝圣经学习氛围。
- 浅色：白底深蓝字，少量金色点缀。
- 整体：圆润、柔和、适合长文阅读，可有克制的 Glass / 磨砂感。
- 避免：强科技感、霓虹色、绿色田园主视觉、大量缩略图卡片、复杂动画。

决策：设计修改必须参考 `DESIGN.md`、`docs/ui-spec.md` 和 `docs/tasks/style-structure-refactor-plan.md`。

## 5. Logo 与图标是受保护资产

Logo、favicon、apple-touch-icon、manifest icons 都属于品牌资产。历史任务中已经明确：不能 AI 重绘、临时替换或随意重新设计。

决策：只使用用户确认过的正式 Logo 文件，或从正式 Logo 等比例裁切/缩放生成尺寸版本。

## 6. 前台与 Admin 样式分层

前台公开页面与 Admin 后台的样式职责不同。公开页面服务阅读体验；Admin 服务编辑、管理、表格、状态和后台操作。

决策：前台样式入口优先维护在 `src/styles/tokens.css` 与 `src/styles/global.css`；Admin 样式保持独立，不把 Admin 表单、编辑器、状态面板等样式合并进前台全局样式。

## 7. 邮件提醒采用谨慎发布策略

邮件提醒 MVP 已完成到手动发送和中性链接阶段。历史验证强调：dryRun、D1 记录、真实发送、退订链接和中性阅读链接都要分开验证。

决策：任何后续邮件提醒修改都要先本地验证，再 dryRun；真实发送、D1 migration、远程操作和 Cloudflare Access 登录都需要明确授权。

## 8. 文档是跨账号接手的事实来源

多个 ChatGPT / Codex / CodexPro / 本地模型无法共享完整聊天记忆。导出的 Codex++ Markdown 只能作为整理材料，不能长期替代仓库文档。

决策：长期规则写入 `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`、专项 workflow / decision 文档。完成任务后必须回写状态。

## 待确认

- Mac 端最终工作目录、外置 SSD 路径和 NAS 挂载方式。
- 本地模型未来是否参与，只能在用户另开任务授权后决定。
- Admin 后台长期内容编辑模式仍需进一步设计与验证。
