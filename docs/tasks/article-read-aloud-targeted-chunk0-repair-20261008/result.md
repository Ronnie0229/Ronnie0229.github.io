# Result — Targeted Chunk-0 Repair

状态：

`PASS_TARGETED_CHUNK0_REPAIR / READY_FOR_SECOND_LISTENING`

## Human selection

- selected replacement: `chunk-000-sample-2.wav`
- reason: pronunciation correct and tone fits overall narration
- chunk-000-sample-3.wav also pronounced correctly but was rejected because the emotional intensity was slightly too strong
- chunk-057 samples 1/2/3 all failed the word `著名`; no further remediation attempted in this task

## Repair

Original chunk 0:
- frames [0, 78720)
- duration 3.28 s

Selected replacement:
- frames=109440
- duration=4.56 s
- SHA-256=`a5f81b27d0d2321a777422445fa438a559194f05a99f28693692108ed68a804b`

Repair method:
- replaced only original chunk 0
- preserved every original sample from frame 78720 onward exactly and in the same order
- no new TTS generation

Replacement delta:
- +30720 frames
- +1.28 s

Chunk 57 proof:
- original boundary: [10277760, 10671360)
- repaired boundary after shift: [10308480, 10702080)
- sample identity: exact PASS

## Outputs

Repaired WAV:
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007/artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot-repaired.wav`

- 24kHz / mono / pcm_f32le
- duration=916.40 s
- bytes=87,974,480
- SHA-256=`ac2bc2d78cb4c87303653e0d727a6cce1054e83a77ccdfe2fc01a981c283a6a1`
- full decode PASS

Repaired 64K MP3:
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007/artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot-repaired-64k.mp3`

- mono / 24kHz / 64 kbps
- duration=916.40 s
- bytes=7,331,949
- SHA-256=`67e0286b29312f24bfc6c5aa9e6cdcd3cdee1a3d15612d3c2e9518c1634e8a47`
- full decode PASS

Original WAV/MP3 were preserved.

No R2/NAS/deploy/player/commit/push.
