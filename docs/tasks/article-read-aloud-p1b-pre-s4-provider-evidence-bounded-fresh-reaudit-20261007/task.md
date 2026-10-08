# Article Read-Aloud P1B-pre — S4 Provider Evidence Bounded Persistence Fresh Independent Re-audit

状态：ACTIVE_FINAL_RESIDUAL_REAUDIT
日期：2026-10-07
Owner：Website / 个人网页项目
ROLE：ARTICLE_READ_ALOUD_P1B_PRE_S4_PROVIDER_EVIDENCE_BOUNDED_FRESH_INDEPENDENT_AUDITOR / AUDITOR
REPORT_TO：ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL

## Audit target

只审 fresh independent re-audit 剩下的唯一 residual：

**provider diagnostic evidence must not durable-persist arbitrary / oversized / malformed provider values merely because they use allowlisted keys.**

Primary sources:
- `docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-targeted-remediation-fresh-reaudit-20261007/audit.md`
- `docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-remediation-20261007/remediation.md`
- 同 remediation package 的 verification/result/task
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`

不得采用 remediation Executor 的 PASS 或 45/45、106/106 数字作为预设结论。

## Scope discipline

Already independently closed and out of scope unless this remediation regressed them:
- F-S4-IA-01 execution mutual exclusion
- authorization one-time claim
- descriptor/request_id derivation
- exact render binding
- artifact SHA verification
- N6/provider truth boundary
- anti-overbuilding

Do not reopen activation design.

## Required independent attacks

### A. Raw-provider-value persistence

Inject unique markers / large payloads into each allowlisted field independently:

- run_id
- artifact_ref
- receipt_ref
- request_id
- failure_code
- artifact_sha256
- status

Use:
- oversized strings
- malformed strings
- list/object/nested values
- strings containing recognizable long provider-body/TTS-like markers

For each invalid identity path, independently inspect the **serialized durable job JSON bytes/text** and prove:

1. Website terminal identity validation still fail-closes correctly.
2. artifact retrieval call count remains 0 where identity invalid.
3. marker/body is absent from durable JSON.
4. invalid raw field is absent rather than truncated/stringified/repaired into identity.
5. locally generated error classification remains bounded.

### B. Unknown-key persistence

Inject unknown keys containing at least ~5KB body/marker and nested structures.
Prove unknown key and marker are absent from durable job state.

### C. Valid evidence regression

Confirm exact valid:
- PASS persists bounded request_id/run_id/artifact_ref/artifact_sha256/receipt_ref and artifact succeeds;
- BLOCKED persists bounded request_id/failure_code and remains TERMINAL_BLOCKED;
- FAIL_CLOSED persists bounded request_id/failure_code and remains TERMINAL_FAIL_CLOSED.

Confirm evidence sanitization does not alter raw provider result used for terminal identity truth.

### D. No semantic regression

Fresh-check:
- execution owner source/design unchanged materially;
- no automatic takeover introduced;
- no full TTS text persists through provider evidence;
- production root remains absent;
- no new generic sanitizer/platform/DB/queue introduced.

## Regression

Independently rerun:
- py_compile
- runner suite
- full Website Python suite
- git diff --check
- production root absence

Chronology must preserve:
- original implementation PASS
- implementation independent audit BLOCKED
- first targeted remediation PASS
- targeted re-audit: F-S4-IA-01 CLOSED; F-S4-IA-02 residual BLOCKED
- bounded evidence remediation PASS
- this independent verdict

## Forbidden

- no implementation fixes
- no real Pilot claim/submit
- no real /v1/speech
- no production runtime root creation
- no LaunchAgent install/bootstrap/kickstart
- no WAV/MP3
- no external project mutation
- no Website src/article mutation
- no R2/NAS/deploy
- no commit/push

## Verdict

Give exactly one:

- `PASS_S4_PROVIDER_EVIDENCE_BOUNDED_FRESH_REAUDIT / READY_FOR_ACTIVATION_DESIGN`
or
- `BLOCKED_S4_PROVIDER_EVIDENCE_BOUNDED_REAUDIT / RETURN_TO_MASTER_CONTROL`

If BLOCKED, report only material residual + minimal remediation boundary; do not fix.

## Deliverables

Under:
`docs/tasks/article-read-aloud-p1b-pre-s4-provider-evidence-bounded-fresh-reaudit-20261007/`

Write:
- `audit.md`
- `verification.md`
- `result.md`
- `files-changed.md`
- `NEXT_HANDOFF.md`

Update `docs/tasks/current.md` if required.

Stop and hand back to Master Control.
