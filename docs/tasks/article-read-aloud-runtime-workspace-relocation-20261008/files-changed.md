# Files / Paths Changed — Runtime Workspace Relocation

Repository changes:
- `scripts/read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s4_runner.py`
- `scripts/tests/test_read_aloud_s5_activation.py`
- `docs/tasks/current.md`
- `STATUS.md`
- `PROJECT_DECISIONS.md`
- `docs/tasks/article-read-aloud-runtime-workspace-relocation-20261008/*`
- current Pilot listening checklist / handoff paths

Runtime migration:
- removed old: `/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`
- new: `/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud`

Local listening artifacts:
- `artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot.wav`
- `artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot-64k.mp3`
- `artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot-96k.mp3`

Local Git metadata:
- repository-local `.git/info/exclude` contains `artifacts/read-aloud/`

No commit/push.
