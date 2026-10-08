# Verification — S4 Provider Evidence Semantic Persistence Closure

正式 verdict：`PASS_S4_PROVIDER_EVIDENCE_SEMANTIC_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`

## Required semantic matrix

- wrong-but-regex-valid PASS request_id：raw fail-closed；artifact=0；marker absent；persisted request_id absent：PASS
- PASS + bounded nonempty failure_code：raw fail-closed；artifact=0；marker absent；persisted failure_code absent：PASS
- valid BLOCKED + matching request_id + valid failure_code：TERMINAL_BLOCKED；request_id/failure_code persisted：PASS
- valid FAIL_CLOSED + matching request_id + valid failure_code：TERMINAL_FAIL_CLOSED；request_id/failure_code persisted：PASS
- BLOCKED carrying syntactically-valid PASS-only identities：all PASS-only identity markers absent：PASS
- FAIL_CLOSED carrying syntactically-valid PASS-only identities：all PASS-only identity markers absent：PASS
- BLOCKED wrong-but-valid request_id：request/failure/PASS-only identity evidence not attributed to current job：PASS
- FAIL_CLOSED wrong-but-valid request_id：request/failure/PASS-only identity evidence not attributed to current job：PASS
- PASS with one invalid success field：invalid marker absent；artifact=0；other individually valid/current-job-compatible diagnostics retained：PASS
- unknown/malformed status with valid-looking fields：provider_result evidence empty；local fail-closed classification bounded：PASS
- exact valid PASS：request_id/run_id/artifact_ref/artifact_sha256/receipt_ref persist；artifact SHA verify/finalize succeeds：PASS
- prior oversized/malformed allowlisted attacks remain passing：PASS
- unknown 5KB provider body marker remains absent：PASS

所有 marker-absence cases 直接读取 serialized durable job JSON text，不只比较 parsed dict。

## Regression

`python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS

First semantic runner matrix => `51/51 PASS`

First full Website Python after semantic implementation => `112/112 PASS`

Expanded current-job/status matrix runner => `53/53 PASS`

Final full Website Python => `114/114 PASS`

既有关键 regression 在 runner suite 中继续通过：

- execution mutual exclusion：PASS
- stale execution owner conservative behavior：PASS
- authorization O_EXCL claim + duplicate submit：PASS
- exact render binding / symlink / SHA / UTF-8 rejection：PASS
- artifact SHA verify/finalize：PASS
- terminal reconcile no duplicate provider call：PASS
- production root never created：PASS

Final boundary：

- `PRODUCTION_ROOT_EXISTS=False`
- implementation task temp leftovers：`[]`
- semantic closure task temp leftovers：`[]`

## Diff hygiene

CodexPro 当前 connector policy 明确要求 Git status/diff 使用 `show_changes`，不得通过 bash 运行 `git diff` 类命令。因此本 Executor没有绕过 policy 执行 literal `git diff --check`。

替代机械核验：

- allowed changed source/task files full-file trailing whitespace scan：PASS
- space-before-tab indentation scan：PASS
- EOF newline scan：PASS
- CodexPro `show_changes` scope review：PASS / no risk signal

该工具约束作为 evidence note 保留，供 fresh independent Auditor 在其允许环境中复跑 literal `git diff --check`。

## Chronology preserved

- original bounded implementation PASS
- independent implementation audit BLOCKED
- targeted execution/identity remediation PASS
- targeted remediation fresh re-audit BLOCKED residual
- bounded evidence remediation PASS
- bounded evidence fresh re-audit `BLOCKED_S4_PROVIDER_EVIDENCE_BOUNDED_REAUDIT`
- semantic closure Executor: 51/51 → 112/112 → expanded 53/53 → final 114/114 PASS

## Forbidden side effects

Pilot remains `UNCLAIMED / NOT_CONSUMED`; no real provider POST; no production runtime root; no LaunchAgent; no audio; no external mutation; no R2/NAS/deploy; no commit/push.
