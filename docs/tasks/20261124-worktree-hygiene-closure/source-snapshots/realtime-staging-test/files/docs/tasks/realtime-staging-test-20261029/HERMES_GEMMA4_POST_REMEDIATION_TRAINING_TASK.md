# REALTIME_STAGING_TEST_20261029 — Hermes Gemma 4 长文本写入整改后实战训练发布单

## 任务身份
- TASK_ID: `REALTIME_STAGING_TEST_20261029_GEMMA4_POST_REMEDIATION_REAL_WORLD_RETEST`
- 业务 Owner: `RONNIECROSS_WEBSITE_PROJECT_OWNER`
- 执行 Owner: `HERMES_CURRENT_LEGAL_MASTER_CONTROL`（仅由 Hermes 项目当前 authority 决定实际 Executor、当前模型和工具配置）
- 本文件性质：**Website 侧训练任务请求 / acceptance contract**，不是 Hermes 项目的执行授权、模型配置或整改完成证明。
- 网站 exact workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`
- 状态：`ISSUED_TO_HERMES_PENDING_EXECUTION`

## 业务背景与已知事实
先前 Hermes STEP20 多次报告完成中文文件写入，但 Website CodexPro 独立检测目标文件不存在，记录在 `STEP20_DELIVERY_AUDIT_LATEST.md`；曾进行文件名空格探针：可成功创建含空格文件，但第三份内容与预期不符。2026-11-01 Website Owner 自行生成的候选文件 **不是 Hermes 训练成果，不计分**，必须隔离，不得读取、复制或覆盖。历史 FAIL、探针 PASS 与后来 Website Owner 独立写入 PASS 均保留。

Hermes 项目据称已解决 Gemma 4 长文本写入问题，**本任务要实证验证该修复在真实翻译工作流中有效**；执行者必须 fresh-read Hermes exact workspace authority、current model runtime、修复证据与当前训练准入，不能根据此业务请求臆断修复已生效。不得从 Website Owner 切换到 Hermes 工程 root 写入或更改配置。

## 冻结的业务输入
- 来源：`data/raw/分享/How Do We Grow in the Grace and Knowledge of Christ.en.txt`
- SHA-256: `5142dc2fc01ba2afb9cc70bb9f6c2da8c2f17a5bcbf4e0c1a339f5c76a88c2e1`
- 8062 bytes、7958 Unicode 字符，四页 PDF 文本型来源已准入，不再做 PDF OCR/视觉切图。
- 原 PDF、英文源稿、existing Website Owner candidate 均只读。
- 不许用聊天记忆、旧候选、其它执行者的中文稿作为本次训练的翻译输入或输出。

## 授权边界与写入白名单
Hermes 本地模型的实际使用/工具调用由 Hermes 项目本身当前有效 authority 决定；先由合法总控验明当前 Gemma 4 模型、oMLX/runtime、工具链版本和修复后 admission。若当前 authority 不允许真实模型运行或跨项目受限目录写入，则报告精确授权断点，**不得静默升级模型/修改服务**。

在 Website Owner 当前训练邀请范围内，仅允许将本次训练产物写入 Website 的以下**新隔离目录**，不覆盖其它文件：
`docs/tasks/realtime-staging-test-20261029/hermes-gemma4-retest-01/`

输出必须至少包含：
- `translation.zh.candidate.md`：Hermes+当前获准模型独立形成的完整中文候选。
- `STEP21_REVIEW_HANDOFF.md`：绑定英文及中文实际 SHA。
- `execution-evidence.md` 或等效原始执行证据路径（不得伪造 shell、模型响应或 tool_calls）。

不许修改 Website Owner 已生成的 `How Do We Grow in the Grace and Knowledge of Christ.zh.candidate.md` 和既有 `STEP21_REVIEW_HANDOFF.md`。

## 连续执行合同
1. Hermes 总控确认 exact root、fresh authority、模型准入、必要的跨项目写入边界；如未授权，阻断并明确需何种合法授权。
2. 在 Hermes 执行环境**真实**读取冻结英文全文，计算 SHA/bytes/chars；确认匹配后才启动实际已批准 Gemma 4 翻译运行（不可假冒模型调用）。
3. 仅按来源逐段翻译完整中文，不删 proposition、问题、引语归属、祷告、经文引用、结束语；Project Bible 定本不可访问时，将经文列为 `PROJECT_BIBLE_GATE_PENDING`，不得自由假装采用标准经文。翻译候选允许进入独立忠实度审核，但不能宣称 Bible Gate PASS。
4. 使用 Hermes 实际工具 dispatch 将全文写入上述隔离输出路径。禁止以自然语言“已写入”替代调用。记录模型响应/工具调用（允许必要的敏感内容脱敏）、调用参数、返回值、错误、目标绝对路径、物理 bytes、readback、SHA。
5. 在**不同于写入调用的后续真实工具调用**中重新打开磁盘文件，全文读取并与待写入字节/内容逐项对照，验证 SHA、UTF-8、大小、全文首尾、内容完整性。工具调用失败可在同一 authority 内定点修复并重测，保留尝试 chronology；不得重用旧 PASS 冒充本次。
6. 真实生成并独立回读 handoff 文件，标记 `INDEPENDENT_FIDELITY_REVIEW_REQUIRED`。
7. 提交准确执行摘要和 evidence 路径。不得代替 Website Owner 宣布翻译独立审核 PASS，也不得部署/发布/Git push/NAS/邮件。

## 双轨验收（由 Website Owner 独立执行）
A. `AGENT_LONG_TEXT_DELIVERY_PASS/FAIL`：验明真实 Gemma 4/工具身份、源文 SHA、写入与 readback 的原始工具证据和跨工具 CodexPro 实际重读候选 SHA/bytes/chars、内容完整性；内容文件必须是 Hermes 自主生成，不可复制 GPT-6 候选。

B. `TRANSLATION_FIDELITY_PASS/FAIL/PENDING`：独立从英文与新中文逐句双向审核 Missing/Compressed/Mistranslated/Needs confirmation、反向新增、引语归属、所有经文、论证及结尾；Project Bible 另行进行受控硬门核验。A PASS 不推出 B PASS，B PASS 不替代 A。

**现阶段禁止**生产页面修改、Git commit/push、部署、通知、NAS 归档、Hermes 模型默认配置变更。

## 完成与失败回执
- 成功交付：`HERMES_RETEST_DELIVERED_FOR_WEBSITE_INDEPENDENT_AUDIT`（不是 E1 PASS）。
- 若模型执行/跨项目写权限未被当前 authority 授权：`BLOCKED_AUTHORITY` 并提供确定缺口。
- 若写入/回读失败：`FAIL_AGENT_DELIVERY`，提供原始失败证据。
- 必须保留旧失败及每次修复历史。
