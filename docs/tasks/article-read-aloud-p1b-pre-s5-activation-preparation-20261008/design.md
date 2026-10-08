# Design — S5 Minimal Pilot Activation Preparation

日期：2026-10-08

正式选择：**复用现有 S4 `worker_once()` / CLI `worker-once`，不新增 daemon loop、不新增 launchd、不新增 runtime framework。**

## Pilot-first decision

Master scope correction 优先于原 activation-preparation 的宽要求。第一篇 Pilot 只需要一个可人工观察、执行一次即退出的 Website-owned worker invocation。

现有入口已经满足：

```text
python3 scripts/read_aloud_s4_runner.py worker-once
```

在未来获得真实 activation authorization 后，省略 `--test-root` 即使用 frozen production root：

```text
/Users/ronnie/Library/Application Support/RonnieCross/read-aloud
```

本 S5 不执行该 production 命令。

## Start / stop model

Start：
- operator 明确执行一次 `worker-once`；
- 若无 queued/nonterminal job，立即返回，不接触 provider；
- 若有 job，仅选择一个并进入既有 S4 `execute_job()` path。

Stop：
- one-shot 正常完成即自动退出；
- 不存在 persistent Website worker，因此没有 daemon unload/disable 动作；
- 停止的最低动作是“不再启动下一次 worker-once”；
- 如执行过程中发生 UNKNOWN/stale owner，不删除 evidence、不自动 takeover、不换 request_id，按既有 S4 reconcile/operator boundary处理。

## Why no launchd for Pilot

第一篇 controlled Pilot 不需要无人值守调度。加入 launchd 会增加：
- 自动重复 invocation；
- install/bootstrap/kickstart side effects；
- restart policy；
- 新的 process lifecycle surface。

这些都不是 exactly one Pilot 的必要条件。因此 launchd template 也不创建。若 Pilot 证明未来需要无人值守，再由新的 business evidence决定。

## Frozen safety semantics

S5 不修改：
- authorization claim；
- descriptor/request_id derivation；
- execution owner；
- UNKNOWN semantics；
- reconcile；
- artifact identity/SHA；
- provider contract。

Single-worker 继续由 S4 execution owner机械保证。Terminal job不再被 `worker_once()` 选中。UNKNOWN 重入只复用原 request_id；N6 exactly-once truth unchanged。Stale owner 不自动 reclaim。

## Logging

S5 不新增 logging layer。现有 CLI stdout只输出 bounded job/result metadata，不打印 full TTS render text。S4 durable files也继续受 no-full-text persistence gate约束。

## Overengineering exclusions

本轮明确不建设 generic scheduler、queue platform、watchdog、registry、health framework、crash orchestration、self-healing launchd、Redis/Celery/database、multiworker 或新安全平台。
