# Website Worktree Hygiene Closure

Date: 2026-11-24
Owner: Website
Role: MASTER_CONTROL

## User authorization
The Owner explicitly authorized archiving, local checkpoint commits, and retirement of the following exact worktree directories; all local branches must remain and no push is authorized.

## Exact scope
Retire after complete source snapshot archival and SHA-256 readback:
- /Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-realtime-staging-test-20261108
- /Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-listening-repairs-20261108

Preserve, do not retire:
- /Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-new-post-automation-20261011

Canonical target:
- /Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目

## Required handling
- Preserve every modified and untracked file from each retiring worktree under a unique immutable archive directory in this canonical repository.
- Do not overwrite canonical files; preserve source versions separately where hashes differ.
- Preserve each source HEAD and branch; do not delete local branches.
- Keep pre-existing canonical dirty changes untouched and outside this task's staging set.
- Stage only this task's archive and closure records; make one local checkpoint commit.
- Do not push, merge unrelated commits, reset, stash, or clean unrelated state.
- Retire only the two exact authorized worktree directories after archive SHA-256 verification and branch-existence verification.
- Reconfirm the third listed worktree remains registered and unchanged.

## Closure gates
1. Source write-set inventory frozen from Git status.
2. Every changed/untracked file copied or represented as a deletion in the archive manifest.
3. SHA-256 readback matches every copied file.
4. Canonical staged diff contains only this task's files.
5. Local commit succeeds; no push.
6. Exact worktree directories are absent from disk and Git worktree registration; branches remain.
