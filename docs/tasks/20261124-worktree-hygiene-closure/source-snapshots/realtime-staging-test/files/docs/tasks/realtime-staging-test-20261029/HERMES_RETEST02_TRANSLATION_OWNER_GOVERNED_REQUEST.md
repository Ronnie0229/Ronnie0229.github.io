# Hermes retest-02 — Translation Owner 规则绑定的真实翻译训练请求

- 发起方：RonnieCross Website Owner；接收入口：Hermes Telegram Agent。
- 业务任务：`REALTIME_STAGING_TEST_20261029_GEMMA4_POST_REMEDIATION_REAL_WORLD_RETEST`。
- 本请求为 **Website source-local handoff**，不写入、不改变 Translation Owner/Hermes authority，不批准越界的模型运行或跨项目写操作。
- 现状：`hermes-gemma4-retest-01/` 中确实存在中文文件（8077 bytes / SHA `2acdeeac663c9161e6db720326a7c96f852e241179ac4898400ad6bb65a2335b`），但独立审查 `HERMES_GEMMA4_RETEST01_INDEPENDENT_AUDIT.md` 已判翻译忠实度 FAIL、模型→工具完整执行证据不足。保留原始 attempt-01。

## 精确输入与输出
- 源文 `data/raw/分享/How Do We Grow in the Grace and Knowledge of Christ.en.txt`，8062 bytes，SHA `5142dc2fc01ba2afb9cc70bb9f6c2da8c2f17a5bcbf4e0c1a339f5c76a88c2e1`。
- 不得读取或复制 Website Owner 的旧中文候选文件。
- 本次只允许在 `docs/tasks/realtime-staging-test-20261029/hermes-gemma4-retest-02/` 保存本轮中文候选、分块原始模型输出、模型/工具调用回执、chunk manifests、quality reports、step21 handoff。不能覆盖旧 attempt-01。

## 受控规则来源（只读，必须现场 fresh-read）
exact root: `/Volumes/DevSSD/RonnieWork/RonnieCross/本地讲章翻译增强项目`。
1. `AGENTS.md`、`STATUS.md`、`tasks/current/index.json`。
2. `01_rules/01_翻译总规则.md`（包括段落、经文占位、分块、四道质量门）；`01_rules/07_错误避免清单.md`。
3. `02_terms/02_术语表_专名表.md`、`03_bible/README.md`、`03_bible/04_经文写法规则表.md`。
4. `05_prompts/translation_prompt_template.md`、`05_prompts/model_system_instructions.md`。
5. `docs/WORKFLOW.md`、`docs/QUALITY_GATES.md`、`docs/BENCHMARK_AND_TESTING.md`。
6. `09_config/model_strategy.json`、`09_config/translation_workflow.json`、`09_config/quality_review_risk_rules.json`；仅按需读取 task-relevant rule registry。
7. 正式经文数据：`03_bible/project_bible/project_cuvmps_verses.tsv`，**仅在现行 Hermes/Translation Owner authority 合法允许的只读路径下读取**；未取得权威经文不可凭模型记忆补写，使用正式占位结构并标 `PROJECT_BIBLE_GATE_PENDING`。

### 实际训练规则摘要（不可代替上述 fresh-read）
- 译文保持英文所有 proposition、引语署名、问题、结尾、结构；不摘要、不增加、不改写神学含义，不复制规则区。
- 默认按自然段/标题边界拆为约 2500–3500 英文字符的块；每块只携带该块相关术语和经文，块输出末尾 `[CHUNK_TRANSLATION_END]`，merge 后去标记，检查块边界重复/漏译。
- 每块先过现有质量门；全文强制进行覆盖完整性、中文可读性、现场语境、反向逐段核对四门，及术语门、经文占位硬门、受控插入后逐节比对。不得发明新质量门或降低阈值。
- 项目固定历史测试结论：T01–T50 closed，363 项自动测试 PASS（截至该项目状态文档）。该状态文档的本地模型配置为 qwen3:14b 主候选、gemma4:e4b 工具/质量测试角色；**不能据此自称当前 Hermes runtime 就是该模型**。实际运行必须由 Hermes 当前 authority 核验并批准，不自动 fallback，不更改默认模型/配置。

## Hermes Telegram 一次性连续执行
1. 当前合法 Hermes 总控先核验 exact root、authority、模型/工具 identity、Translation Owner 只读接口和本次跨项目写入范围；若不允许则 `BLOCKED_AUTHORITY`，不得自行改配置。
2. 读取冻结英文 source 并按规则分块，保存 chunk manifest（原文边界、编号、来源 SHA、长度）。检查每个块恰好一次拼接可恢复全篇。
3. 使用获准 Gemma 4 真实模型进行分块翻译。保留原始响应和工具证据；不得将 GPT-6 译文、旧 Hermes 译文或工具日志伪装成模型生成结果。
4. 执行现有术语、经文结构和逐块质量门；不合格块在合法范围内定点重译，完整保留 FAIL→修复→PASS chronology。对 retest-01 已知 `不可理喻`、`我们受伤`、`基督щу`、`We deserve death` 缺失、罗马书1:16–17 误译、rich young ruler 动作遗漏等必须专项检查。
5. 合并、运行全文四质量门，缺失受控经文时保留正式占位，不得自由翻经文；生成可复核中文候选。
6. 由真实 write_file/工具 dispatch 将中文候选写入 `hermes-gemma4-retest-02/translation.zh.candidate.md`，后续**独立**回读整文件，与生成的目标中文全文逐字节一致，记录 bytes/chars/SHA，确认不等于英文 SHA。保留实际 model response、tool_calls、dispatch、write receipt、readback 原始证据。
7. 生成且独立回读 `STEP21_REVIEW_HANDOFF.md` 及质量/证据文档，绑定准确 SHA、经文 Gate 状态、尚待独立审核风险。仅可报告 `DELIVERED_FOR_WEBSITE_INDEPENDENT_AUDIT`；不得宣布独立 E1 PASS 或发布。

## 双轨正式验收
- Agent delivery: 真实模型来源→完整中文文本→工具写入→独立回读的物理和内容映射。
- Translation fidelity: Website Owner 独立双向逐句检查 Missing、Compressed、Mistranslated、Needs confirmation、反向新增；Project Bible 受控文本另行验证；不把执行者自检当正式 PASS。

无 Git commit/push、网站部署、邮件、NAS 归档或其它项目配置修改。
