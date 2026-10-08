# Rollback / Deactivation — S5 Minimal Pilot Activation

S5选择 one-shot worker，因此 rollback/deactivation保持极简。

## Normal deactivation

- `worker-once` 正常返回后进程已退出；
- 不需要 unload launchd，因为本 S5未创建或安装任何 launchd服务；
- 不再调用 `worker-once` 即完成 deactivation。

## Evidence preservation

Deactivation不得删除或重写：
- `jobs/`
- `claims/`
- `execution-owner.json`（若存在）
- `artifact-cache/`
- bounded logs/evidence。

不得为了“恢复干净”释放 claim、删除 owner、换 request_id或重建 generation epoch。

## Ambiguous state

若 job 为 `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`：
- 不推断 provider未执行；
- 不生成新 request_id；
- 不重新 submit；
- 只允许同 request_id reconcile语义；
- 若同时有 stale owner，则先停下并保留 owner/evidence，等待现有 operator/manual authority。

## External boundary

Deactivation不启动/停止/重启 VOICE_AI，不修改 N6/provider state，不触碰R2/NAS/deploy。
