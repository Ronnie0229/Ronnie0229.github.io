# Article Read-Aloud — Targeted Chunk-57 Fidelity-Exception Repair

状态：PASS_TARGETED_CHUNK57_PRODUCTION_REPLACEMENT / INTEGRATED_LISTENING_AND_REMOTE_VERIFY_PASS
日期：2026-10-09

PROJECT_OWNER 明确批准 fidelity 例外：
- 原文：`著名教师`
- 音频允许：`著名的教师`
- 使用 VOICE_AI 已人工确认发音正确的 `candidate-2.wav`
- 不新增 TTS generation

输入：
- base WAV: `artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot-repaired.wav`
- base WAV SHA: `ac2bc2d78cb4c87303653e0d727a6cce1054e83a77ccdfe2fc01a981c283a6a1`
- replacement:
  `/Volumes/DevSSD/RonnieWork/语音模型/tasks/voice-ai-pronunciation-candidate-isolated-20261008/candidate-2.wav`
- replacement SHA:
  `bf23d2ad2cf307948d4699437992edb64021d1af05d4faa98fd7a249729cfecc`
- current chunk 57 boundary in base WAV: [10308480, 10702080)

要求：
- preserve base WAV/MP3;
- replace exactly current chunk 57 only;
- all samples before frame 10308480 remain exact;
- all samples after frame 10702080 remain exact and ordered, shifted only by replacement length delta;
- chunk 0 repair must remain sample-identical;
- output 24kHz mono FLOAT WAV;
- re-encode mono 64 kbps MP3;
- full decode both outputs;
- no R2 replacement before integrated listening verification;
- no commit/push/deploy in this local repair step.

终态：
`PASS_TARGETED_CHUNK57_REPAIR / READY_FOR_INTEGRATED_LISTENING`
