# REALTIME_STAGING_TEST_20261029 — Owner 修订：会话式 GPT 分块翻译 / Hermes 文件执行

状态：`OWNER_WORKFLOW_CHANGE_APPROVED / TELEGRAM_DISPATCH_PENDING`。
生效范围：本任务后续新尝试；不追溯改写 `hermes-gemma4-retest-01` 的 FAIL，也不抹除 retest-02 manifest 错误记录。本修订覆盖旧任务书中“Gemma 4 必须负责中文翻译”的限定，其他授权边界与质量硬门继续生效。

## 分工
1. **Hermes（Telegram）**：确认当前 Authority；读取并验证冻结英文 PDF 提取产物；确定性分成 2–3 块；将**单块英文全文**直接发送 Telegram 会话，不用文件作为英中翻译交接载体；接收 GPT 在 ChatGPT 会话生成的对应中文全文；以 Hermes 自身工具将该段中文真实落盘、独立回读、记录 SHA/bytes/chars；依序处理各块；核验合并、输出最终中文候选并交独立审核。
2. **GPT（ChatGPT 会话）**：只依据用户粘贴的当前块英文与业务翻译规则，按忠实度优先逐块翻译中文；不自行改写英文、不借用旧 Hermes/GPT 译稿；不通过文件传递译文，不代替 Hermes 执行写入或完成声明。
3. **用户**：目前没有已授权且已验证的 Telegram↔ChatGPT 自动消息传递接口，用户在两种会话间转发当前块文本。不得假装 GPT 可直接给 Telegram 发消息。
4. **Owner 独立审核**：在 Hermes 全文写入合并且有真实证据后，双向比对冻结英文原稿和中文候选，独立做 Missing、Compressed、Mistranslated、Needs confirmation 审核及 Project Bible 门。物理写入 PASS ≠ 忠实度 PASS。

## 输入与分块
冻结英文 `data/raw/分享/How Do We Grow in the Grace and Knowledge of Christ.en.txt`；8062 bytes、7958 Unicode 字符、126 行、SHA-256 `5142dc2fc01ba2afb9cc70bb9f6c2da8c2f17a5bcbf4e0c1a339f5c76a88c2e1`。
既定非重叠块：01 = 1–32 行（包括换行 2073 字符）；02 = 33–75 行（2634）；03 = 76–126 行（3251）。拼接必须逐字节还原冻结英文。旧 `hermes-gemma4-retest-02/manifest.json` 记录源 SHA 与字符数错误，必须由 Hermes 使用真实文件工具自修自证，不得把旧 FAIL 标为历史不存在。
“翻译不用文件交接”指跨 GPT/Hermes 之间**只交换当前块的会话正文**；Hermes 内部按训练目标**必须持久化**译文、运行证据和最终稿，避免上下文重置导致丢失。

## 会话协议
- Hermes 每次只发送一个完整英文块：任务 ID、`CHUNK_ID`、行范围、源 SHA、块英文原文，及该块涉及的相关术语、经文约束；不得把整个规则库/历史对话拼入 Telegram 上下文。
- GPT 只返回本块中文，保留所有句意、问题、引语归属及段落/标题、经文引用、结语；不做摘要。经文必须从 Translation Owner 当前受控 `CUVMPS Rv2 Project Bible` 提供的真实文本获取；若未由受控来源提供，对英文引文使用准确的经文占位和引用信息，不可凭记忆生成标准和合本正文，也不可在输出中自称 Bible Gate PASS。
- 每块中文传回 Telegram 时明确 `CHUNK_ID`；Hermes 真实写入其隔离工作目录，只接受该 ID 一次，独立读取并返回文字大小及 SHA；再继续下一块。
- 三块全部验收后，Hermes 按顺序合并，消除仅用于分块识别的控制标记，运行 Translation Owner 的完整性、中文可读性、现场语境、反向核对四门、术语和经文硬门；禁止因为自动门通过就宣称正式 E1 PASS。
- 不修改既有 Gemini/Gemma 测试证据及 Website Owner 旧候选、不发布、不 Git push、不 NAS、不邮件。

## 验收
分离三项裁决：`HERMES_SOURCE_CHUNKING_PASS/FAIL`、`GPT_CHAT_TRANSLATION_FIDELITY_PASS/FAIL/PENDING`、`HERMES_WRITE_MERGE_READBACK_PASS/FAIL`；最终忠实度与 Project Bible 独立审查由 Owner 裁决。
