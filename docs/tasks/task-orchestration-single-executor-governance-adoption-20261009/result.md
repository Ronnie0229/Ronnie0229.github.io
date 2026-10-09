# Governance Adoption — Single Executor Until Real Authority Breakpoint

日期：2026-10-09

## 起因

Article Read-Aloud Pilot 在“exactly one article 试读”阶段曾出现 task fragmentation / over-orchestration：
implementation、局部修复、回归、re-audit、handoff 被切成过多小任务，导致 Pilot 建设周期被流程本身拉长。

PROJECT_OWNER 随后明确要求：
- 不要为了流程形式把同一目标链路切碎；
- 同一个 Owner / authority / bounded write-set 内，普通实现、测试、局部修复、回归和 evidence closure 应由同一个 Executor 连续推进；
- 只有到真正 authority breakpoint 才停止交回。

## Adoption

正式采用现有两个治理改动：

1. `AGENTS.md`
   - 新增 `Task orchestration — single executor until authority breakpoint`
   - 将上述原则设为项目级默认行为。

2. `docs/task-handoff-protocol.md`
   - 将“什么时候继续推进 / 什么时候必须停”写成正式 handoff 规则。

## 边界

该规则：
- 不减少 PROJECT_OWNER 对真实副作用的控制；
- 不改变 commit / push / deploy / production mutation / TTS generation 等显式授权边界；
- 不允许扩大 Owner / scope / write-set；
- 不取消 fresh independent Auditor / Reviewer 的独立性；
- 不授权 Executor 自审代替独立审核；
- 不改变 Publication Fast Lane、Construction Isolation 或任何业务 authority；
- 目的仅是减少同一合法任务内部的无意义碎片化交接。

## Verification

- fresh-read `AGENTS.md`
- fresh-read `docs/task-handoff-protocol.md`
- current Git baseline verified
- `HEAD == origin/main`
- current dirty set before adoption closure: exactly two files
- `git diff --check -- AGENTS.md docs/task-handoff-protocol.md`: PASS
- no code/build/runtime change required

## Verdict

`PASS_USER_DIRECTED_TASK_ORCHESTRATION_GOVERNANCE_ADOPTION / READY_FOR_GIT_CLOSURE`
