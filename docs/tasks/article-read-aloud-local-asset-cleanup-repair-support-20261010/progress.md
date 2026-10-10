# Progress — Local Asset Cleanup + Repair Support

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| Worktree temporary-asset role | FROZEN | 只用于试听/局部修复 |
| Runtime durable-state role | FROZEN | jobs/claims/workflows/logs 长期小体积保留 |
| Runtime media-cache role | FROZEN | archive/live closure 后可清理 |
| NAS WAV authoritative role | PASS/FROZEN | `/Volumes/home/RonnieArchive/ReadAloud` |
| R2 MP3 authoritative role | PASS/FROZEN | Website delivery |
| Cleanup gate | PASS_IMPLEMENTED | controller 机械计算 required checks |
| Pilot 2 cleanup | NOT_ELIGIBLE | 当前 WAIT_HUMAN_LISTENING；未删除任何媒体 |
| Repair-support schema | PASS_V1 | identity + acoustic chunk map |
| Pilot 2 chunk map | PASS_CAPTURED | 75 chunks；frame total=14542080 |
| Exact text↔chunk alignment | NOT_AVAILABLE | current VOICE_AI public contract 不提供，不猜测 |
| Post-cleanup repair path | FROZEN | NAS restore → targeted regeneration/splice |
