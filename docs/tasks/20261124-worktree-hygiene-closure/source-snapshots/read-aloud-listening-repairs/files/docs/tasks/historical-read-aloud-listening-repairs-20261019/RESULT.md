# 历史文章有声阅读｜2026-10-19 用户线上人工试听验收与修复收件

状态：**ONE_PASS / THREE_REPAIR_REQUIRED / 18_DEFECT_TIMESTAMPS_RECEIVED / REGENERATION_NOT_YET_AUTHORIZED_OR_EXECUTED**。

此处为用户直接确认的试听结果，不将声学自动 QC 的 PASS 误记成人耳 PASS，也不将有声阅读缺陷转嫁为正文、经文或翻译质量失败。

| 文章 | Article ID | 正式音频时长 | 线上人工试听结果 | 需要定点核对的时间点 |
|---|---|---:|---|---|
| 《活着就是基督》 | `post-072eda6a5bfbe1f9` | 23:16 | REPAIR_REQUIRED（7） | `01:36`, `08:11`, `11:03`, `13:22`, `15:21`, `18:58`, `23:08` |
| 《如何荣耀神并永远以祂为乐？》 | `post-c313198e37dddf21` | 12:38.56 | REPAIR_REQUIRED（7） | `02:53`, `05:59`, `07:34`, `07:51`, `10:37`, `11:57`, `12:31` |
| 《以利亚与撒勒法寡妇：信靠神的供应》 | `post-d6033867e9b33cc1` | 08:35.92 | **HUMAN_LISTENING_PASS（0）** | 无 |
| 《帖撒罗尼迦前书 4:16｜在基督里死了的人必先复活是什么意思》 | `post-0d153ce310d0eebd` | 08:53.60 | REPAIR_REQUIRED（4） | `00:34`, `01:51`, `03:01`, `07:29` |

## 证据与边界

- 现场 fresh-read 正式生产仓库、现有 S4 workflows；四篇现有 workflow 均未挂载 `repair_support`（不代表原始 Provider 从未保留独立 chunk 证据，后续须查证）。
- 时间戳为**用户报告的缺陷附近位置**，不等同可直接切割的精确采样帧；用户没有提供问题类型（啸音、漏字、重复、发音、音量波动等），不得猜测。
- 其中 `23:08` 距《活着就是基督》已记录总时长 `23:16` 仅约 8 秒，属于应优先核对的尾段，保留实际结束语与完整性门。
- 第三篇用户确认整体人工试听 PASS，应保留原有发布资产，不再重新生成。
- 其余三篇先核对 NAS 既有 WAV、R2 已发布 MP3、Render View/source SHA、可用 chunk-to-text 映射和各时间点附近的音频片段，再制定**最小定点重新生成**方案；必须使用新 request/epoch，禁止复用已消费的一次性 TTS 凭据。
- 替代片段产物单独保存，原 WAV/R2/网页保持不变；每处对照原中文文本、前后语气和音量，验证无漏读、重复、拼接突变，完整新音频经最终技术 QC 才能提议受控替换发布。
- 用户此前明确以**发布后线上试听**为人工验收方式；不得将当前三篇的缺陷状态标记为 PASS 或完成修复，也不得宣称这 18 处已被定位至具体原始 TTS chunk。
- 本次只记录人工反馈及检查状态，不执行 TTS、媒体覆盖、网站修改、Git commit/push 或邮件。

## 2026-10-19 Owner 批准后执行进度

- 已再次 fresh-read RonnieCross authority；未改动 VOICE_AI 外部工程，未操作现有 R2/NAS/网站。
- 以原始 S4 WAV 为唯一声学输入，验证了每篇 WAV 的正式 SHA；从原音频完成 18 份无损 PCM 定位样本，每处取报告点前约 5 秒、后约 7 秒（尾段按实际结束时间截断）。这些样本**只用于诊断，不是修复版**。
- 机器可读清单：`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud/listening-repair-20261019/DEFECT_CLIP_MANIFEST.json`。其每条记录提供 article ID、报告时间、实际起止秒数、绝对路径、截取文件 SHA、原 WAV SHA。
- 原始 VOICE_AI 记录存在三个 `receipt_ref`：
  - Patrick：`voice-ai-receipt:8463b0be6c46c911ee9c4ddb18cdbb67983bfb45d2538315632e43237a768046`
  - 荣耀神分享：`voice-ai-receipt:8425d9c190d5fcc4fc12bb5ff992aa7931ab11b8da51f1936024bc110cadd7e7`
  - 帖撒罗尼迦前书分享：`voice-ai-receipt:338398c55add2db355710b37c420295255d40a55a4c2e8beb40acd4754f3626f`
