# Article Read-Aloud — Targeted Chunk-0 Repair and 64K Re-encode

状态：PASS_TARGETED_CHUNK0_REPAIR / READY_FOR_SECOND_LISTENING
日期：2026-10-08

用户裁决：
- chunk-000-sample-2.wav：发音正确，语气符合整体风格，选中；
- chunk-000-sample-3.wav：发音正确但情绪略强，不采用；
- chunk-057 samples 1/2/3：“著名”均不正确，本轮放弃继续改善；
- 允许仅替换整体 WAV 的 chunk 0，并重新编码 64K MP3 供二次试听；
- 不授权新的 TTS generation。

输入：
- original WAV:
  `artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot.wav`
- replacement chunk:
  `/Volumes/DevSSD/RonnieWork/语音模型/tasks/voice-ai-targeted-pronunciation-chunk-diagnostic-20261008/audio/chunk-000-sample-2.wav`
- original chunk 0 boundary: frames [0, 78720), 24kHz mono float
- original chunk 57 remains untouched.

输出：
- `pilot-repaired.wav`
- `pilot-repaired-64k.mp3`

要求：
- preserve original files;
- no TTS/provider calls;
- replacement input SHA must equal `a5f81b27d0d2321a777422445fa438a559194f05a99f28693692108ed68a804b`;
- original WAV SHA must equal `7e867f541eab83276233377d68d895df3461c047ee4b56a176216d91a9ca25c0`;
- after replacement, all original audio from frame 78720 onward must remain sample-identical and in the same order;
- verify original chunk 57 samples remain bit-identical in repaired WAV, shifted only by replacement length delta;
- output 24kHz mono FLOAT WAV;
- encode mono 64 kbps MP3;
- full decode both outputs;
- record duration/bytes/SHA;
- no R2/NAS/deploy/player/commit/push.

终态：
`PASS_TARGETED_CHUNK0_REPAIR / READY_FOR_SECOND_LISTENING`
