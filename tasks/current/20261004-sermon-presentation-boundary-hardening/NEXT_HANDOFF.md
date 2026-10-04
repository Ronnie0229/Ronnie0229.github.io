# NEXT_HANDOFF

角色：

`SERMON_PRESENTATION_BOUNDARY_HARDENING_INDEPENDENT_AUDITOR / AUDITOR`

正式审计对象为两个 Owner-local construction worktree，均保持 uncommitted：

Website：
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-presentation-hardening`

Sermon：
`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-presentation-hardening`

本轮严格：

`SEPARATE / INDEPENDENT / READ_ONLY / COUNTEREXAMPLE_ORIENTED / ZERO_REMEDIATION / ZERO_COMMIT / ZERO_PUSH / ZERO_PRODUCTION`

必须 fresh 独立确认：

1. 事故根因确实被 contract 分层闭合：frozen fidelity candidate != presentation artifact。
2. Sermon producer Gate：
   - `validate_sermon_presentation_artifact.py` 对允许的 presentation-only markup 能 exact-record restore；
   - wording change / omission / reorder / forbidden construct 必须 FAIL；
   - v1.2 sermon package 缺 presentation manifest 必须 FAIL。
3. Website consumer Gate：
   - 历史无 binding package 可 read-only validate/plan；
   - 新 sermon dry-run/publish 无 binding 必须 `PRESENTATION_ARTIFACT_REQUIRED`；
   - canonical importer 不再从 plain TXT `normalize_body()` 猜正式段落。
4. Website structural Gate：
   - long-form single-paragraph fixture 必须 FAIL `paragraph_collapse_guard` + `rendered_block_density`；
   - healthy long-form fixture必须 `SERMON_PRESENTATION_STRUCTURE_PASS / publication_structure_ready`；
   - old `MECHANICAL_PRESENTATION_PASS` 只能是 legacy field，不得作为 current acceptance authority。
5. 真实 Curve Ahead integration evidence：
   - frozen candidate SHA=`096a21672fc3a353b94b86749ae31d3bb5e0e17de553d83bc8a4ca0d083d8b73`
   - 144/144 exact record identity；
   - presentation artifact 138 paragraph + 6 H2；
   - artifact SHA=`cee4791eab18fea14e0df5775641771d2adeca65a53a5ac45b06a00d1d239328`
   - non-production package candidate SHA=`1b68bdde1754fdfde4390db0c588a54ae4465845ab8c760491de34d19375f8eb`
   - Website structure validator/package validator/consumer plan 全 PASS。
6. 历史 read-only scan denominator=219；same-class collapse exact1=`2026-07-09-马太福音-7-1-6｜论断人.md`；不得自动修复。
7. 全套验证应 fresh 重跑：
   - Website Python 61/61
   - Website Node presentation 14/14
   - mirrors 600/600
   - Knowledge 300/0/0
   - tag fixtures 27/27
   - forced build 344 pages
   - Sermon Python 20/20
   - relevant py_compile
   - both `git diff --check`
8. fresh review changed paths：不得夹带 production article content、node_modules/symlink、workspace-control mutation 或无关业务资产。
9. 文档 current authority 必须一致：AGENTS / workflow / skill / audit orchestration 都不得保留 canonical sermon plain-TXT publish path 或把 legacy mechanical PASS 误写成完整 presentation acceptance。

完成后只写 auditor-owned result/evidence 到：

Website：
`tasks/current/20261004-sermon-presentation-boundary-hardening/independent-audit/result.md`

`tasks/current/20261004-sermon-presentation-boundary-hardening/independent-audit/evidence.json`

不得修改实现文件。返回正式 PASS/FAIL 后停止。
