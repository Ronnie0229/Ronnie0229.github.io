# PROJECT.md

## 项目名称

RonnieCross 个人文章网站。

## 项目定位

这是一个使用 Astro 构建的中文个人文章网站，部署到 Cloudflare Pages。网站主要用于发布个人文章、信仰随笔、讲道整理、分享资料和长期写作内容。

本项目的目标不是只完成一个静态页面，而是建立一个可以长期维护、可以持续发布内容、可以让多个 ChatGPT / Codex 账号顺滑接手的完整个人网站项目。

## 技术栈

- Astro 5
- Markdown / Astro Content Collections
- JavaScript / TypeScript 配置
- Cloudflare Pages
- Cloudflare Functions / D1 相关后台接口
- Node.js 脚本
- Python 内容导入和整理脚本

## 正式仓库

- 正式本地路径：`C:\Users\caoyi\Projects\个人网页项目`
- GitHub 是代码与正式内容的长期事实来源。
- NAS 只用于收件、原始资料和受保护归档，不是开发工作区。

## 重要目录

| 路径 | 用途 |
| --- | --- |
| `src/content/posts/` | 正式网站文章 |
| `src/components/` | Astro 组件 |
| `src/layouts/` | 页面布局 |
| `src/pages/` | 页面路由、RSS、Sitemap、后台入口 |
| `src/styles/` | 网站样式 |
| `assets/` | 静态资源、后台前端资源、图片、robots、manifest |
| `data/raw/分享/` | 分享原始资料 |
| `data/raw/教会讲道/` | 讲道原始资料 |
| `data/processed/整理后的分享文章/` | 分享文章中间稿 |
| `data/processed/整理后的讲道文章/` | 讲道文章中间稿 |
| `docs/内容整理报告/` | 内容目录、审计、待确认报告 |
| `docs/` | 项目文档、流程、交接记录 |
| `skills/` | 给 Codex 使用的专项工作流文档 |
| `scripts/` | 内容整理、导入、同步和构建辅助脚本 |
| `functions/` | Cloudflare Functions 接口 |
| `风格重新设计素材/` | 深浅主题、Logo、背景图、设计规格和效果图素材 |

## 项目事实来源优先级

当聊天记忆、旧说明和当前仓库内容发生冲突时，按以下优先级判断：

1. 当前仓库文件和 Git 状态。
2. `AGENTS.md`、`STATUS.md`、`docs/tasks/current.md`。
3. 专项文档：`RUNBOOK.md`、`docs/account-switching.md`、`docs/统一内容整理与发布流程.md`、`docs/content-style.md`、`skills/article-workflow.md`。
4. 设计素材和规格文档。
5. 过去聊天记录或账号记忆。

## 长期维护目标

1. 任何账号都能通过仓库文档接手项目。
2. 网站开发、设计、内容、SEO、部署流程都沉淀为文档。
3. 每次任务有明确交接记录。
4. 保留原始资料和整理中间稿，避免不可逆丢失。
5. 网站保持可构建、可预览、可部署。
6. 设计修改与内容发布互不破坏。

## 非目标

- 不把 NAS 当成 Git / Node / Astro 工作目录。
- 不把重要规则只保存在聊天记录中。
- 不用某个账号的个人记忆作为唯一依据。
- 不在没有任务记录和验证的情况下做大规模重构。
