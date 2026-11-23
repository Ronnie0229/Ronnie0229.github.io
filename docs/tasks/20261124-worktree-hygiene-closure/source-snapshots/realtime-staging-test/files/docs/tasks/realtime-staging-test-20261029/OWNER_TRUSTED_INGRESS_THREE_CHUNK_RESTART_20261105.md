# REALTIME_STAGING_TEST_20261029｜三段受信写入业务接入授权与重启任务（2026-11-05）

状态：OWNER_APPROVED / SCOPED_RUNTIME_BOUND / CHUNK01_T1_T5_INDEPENDENT_BYTE_PASS / CHUNK02_ATTEMPT01_BLOCKED_TOOL_DISPATCH / CHUNK02_ATTEMPT02_PENDING / FULL_INDEPENDENT_AUDIT_PENDING。

## 本轮 Owner 授权与目标

Owner 已批准把 Hermes 现有 `hermes_telegram_ingress_a` 受信 Telegram T1→T5 写入机制接入 RonnieCross 真实隔离业务，并**重新执行三段中文会话消息原样写入**。本次不是让 Hermes 从旧文件读取中文，不是 Gemma 4 翻译，也不是普通 `write_file` 测试。翻译文本由 ChatGPT 当前会话完整提供，经用户复制并在 Telegram 以纯文本发送。每段新 Telegram 消息独立从真实 T1 入站正文提取，模型调用参数只能包含受信固定标识。

正式业务 root：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`。
允许写入的三个新文件，必须是受信宿主预先绑定的**精确绝对路径**：
- `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目/docs/tasks/realtime-staging-test-20261029/chunk_01_zh_trusted_01.txt`
- `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目/docs/tasks/realtime-staging-test-20261029/chunk_02_zh_trusted_01.txt`
- `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目/docs/tasks/realtime-staging-test-20261029/chunk_03_zh_trusted_01.txt`

固定受信目标 ID 已在 Hermes 安装模块绑定：`RCS_CH01_OUT`、`RCS_CH02_OUT`、`RCS_CH03_OUT`，消息 fixture 分别为 `RCS_CH01_T1`、`RCS_CH02_T1`、`RCS_CH03_T1`。2026-11-05 新模块 SHA `821601d6183dfeb25054be064d6a7a35a0bf56018a7d3b7a7bb0754d30865b52`，17/17 隔离测试 PASS，Gateway 重启并通过状态检查；真实 Telegram 尚未测试，独立审核仍 PENDING。模型不得自选目标路径、提交正文、读取旧中文文件，也不得走“最新消息”退路。

## 现场事实与硬门

- Hermes exact workspace：`/Volumes/DevSSD/RonnieWork/Hermes本地模型测试`；2026-11-05 fresh selector epoch-43 返回 `PASS_CURRENT_AUTHORITY`，但 `business_dispatch_authorized=false`，当前是 `COMPLETE_NO_ACTIVE_EXECUTOR`。
- 已安装 E41 受信工具固定 `FID=E41_T1`、`TID=E41_OUT`、`MARK=HERMES_E41_T1_TEST_20261105`，BASE 指向 Hermes 内部 E41 live 目录。其支持的是限定 E41 场景，而不是上述三项目文件。
- 旧 **BLOCKED_RUNTIME_TARGET_NOT_BOUND** 已由 epoch-44 有界接入解决，当前进入 CHUNK01 实发准入；尚无三段业务 T1→T5 证据，不得宣称 E2E PASS。不得退回 `write_file`，不得从磁盘旧候选复制文本替代用户消息。
- Hermes 源项目的 runtime/Authority 由 Hermes Owner 当前治理机制负责；本授权提供 RonnieCross/source Owner 精确跨项目业务写入边界，但不能伪造 Hermes 已安装 tool 或跳过受信工具的合法治理/独立审核。单一最小接入任务可在保持所有边界下推进，不要建设通用平台。
- 采用「只创建，不覆盖」语义；旧 `chunk_03_zh_retest_02.txt` 与过去失败保留。
- `BEGIN_TEXT` / `END_TEXT` 必须各自独立占一整行；宿主在冻结的 T1 上直接解析，不能由模型删减首尾空白；Telegram「以纯文字发送」后仅以真正入站 T1 为验收基准。
- T0 冻结（若能获取）、T1 完整消息、T1 payload、tool call identity、宿主 receipt 与 T5 磁盘逐字节 SHA/bytes/Unicode codepoints/LF 全部留证；任何 SHA、chars、bytes 不一致均 FAIL。模型最终口头成功不是验收。
- 三段串行：01 PASS 后 02，02 PASS 后 03；任一真实硬门 FAIL 则停止并最小修复；之后才能进入合并与 GPT 忠实度/Project Bible 独立审核。仅物理写入通过不等于译文忠实度通过。
- 本轮不授权网站正文修改、发布、commit/push、部署、NAS、邮件、其它 runtime/model 或 Telegram 附件 B。
- 保留 epoch-39/40/41/42/43、旧 CHUNK03 两次 write_file、两次覆盖、虚假回执及旧 01/02 文件等全部 FAIL/BLOCKED/PASS chronology。

## 当前未完成与立即下一步

1. Hermes 项目必须根据本轮 Owner 精确授权与本业务目标，合法开启最小 runtime binding（必要的 Gateway reload/restart 只在授权和前置备份、身份校验通过后），并由独立身份验证上述三个固定目标已真实生效。
2. 本轮 ChatGPT 必须按 01→02→03 在 Telegram 提供**全文在消息中**的短执行指令，不使用旧文件复制，不使用未知目标 ID 冒充已注册。
3. 三块各以新入站消息写入指定新文件，独立核验 T1→T5。若不具备本次受信工具映射，不发送无效测试命令。

请分发给：执行者（Hermes 受信工具固定业务目标接入），然后独立审核者复核，最后 RonnieCross 发出三段 Telegram 正文。
