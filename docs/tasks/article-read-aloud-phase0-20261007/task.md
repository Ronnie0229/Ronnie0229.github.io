# Article Read-Aloud Phase 0 — Construction Intake

状态：PHASE0_INTAKE_VERIFIED_PENDING_MASTER_CLOSURE
日期：2026-10-07
Owner：Website / 个人网页项目
lane_class：construction

## 最初需求与目标

为 RonnieCross 网站文章建立低侵入、可选的“有声阅读”能力。第一业务验证目标是用 1 篇真实文章证明：Website 能生成正确的 TTS-ready 文本，经现有 VOICE_AI HTTP V1 生成可信 WAV，再从同一母版生成 64/96 kbps MP3 供人工 A/B；声音体验通过后才进入 R2 与网站播放器。

## 当前唯一目标

完成 Phase 0 construction intake：建立合规的 Website Owner-local bounded-stage worktree，冻结 baseline、scope、write-set、停止条件和执行交接。Phase 0 本身不实施 Phase 1A/1B/1C。

## 本计划如何直接服务最初目标

当前唯一阻断是有声阅读尚无合规 construction lane。建立 bounded-stage worktree 后，下一执行会话才能在不占用 canonical publication lane 的前提下安全开展第一篇 Pilot。

## Lane evidence

- exact Owner：Website / 个人网页项目
- canonical workspace：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- construction workspace：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007`
- branch：`task/article-read-aloud-phase0-20261007`
- lane_class：`construction`
- canonical_use_authorized：`false`
- baseline：`029419a13921c065e6864be6dc57b55542038905`
- baseline origin/main：`029419a13921c065e6864be6dc57b55542038905`
- worktree creation precondition：canonical clean + `main == origin/main`
- worktree initial state：clean
- lane verdict：`PASS_CONSTRUCTION_WORKTREE_READY`

## 本轮目标价值 Gate

- FINAL_GOAL：验证 1 篇真实文章的端到端有声阅读质量，再决定网站正式接入。
- CURRENT_UNIQUE_BLOCKER：此前没有合规独立 construction lane。
- WORTH_CONTINUING：是；建立 lane 是进入真实 Pilot 的最小必要条件。
- SCOPE_DRIFT_CHECK：PASS；未转向第四 Owner、平台治理或无关基础设施。
- OVERBUILDING_CHECK：PASS；仅建立一个 bounded-stage worktree 与必要任务文档。
- OWNER_BOUNDARY_CHECK：PASS；Website 只消费 VOICE_AI HTTP V1，不吸收语音模型 runtime 职责。
- MINIMAL_REUSE_CHECK：PASS；复用现有 Website repo、现有 VOICE_AI HTTP V1 与既有 worktree 机制。
- DECISION：`CONTINUE`
- 裁决：`PASS_MINIMAL_AND_ALIGNED / GOAL_ALIGNED / WORTH_CONTINUING / NO_SCOPE_DRIFT / NO_OVERBUILDING / OWNER_BOUNDARY_OK / MINIMAL_REUSE_OK`

## 最小必要范围

Phase 0 仅允许：

1. fresh-read current Website/root governance。
2. 记录 Git/worktree/lane evidence。
3. 建立本 task 的正式文档与交接。
4. 为下一阶段明确 Phase 1A 的边界。

## 明确非目标

本轮不得：

- 调用 `POST /v1/speech`；
- 生成 WAV/MP3；
- 选择或修改正式文章内容；
- 修改 `src/`、`scripts/`、schema 或播放器；
- 建 R2 bucket/custom domain；
- 写 NAS；
- deploy；
- 把有声阅读建立为第四个 RonnieCross Owner；
- 自动进入 Phase 1A 实施或独立审计。

## Write-set

允许写入：

- `docs/tasks/article-read-aloud-phase0-20261007/`
- 为本 task 必要时更新 Website `docs/tasks/current.md`，但不得把 canonical tree 当 construction implementation lane。

禁止修改业务代码和正式文章。

## 验证与证据

Phase 0 完成需证明：

- canonical closure commit 已 push，canonical clean/synced；
- construction branch/worktree 从同一 baseline 创建；
- worktree clean；
- task/handoff 完整；
- lane evidence 为 `PASS_CONSTRUCTION_WORKTREE_READY`；
- scope/overbuilding Gate 为 `PASS_MINIMAL_AND_ALIGNED`。

## 停止条件

达到 `PHASE0_READY_FOR_EXECUTOR_HANDOFF` 后停止。不得在本会话继续实施 Phase 1A，也不得生成真实音频。
