# ProjectStandard Mandatory Git Disposition Adoption

日期：2026-09-09

项目：RonnieCross / 个人网页项目

状态：`ADOPTED / EFFECTIVE_FOR_ALL_BOUNDED_TASK_STAGE_CLOSURES_FROM_2026-09-09`

上游共同规则：`/Volumes/DevSSD/RonnieWork/ProjectStandard/standards/v1/TASK_LIFECYCLE.md` 当前 release 的 `GIT_DISPOSITION_CLOSURE`。

## 本地采用规则

每个 bounded task / stage 在 Master 宣告最终 closure 前，必须完成 repository/version-control disposition：确认 exact repo/branch、task-local changed/write-set、concurrent/unrelated dirty state、commit disposition、push disposition，以及 action 后的 clean/deferred state。无变化也必须明确 `NO_CHANGES`；mutation 不在当前 authority 内时必须明确 `PUSH_NOT_AUTHORIZED / DEFER_DUE_TO_*` 等 disposition。

不得把 unrelated dirty changes 混入本任务 commit，不得为了清理时间线 rewrite/amend 历史。Git add/commit/push 继续服从 Website Owner current authority、write-set isolation 与 remote/push authorization。

本规则只补充 closure completeness，不改变 Website 内容、发布、部署、runtime 或业务阶段 truth。
