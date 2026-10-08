# Article Read-Aloud P1B-pre — Targeted Remediation Fresh Independent Re-audit

状态：ACTIVE_FRESH_REAUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_TARGETED_REMEDIATION_FRESH_INDEPENDENT_AUDITOR / AUDITOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Audit target

只审计以下 material closure，不重开已通过总体架构：

1. independent audit Finding A：
   generation authorization one-time atomic claim。
2. independent audit Finding B：
   every-possible-POST exact Render View binding。
3. implementation 前 runtime state root exact path/owner/permissions freeze。

Primary sources：
- `docs/tasks/article-read-aloud-p1b-pre-async-independent-audit-20261007/audit.md`
- `docs/tasks/article-read-aloud-p1b-pre-targeted-remediation-20261007/amendment.md`
- 同 remediation package 的 verification/result/task
- 必要的 Website/VOICE_AI current authority 只读核对

不得采用 remediation Executor 的 PASS 为预设结论。

## Required independent checks

### A. Authorization claim

确认：

- authorization_ref + generation_epoch claim key 唯一且 deterministic；
- one authorization 只能绑定 one immutable descriptor + one request_id；
- claim 在 provider POST 前完成；
- concurrent submit 下 exclusive-create/lock discipline 可以机械排他；
- same binding duplicate submit 只返回 existing job；
- same authorization + different descriptor/request_id 在 POST 前 fail-closed；
- crash after create but before durable complete 不会释放 authorization 或形成第二 identity；
- timeout/restart/busy 不会隐式 mint new epoch；
- Website claim truth 与 N6 provider exactly-once truth 不混淆。

### B. Render exact binding

确认：

- every possible provider POST（first/reconcile）都重新读取 bounded render_ref exact bytes；
- SHA-256 exact match frozen render_sha256；
- strict UTF-8 decode；
- POST text 来自同一已验证内存对象，不二次读取/normalize/trim；
- path escape/symlink/rebinding/missing/unreadable/SHA/decode mismatch 均 provider POST=0；
- read-only terminal result/status 不被错误要求重新 POST；
- current Pilot render_ref/SHA identity 与 P1A frozen artifact 相符。

### C. Runtime root

确认：
- exact path：`/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`
- Git/NAS/VOICE_AI workspace 外；
- Website-owned/local-only/no-root；
- parent current evidence 足够支持后续 bounded implementation；
- root/subdirs 0700, files 0600, no fallback；
- 当前 target 尚未创建；
- logs/job/claim 不持久化完整 TTS 正文。

### D. Pilot identity

独立重算 canonical descriptor SHA 与 request_id，必须精确得到：

- authorization_ref=`article-read-aloud-pilot-generation-authorization-20261007-a1`
- generation_epoch=`pilot-20261007-a1`
- descriptor SHA=`49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`
- request_id=`rc-readaloud-v1:49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`

确认该 identity 满足 VOICE_AI current request_id contract。

## Scope discipline

不得重开：
- Owner = Website S4
- VOICE_AI Local HTTP V1 unchanged
- N6 sole provider exactly-once authority
- filesystem spool + atomic JSON
- single worker
- short submit/status/result/reconcile callers
- no Redis/Celery/database/VOICE_AI async V2
除非发现新的 material contradiction，并必须明确给出证据和 materiality。

## Forbidden

- no implementation code
- no /v1/speech
- no claim/submit
- no runtime spool creation
- no WAV/MP3
- no LaunchAgent install
- no external project mutation
- no Website src/article mutation
- no commit/push
- no Pilot authorization consumption

## Verdict

只能给：

- `PASS_TARGETED_REMEDIATION_FRESH_REAUDIT / READY_FOR_BOUNDED_IMPLEMENTATION`
或
- `BLOCKED_TARGETED_REMEDIATION_REAUDIT / RETURN_TO_MASTER_CONTROL`

如 BLOCKED，只报告新的/仍未关闭的 material finding + 最小整改边界；不得实施。

## Deliverables

仅写：
- `docs/tasks/article-read-aloud-p1b-pre-targeted-remediation-fresh-reaudit-20261007/audit.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`
- 必要时更新 `docs/tasks/current.md`

完成后停止并交回 Master Control。
