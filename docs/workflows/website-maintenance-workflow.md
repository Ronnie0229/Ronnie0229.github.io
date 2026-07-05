# 网站维护工作流

整理日期：2026-07-06  
资料来源：`C:\Users\caoyi\Desktop\codex++` 导出的 Codex Markdown 会话备份，以及当前仓库已有 `AGENTS.md`、`STATUS.md`、`PROJECT_DECISIONS.md`、`DESIGN.md` 等文档。本文只沉淀长期规则，不保存隐藏 reasoning、系统/开发者提示、token 或 auth 信息。

## 项目定位

RonnieCross 是 `ronniecross.com` 的 Astro 内容站，主要承载信仰随笔、圣经学习、分享文章、教会讲道整理和后续邮件提醒 / 后台管理能力。正式代码和正式文章内容以 GitHub 仓库与本机正式目录为准：

```text
C:\Users\caoyi\Projects\个人网页项目
```

NAS 目录用于资料收件、归档和历史材料，不作为日常 Git、Node、Astro 或文件监听工作区。

## 日常维护入口

接手网站任务时先读：

```text
AGENTS.md
STATUS.md
docs/tasks/current.md
PROJECT_DECISIONS.md
DESIGN.md
CONTENT_WORKFLOW.md
DEPLOY.md
```

按任务类型继续读：

```text
内容发布：docs/content-publishing-error-prevention.md、docs/统一内容整理与发布流程.md
设计样式：DESIGN.md、docs/ui-spec.md、docs/tasks/style-structure-refactor-plan.md
后台/邮件：docs/网站后台使用与配置.md、functions/、wrangler.jsonc
Git/账号/迁移：docs/branch-workflow.md、docs/account-switching.md
```

## 标准维护流程

1. 确认任务范围：前端、内容、后台、SEO、部署、文档，还是迁移。
2. 读取 `STATUS.md` 和 `docs/tasks/current.md`，确认当前状态和未完成事项。
3. 检查本地 Git 状态；如果用户没有授权，不要提交、push 或部署。
4. 修改前确认是否涉及受保护路径，例如 Logo、favicon、文章正文、`data/raw/`、Admin、D1 migration。
5. 小范围修改后运行对应验证。Windows PowerShell 下优先使用 `npm.cmd`，例如：

```powershell
npm.cmd run build
npm.cmd run check:admin-save
npm.cmd run check:knowledge
```

6. 发布前检查生成物、关键页面、sitemap、RSS、搜索索引、文章数量和路由。
7. 完成后更新 `STATUS.md` 与 `docs/tasks/current.md`，记录修改文件、验证结果、提交/推送状态和待确认事项。

本次继承文档整理没有运行 build/test，因为只创建和更新 Markdown 文档。

## 内容发布维护流程

内容进入网站前要保留来源链路：

```text
原始资料 / NAS 收件
→ data/raw/ 或讲道整理项目原始资料
→ data/processed/ 或讲道整理项目发布前 MD
→ src/content/posts/
→ build / 线上验证
→ STATUS.md 与 current.md 回写
```

讲道和分享类内容要特别检查：

- `description` 是否完整，不要只写一句空泛摘要。
- `scripture` 是否是完整经文范围，不要丢掉章、节或跨段。
- `title`、`slug`、`author/speaker`、`category` 是否与内容一致。
- `articleId` 是否唯一。
- `source` 是否指向真实来源；不要伪造不存在的 raw 文件。
- 导入脚本是否意外重写旧文章；发布前必须看 diff。

## Codex / CodexPro 接手流程

未来 Codex、CodexPro、本地模型或 Mac mini 接手时，默认按照仓库文档恢复上下文，不依赖旧聊天。

推荐分工：

```text
ChatGPT：整理规则、澄清任务、制定小范围计划。
Codex / CodexPro：按明确文档执行文件修改、批量检查、构建验证、Git 操作。
本地模型：只在用户明确授权和配置后使用；Windows 当前不要配置 provider/API Key。
```

任何账号都必须遵守：

- 不读取或处理 `.codex/auth.json`。
- 不配置 CC Switch、本地模型、provider 或 API Key，除非用户另开任务明确要求。
- 不把导出的 Codex Markdown 直接提交到网站仓库。
- 不把聊天记录当作长期事实来源，重要规则要写入项目文档。

## Windows 到 Mac 迁移接手说明

迁移时以 GitHub 为代码事实来源，在 Mac 上重新 clone 本仓库。Windows 本机目录和 NAS 路径只作为历史路径和资料入口参考。

待确认：Mac 端最终项目根目录、外置 SSD 挂载路径、NAS 挂载方式、Node 版本安装方式、Cloudflare/Wrangler 登录方式。

在 Mac 端未确认前，不要把 Windows 的绝对路径硬编码进脚本或文档示例；需要路径时写成“当前项目根目录”或单独列出 Windows/Mac 两套示例。
