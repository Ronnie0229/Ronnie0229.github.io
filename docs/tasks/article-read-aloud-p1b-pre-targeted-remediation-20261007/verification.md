# Verification — P1B-pre Targeted Architecture Remediation

正式 verdict：`PASS_TARGETED_ARCHITECTURE_REMEDIATION / READY_FOR_FRESH_REAUDIT`

## Finding A

PASS by contract. 已冻结 authorization_ref/generation_epoch -> one immutable descriptor/request_id 的 one-to-one binding；submit-side 使用 atomic exclusive-create claim file；same binding 重复 submit 返回 existing job；same authorization + any different identity fail-closed，provider POST=0；claim 不因 timeout/restart/busy 自动释放。

当前 Pilot authorization_ref=`article-read-aloud-pilot-generation-authorization-20261007-a1`，generation_epoch=`pilot-20261007-a1`，descriptor SHA=`49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`，request_id=`rc-readaloud-v1:49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`。

## Finding B

PASS by contract. 每次任何可能 provider POST 前必须读取 bounded render_ref exact bytes、SHA-256 exact match frozen value、strict UTF-8 decode，并直接使用同一刚验证内存对象构造 POST text；任何 path/SHA/decode ambiguity fail-closed，provider POST=0；不得 normalize/trim/re-read。

Pilot fresh render evidence：SHA-256=`5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`，bytes=10658，UTF-8 PASS。

## Runtime state root

PASS frozen before implementation：`/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`。Fresh check only；target remains absent。Parent `/Users/ronnie/Library/Application Support` exists, owner uid=501, mode=0700, readable/writable by current user ronnie。Future root/subdirs 0700, files 0600, no fallback。

## Architecture invariants

- no dual truth：authorization claim / Website orchestration / N6 provider truth 分层明确；PASS
- VOICE_AI provider semantics changed：NO
- hidden second-generation path：CLOSED BY CONTRACT
- Redis/Celery/database/lease platform：NOT INTRODUCED
- runtime spool creation：NOT RUN
- LaunchAgent install：NOT RUN
- implementation code：NOT WRITTEN
- POST /v1/speech：NOT RUN
- WAV/MP3：NOT GENERATED
- Pilot claim/submit：NOT RUN
- Pilot authorization：NOT CONSUMED
- commit/push：NOT RUN