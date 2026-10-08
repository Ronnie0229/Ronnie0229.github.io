# Article Read-Aloud P1B — Pilot Operator Resolution + Local Audio Closure

状态：PASS_PILOT_OPERATOR_RESOLUTION_AND_LOCAL_AUDIO_CLOSURE / READY_FOR_MANUAL_LISTENING_AND_PLAYER_PUBLICATION_DECISION
日期：2026-10-08
Owner：Website / 个人网页项目

ROLE：
`ARTICLE_READ_ALOUD_P1B_PILOT_OPERATOR_RESOLUTION_AND_LOCAL_CLOSURE_EXECUTOR / EXECUTOR`

REPORT_TO：
`ARTICLE_READ_ALOUD_MASTER_CONTROL / MASTER_CONTROL`

LIFECYCLE：
`LONG_RUNNING_UNTIL_NEXT_REAL_AUTHORITY_BREAKPOINT`

## Current proven state

Frozen Pilot identity:

- article_id=`post-32d30724d859c99c`
- request_id=`rc-readaloud-v1:49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`
- render_sha256=`5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`
- generation_epoch=`pilot-20261007-a1`
- authorization_ref=`article-read-aloud-pilot-generation-authorization-20261007-a1`

Website:
- job status=`CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`
- execution owner exists
- owner pid=`96759`
- owner pid fresh-read=`not alive`
- claim bound/consumed
- Website artifact=null

VOICE_AI N6 fresh-read:
- phase=`TERMINAL_PASS`
- generation_consumed=true
- request_id exact match
- text_sha256 exact match
- run_id=`n3v1-a3276246f6c748e09d93ef669fdd979e`
- artifact_ref=`voice-ai-artifact:n3v1-a3276246f6c748e09d93ef669fdd979e`
- artifact_sha256=`7e867f541eab83276233377d68d895df3461c047ee4b56a176216d91a9ca25c0`
- failure_code=null

Existing generation chronology:
- generation_count=1
- retry_count=0
- no second request_id
- no second generation identity

## Why explicit operator authority is required

S4 intentionally never auto-deletes an ambiguous execution owner after provider entry.

The original Website worker was SIGTERM'd by CodexPro after entering provider speech. The stale owner is therefore retained by design.

Now that provider N6 has authoritative `TERMINAL_PASS` and the original owner PID is dead, operator resolution is eligible.

This task is NOT a new generation authorization.

## Bounded operator-resolution authority requested

If user explicitly authorizes this task, Executor may perform exactly:

### A. Pre-mutation revalidation

Immediately before mutation, fresh-read and require all of:

1. Website job request_id exact frozen value.
2. Website status still `CALL_IN_PROGRESS_OR_RESULT_UNKNOWN`.
3. execution-owner job_id/request_id exact current Pilot.
4. execution-owner PID still not alive.
5. claim exact current authorization_ref/generation_epoch/request_id.
6. N6 still terminal for exact same request_id/text SHA.
7. N6 terminal status=`PASS`.
8. N6 run_id/artifact_ref/artifact_sha256 exact currently observed terminal evidence.
9. no second generation/request_id/retry evidence.

If any mismatch: STOP / BLOCKED, no owner deletion, no replay.

### B. Exact stale-owner resolution

Allowed mutation:
- delete exactly the current production `execution-owner.json`
- only after A passes
- no claims/jobs/artifacts/state deletion
- fsync/verify owner absent
- record before/after evidence

No PID/TTL generalized takeover logic may be added.

### C. Exactly one same-id reconcile

After exact owner removal:

- invoke Website `reconcile` exactly once
- use existing frozen job_id
- use exact same request_id
- no new request_id
- no new generation_epoch
- no resubmit
- no new authorization claim
- no retry loop

Provider interaction may include exactly one same-id terminal replay through existing HTTP V1 `/v1/speech`.

This replay is permitted ONLY as operator resolution because N6 is already terminal and exactly-once authority must return persisted terminal result with generation delta=0.

Hard invariant after reconcile:
- provider generation_count remains 1
- retry_count remains 0
- no second N3 run
- no second request_id
- no new generation identity

If these invariants fail or cannot be proven: STOP / BLOCKED.

### D. Website terminal closure

Expected:
- Website job => `TERMINAL_PASS`
- provider_result request_id/run_id/artifact_ref/artifact_sha256/receipt_ref exact
- artifact retrieved exactly through opaque artifact_ref
- Website verifies artifact SHA exact `7e867f...25c0`
- verified Website artifact cache exists
- execution owner absent after terminal closure
- terminal status/result reads stable
- second reconcile/readback must not call provider again

No additional speech POST after the one operator-resolution same-id replay.

### E. Local Pilot audio closure

If D is PASS, continue in same task without another handoff:

1. inspect verified WAV metadata
2. confirm expected 24kHz / mono / float WAV contract
3. compute duration and file SHA/size
4. perform bounded technical QC (decode/readability/nonzero audio/no obvious truncation if mechanically testable)
5. create local delivery candidates:
   - mono MP3 64 kbps
   - mono MP3 96 kbps
6. record file sizes/durations/SHA
7. prepare listening comparison paths and a short manual listening checklist

No model regeneration is allowed for QC findings in this task.

If audible/content quality is unacceptable, record result and stop; do not generate again without a new explicit generation authorization.

## Stop before these operations

This task must STOP before:

- modifying article frontmatter/player
- copying/uploading to R2
- NAS publication/archive writes
- Website production publish/deploy
- commit/push
- second TTS generation
- new request_id/epoch
- model/voice/speed/text changes

Those are next authority breakpoint(s).

## Anti-overengineering

Do not build:
- generalized operator recovery framework
- stale-lock daemon
- registry/watchdog
- retry manager
- generic audio pipeline
- queue/scheduler
- new provider API

Use the existing S4/S5 path plus the smallest task-local operator action.

## Required final disposition

One of:

### PASS
`PASS_PILOT_OPERATOR_RESOLUTION_AND_LOCAL_AUDIO_CLOSURE / READY_FOR_MANUAL_LISTENING_AND_PLAYER_PUBLICATION_DECISION`

### BLOCKED
`BLOCKED_PILOT_OPERATOR_RESOLUTION / NO_REPOST / RETURN_TO_MASTER_CONTROL`

## Forbidden without explicit user authorization

Until the user explicitly authorizes this task:
- do not delete execution-owner.json
- do not call reconcile
- do not POST /v1/speech
- do not retrieve/copy artifact into Website cache
- do not encode WAV/MP3
- do not modify production runtime

Read-only verification remains allowed.
