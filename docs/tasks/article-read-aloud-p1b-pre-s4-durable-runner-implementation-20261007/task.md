# Article Read-Aloud P1B-pre — S4 Durable Runner Bounded Implementation

状态：PASS_S4_DURABLE_RUNNER_IMPLEMENTED / READY_FOR_INDEPENDENT_AUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_S4_DURABLE_RUNNER_IMPLEMENTATION_EXECUTOR / EXECUTOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Authority basis

- architecture redecision：PASS_MINIMAL_ARCHITECTURE_SELECTED
- independent audit chronology：BLOCKED_ARCHITECTURE_GAP（历史保留）
- targeted remediation：PASS_TARGETED_ARCHITECTURE_REMEDIATION
- fresh independent re-audit：PASS_TARGETED_REMEDIATION_FRESH_REAUDIT / READY_FOR_BOUNDED_IMPLEMENTATION

Primary authority:
- `docs/tasks/article-read-aloud-p1b-pre-async-redecision-20261007/decision.md`
- `docs/tasks/article-read-aloud-p1b-pre-async-independent-audit-20261007/audit.md`
- `docs/tasks/article-read-aloud-p1b-pre-targeted-remediation-20261007/amendment.md`
- `docs/tasks/article-read-aloud-p1b-pre-targeted-remediation-fresh-reaudit-20261007/audit.md`

## Goal-value Gate

- GOAL_ALIGNMENT=ON_PLAN
- BLOCKER_MATERIALITY=REQUIRED
- OVERBUILDING_RISK=LOW
- OWNER_BOUNDARY=PASS
- MINIMAL_NEXT_STEP=YES
- NEXT_TASK_JUSTIFIED=YES
- decision：PASS_MINIMAL_AND_ALIGNED / IMPLEMENT_BOUNDED_S4_RUNNER

## Goal

实现 Website Owner-local 的最小 durable execution layer，使 caller 可以在几秒内完成 submit/status/result/reconcile，而长时间同步 VOICE_AI POST 只由单一 Website worker 持有。

本任务只做 implementation + local mechanical verification。

**本任务不激活真实 Pilot，不消耗 generation authorization。**

## Frozen architecture

必须保持：

- provider：`VOICE_AI_LOCAL_HTTP_V1`，不修改；
- provider exactly-once truth：VOICE_AI N6；
- Website authorization claim：user generation authorization single-use binding truth；
- Website job state：orchestration truth；
- persistence：filesystem spool + atomic JSON；
- execution concurrency：single worker；
- callers：short-lived submit/status/result/reconcile；
- supervision：future Website launchd，**本任务不安装**；
- no Redis/Celery/database/distributed queue/VOICE_AI async V2；
- RonnieAutomation/Hermes 不是 worker。

## Frozen runtime root

Production identity:
`/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`

Contract:
- owner ronnie uid=501
- root/subdirs 0700
- files 0600
- local-only
- no fallback
- Git/NAS/VOICE_AI workspace 外
- jobs/claims/logs 不复制完整 TTS 正文

**本 implementation verification 默认必须使用 task-local temporary test root，而不是创建 production runtime root。**
若代码需要 production root 常量，应精确冻结上述路径，但测试通过 explicit test-root override/injection；test override 只能存在于 test/CLI verification surface，不能成为 production fallback。

## Frozen Pilot identity — for fixtures only

- authorization_ref=`article-read-aloud-pilot-generation-authorization-20261007-a1`
- generation_epoch=`pilot-20261007-a1`
- article_id=`post-32d30724d859c99c`
- operation_id=`article-read-aloud-pilot-post-32d30724d859c99c`
- render_sha256=`5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`
- voice_contract_id=`VOICE_AI_LOCAL_HTTP_V1`
- descriptor_sha256=`49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`
- request_id=`rc-readaloud-v1:49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`

Pilot authorization remains `UNCLAIMED / NOT_CONSUMED`.
Tests must never claim the real production authorization path/root.

## Minimal implementation surface

