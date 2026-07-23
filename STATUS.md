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

最近一次完整生产验收为 2026-07-22 的 Psalm 7 分享文章：

- `npm run check:knowledge`：282 篇，0 错误，0 警告；
- Python 发布契约测试：12 tests OK；
- `npm run build -- --force`：323 pages built；
- 网站 `main` 已推送到 `e09641e79d885db971e5f569c3f2eacf43eea5d7`；
- Cloudflare deployment commit 与网站 HEAD 一致；
- 首次邮件 workflow `29927545169` 为 1 篇、3 名收件人、3 次成功、0 次失败；
- 幂等 workflow `29928285307` 为 0 篇、0 收件人，并安全 skip 已发布 slug。

该批次已通过 V2 production acceptance，正式证据位于 `workspace-control/acceptance-runs/20260722-v2-production-acceptance-thessalonica-01/`。

## 当前阻断与待办

- 当前无阻断项。
- 后续真实修改前仍应先同步 `origin/main`，确认 Admin 或其他入口没有产生远端新内容。
- 当前无项目内活动任务；新任务必须先登记到 `docs/tasks/current.md`。

## 历史说明

2026-07-13 以前及其后累积在旧 `STATUS.md` 中的阶段过程、邮件 MVP、访问量修复、source 路径审计和迁移记录，应完整归档为历史状态快照，不再保留在当前 STATUS 中。正式归档后，当前状态只由本文件替换后的 `STATUS.md` 表达。