- **剩余阻断：原始 Provider receipt 中的 acoustic chunk 时间轴、对应原始朗读文字的准确边界及适合替换的声学切口尚未由可验证正式证据确定；即使知道用户时间戳也不能凭比例推算对应文本，更不能直接生成并拼接。**
- 下一执行工作应由语音模型项目在其 exact workspace 内读取上述 receipt_ref 与 18 份样本，出具问题类型、相邻 acoustic chunk 起止帧、实际中文片段和定点重生成方案（要保留模型音色、语速、语气连续性），并以新的一次性 request 生成替代片段。若 Provider 无法复原 chunk-to-text，应明确 BLOCKED，不能编造。
- RonnieCross 取得可信替代片段和文本覆盖证据后，再进行非破坏性拼接候选、完整 QC、NAS append-only **修订版**归档与网站受控版本交付；同一路径 R2 MP3 的替换需要独立的缓存/回滚/sha 验证方案，不可在现有 `upload_r2()` exact-object 一次性合同下强行覆盖。
- 本轮结果：`DEFECT_REFERENCE_CLIPS_PASS_18_OF_18 / TARGETED_REGENERATION_BLOCKED_PENDING_PROVIDER_CHUNK_AND_TEXT_EVIDENCE / PRODUCTION_UNCHANGED`。

## 2026-10-22 继续推进复核（未发布修订版）

- 精确打开 RonnieCross 与外部 VOICE_AI 项目，fresh-read 各自的 current authority；RonnieCross 本轮基线 Git HEAD=`e2ec8f1fd5dc0f385749f999d4d1f0c42f85ca83`。
- 已从 VOICE_AI 当前源码 `voice_ai_n3.py` 直接核查：`_invoke_backend` 调用 `inference_zero_shot` 并仅从 generator 的 `tts_speech` 提取模型输出片段；最终 receipt 的 `chunk_qc.chunks` 仅记录声学帧数/QC，不记录同一分段所对应的中文原文或文本跨度。原始 `full.wav` 和 receipt 存在，不等于具有文本对齐。
- 继续确认 `RECEIPT_ACOUSTIC_CHUNK_MAPPING_18.json` 的 18 个位置是**声学输出 chunk** 而非可保证句子边界的 text chunk；直接按其帧边界和自行猜测的句子做局部再生成，存在漏读、重复、音色断裂风险。
- 所以本阶段的剩余唯一阻断仍为 `EXACT_TEXT_TO_ACOUSTIC_CHUNK_ALIGNMENT_NOT_PROVEN`。可以复用现有18份故障片段和声学坐标做外部语音模型诊断，但没有证明的词句映射与修订段生成合同前，不覆盖既有 NAS WAV/R2 MP3。
- 最小后续行为应当是针对三个冻结的原始输入及其 receipt 做 source-owned 对齐取证，不能把 acoustic chunk 列表当作语句列表。取得可独立复核的每处文本跨度之后，独立 new request 生成替代候选，再进行全篇无漏读无重复核验与 append-only 修订版发布。此前人工反馈（3篇18点待修、一篇PASS）保留。
- 本轮执行状态：`EVIDENCE_FRESH_RECHECK_PASS / EXACT_TEXT_ALIGNMENT_BLOCKED / NO_TTS_REGENERATED / ORIGINAL_MEDIA_UNCHANGED / NO_PUBLICATION`。不声称已完成用户期待的音频修复。

## 2026-10-25｜四处中文转写/对齐能力现场复核

- 精确打开 VOICE_AI `/Volumes/DevSSD/RonnieWork/语音模型`，fresh-read `AGENTS.md`、`START_HERE.md`、`VOICE_AI_CURRENT_MASTER_PLAN.md`、`PROJECT_STATUS.md`、`PROJECT_PROGRESS.md`，只读检查本地环境。
- 两套既有 CosyVoice venv 均有 `whisper` 包和 CLI，但未找到本机 `/Users/ronnie/.cache/whisper` 权重缓存；已检查的 DevSSD 本地路径下未找到常见 Whisper `.pt` 模型。`~/.cache/huggingface` 体积约 5.4MB，不能据此宣称有可用 ASR 模型。
- 重读 VOICE_AI 现有 `EXISTING_TIMING_AND_ALIGNMENT_SURFACE.md`：其已明确说明源文本 token 到 speech token 的确切桥接缺失；不能把 acoustic chunk 证据当作原文词句时间戳。
- 因而本次没有离线可运行、可验证的中文转写/强制对齐能力；没有执行自动下载模型、外网调用、改动 VOICE_AI runtime 或单次 TTS 消费。冻结的第二篇四个问题点及原始文件身份仍有效。
- **状态：ASR_MODEL_NOT_AVAILABLE_LOCALLY / TEXT_AUDIO_ALIGNMENT_BLOCKED / NO_REGENERATION / NO_MEDIA_CHANGE。** 下一步只需在 VOICE_AI 自有 authority 下引入或提供一个可核验中文 ASR 模型，然后用四处原始 WAV 对照冻结文本生成候选边界，经文本覆盖/音频切点审核后才能调用一次性新 TTS 修复。
