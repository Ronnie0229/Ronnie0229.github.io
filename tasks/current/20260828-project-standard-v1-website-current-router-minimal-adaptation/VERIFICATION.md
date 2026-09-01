# VERIFICATION｜Project Standard v1｜网站 current router 最小适配

结论：`PASS_CANDIDATE / WCRA-01..WCRA-07 = 7/7`

## Fresh evidence

- RonnieCross root `workspace-control/CURRENT.md` 当前仍把网站 cold-start locator 固定为 `AGENTS.md → STATUS.md → docs/tasks/current.md`，并明确 Owner current authority 高于 root/history chronology。
- 讲道 Owner publication result：`status=deployed`、`push_status=pushed`、`deployment_status=deployed`、`notification_status=sent`、commit=`a72f499f67be090dc407f0185b8f9946bee80ea4`。
- `tasks/current/` 未出现比本任务更晚、与摩西文章 production truth 冲突的网站业务/生产 task。
- F004 当前 authority reference 整改及 targeted independent re-audit 保持通过事实；本轮未改动其 authority。

## Static verification

- `STATUS.md` 顶部 current 区明确摩西文章生产动作已完成，并写明 current-over-history precedence。
- `docs/tasks/current.md` 顶部新增 current-effective override；2026-08-23 旧 pending 条目保留为历史且显式 superseded。
- 两个入口对当前 production truth 无直接冲突。
- split router 仍为 `STATUS.md + docs/tasks/current.md`，没有引入第三个 current registry、schema、service 或 watcher。
- 没有新的正式网站业务任务时，两个入口均明确不得伪造 ACTIVE production task。

## Scope verification

本轮业务/current authority write-set 精确为：

- `STATUS.md`
- `docs/tasks/current.md`

task-local evidence write-set 精确为：

- `tasks/current/20260828-project-standard-v1-website-current-router-minimal-adaptation/RESULT.md`
- `tasks/current/20260828-project-standard-v1-website-current-router-minimal-adaptation/VERIFICATION.md`
- `tasks/current/20260828-project-standard-v1-website-current-router-minimal-adaptation/NEXT_HANDOFF.md`

未运行 build/test/npm sync/Git/Cloudflare/email/notification/production；未修改网站源码、文章、讲道 Owner、publication contract、RonnieCross root router 或 Frozen Project Standard v1。

最终自验证：

`GOAL_ALIGNED / NO_SCOPE_DRIFT / NO_OVERBUILDING / OWNER_BOUNDARY_PASS / MINIMAL_REUSE_PASS`