Prefer a small Python module/CLI under Website-owned `scripts/`, for example:
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`

Names may vary only if existing repo conventions clearly justify it; avoid package/platform expansion.

Implementation must provide bounded commands/functions equivalent to:

- `submit`
- `status`
- `result`
- `reconcile`
- `worker-once` or equally narrow single-worker execution primitive

No web server/API is required for this phase.

## Immutable descriptor / request identity

Implement exact schema:
`ronniecross-readaloud-generation-operation/v1`

Identity fields:
- schema
- authorization_ref
- generation_epoch
- operation_id
- article_id
- render_sha256
- voice_contract_id

Canonical serialization:
UTF-8 JSON, sorted keys, separators `(',', ':')`, `ensure_ascii=True`.

request_id:
`"rc-readaloud-v1:" + sha256(canonical_descriptor_bytes).hexdigest()`

Any supplied request_id that differs must fail-closed before claim/provider access.

## Authorization one-time claim

Implement Website-local atomic exclusive-create claim keyed only by deterministic authorization_ref + generation_epoch identity.

Requirements:
- claim before any provider POST;
- exact same binding duplicate submit returns existing logical job;
- same authorization + any differing immutable identity => fail-closed / provider POST=0;
- incomplete/corrupt/unreadable claim => operator-required fail-closed;
- no delete/retry, TTL, lease takeover, timeout release, auto new epoch;
- atomic exclusive-create must withstand concurrent submit tests;
- claim durable-completion ordering must follow frozen amendment;
- test crash/partial-claim behavior conservatively.

## Job state

Minimal states:
- QUEUED
- WAITING_PROVIDER_READY
- CALL_IN_PROGRESS_OR_RESULT_UNKNOWN
- TERMINAL_PASS
- TERMINAL_BLOCKED
- TERMINAL_FAIL_CLOSED

Atomic JSON updates via temp + fsync/durability discipline + atomic replace where appropriate.

Job record must contain identity/status/result metadata but not full TTS text.

Do not make Website state assert provider generation truth.

## Exact render binding

Before **every** code path that could execute provider POST:
- resolve bounded workspace-relative render_ref under frozen Website root;
- reject absolute injection / `..` escape / symlink/rebinding ambiguity;
- read exact bytes once;
- SHA-256 must equal immutable render_sha256;
- strict UTF-8 decode;
- no trim/normalize/newline rewrite;
- provider body text must come from same validated in-memory object;
- descriptor/request_id match required;
- any failure => provider POST=0.

Tests must prove provider function is not called on every negative case.

## Provider adapter boundary

Implement a very thin adapter to:
- GET `http://127.0.0.1:8765/ready`
- POST `/v1/speech` with exactly `text` + `request_id`
- GET artifact by opaque artifact_ref on terminal PASS

But unit/integration verification in this task must use a local fake/stub provider or dependency injection.

**Forbidden in this task: any real POST /v1/speech.**
Read-only real `/health` or `/ready` is allowed only if needed, but not required.

No automatic provider daemon restart/admin action.

## Reconcile

Reconcile must:
- never mint a new request_id or epoch;
- re-use same immutable descriptor;
- if another possible POST is required, rerun exact render binding gate;
- treat busy/not-ready as wait/block, not regeneration authority;
- preserve unknown/in-progress conservatively;
- terminal replay must map back to same logical job;
- no alternate job creation.

## Artifact handling

For fake-provider verification implement logic contract:
- only terminal PASS with opaque artifact_ref can retrieve;
- download/write to temp first;
- verify bytes SHA-256 == artifact_sha256;
- only then atomically finalize local artifact-cache state;
- partial/mismatch never marked verified/terminal downstream;
- no VOICE_AI internal output path consumption.

Do not create real WAV in production root.

## Tests / mechanical acceptance

At minimum cover:

1. Pilot canonical descriptor SHA/request_id exact fixture.
2. request_id regex compatibility.
3. first submit creates one claim/job.
4. exact duplicate submit returns same job.
5. concurrent duplicate submit yields exactly one successful claim identity.
6. same authorization + changed article/render/operation/voice identity fail-closed.
7. incomplete/corrupt claim fail-closed.
8. claim survives simulated restart/no auto-release.
9. render exact bytes PASS.
10. render SHA mismatch => provider call count 0.
11. render missing/unreadable/path escape/symlink ambiguity/decode failure => provider call count 0.
12. verify-once/send-same-object semantics testable by injected provider capture.
13. initial provider READY->PASS fake lifecycle.
14. provider busy/not-ready no new identity.
15. unknown/connection failure enters conservative state, no new ID.
16. same-id reconcile terminal replay returns same run/artifact identity.
17. artifact SHA PASS and mismatch/partial fail-closed.
18. status/result are short read-only operations and never POST.
19. production root is never created during tests.
20. permissions/path contract validation where mechanically testable.
21. no full TTS text persisted in job/claim/log fixtures.

## Write-set

Allowed:
- minimal new/edited Website-owned scripts required for runner;
- tests/fixtures strictly for this runner;
- this task package;
- `docs/tasks/current.md`.

Do not modify:
- `src/`
- formal articles/render output
- VOICE_AI
- RonnieAutomation
- Hermes
- R2/NAS
- deployment config
- existing unrelated scripts unless strictly unavoidable and justified.

## Deliverables

Under `docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-implementation-20261007/`:
- `implementation.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md`.

## Forbidden side effects

- do not claim the real Pilot authorization
- do not submit the real Pilot
- do not POST real /v1/speech
- do not generate WAV/MP3
- do not create production runtime root
- do not install/bootstrap/kickstart LaunchAgent
- do not modify VOICE_AI/RonnieAutomation/Hermes
- do not R2/NAS/deploy
- do not commit/push

## Stop / verdict

Give one:
- `PASS_S4_DURABLE_RUNNER_IMPLEMENTED / READY_FOR_INDEPENDENT_AUDIT`
- `BLOCKED_S4_DURABLE_RUNNER_IMPLEMENTATION / RETURN_TO_MASTER_CONTROL`

Stop after implementation + verification. Do not activate Pilot.
