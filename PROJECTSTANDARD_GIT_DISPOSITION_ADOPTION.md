# ProjectStandard Mandatory Git Disposition Adoption

日期：2026-09-09

项目：RonnieCross / 个人网页项目

状态：`ADOPTED / EFFECTIVE_FOR_ALL_BOUNDED_TASK_STAGE_CLOSURES_FROM_2026-09-09`

上游共同规则：`/Volumes/DevSSD/RonnieWork/ProjectStandard/standards/v1/TASK_LIFECYCLE.md` 当前 release 的 `GIT_DISPOSITION_CLOSURE`。

## 本地采用规则

每个 bounded task / stage 在 Master 宣告最终 closure 前，必须完成 repository/version-control disposition：确认 exact repo/branch、task-local changed/write-set、concurrent/unrelated dirty state、commit disposition、push disposition，以及 action 后的 clean/deferred state。无变化也必须明确 `NO_CHANGES`；mutation 不在当前 authority 内时必须明确 `PUSH_NOT_AUTHORIZED / DEFER_DUE_TO_*` 等 disposition。

不得把 unrelated dirty changes 混入本任务 commit，不得为了清理时间线 rewrite/amend 历史。Git add/commit/push 继续服从 Website Owner current authority、write-set isolation 与 remote/push authorization。

本规则只补充 closure completeness，不改变 Website 内容、发布、部署、runtime 或业务阶段 truth。

## 2026-09-14 Successor — Recoverable Repository Checkpoints

- `COMMIT_AUTHORITY_NOT_ESTABLISHED` 不等于 `USER_EXPLICIT_NO_COMMIT`；前者进入 `GIT_DECISION_REQUIRED`，不得静默当作 NO_COMMIT。
- unresolved dirty/lineage blocker 只能形成 `REPOSITORY_CLOSURE=OPEN`，并记录 exact blocker、affected write-set/lineage 与 recheck target。
- G0=transient 通常不提交；G1=稳定且可恢复的 bounded result 原则上 local task-lineage commit；G2=audit/acceptance/release/stage closure 等 canonical milestone 原则上 milestone commit，并另判 push。
- Website 长期任务按稳定 stage/milestone 判断，不等待整个项目结束，也不机械要求每个内容处理动作 commit；经验证 FAIL/BLOCKED 可成为合法 checkpoint。
- 至少在 bounded closure、audit verdict、parent acceptance/redecision、release、stage transition、master transfer、长期 HOLD/BLOCKED，以及 publication/deployment 前做 checkpoint review。
- commit 与 push 分开 Gate；push 未授权不得阻止安全、可隔离的 local commit。
- 本 successor 不改变内容/发布/部署 authority，不清理历史 dirty，不热切 in-flight task。
