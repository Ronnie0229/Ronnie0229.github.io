# 2026-10-18 讲道发布链四项定向缺陷整改与回归结果

状态：`LOCAL_IMPLEMENTED_AND_REGRESSION_PASS / NOT_COMMITTED / NOT_PUSHED / NO_PRODUCTION_MUTATION`

正式根：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`。跨 Owner `讲道整理` 根：`/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`。两仓库本轮开始均为 clean。范围只限现有 prepublish generator、sermon articleId import、frozen presentation record gate、Website HTML structure gate 与流程文档、对应正反向回归；无新增服务或平台。

1. **旧版 prepublish generator**：讲道整理 `scripts/generate_prepublish_md.py` 对新讲道的真实写入强制 `--presentation-manifest`，同时检查 E1 官方中文 SHA、manifest identity 与 artifact SHA；最终正文直接消费已验证的 presentation，而不是以 plain text 生成后再定向补写。讲道标签剔除通用类别和 speaker，遵守 2–6 精准标签。未达 metadata ready 的 draft 不误触正式标签数量发布门。
2. **导入 articleId 为空**：Website `scripts/import_sermons.py` 在 processed/posts 写入前调用同 `add_article_ids.mjs` 一致的 slug sha256→`post-xxxxxxxxxxxxxxxx` 算法绑定 ID；原有 ID 可重复验证，空值补齐，不匹配或重复 fail-closed，两份镜像一并生成。
3. **冻结 E1 原有列表编号误剥离**：此前已落盘的 `讲道整理/scripts/validate_sermon_presentation_artifact.py` 改动通过新增测试确认：原 frozen `1./2./3.` 保留、changed word FAIL、受控 heading 重用 PASS、错误复用 FAIL。没有修改原 frozen E1 内容。
4. **零 H2 虚假通过**：Website `scripts/validate_sermon_presentation.mjs` 新增 `three_point_outline_h2_presence`；在检测到明确的三点讲道提纲时要求三个对应的 H2，缺一个即结构 FAIL。普通 `三个重点` 列表不错误地要求三个新章节。本篇真实排版稿 PASS，原未排版 E1 candidate FAIL（缺 3 H2）。

## Regression evidence / chronology

- Sermon Owner Python unittest：26/26 PASS；真实《藉着谦卑实现合一》官方中文原稿经新生成器 presentation SHA identity probe PASS；`python3 -m py_compile` PASS。
- Website Python focused：articleId 4/4、scripture parser 9/9、package consumer 7/7、既有 prepublication structure gate 3/3 PASS。
- Website `node --test scripts/tests/test_sermon_presentation_gate.mjs`：21/21 PASS，含新增三大纲正反例。
- Website `check_content_mirrors.py`：608 checked，PASS；`npm run check:tags`：27/27 PASS；`npm run build`：348 pages，PASS。
- 两仓库 `git diff --check`：PASS，未更改任何既有文章、raw、processed/posts、NAS、Git 生产发布内容。
- 实现过程中 Website import_sermons 的局部代码编辑曾出现 `SyntaxError` 和重复尾段（FAIL）；在同一轮由原 HEAD 完整复原该文件并重放 24 行最小 articleId 改动，`py_compile` 与正反向测试后续 PASS，旧 FAIL 不覆盖。
- 此次仅在正式本地仓库写入修改并运行离线测试和本地 Astro build；**未 commit/push、未部署、未触发邮件、未重新发布本篇文章**。本地 PASS 不得误写成远端正式 rollout PASS。后续如获 exact 两仓库治理代码 commit/push 授权，先 fresh-review diff/write-set，再分仓提交、推送和 readback。


## 2026-10-19 Git closure addendum

Original local implementation conclusions and historical FAIL/PASS above are preserved as observed; their earlier `NOT_COMMITTED / NOT_PUSHED` labels describe the **2026-10-18 point-in-time**, not the final closure.

Fresh 2026-10-19 regression rerun: Website articleId Python 4/4 PASS; presentation Node 21/21 PASS; content mirrors 608 PASS; tag pipeline 27/27 PASS. Sermon Owner focused Python 3/3 and 6/6 PASS, plus py_compile PASS. The exact two-repository changesets are committed separately, with independent remote-branch readback.

The Oct 18 Patrick sermon quote-amendment audit chronology (attempt-01 BLOCKED, attempt-02 E1 PASS) and slide-source evidence are held in the Sermon Owner repository, without changing the old 85/85 frozen E1 record. The already-published article and TTS/audio workflow had separate production commits; these four defect code changes are a **subsequent regression-tested governance rollout**, not a retroactive proof that the earlier publication used the new gates.

No email, TTS or NAS/R2 actions are part of these governance closure commits. Website workflow remains subject to normal post-push live deployment verification and historical release-receipt reconciliation.
