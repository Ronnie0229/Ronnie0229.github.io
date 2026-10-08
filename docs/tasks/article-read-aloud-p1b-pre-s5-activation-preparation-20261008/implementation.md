# Implementation — S5 Minimal Pilot Activation Preparation

日期：2026-10-08

正式 verdict：`PASS_S5_MINIMAL_PILOT_ACTIVATION_PREP / READY_FOR_CONTROLLED_SINGLE_ARTICLE_PILOT_AUTHORIZATION`

## Actual implementation

根据 Master scope correction，没有新增 activation wrapper，也没有修改 `scripts/read_aloud_s4_runner.py`。

复用现有：
- `worker_once()`
- CLI `worker-once`
- `submit/status/result/reconcile`
- S4 execution owner / exactly-once / artifact gates。

唯一新增 executable-facing code 是 isolated Pilot-readiness regression：
- `scripts/tests/test_read_aloud_s5_activation.py`

它使用 temp runtime root + fake provider，不接触真实 provider或 production root。

## Activation-specific proofs

新增 5 个测试证明：
1. idle one-shot => provider ready/speech/artifact 全部 0；
2. queued job => 只走既有 S4 path一次，request_id保持不变；terminal后第二次 one-shot idle、无第二次 speech；
3. provider not ready => `WAITING_PROVIDER_READY`，speech/artifact=0；
4. UNKNOWN reentry => 只使用原 request_id，不生成新 identity；
5. tests 全程 production root absent。

Stale-owner、single-worker concurrency、terminal reconcile、no-full-text、authorization claim、render binding、artifact SHA 等无需在 S5复制实现，直接由 fresh-PASS S4 regression suite继续验证。

## Long-lifecycle chronology

- 第一次写 activation test 文件被 CodexPro secret-looking-content guard 在落盘前拒绝；无项目 mutation。
- 第二次仍因 fixture形态触发同一 pre-write guard；无项目 mutation。
- 去掉非必要 stale-owner fixture duplication，改为复用 S4既有 stale-owner regression；测试文件成功写入。
- 第一次 py_compile错误引用原宽 scope 下并未创建的 `scripts/read_aloud_s5_activation.py`，命令 FAIL；这确认没有新增不必要 wrapper。
- 按实际 write-set重跑 py_compile => PASS。
- S5 activation tests => `5/5 PASS`。
- S4 runner => `54/54 PASS`。
- full Website Python => `120/120 PASS`。

所有中途 FAIL/guard chronology 保留，不被最终 PASS覆盖。

## No S4 semantic change

S5 没有修改 S4 runner，因此没有触发“Pilot前必须再做 fresh independent audit”的条件。
