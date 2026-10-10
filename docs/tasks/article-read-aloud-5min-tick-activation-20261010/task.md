# Article Read-Aloud — 5-minute Thin Tick Activation

日期：2026-10-10
Owner：Website / 个人网页项目
状态：PASS

## Goal

启用已经由 PROJECT_OWNER 冻结为每 5 分钟一次的极薄本地触发层：

```text
LaunchAgent
→ every 300 seconds
→ read_aloud_workflow.py tick-all
→ deterministic durable-state advance
→ process exits
```

触发层不得拥有业务逻辑，不保存 workflow truth，不成为第二 authority。

## Canonical execution path

- repo/workdir: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- controller: `scripts/read_aloud_workflow.py`
- command: `tick-all`
- durable runtime: `/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud`
- cadence: `300 seconds`

## System asset

- label: `com.ronniecross.read-aloud.tick`
- plist: `/Users/ronnie/Library/LaunchAgents/com.ronniecross.read-aloud.tick.plist`
- stdout: `/Users/ronnie/Library/Logs/RonnieCross/read-aloud-tick.stdout.log`
- stderr: `/Users/ronnie/Library/Logs/RonnieCross/read-aloud-tick.stderr.log`

## Boundary

- no daemon framework;
- no Redis/Celery/database;
- no business auto-trigger/backfill;
- tick-all only observes/advances existing durable workflows;
- human/operator gates remain hard stops.
