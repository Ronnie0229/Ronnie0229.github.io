# REALTIME_STAGING_TEST_20261029 — 新会话正式交接（2026-11-05）

## 0. 交接定位与当前裁决

- 正式工作区：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`。
- 任务根目录：`docs/tasks/realtime-staging-test-20261029/`。
- 当前流程权威修订：`OWNER_CHAT_TRANSLATION_HERMES_WRITE_WORKFLOW_20261105.md`；原 `HERMES_RETEST02_TRANSLATION_OWNER_GOVERNED_REQUEST.md` 仅为历史训练请求，曾要求 Gemma 4 自己翻译，**已由本次 Owner 流程调整取代该执行职责**。
- 当前精确状态：`CHUNK01_02_PHYSICAL_FILES_PRESENT / RECEIPT_IDENTITY_FAIL / CHUNK03_GPT_TRANSLATED_IN_CHAT_NOT_WRITTEN / MERGE_PENDING / FIDELITY_PENDING / PROJECT_BIBLE_GATE_PENDING`。
- 这是业务交接，不代表自动执行、Telegram 发送或授权生产副作用。

## 1. Owner 最新明确决策（不可再按旧流程执行）

Hermes（Telegram Agent）负责 PDF 英文提取、核对冻结原稿、确定性分块，以及**收到 GPT 中文后使用真实工具原样写入、独立回读和合并**；GPT 在 ChatGPT 会话接收英文块、依据正式翻译增强规则翻译中文，并通过会话正文交给用户转发至 Telegram。**翻译交接不使用文件**，但 Hermes 必须将接收的中文落盘，以免会话上下文重置。不要让 Hermes/Gemma4 再译正文，也不要由 GPT/CodexPro 代替 Hermes 写训练结果。

跨 Telegram / ChatGPT 的内容目前由用户转发，未建立已验证的自动消息连接。优先在同一执行授权下连续处理，避免每一步都让用户催。每次 Telegram 只给一个当前块，避免历史曾出现的 `Context length exceeded (25,971 tokens)` / 自动重置。

## 2. 冻结英文源稿与已准入边界

- 原 PDF：`data/raw/分享/How Do We Grow in the Grace and Knowledge of Christ.pdf`，历史冻结 SHA `7e98a87c3a359ec4abb4f270b93ed669c692ae4582d3a57e7fd4c590cd94c0ab`。
- 当前正式英文稿：`data/raw/分享/How Do We Grow in the Grace and Knowledge of Christ.en.txt`；本次独立复算 SHA `5142dc2fc01ba2afb9cc70bb9f6c2da8c2f17a5bcbf4e0c1a339f5c76a88c2e1`；8062 bytes、7958 Unicode 字符、126 行。文本型 PDF 英文提取已有 `PASS_TEXT_BASED_SOURCE_ADMISSION`，不默认重做 OCR/图片核查。
- 英文分块按原始带换行文本计算：Chunk 01 第 1–32 行/2073 字符；Chunk 02 第 33–75 行/2634 字符；Chunk 03 第 76–126 行/3251 字符。无损合并曾验证 PASS。
- `hermes-gemma4-retest-02/manifest.json` 的来源 SHA 和分块字符计数曾错误，独立报告 `HERMES_RETEST02_MANIFEST_INDEPENDENT_AUDIT.md` 为 FAIL，必须保留历史。

## 3. 中文分块现场文件事实（本次通过 CodexPro exact workspace 独立重新读取）

| 对象 | 实际状态 | bytes | Unicode chars | 独立 SHA-256 |
|---|---|---:|---:|---|
| `chunk_01_zh.txt` | 文件存在，内容不是与 GPT 发出文本逐字符一致 | 2204 | 803 | `55732a5c1bb2d33918e2440868418d3abfe6cb79f84091f5748ab8567f643424` |
| `chunk_02_zh.txt` | 文件存在，内容未保留原 GPT markdown/空行等格式 | 3057 | 1132 | `b934aebca9bf72e35f9b862ac48ae8b9d78c50cca91cb8a146837553635862c6` |
| `chunk_03_zh.txt` | 文件尚不存在 | — | — | — |

- Hermes 自报 CHUNK 01 为 2258 bytes / 857 chars / SHA `0c529efe46c393f38daf5ab13559c68080c2c4b359ff3aedc296b409b65d4046`，与实际文件不符。实测文字还有 `使徒彼德` vs GPT 原文 `使徒彼得`、丢失标题 `#`、小标题 `##`。
- Hermes 自报 CHUNK 02 为 3111 bytes / 1186 chars / SHA `b832bb598279391923c4e9bc6ef7c08eb18c480d9202aafe15724e042da93129`，与实际文件不符。它解释差异由 `read_file` 行号前缀造成，但未给出可验证的输入→工具参数→磁盘 SHA 链，不应认可。**两块自报与独立实际均恰好差 54 bytes/字符**，需检查固定偏置/计算路径，但不能擅自宣称其根因。
- 物理文件存在不等于原样交付 PASS，且绝对不能把 Hermes 自报 `WRITE_VERIFIED` 当成独立身份验收。

