# Article Read-Aloud — Runtime Workspace Relocation + Pilot Artifact Move

状态：PASS_READ_ALOUD_RUNTIME_WORKSPACE_RELOCATION / PILOT_ARTIFACTS_IN_WORKTREE
日期：2026-10-08
Owner：Website / 个人网页项目

用户授权：
- 批准作业区目录整改；
- 之前生成的试听文件不得重新生成；
- 整改后移动到当前工作区；
- 不包含 commit/push/deploy/R2/NAS/第二次 TTS generation。

## Goal

把此前位于用户 Library 下的 Website read-aloud runtime state 迁移到 RonnieCross DevSSD 项目域，同时把已经生成并验证过的 Pilot WAV/MP3 原样移动到当前正式 worktree 的本地 artifacts 目录。

## New layout

Runtime state（不属于 Git worktree）：

`/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud`

Pilot listening artifacts（当前正式 worktree，本地不入 Git）：

`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007/artifacts/read-aloud/pilot/post-32d30724d859c99c`

## Migration rules

- no TTS regeneration;
- preserve jobs/claims/logs/cache identities and bytes;
- verify hashes before removing old runtime root;
- old `/Users/ronnie/Library/Application Support/RonnieCross/read-aloud` may be removed only after exact migration verification;
- update runner default PRODUCTION_ROOT to new runtime path;
- tests must continue using isolated test roots and must not require production root absence;
- historical documents remain chronology; do not rewrite old PASS evidence;
- update current authority / current task / relevant current runbook-style docs only;
- audio artifacts must remain local/untracked; use worktree-local Git exclude rather than repository-wide .gitignore if needed.

## Acceptance

1. new runtime root exists with 0700 dirs / 0600 files as applicable;
2. exact Pilot job/claim/verified cache preserved;
3. Website terminal status remains TERMINAL_PASS;
4. N3 remains generation_count=1 / retry_count=0;
5. no execution owner reappears;
6. old Library runtime root absent after verified migration;
7. WAV/64k/96k exist under worktree artifact directory with exact pre-migration SHA;
8. no TTS/provider generation call;
9. runner tests + S5 tests + full Website Python PASS;
10. git diff --check PASS;
11. no commit/push.

Final verdict:

`PASS_READ_ALOUD_RUNTIME_WORKSPACE_RELOCATION / PILOT_ARTIFACTS_IN_WORKTREE`
