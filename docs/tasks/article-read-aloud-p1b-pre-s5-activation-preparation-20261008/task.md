# Article Read-Aloud P1B-pre — S5 Activation Preparation

状态：PASS_S5_MINIMAL_PILOT_ACTIVATION_PREP / READY_FOR_CONTROLLED_SINGLE_ARTICLE_PILOT_AUTHORIZATION
日期：2026-10-08
Owner：Website / 个人网页项目

ROLE：
`ARTICLE_READ_ALOUD_P1B_PRE_S5_ACTIVATION_PREPARATION_EXECUTOR / EXECUTOR`

REPORT_TO：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

LIFECYCLE：
`LONG_RUNNING_UNTIL_NEXT_AUTHORITY_BREAKPOINT`

RETURN_CONDITION：
`READY_FOR_CONTROLLED_SINGLE_ARTICLE_PILOT_AUTHORIZATION_OR_TRUE_AUTHORITY_BLOCKER`


## 2026-10-08 Master scope correction — Pilot-first / anti-overengineering

本节为后加的 Master scope correction，**优先级高于下文任何更宽的 activation-preparation 要求**。

触发依据：项目独立目标/范围审计裁决为 `REVISE_SCOPE_OVERENGINEERED`，指出有声阅读当前风险不是 S4 不可靠，而是继续把内部可靠性建设前置于第一篇真实可播放文章。

### 修正后的业务目标

S5 不再以“形成长期完整 activation framework”为目标。

S5 唯一价值目标：

**为 exactly one 受控真实文章 Pilot 准备足够且不过度的 Website 启动/停止能力，使下一步可以在用户明确授权后安全生成第一篇真实音频。**

### 修正后的 return condition

正常 PASS 应改为：

`PASS_S5_MINIMAL_PILOT_ACTIVATION_PREP / READY_FOR_CONTROLLED_SINGLE_ARTICLE_PILOT_AUTHORIZATION`

不是默认：

`READY_FOR_FRESH_INDEPENDENT_AUDIT`

只有当本 S5 实际修改了 S4 已 fresh-independently closed 的核心安全语义（claim / request_id / execution owner / UNKNOWN / reconcile / artifact identity 等），才必须在 Pilot 前新增 fresh independent audit。

若 S5 只新增薄的 activation wrapper / one-shot entrypoint / launchd template / operator checklist，并机械证明它不改变 S4 semantics，则不再为了流程完整性额外增加一轮独立审核。

### 必须保留

仅保留直接服务第一篇 Pilot 的最低必要能力：

- 一个 Website-owned single-worker 启动入口；
- 明确 stop/deactivate 方法；
- idle 启动不得触发 provider POST；
- queued job 只能进入既有 S4 exactly-once path；
- UNKNOWN / stale-owner 继续保守，不自动 takeover；
- terminal job 不重复 POST；
- no new request_id / no new generation epoch；
- no full TTS text in logs；
- production runtime root / file mode / exact path 明确；
- 一个最小非安装 launchd artifact/template（仅当真实 Pilot 激活确实需要）；
- 一个短 operator checklist，足够执行“启动 → 单篇 Pilot → 停止/保留证据”。

### 明确降级 / 删除为非阻塞

除非第一篇 Pilot 的真实运行证明必要，否则以下不得继续扩建：

- generic worker framework；
- 通用调度/优先级/取消；
- 多任务长期 queue 管理；
- 通用 crash orchestration platform；
- watchdog / registry / health platform；
- 更复杂的 launchd 自愈策略；
- 通用 runtime supervisor；
- Redis/Celery/database；
- 多 worker；
- 为恶意内部篡改设计新的递归安全框架；
- 与第一篇 Pilot 无直接关系的新 validator / abstraction / platform。

内部恶意篡改型、正式 threat model 外的边角项，如不影响“单篇 Pilot 不重复计费/不串 job/不泄漏正文/不误发 POST”，登记为 non-blocking hardening，不继续递归整改。

### 最小实现选择

优先选择**最简单、最可停、最容易人工观察**的 activation 方式。

若“one-shot worker + 人工/launchd 单次触发”足够完成 Pilot，就不得为了未来长期无人值守而实现 daemon loop。

如果现有 `worker_once()` 已足够通过薄入口被安全调用，优先复用，不新增通用 worker runtime。

### S5 最终验收只回答 5 个问题

1. 能否在用户授权后启动 Website worker，而不触发 idle provider POST？
2. 能否让 exactly one Pilot job 只走既有 S4 exactly-once path？
3. UNKNOWN / stale-owner / terminal 状态会不会导致重复 TTS 成本？
4. 能否明确停止 worker 并保留 jobs/claims/owners/evidence？
5. 下一步是否已经只差用户对“真实 activation + exactly one Pilot generation”的明确授权？

如果 5 个问题均为 YES，S5 应停止，不继续完善系统。

### 下一阶段价值顺序

