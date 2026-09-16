# ProjectStandard Cross-Project Mutation Binding — Website Source Adoption

DATE=`2026-09-16`
ROLE=`PROJECTSTANDARD_CROSS_PROJECT_MUTATION_BINDING_SOURCE_ADOPTION_MASTER / MASTER_CONTROL`
REPORT_TO=`WEBSITE_OWNER / USER`
LIFECYCLE=`ONE_BOUNDED_STAGE`

## 最初需求与目标

严格执行 ProjectStandard source-local adoption matrix 的 `A5 — RonnieCross / 个人网页项目`，在 Website 自己的 current authority 下做极薄 cross-project mutation / repository binding governance adoption。

## 本计划如何直接服务最初目标

只在现有 root governance entry `AGENTS.md` 中补入必要语义：

- lawful cross-project `READ_ONLY` 保持允许；
- mutation 前必须由 Website/source-local current authority fresh/exact 绑定 `target root + task/role + bounded write-set + operation class`；
- 默认/最近 workspace、聊天/Project 上下文、历史授权或 ProjectStandard release/proposal 不能替代本次 mutation authority；
- `COMMIT` / `PUSH` 额外绑定 exact Website repository identity，并继续作为两个独立 Gate；
- wrong-root / wrong-repo chronology 保留，不自动 reset/rebase/amend/force-push；
- 不建设 validator/service/platform/registry/watcher/daemon。

## 最小必要范围

允许修改：

- `AGENTS.md`
- `STATUS.md`
- `docs/tasks/current.md`
- 本 task 目录内 `task.md / RESULT.md / VERIFICATION.md / NEXT_HANDOFF.md`

## 明确非目标

- 不改变 publication/deploy/email authority；
- 不改变 `PUBLICATION_FAST_LANE + CONSTRUCTION_ISOLATION`；
- 不修改 `src/`、`functions/`、`assets/`、`scripts/`、content/raw/processed；
- 不运行真实 publish/build/deploy/notification；
- 不增加 validator/service 或中央治理设施；
- 不自动 commit，不自动 push。

## 目标价值 Gate

`FINAL_GOAL`：让 Website 当前治理明确采用 source-local exact mutation/repository binding。

`CURRENT_UNIQUE_BLOCKER`：现有规则要求 cross-project write separate authorization 与 Git closure，但未机械明确 exact binding tuple 及 repository identity 分 Gate。

`WORTH_CONTINUING`：是；一个极薄长期规则即可关闭 A5。

`SCOPE_DRIFT_CHECK=NO_SCOPE_DRIFT`

`OVERBUILDING_CHECK=NO_OVERBUILDING`

`OWNER_BOUNDARY_CHECK=OWNER_BOUNDARY_OK`

`MINIMAL_REUSE_CHECK=MINIMAL_REUSE_OK`

`DECISION=CONTINUE`

裁决：`PASS_MINIMAL_AND_ALIGNED / GOAL_ALIGNED / WORTH_CONTINUING / NO_SCOPE_DRIFT / NO_OVERBUILDING / OWNER_BOUNDARY_OK / MINIMAL_REUSE_OK`

## 停止条件

完成规则写入、只读验证、source-local RESULT/VERIFICATION/NEXT_HANDOFF 与 Git disposition 后立即停止并交回 Website Owner / User。任何 commit、push、deploy、notification 或业务 mutation 均不在本 stage 自动授权范围内。
