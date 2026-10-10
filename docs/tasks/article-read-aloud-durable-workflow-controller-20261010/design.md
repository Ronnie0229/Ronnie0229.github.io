# Design — Durable Read-Aloud Workflow Controller v0

## Problem

现有 S4 已能把 TTS 结果持久化成 durable job，但调用层仍容易把“继续下一步”绑定在 CodexPro/Hermes 当前 session。

v0 只建立一个 deterministic state cursor：

```text
model/tool invocation
→ short tick
→ durable state
→ process exits

5 minutes later
→ short tick
→ read durable state
→ continue
→ process exits
```

## Runtime layout

```text
/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/
├── jobs/
├── claims/
├── artifact-cache/
├── logs/
└── workflows/
    └── <workflow-id>.json
```

workflow 不复制 TTS 全文，只保存 identity、state、S4 job id、verified artifact metadata 和 next-action evidence。

## 5-minute trigger

未来优先用系统已有轻量调度能力执行：

```text
*/5 minutes → python3 scripts/read_aloud_workflow.py tick --all
```

真正安装方式（launchd 等）必须在 controller 本身通过验证后另行决定。调度器不得拥有业务逻辑。

## Hermes compatibility

Hermes 以后只需要：
1. 读 `status`；
2. 当 `automatic_action_available=true` 时调用 `tick`；
3. 当状态是 `WAIT_HUMAN_*` / `BLOCKED_*` 时停止并报告；
4. 不依靠模型记忆判断上一阶段是否完成。

Hermes 与 CodexPro 都是 interchangeable operator；durable files 才是 workflow current truth。

## Crash / unknown

v0：
- live execution-owner → WAIT，不重复启动 worker；
- terminal S4 → consume terminal result；
- UNKNOWN + owner missing/dead → `RESULT_UNKNOWN_OPERATOR_REQUIRED`；
- 不自动删除 stale lock。

v1 recovery candidate：
只在 request_id / claim / provider terminal identity / dead PID / no-second-generation 全部机械成立时允许 same-id reconcile；永不换 request_id。

## Phase boundary

Durable control 属于 Phase 2/3 reliability foundation。
真正自动业务触发、批量历史生成、全自动发布仍属于 Phase 4。
