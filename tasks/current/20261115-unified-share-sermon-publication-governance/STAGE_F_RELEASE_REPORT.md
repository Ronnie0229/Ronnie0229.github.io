# Stage F Bounded Repository Release / Production Cutover Report

Date: 2026-11-20
Authority: Owner's explicit Stage F authorization; Master acceptance PASS_WITH_FINDINGS.

## 1. Acceptance

- Fixed audit denominator F-01..F-11 unchanged.
- Master accepted the Independent Auditor result as PASS_WITH_FINDINGS.
- F-01..F-07 and F-09..F-11: PASS.
- F-08: PASS_WITH_FINDINGS. Non-blocking limitation retained: selected Workflow→Importer subprocess dispatch tests use mocked subprocesses; this is not represented as a real production import.
- Independent report SHA-256: `27700237647643af609c5c3102ed13a6422cc9453997cbb577ea3c0f325bebe41`.
- Stage E E-AUDIT-01 remains preserved.

## 2. Bounded repository release disposition

### Website repository

- Repository: `Ronnie0229/Ronnie0229.github.io`.
- PR #3: https://github.com/Ronnie0229/Ronnie0229.github.io/pull/3
- PR merged: yes.
- Merge commit: `79e5be408b1830d14afe555dbef852a3828e3e8a`.
- Remote `refs/heads/main` readback matched the merge commit.
- Construction commit: `5f8ac4c62e64b1deb7504719a6206c780ff89d75`.
- Local `npm run build`: PASS; 353 pages built.
- Construction branch was committed and pushed; canonical local worktree's four pre-existing dirty files were not staged, modified, reset or included.

### Sermon repository

- Repository: `Ronnie0229/sermon-workflow`.
- PR #3: https://github.com/Ronnie0229/sermon-workflow/pull/3
- PR merged: yes.
- Merge commit: `ab88dc629bd3391507f10a5e3c8b3be85018c0fa`.
- Remote `refs/heads/master` readback matched the merge commit.
- Release branch was created from `origin/master`, then only the producer v1.3 change was cherry-picked. Two pre-existing local-only canonical commits were not included.
- Construction full Python suite: 60/60 PASS; py_compile, CLI help and scoped diff-check PASS. One historical trailing-whitespace line in Stage A Remediation 01 evidence was excluded from the scoped whitespace check and left unchanged.
- Canonical Sermon local dirty files and historical content artifacts were not staged, modified, reset or included.

## 3. Production deployment identity check

- `https://ronniecross.com/`: HTTP 200.
- `https://ronniecross.com/deployment.json` returned the old deployment identity:
  - commit: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
  - builtAt: `2026-11-15T13:35:39.860Z`
- The Website repository's remote `main` is now `79e5be408b1830d14afe555dbef852a3828e3e8a`. Therefore the live deployment identity does not match the released main commit.
- The construction environment has no local Wrangler executable and no `CLOUDFLARE_API_TOKEN`, `CF_API_TOKEN`, or `CLOUDFLARE_ACCOUNT_ID` environment variable. Plugin discovery found no Cloudflare integration.
- No Cloudflare deployment trigger could be executed or independently verified in this environment.

## 4. Final disposition

- Stage F implementation: **MASTER ACCEPTED · PASS_WITH_FINDINGS**.
- Website and Sermon repository release: **MERGED**.
- Production capability cutover: **BLOCKED / NOT DEPLOYED** pending an authorized Cloudflare Pages deployment path and live deployment identity matching the Website merge commit.
- No real article import/publication; no NAS access; no TTS, email, notification, subscription action or GitHub workflow dispatch.
- Canonical local worktrees were not synced or otherwise modified; their pre-existing dirty state is preserved.

The production cutover must remain BLOCKED until `/deployment.json` reports the Website release commit (or a verified descendant containing it) and the required live checks pass.
