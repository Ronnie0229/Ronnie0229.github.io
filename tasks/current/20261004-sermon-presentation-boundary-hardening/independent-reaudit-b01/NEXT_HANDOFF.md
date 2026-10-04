# TARGETED_REAUDIT_NEXT_HANDOFF

角色：

`SERMON_PRESENTATION_BOUNDARY_HARDENING_B01_TARGETED_INDEPENDENT_REAUDITOR / AUDITOR`

前置 chronology 必须保留：

- Attempt 1 formal terminal：
  `BLOCKED_INDEPENDENT_AUDIT_WEBSITE_NODE_DEPENDENCIES_NOT_MATERIALIZED`
- Attempt 1 auditor result：
  `tasks/current/20261004-sermon-presentation-boundary-hardening/independent-audit/result.md`
- Attempt 1 auditor evidence：
  `tasks/current/20261004-sermon-presentation-boundary-hardening/independent-audit/evidence.json`
- Attempt 1 已独立确认的非阻断项目不得无故重做或改判；本轮只针对 B-01 environment blocker closure。

正式 Website construction worktree：

`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-presentation-hardening`

正式 Sermon construction worktree：

`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-presentation-hardening`

本轮严格：

`SEPARATE / INDEPENDENT / READ_ONLY / COUNTEREXAMPLE_ORIENTED / TARGETED_B01_ONLY / ZERO_REMEDIATION / ZERO_COMMIT / ZERO_PUSH / ZERO_PRODUCTION`

Owner remediation facts（全部不得直接采信，必须 fresh 独立核验）：

1. Website construction worktree 已使用其自身 `package-lock.json` 执行 `npm ci`。
2. Owner 自报 fresh：
   - Node presentation suite 14/14 PASS；
   - Curve Ahead structure validator：
     `SERMON_PRESENTATION_STRUCTURE_PASS / publication_structure_ready`；
   - forced build：
     `344 pages / Complete`。
3. Owner 自报 `node_modules` 未进入 Git changed paths，且没有 package.json/package-lock.json mutation。

本轮只需要 fresh 独立验证：

### B01-1 Dependency materialization integrity

- exact Website construction worktree 中 required Node/Astro dependencies 确实可解析；
- 不得使用 canonical node_modules symlink；
- 不得静默借用邻近 worktree dependency tree；
- `node_modules` 可以作为 ignored local dependency materialization 存在，但不得进入 Git changed paths；
- `package.json` / `package-lock.json` 不得因 audit-enablement 被修改。

### B01-2 Node presentation suite

fresh run：

`node --test scripts/tests/test_sermon_presentation_gate.mjs`

必须达到：

`14 / 14 PASS`

并确认 long-form single-paragraph negative fixture 真正命中：

- `paragraph_collapse_guard`
- `rendered_block_density`

healthy long-form fixture 必须返回：

- `SERMON_PRESENTATION_STRUCTURE_PASS`
- `completion_ceiling=publication_structure_ready`

### B01-3 Real Curve Ahead dynamic structure validation

fresh run exact presentation artifact：

`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-presentation-hardening/tasks/current/20261004-sermon-presentation-boundary-hardening/evidence/curve-ahead.presentation.md`

candidate id：

`096a21672fc3a353b94b86749ae31d3bb5e0e17de553d83bc8a4ca0d083d8b73`

必须 fresh 确认：

- source SHA：
  `cee4791eab18fea14e0df5775641771d2adeca65a53a5ac45b06a00d1d239328`
- status：
  `SERMON_PRESENTATION_STRUCTURE_PASS`
- completion ceiling：
  `publication_structure_ready`
- rendered metrics：
  - paragraphs=138
  - H2/H3=6
  - content blocks=144
- all structure checks PASS。

### B01-4 Forced build

fresh run：

`npm run build -- --force`

必须达到：

- exit 0
- `344 page(s) built`
- `Complete!`

### B01-5 Diff/scope hygiene after dependency materialization

fresh review Website construction changed paths，确认：

- no `node_modules` tracked/untracked changed-path contamination；
- no dependency symlink；
- no `package.json` mutation；
- no `package-lock.json` mutation；
- no production article mutation；
- no workspace-control mutation；
- no unrelated business assets；
- no commit/push/deploy/notification/NAS side effects。

如果上述 targeted B-01 全部 PASS，则可以正式继承 Attempt 1 中已经 independent PASS 的非阻断 findings，并给出：

`PASS_TARGETED_INDEPENDENT_REAUDIT_B01 / READY_FOR_CANONICAL_ADOPTION`

如果任何 targeted 项不成立，则给出：

`FAIL_TARGETED_INDEPENDENT_REAUDIT_B01`

或真实 BLOCKED terminal。

只允许写新的 auditor-owned 输出，不得覆盖 Attempt 1：

`tasks/current/20261004-sermon-presentation-boundary-hardening/independent-reaudit-b01/result.md`

`tasks/current/20261004-sermon-presentation-boundary-hardening/independent-reaudit-b01/evidence.json`

不得修改 implementation/tests/fixtures/docs/STATUS/task Owner result。
完成后立即停止。
