# Audit — P1B-pre Targeted Remediation Fresh Independent Re-audit

日期：2026-10-07

角色：`ARTICLE_READ_ALOUD_P1B_PRE_TARGETED_REMEDIATION_FRESH_INDEPENDENT_AUDITOR / AUDITOR`

正式裁决：

`PASS_TARGETED_REMEDIATION_FRESH_REAUDIT / READY_FOR_BOUNDED_IMPLEMENTATION`

## 1. Independent basis

本轮未采用 remediation Executor 的 `PASS_TARGETED_ARCHITECTURE_REMEDIATION` 作为预设结论。

独立 fresh-read / fresh-check：
- 原 independent audit material findings；
- targeted remediation amendment / task / verification / result；
- 当前 frozen Pilot Render View；
- VOICE_AI current request_id contract / S1 replay boundary；
- 当前 host runtime parent 的只读 owner/permission/target-absence evidence。

本轮仅重审 Finding A、Finding B、runtime root freeze 与 Pilot deterministic identity；未重开此前已独立通过的总体架构。

## 2. Finding A — authorization one-time atomic claim

结论：`PASS / MATERIAL FINDING CLOSED BY CONTRACT`

整改已冻结：
- claim key 仅由 immutable `authorization_ref + generation_epoch` 决定，deterministic；
- 一个 authorization epoch 只能通过 Website-local OS-level exclusive-create 占用一次；
- claim 必须在任何 provider POST 前成立；
- claim 内容绑定 descriptor SHA、request_id、operation/article/render/voice contract identity；
- exact same binding duplicate submit 只能读取 existing claim / existing logical job identity；
- same authorization + different descriptor/request_id 必须 provider POST=0 并 fail-closed；
- crash 若发生在 claim create 后、durable completion 前，authorization 保持占用且进入人工 resolution，不会自动释放；
- timeout / disconnect / worker restart / host restart / busy / not-ready 均不能 mint new epoch；
- Website authorization claim 只拥有 user-authorization single-use truth，N6 继续独占 provider generation exactly-once truth。

Atomic exclusive-create + fail-closed-on-partial 的设计对当前单机短时 caller concurrency 已足够。无需 lease、DB、Redis、Celery 或 distributed lock。

## 3. Finding B — exact Render View binding before every possible POST

结论：`PASS / MATERIAL FINDING CLOSED BY CONTRACT`

整改已冻结：
- every possible provider POST（首次或 same-id reconcile replay）前都必须重新读取 bounded `render_ref` exact bytes；
- 对该同一 bytes object 计算 SHA-256，并要求 exact match immutable `render_sha256`；
- strict UTF-8 decode；
- POST `text` 直接来自刚验证的同一内存对象，不得 second read / trim / normalize / newline rewrite；
- missing / unreadable / path escape / symlink-rebinding ambiguity / SHA mismatch / decode failure / descriptor-request_id mismatch 全部 Website-side fail-closed，provider POST=0；
- read-only status/result path 不被错误强制重新 POST；
- frozen SHA 定义为 exact file-byte identity，不接受“语义等价但 bytes 不同”。

独立 fresh-read 当前 Pilot Render View：
- bytes=`10658`
- SHA-256=`5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`
- 与 P1A frozen identity 和 amendment 完全一致。

## 4. Runtime state root

结论：`PASS / FROZEN BEFORE IMPLEMENTATION`

exact root：

`/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`

独立只读现场核对：
- current uid=`501`
- parent exists=true
- parent owner uid=`501`
- parent mode=`0700`
- parent readable=true
- parent writable=true
- target root exists=false

合同已冻结：
- Website-owned / local-only / no-root；
- Git、NAS、VOICE_AI workspace 外；
- root/subdirs `0700`；
- files `0600`；
- no fallback；
- jobs/claims/logs 不持久化完整 TTS 正文；
- target 尚未创建，因此本 re-audit 没有产生 runtime spool side effect。

## 5. Pilot deterministic identity

独立使用 amendment 冻结字段和 canonical serialization 规则重算：

canonical descriptor：

`{"article_id":"post-32d30724d859c99c","authorization_ref":"article-read-aloud-pilot-generation-authorization-20261007-a1","generation_epoch":"pilot-20261007-a1","operation_id":"article-read-aloud-pilot-post-32d30724d859c99c","render_sha256":"5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a","schema":"ronniecross-readaloud-generation-operation/v1","voice_contract_id":"VOICE_AI_LOCAL_HTTP_V1"}`

独立重算：
- descriptor SHA-256=`49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`
- request_id=`rc-readaloud-v1:49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`
- request_id length=`80`

VOICE_AI current request_id regex：
`^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`

该 request_id 满足当前 contract。

## 6. Dual-truth / second-generation check

`PASS`

三层 truth 已机械分离：
- Website authorization claim：用户授权 single-use binding truth；
- Website job state：consumer orchestration truth；
- VOICE_AI N6：provider generation exactly-once/result truth。

未发现 Website claim/job state 被写成 provider generation truth，也未发现 N6 被错误用于替代用户授权 one-time consumption。

当前 contract 下没有合法 hidden second-generation path：
- same authorization 不允许 different request_id；
- timeout/restart/busy 不允许 new epoch；
- claim 不允许 delete-and-retry；
- render drift 不允许换 text/request_id；
- unknown/in-progress 不允许另建 job；
- launchd restart 不授权 regeneration。

## 7. Scope / overbuilding

`PASS`

整改严格停留在 Website S4 contract freeze：
- no VOICE_AI semantic change；
- no RonnieAutomation/Hermes worker dependency；
- no Redis/Celery/database；
- no generalized lease platform；
- no runtime creation；
- no implementation code。

## 8. Verdict

Finding A、Finding B 与 runtime root pre-implementation freeze 均已达到本 targeted re-audit denominator。

Formal verdict：

`PASS_TARGETED_REMEDIATION_FRESH_REAUDIT / READY_FOR_BOUNDED_IMPLEMENTATION`

该 PASS 只表示 architecture remediation 足以成为下一 bounded implementation task 的 authority basis；不等于已实现、已 claim、已 submit、已生成音频或已消耗 Pilot generation authorization。

