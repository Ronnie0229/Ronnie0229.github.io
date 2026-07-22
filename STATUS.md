# 个人网页项目状态

最后更新：2026-07-22 +09:00

## 当前状态

- 项目：使用 Astro 构建的中文文章网站，部署目标为 Cloudflare Pages。
- 当前分支：`main`。
- 当前任务入口：`docs/tasks/current.md`。
- 当前活动任务：无。

## 当前事实源

接手项目时按以下顺序读取：

1. `README.md`
2. `AGENTS.md`
3. `STATUS.md`
4. `docs/tasks/current.md`
5. 与具体任务相关的 workflow、decision 或专项任务文档

`docs/tasks/archive/` 保存历史任务；`.ai-bridge/` 不得保存唯一长期事实。

## 当前发布与接口边界

- 正式内容位于 `src/content/posts/`，网站 raw 与 processed 镜像分别位于 `data/raw/` 和 `data/processed/`。
- 网站拥有 `website-publication-package/v1.1` 的消费和 `website-publication-result/v1.1` 的生成职责。
- v1.1 接口状态为 `contract_stable`，不等于自动发布，也不等于 `production_acceptance_passed`。
- 网站写入、构建、push、Cloudflare 部署和邮件发送必须按任务授权和发布流程执行。
- 已发布讲道正文修正不得改变 slug、articleId、日期、作者、分类、经文等锁定身份字段，除非任务明确授权。

## 最近已验证基线

最近一次记录完整的网站发布批次为 2026-07-21 的三篇帖撒罗尼迦分享文章：

- `npm run check:knowledge`：281 篇，0 错误，0 警告；
- Python 发布契约测试：12 tests OK；
- `npm run build -- --force`：322 pages built；
- 对应网站提交、Cloudflare 页面和邮件工作流结果记录在 `docs/tasks/current.md` 与月份归档中。

这些结果属于该次运行证据，不应自动外推为当前所有生产状态仍一致。

## 当前阻断与待办

- V2 完整生产验收仍由 `workspace-control` 统一管理，当前不能标记 `production_acceptance_passed`。
- 后续真实修改前应先同步 `origin/main`，确认 Admin 或其他入口没有产生远端新内容。
- 当前无项目内活动任务；新任务必须先登记到 `docs/tasks/current.md`。

## 历史说明

2026-07-13 以前及其后累积在旧 `STATUS.md` 中的阶段过程、邮件 MVP、访问量修复、source 路径审计和迁移记录，应完整归档为历史状态快照，不再保留在当前 STATUS 中。正式归档后，当前状态只由本文件替换后的 `STATUS.md` 表达。