## 4. CHUNK 03 翻译状态及回收方法

用户将 CHUNK 03 英文先分成 `(1/2)` 和 `(2/2)` 两条提供。GPT 已在**此前聊天**输出完整第 76–126 行中文译文和 Telegram 单次可复制写入指令，包含标题“那么，我们如何在基督的恩典和知识上长进？”及结尾“所以，去吧！靠着主的灵在你们里面运行的大能，不断长进。”，其中罗马书1:16–17、腓立比书1:6下采用了正式 CUVMPS Rv2 Project Bible 来源。**本次未检到 `chunk_03_zh.txt`。**

如果新会话缺少此前那条完整中文 Telegram 消息，应先从用户转发内容或本项目明确授权的聊天上下文中恢复，而不是凭文件不存在就虚构 Hermes 写入成功。必要时基于冻结英文第三块由 GPT 再译，并明确标明新候选与旧会话候选的区别；不要让 Hermes 自行重译。

## 5. 正式翻译规则和经文硬门

只读正式项目：`/Volumes/DevSSD/RonnieWork/RonnieCross/本地讲章翻译增强项目`，fresh-read `AGENTS.md`、`STATUS.md`、`01_rules/01_翻译总规则.md`、`02_terms/02_术语表_专名表.md`、`05_prompts/translation_prompt_template.md`、`docs/QUALITY_GATES.md` 和 task-relevant authority。
- 不删减原文 proposition、引语署名、问句、劝勉、标题、大纲、结尾；不新增解释；结构与同篇术语一致。
- 使用经文正式受控数据 `03_bible/project_bible/project_cuvmps_verses.tsv`（CUVMPS Rv2），不凭记忆生成“似乎标准”的经文。独立 GPT 翻译候选仍需完整 E1 fidelity 及 Project Bible Gate；逐节经文核验未全篇完成不得声称 PASS。
- 翻译质量门：覆盖完整性、中文可读性、现场语境、反向逐段核对，加术语与经文硬门。Hermes 的工具写入测试与忠实度审核必须分开裁决。

## 6. 新会话应连续完成的事项

1. CodexPro **先打开 exact Website workspace**，fresh-read `AGENTS.md`、当前 authority、上述流程修订和本交接文件。若 root 不一致则停止，不静默借用其它项目。
2. 重新只读确认 CHUNK 01/02/03 的物理文件身份、sha、字节数；复查是否存在新的执行/回读证据或合并稿；以现场新证据为准。
3. CHUNK 03 若仍未真实落盘，继续让用户通过 Telegram 将 GPT 中文正文交给 Hermes，要求它原样写入并保留真实回执；**新会话不要由 CodexPro/GPT 代写训练文件**。
4. 对 CHUNK 01/02 已发现的身份回执差异做最小真实工具链诊断。优先取得原始 Telegram 消息文本、真实 write_file 参数/回执、独立磁盘 readback；不能单靠模型复述解释。不要贸然覆盖历史错误文件；以隔离新尝试保存定点修复并留 chronology。
5. 直到三个块的完整内容和原样写入均通过，才由 Hermes 合并全文，检查换行、Markdown 标题、经文、引语、首尾、段落覆盖以及 SHA、bytes、chars。
6. 之后 GPT 以全篇冻结英文和 Hermes 合并的中文文件进行独立双向忠实度审核，配合 Project Bible 受控经文逐节硬门；失败则指导执行方定点修复，不跳过 Gate。
7. 本任务不授权正式网站内容写入、Git commit/push、部署、邮件、NAS 归档。所有历史 PASS/FAIL/BLOCKED chronology 保留。

## 7. 关键项目文件索引

- `OWNER_CHAT_TRANSLATION_HERMES_WRITE_WORKFLOW_20261105.md`：当前分工及会话翻译流程。
- `HERMES_RETEST02_MANIFEST_INDEPENDENT_AUDIT.md`：原分块清单身份错误。
- `HERMES_GEMMA4_RETEST01_INDEPENDENT_AUDIT.md`：早期 Gemma4 翻译及工具证据失败。
- `HERMES_GEMMA4_POST_REMEDIATION_TRAINING_TASK.md`、`HERMES_RETEST02_TRANSLATION_OWNER_GOVERNED_REQUEST.md`：历史任务来源，涉及 Gemma4 自己翻译的部分不再适用。
- `SOURCE_ADMISSION_DECISION.md`：冻结英文源稿身份准入。
- `STEP20_DELIVERY_AUDIT_LATEST.md`、`DELIVERY_NEXT_ACTION.md`：历史错误交付。
