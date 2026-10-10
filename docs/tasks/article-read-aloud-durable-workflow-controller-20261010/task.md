# Article Read-Aloud — Durable Workflow Controller Foundation

日期：2026-10-10
Owner：Website / 个人网页项目
状态：V0_PASS / CONTINUATION_IN_PROGRESS
LIFECYCLE：LONG_RUNNING_UNTIL_NEXT_REAL_AUTHORITY_BREAKPOINT

## Goal

为长时间 TTS 和未来 Hermes 本地模型独立执行建立最小、模型无关的 durable workflow control foundation。

不是建设通用 workflow platform。只解决当前有声阅读链路的一个真实可靠性问题：

- CodexPro / Hermes 的一次命令调用可以很短；
- TTS 可以独立运行 20–30+ 分钟；
- 调用者退出后，生产 job 状态继续持久存在；
- 后续 5 分钟一次的薄触发只调用一次 `tick`；
- `tick` 根据 durable state 只推进当前合法下一步并立即退出；
- 不依赖聊天记忆、模型上下文或长 shell session；
- 人工 QC / 授权 Gate 必须显式停住。

## Architecture correction

原计划将“自动化”整体放在 Phase 4。现拆分：

1. **Durable workflow control**：属于 Phase 2/3 的可靠性基础，可以现在建设。
2. **Business automation**：文章自动触发、批量补历史音频、无人值守生产发布等仍属于 Phase 4，不提前建设。

这不是扩大业务自动化，而是把长任务生命周期从 CodexPro/Hermes session 生命周期中解耦。

## Frozen trigger cadence

未来本地薄触发层：

```text
every 5 minutes
→ read_aloud_workflow.py tick
→ execute at most the currently legal bounded transition
→ exit
```

当前本任务只实现 controller 与机械测试；不安装/启用 launchd/cron。

## Minimal interface

```text
start
status
tick
```

- `start`：创建幂等 durable workflow identity/state。
- `status`：只读返回机器可读 current state / next action。
- `tick`：推进一次，不保持常驻进程。

## Initial state model

```text
RENDER_READY
→ TTS_SUBMITTED
→ TTS_RUNNING
→ WAV_VERIFIED
```

异常/等待：

```text
WAIT_PROVIDER
RESULT_UNKNOWN_OPERATOR_REQUIRED
TERMINAL_BLOCKED
TERMINAL_FAIL_CLOSED
```

后续迭代在同一 controller 上继续接：

```text
TECHNICAL_QC_PASS
→ MP3_READY
→ WAIT_HUMAN_LISTENING
→ NAS_ARCHIVED
→ R2_PUBLISHED
→ WEBSITE_BOUND
→ BUILD_PASS
→ DEPLOYED
→ LIVE_VERIFIED
→ COMPLETE
```

## Hard invariants

- stable request_id / generation_epoch / authorization_ref；
- exactly-once TTS 语义继续由现有 S4 + provider contract 保证；
- 不因 tick 重跑创建第二 generation；
- durable state 必须在 runtime root，不依赖 Git worktree；
- controller 不保存全文 TTS；
- RESULT_UNKNOWN 不允许猜测成功或重新生成；
- 自动 stale-owner recovery 暂不在 v0 实现，必须先用严格同 request_id 机械规则单独验证；
- human/device QC 不能自动 PASS；
- TTS failure 仍不阻塞普通文章发布。

## Current Pilot 2 evidence

Pilot 2：
- articleId=`post-fa05168ade9ea9b8`
- render SHA=`5c92d640795b98840c7bf62ee4e6c488727127997750da22caa28cb8988574b7`
- S4 job=`2acf76da2669d766c4d8fb651533267af7dc7e3876be0e2c9f053194557eb523`
- request_id=`rc-readaloud-v1:2acf76da2669d766c4d8fb651533267af7dc7e3876be0e2c9f053194557eb523`
- current TTS=`TERMINAL_PASS`
- verified artifact SHA=`551db6adb34d478dd40d13cdd34fe826121d42523121a63a8f5c059b6b2a2ca6`
- worker 已自然退出，execution owner absent，provider READY。

这证明“长 TTS 独立完成”已经成立；本任务补上“session-independent automatic continuation”的最小 controller。

## Write-set

- `scripts/read_aloud_workflow.py`
- `scripts/tests/test_read_aloud_workflow.py`
- 本 task 目录
- `docs/tasks/article-read-aloud-construction-plan-20261007.md`
- `docs/tasks/article-read-aloud-phase2-repeatability-20261010/task.md`
- `PROJECT_DECISIONS.md`
- `STATUS.md`
- `docs/tasks/current.md`

## Not authorized in this controller-foundation task

- 安装或启用 launchd/cron；
- 新 daemon；
- Redis/Celery/database；
- 自动 batch/backfill；
- 自动通过人工试听；
- 自动 production deploy；
- commit/push。

## v0 closure target

`PASS_DURABLE_WORKFLOW_CONTROLLER_V0 / LONG_TTS_SESSION_DECOUPLING_MECHANICALLY_VERIFIED`