S5 PASS 后，Master 不得自动创建新的工程阶段。

优先动作必须是请求/等待用户对以下 bounded real operation 的明确授权：

- minimal Website activation；
- exactly one frozen Pilot article generation；
- 真实 TTS；
- WAV QC；
- 64/96 kbps MP3 对比；
- 人工听感验收；
- simple article player；
- 第一篇真实可播放文章。

第一篇 Pilot 成功前，不建设 feed/highlight/general queue/platform。

## Entry condition

S4 durable runner implementation 已经过 fresh independent closure：

`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_FRESH_INDEPENDENT_AUDIT / READY_FOR_ACTIVATION_DESIGN`

Aggregate material findings：0。

这表示 S4 implementation blockers 已 closure，但不等于 production activation 已授权，也不等于 Pilot generation 已授权消费。

Frozen Pilot authorization 仍：

`UNCLAIMED / NOT_CONSUMED`

## Goal

在不触发任何 production/runtime side effect 的前提下，一次性完成 Website-owned durable runner 的 activation preparation：

1. activation design；
2. minimal worker lifecycle implementation；
3. launchd/plist 或等价 local service definition 的非安装版 artifact；
4. isolated temp-root lifecycle tests；
5. crash/restart/reconcile/stale-owner safety tests；
6. operator runbook / activation checklist；
7. bounded verification；
8. 同 scope 内发现的局部 bug 持续最小修复并重跑；
9. 到 controlled single-article Pilot authorization breakpoint 才停止；只有实际修改 S4 核心安全语义时才额外进入 fresh independent audit。

不要把 design / implementation / test 再拆成多个 tiny tasks。

## Fresh-read requirements

先 fresh-read Website current authority：
- `AGENTS.md`
- `docs/task-handoff-protocol.md`
- `docs/tasks/current.md`
- S4 runner implementation / tests
- 最近 S4 fresh independent audit

如 activation lifecycle 需要 provider current contract，只允许对 VOICE_AI 项目做 read-only fresh-read：
`/Volumes/DevSSD/RonnieWork/语音模型`

只读取 current interface/runtime contract；不得修改、启动、停止或重启 VOICE_AI。

## Frozen architecture

保持以下 frozen boundaries：

- Website owns durable job spool / claims / execution owner / submit-status-result-reconcile；
- VOICE_AI HTTP V1 unchanged；
- provider endpoint remains localhost only；
- Website does not start/restart VOICE_AI；
- stable request_id / exactly-once / N6 ownership unchanged；
- production runtime root remains:
  `/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`
- single Website execution worker only；
- no Redis/Celery/database/distributed queue；
- no multiworker scheduler；
- no generic platform。

## Activation design requirements

### A. Process ownership

Define one Website-owned long-lived worker process whose only job is to service the durable spool.

Must specify:
- exact executable / Python entrypoint；
- exact workspace / working directory expectations；
- exact runtime root；
- environment requirements；
- stdout/stderr destination；
- log-content restrictions；
- single-worker guarantee；
- behavior when no jobs exist；
- behavior when provider /ready is unavailable；
- behavior when job is terminal；
- behavior when execution owner exists；
- behavior when job is UNKNOWN；
- behavior on process restart。

### B. Worker loop semantics

Implement the thinnest safe loop around existing `worker_once()` / runner primitives.

Requirements:
- one process；
- bounded idle polling interval；
- no busy-spin；
- no concurrent thread/process execution；
- one call to existing execution path at a time；
- errors converted to bounded local logging/exit behavior；
- worker loop must not mutate request_id/epoch；
- worker loop must not delete claims/owners/jobs automatically；
- no stale-owner takeover；
- no job cancellation/priority/scheduling platform；
- no full TTS text in logs。

If a one-shot worker + launchd periodic invocation is safer/thinner than daemon loop, compare explicitly and choose one. Prefer the simplest mechanism that preserves frozen safety.

### C. launchd definition

Produce a non-installed launchd plist/template or equivalent activation artifact.

Must define:
- stable Label；
- ProgramArguments；
- WorkingDirectory；
- RunAtLoad decision；
- KeepAlive decision；
- restart policy；
- stdout/stderr file locations；
- environment variables only if necessary；
- file ownership/mode expectations；
- no provider daemon control；
- no network exposure。

Do NOT install/bootstrap/kickstart it.

### D. Crash / restart semantics

Must explicitly preserve:

- if crash before provider entry and no ambiguous side effect, safe recovery path；
- if job durable state is `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`, restart must not infer no provider side effect；
- execution owner semantics remain conservative；
- no PID/TTL auto reclaim；
- no new request_id；
- same-id reconcile only；
- terminal jobs never re-POST；
- stale owner requires operator/manual authority if existing frozen model requires it。

### E. Production activation checklist

Produce an exact operator checklist for later authorized activation:

