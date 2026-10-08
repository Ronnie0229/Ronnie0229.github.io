# Article Read-Aloud P1B-pre — Targeted Architecture Gap Remediation

状态：ACTIVE_TARGETED_REMEDIATION
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_TARGETED_ARCHITECTURE_REMEDIATION_EXECUTOR / EXECUTOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Trigger

Independent audit verdict:
`BLOCKED_ARCHITECTURE_GAP / RETURN_TO_MASTER_CONTROL`

Audit source:
`docs/tasks/article-read-aloud-p1b-pre-async-independent-audit-20261007/audit.md`

总体架构方向继续有效，仅有两个 material gaps 阻断 bounded implementation：
1. generation authorization one-time atomic claim 未冻结；
2. every possible provider POST 前 exact render SHA binding 未冻结。

Auditor 同时要求 implementation 前冻结 runtime state root exact path/owner/permissions。

## Goal-value Gate

- FINAL_GOAL：用 Website S4 durable runner 安全承接长时间 TTS，使 CodexPro/Hermes/future automation 只做短时 caller。
- CURRENT_UNIQUE_BLOCKER：上述两个首次 POST 前 contract gap。
- WORTH_CONTINUING：YES
- SCOPE_DRIFT_CHECK：PASS
- OVERBUILDING_CHECK：PASS
- OWNER_BOUNDARY_CHECK：PASS
- MINIMAL_REUSE_CHECK：PASS
- DECISION：`PASS_MINIMAL_REMEDIATION_JUSTIFIED / CONTINUE`

## Scope

本轮只做 architecture amendment / contract freeze。不得实现代码。

必须保留原 decision 中已经通过的内容，不重开：
- Website S4 owns durable orchestration；
- VOICE_AI Local HTTP V1 unchanged；
- N6 is sole generation exactly-once truth；
- filesystem spool + atomic JSON；
- single worker；
- short submit/status/result/reconcile callers；
- no Redis/Celery/database/VOICE_AI async V2；
- Hermes/RonnieAutomation not workers。

## Required amendment A — authorization one-time atomic claim

必须冻结 mechanical contract：

1. 每个 explicit generation authorization 有 immutable `authorization_ref` / `generation_epoch`。
2. 一个 authorization 只能绑定一个 immutable logical job identity 和一个 deterministic request_id。
3. 首次 submit 必须在任何 provider POST 之前完成 atomic claim。
4. claim 必须机械排他，至少能防止两个短时 caller 并发各自成功消费同一 authorization。
5. exact same authorization + exact same immutable descriptor 的重复 submit：
   - 返回 existing job；
   - 不产生新 request_id；
   - 不产生第二 provider POST 权利。
6. same authorization + any different operation/article/render SHA/request_id：
   - fail-closed；
   - provider POST=0。
7. claim 一旦成功，不因 caller disconnect、worker timeout/restart、host restart、provider busy/not-ready 自动释放或生成新 epoch。
8. 新 generation 必须来自新的 explicit user authorization / generation epoch；不能由 retry/reconcile 隐式产生。
9. N6 exactly-once 仍只约束 provider request_id；Website authorization claim 只约束“用户授权可产生多少 logical generation identities”，不得宣称替代 N6。

必须选择最小 filesystem primitive，不得设计通用 lease system。优先：
- atomic exclusive-create claim file，或
- bounded file lock + atomic write，
并说明 crash-safe invariant。

## Required amendment B — exact render binding before every possible POST

必须冻结：

1. job descriptor 保存 bounded `render_ref` + immutable `render_sha256`，不复制全文到 job JSON。
2. 每一次 worker 即将执行可能进入 provider 的 POST（首次或 reconcile replay）之前：
   - 从 bounded render_ref 读取 exact bytes 一次；
   - 计算 SHA-256；
   - require exact match frozen render_sha256。
3. missing / unreadable / path escape / symlink/rebinding ambiguity / SHA mismatch：
   - Website-side terminal or operator-required fail-closed；
   - provider POST=0。
4. POST body 必须由**刚刚完成 SHA 验证的同一内存 bytes/string instance**构造；不得 verify 后再次从路径重新读取。
5. 编码必须冻结：UTF-8 exact bytes -> decoded text；decode failure fail-closed。
6. reconcile 若不需要 POST，仅查询 Website terminal state，不要求重新加载全文；只有可能 POST 时才重新执行 render binding gate。
7. 不得自动修改/normalize/trim TTS Render View。
8. frozen SHA 指的是 exact file bytes identity；文本语义等价但 bytes 不同也必须视为 mismatch。

## Required amendment C — runtime state root freeze

在 implementation 之前冻结 exact Website-owned local state root，要求：
- Git repo 外；
- NAS 外；
- VOICE_AI workspace 外；
- Website Owner；
- normal user `ronnie` 可读写；
- 不需要 root；
- only local machine；
- job/claim/temp/artifact-cache 子目录边界明确；
- logs/job state 默认不复制全文；
- path unavailable 时 fail-closed，不 fallback 到别处。

选择一个与当前机器/project layout 最小一致的 exact path；必须 fresh-check parent 可用性与权限，但本轮不得创建/写该 runtime root（除非仅在 task docs 中记录路径）。

## Pilot binding

当前 Pilot generation authorization 仍未消耗。

必须为当前 Pilot提出并冻结：
- exact authorization_ref / generation_epoch identity；
- canonical immutable descriptor fields；
- deterministic request_id derivation rule；
- proof rule：same authorization cannot produce two different request_ids。

不得执行 claim，不得 submit，不得 POST。

## Deliverables

仅写：
- `docs/tasks/article-read-aloud-p1b-pre-targeted-remediation-20261007/amendment.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`
- 必要时更新 `docs/tasks/current.md`

## Verification

至少证明：
- Finding A fully closed by contract；
- Finding B fully closed by contract；
- runtime root frozen before implementation；
- no dual-truth introduced；
- no new provider semantics；
- no hidden second-generation path；
- no overbuilding；
- Pilot authorization remains unconsumed。

## Forbidden

- no implementation code
- no /v1/speech
- no WAV/MP3
- no LaunchAgent install
- no runtime spool creation
- no VOICE_AI/RonnieAutomation/Hermes mutation
- no Website src/article mutation
- no commit/push
- no Pilot authorization consumption

## Verdict

Give exactly one:
- `PASS_TARGETED_ARCHITECTURE_REMEDIATION / READY_FOR_FRESH_REAUDIT`
- `BLOCKED_TARGETED_REMEDIATION_INCOMPLETE / RETURN_TO_MASTER_CONTROL`

Then stop.
