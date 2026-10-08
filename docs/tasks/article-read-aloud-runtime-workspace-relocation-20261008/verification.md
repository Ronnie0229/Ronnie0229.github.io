# Verification — Runtime Workspace Relocation

状态：PASS

## Runtime

Old runtime root:
`/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`

New runtime root:
`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud`

Migration method:
- copied complete old runtime tree first;
- compared full file manifest by relative path, size, and SHA-256;
- only after exact match, removed old Library runtime;
- listening deliverables were separated from runtime cache into the active worktree.

Readback:
- old Library runtime exists: false
- new runtime exists: true
- runtime root/subdirs mode: 0700
- runtime files mode: 0600
- Pilot Website job: TERMINAL_PASS
- verified artifact cache preserved
- execution-owner.json: absent

## Pilot artifacts

Destination:
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007/artifacts/read-aloud/pilot/post-32d30724d859c99c`

Files preserved without regeneration:

- `pilot.wav`
  - bytes=87851600
  - SHA-256=`7e867f541eab83276233377d68d895df3461c047ee4b56a176216d91a9ca25c0`
- `pilot-64k.mp3`
  - bytes=7321581
  - SHA-256=`71af88368246bfc1bb85d6752f0f1e89ac982602964ca57ffa03e9cfa22db585`
- `pilot-96k.mp3`
  - bytes=10982349
  - SHA-256=`824f607267234f4dc6e3cbdc8ed04ca9d083f6f8d7720093133f661a37922fe4`

The artifact directory is excluded locally through repository-local `.git/info/exclude`; no repository `.gitignore` change was made.

## Code

`scripts/read_aloud_s4_runner.py` default `PRODUCTION_ROOT` now points to:

`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud`

Tests were updated so production-root existence is no longer treated as an error; instead they assert the production runtime is outside the active Git worktree.

## Regression

- py_compile: PASS
- S4 runner tests: 54/54 PASS
- S5 activation tests: 5/5 PASS
- full Website Python suite: 120/120 PASS
- git diff --check: PASS
- migration readback: PASS

## Side effects not performed

- no TTS generation
- no reconcile/worker-once/provider speech
- no new request_id/epoch
- no R2/NAS/deploy
- no commit/push