1. fresh verify code/tests；
2. confirm production runtime root absent or expected state；
3. create runtime root/subdirs with exact 0700；
4. deploy/copy only approved activation artifacts if needed；
5. install/bootstrap launchd；
6. verify process identity；
7. verify no provider POST on idle start；
8. verify submit/status/result/reconcile surfaces；
9. verify logs contain no TTS text；
10. stop before Pilot claim unless separate generation authorization is explicitly consumed.

Checklist must distinguish:
- activation authorization；
- Pilot generation authorization；
- commit/push authorization；
- any future deploy/publication authorization。

### F. Explicit rollback/deactivation plan

Design only:
- how to unload/disable Website worker；
- how to preserve jobs/claims/owners；
- no deletion of runtime evidence；
- no automatic retry after ambiguous state；
- no VOICE_AI restart；
- no provider state mutation。

## Non-production implementation scope

Executor MAY implement/test only Website-local activation artifacts required by the design, for example:

- a worker-loop or one-shot activation entrypoint under `scripts/`；
- tests under `scripts/tests/`；
- launchd plist template under a Website-owned config/docs/task path；
- operator runbook/docs under this task package.

All implementation/testing must use isolated temp runtime roots and fake/stub providers where provider calls could occur.

Do NOT point tests at production runtime root.

## Required isolated acceptance matrix

At minimum test:

1. idle start => no provider speech；
2. queued job + ready provider fake => existing runner path invoked once；
3. provider not ready => bounded waiting state, no speech；
4. terminal job => no speech；
5. UNKNOWN job => no new request_id and no unsafe automatic POST except frozen same-id reconcile semantics；
6. existing execution owner => no speech；
7. stale/dead-looking owner => no auto takeover；
8. malformed job => bounded fail-closed / no worker crash where existing runner contract permits；
9. worker restart after terminal => no duplicate provider call；
10. worker restart with UNKNOWN => conservative behavior；
11. logs exclude full text/provider body；
12. only one worker can actively execute；
13. launchd artifact references exact Website paths；
14. activation artifact does not control VOICE_AI daemon；
15. production runtime root remains absent throughout test；
16. no real provider endpoint used。

## Long-lifecycle rule

Do not stop for:
- ordinary unit/integration test failures；
- local lifecycle bugs；
- plist syntax errors；
- same write-set edge cases；
- local regression；
- documentation mismatch。

Preserve FAIL chronology, fix minimally, rerun, and continue.

Stop only at next true authority breakpoint:
- fresh independent Auditor required after local closure；or
- continuation would require production activation/install/bootstrap/kickstart；
- real Pilot claim/generation；
- expanded scope/write-set/Owner；
- external-project mutation；
- commit/push if not separately authorized；
- unresolved evidence conflict requiring user decision。

## Allowed write-set

Expected bounded write-set:
- `scripts/read_aloud_s4_runner.py` only if strictly needed for activation-compatible entrypoint and without reopening frozen semantics；
- new Website activation worker entrypoint under `scripts/`；
- tests under `scripts/tests/`；
- Website-owned launchd template/config artifact；
- this task package；
- `docs/tasks/current.md`；
- narrowly relevant Website runbook doc if necessary.

If a change would materially alter S4 semantics, STOP and escalate rather than silently expanding scope.

## Forbidden real side effects

- no real Pilot claim/submit；
- no real `/v1/speech`；
- no creation of production runtime root；
- no LaunchAgent install/bootstrap/kickstart；
- no persistent worker process；
- no VOICE_AI start/stop/restart；
- no WAV/MP3；
- no R2/NAS/deploy；
- no external project mutation；
- no commit/push。

## Final local acceptance

Before return, independently within Executor scope run:

- py_compile for changed Python；
- activation-specific tests；
- full S4 runner tests；
- full Website Python suite；
- plist syntax/static validation if applicable；
- production runtime root absence；
- no persistent test worker left；
- temp roots clean；
- whitespace/EOF hygiene；
- `git diff --check` if permitted, otherwise record connector limitation and use show_changes + equivalent hygiene.

## Verdict

### PASS

`PASS_S5_MINIMAL_PILOT_ACTIVATION_PREP / READY_FOR_CONTROLLED_SINGLE_ARTICLE_PILOT_AUTHORIZATION`

Use only if the minimum Pilot-facing activation path is prepared and mechanically verified, no production activation occurred, and the five Pilot-readiness questions in the Master scope correction are all YES.

### BLOCKED

`BLOCKED_S5_ACTIVATION_PREPARATION / RETURN_TO_MASTER_CONTROL`

Use only for a true authority blocker, not ordinary implementation/test iteration.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s5-activation-preparation-20261008/`

Maintain:
- `task.md`
- `design.md`
- `implementation.md`
- `verification.md`
- `activation-checklist.md`
- `rollback.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md`.

At PASS, stop and return to Master for the controlled single-article Pilot authorization decision. Do not create another engineering stage by default. Only require fresh independent audit if S5 materially changed S4 closed safety semantics.
