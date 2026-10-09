# Article Read-Aloud Phase 1D — Media Lifecycle Pilot Closure

日期：2026-10-09
Owner：Website / 个人网页项目

## Goal

按冻结总计划完成 Phase 1D 剩余缺口：

- WAV -> NAS archival master
- MP3 -> R2 delivery readback
- manifest -> NAS metadata + Git evidence
- 冻结 NAS archive path / naming / R2 object path
- 不扩建通用媒体平台

## Fresh preflight

- exact worktree: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007`
- HEAD == origin/main before Phase 1D write
- worktree clean
- archive mount `/Volumes/home` mounted from `RonnieNAS.local/home`; PROJECT_OWNER designated `/Volumes/home/RonnieArchive` as the formal archive root
- final destination `/Volumes/home/RonnieArchive/ReadAloud/articles/2026-10-06_基督徒不应该做计划吗_post-32d30724d859c99c` did not exist before final archive write
- source final WAV SHA verified before copy

## Frozen storage layout

NAS root:
`/Volumes/home/RonnieArchive/ReadAloud/articles`

Per article:
`/Volumes/home/RonnieArchive/ReadAloud/articles/YYYY-MM-DD_<title>_<articleId>/`

Pilot:
- master: `/Volumes/home/RonnieArchive/ReadAloud/articles/2026-10-06_基督徒不应该做计划吗_post-32d30724d859c99c/master/2026-10-06_基督徒不应该做计划吗_master.wav`
- manifest: `/Volumes/home/RonnieArchive/ReadAloud/articles/2026-10-06_基督徒不应该做计划吗_post-32d30724d859c99c/metadata/audio-manifest.json`

R2:
- bucket: `ronniecross-audio`
- key: `audio/articles/<article-id>/article.mp3`
- Pilot URL: `https://audio.ronniecross.com/audio/articles/post-32d30724d859c99c/article.mp3`

## Human-readable archive naming

- directory pattern: `YYYY-MM-DD_<title>_<articleId>`
- WAV filename pattern: `YYYY-MM-DD_<title>_master.wav`
- date/title are human-facing; `articleId` remains the stable machine identity in the directory suffix and manifest

## Chronology correction

- Initial archive attempt wrote the Pilot to `/Volumes/share/网站有声阅读/post-32d30724d859c99c` using machine-oriented naming.
- PROJECT_OWNER rejected `/Volumes/share` as the archive root and later designated `/Volumes/home/RonnieArchive` as the formal long-term asset root.
- PROJECT_OWNER then approved human-readable naming.
- The final WAV and manifest were written to the approved RonnieArchive path and re-verified; R2 delivery was also re-read and matched the accepted production SHA/bytes.
- Only after those checks passed was the mistaken Pilot-only `/Volumes/share/网站有声阅读/post-32d30724d859c99c` copy removed. No unrelated share content was deleted.

## Archive result

Final archival WAV:
- SHA-256: `bf26a7cddd1900bbe4abe00ce835611de5ada45204832ba0a01403ab7167a245`
- bytes: 88047440
- duration: 917.16s
- 24kHz / mono / pcm_f32le

NAS readback:
- exact SHA match: PASS
- exact bytes: PASS

Manifest:
- schema: `ronniecross-readaloud-audio-manifest/v1`
- valid JSON: PASS
- binds article identity, render SHA, request_id, generation epoch, WAV master, R2 delivery, human acceptance, approved audio-only fidelity exception, and storage roles

R2 final readback:
- SHA-256: `d5f465053f9a217a35a917c8a616d460a315883fc2774abb311fa27c8f4f466b`
- bytes: 7337901
- exact current accepted delivery: PASS

## Storage roles frozen

- RonnieArchive = WAV archival master + archival manifest
- R2 = MP3 Website delivery
- Git = Website code, article audio pointer, governance/evidence
- WAV/MP3 do not enter Git

## Verdict

`PASS_PHASE1D_MEDIA_LIFECYCLE_PILOT / NAS_R2_MANIFEST_PATHS_FROZEN`

Next:
Phase 2 remaining work: bring total enabled Pilot articles to 2–3 and perform the planned multi-device/browser validation without expanding platform scope.
