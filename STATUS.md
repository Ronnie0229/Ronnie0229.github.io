# 个人网页项目状态

## 2026-09-16 — ProjectStandard cross-project mutation / repository binding A5 adoption

- 当前 verdict：`PASS_MINIMAL_GOVERNANCE_IMPLEMENTATION / SOURCE_ADOPTION_IMPLEMENTED / REPOSITORY_CLOSURE_OPEN / GIT_DECISION_REQUIRED`。
- Website 已在现有 root governance entry `AGENTS.md` 极薄采用 cross-project mutation exact binding：lawful `READ_ONLY` 保持允许；mutation 前必须由 source-local current authority fresh/exact 绑定 `target root + task/role + bounded write-set + operation class`；`COMMIT` / `PUSH` 额外绑定 exact Website repository identity 且继续分 Gate。
- publication/deploy/email/content/runtime authority 与 `PUBLICATION_FAST_LANE + CONSTRUCTION_ISOLATION` 均未改变；未新增 validator/service/platform/registry/watcher/daemon；未修改 `src/`、`functions/`、`assets/`、`scripts/`、raw/processed/posts。
- 本轮为 governance-only 文档 adoption，不运行 build/publish/deploy/notification。当前 Website exact repo=`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`，branch=`main`；stage 开始前 clean。根据 `PROJECTSTANDARD_GIT_DISPOSITION_ADOPTION.md`，该 bounded governance milestone 的 commit authority 尚未成立，因此 repository closure 保持 `OPEN / GIT_DECISION_REQUIRED`；未 commit、未 push。

## 2026-09-13 — Sermon presentation list / small-group heading incident remediation COMPLETE

- 正式 verdict：`COMPLETE / TARGETED_REMEDIATION_PASS / 12_OF_12_PRESENTATION_REGRESSION_PASS / COMMITTED_PUSHED_DEPLOYED / NO_FURTHER_ACTION_REQUIRED`。
- 《为爱心祷告》发布后暴露的两类 Website presentation 缺口已做最小 source-owner remediation：非 CommonMark 视觉编号（`1）/1、/1．` 等）不再被当作稳定列表；公开小组分享 H2/H3 仍含 `WAKACHIAI` 时 fail-closed。
- `scripts/validate_sermon_presentation.mjs` 新增 `pseudo_ordered_list_requires_markdown_list` 与 `small_group_heading_public_label`；标准有序列表只接受可稳定渲染的 `1.` / `1)`。新增 5 个事故 fixtures（4 个负向 + 1 个真实 Astro renderer 正向），presentation regression fresh `12/12 PASS`，既有 7 项全部保持 PASS；正向 fixture 机械确认三个问题为独立 `<li>`、H2 精确为 `小组分享` 且无 `WAKACHIAI`。
- 今天修正后的《为爱心祷告》在新 Gate 下 `MECHANICAL_PRESENTATION_PASS`；Knowledge Layer 296 posts / 0 errors / 0 warnings；fresh forced build 338 pages PASS。
- 整改 commit=`5ad5bcd37d70f8f4ad927023a8ff4f611d411b38` 已 push；fresh readback `HEAD=origin/main`。Cloudflare Pages check 已 `completed/success`，生产 `/deployment.json` 绑定同一 commit，builtAt=`2026-09-13T03:00:34.652Z`。
- 规则已同步进入 `docs/sermon-content-rendering-binding.md` 与 `docs/content-publishing-error-prevention.md`。本整改仅属于 Website presentation/display；未重开 sermon fidelity、Project Bible、翻译正式稿或通知语义，也未修改当前线上文章内容。后续新反例必须新建 bounded task，不自动重开本任务。

## 2026-09-13 — Publication Fast Lane dirty-state restoration PASS

- Sermon Parent handoff 指定的 Website canonical dirty-state blocker 已关闭：既有 P4→P5 shadow/preflight/parser lineage 经 formal evidence 归属确认后，以独立本地 commit `6fc35cc` 封存；没有 stash/reset/覆盖/删除或夹带未归属 concurrent change。
- parser remediation fresh regression `55/55 PASS`；随后 `npm run sync` exit=0，`main` 对 `origin/main` 检查为 up to date，canonical 已恢复可 sync 的稳定 fast-lane 状态。
- 本 bounded redecision 未重做 sermon translation/fidelity，未消费新讲道 publication package，未执行 article import/build/deploy/notification。P5/parser commit 的 push 不在本轮单独扩大执行；返回 Sermon Parent 继续 current production route。

## 2026-09-11 — P5 Website scripture parser targeted remediation + independent read-only audit PASS

- Parent-classified blocker `WEBSITE_OWNER_DETERMINISTIC_SCRIPTURE_RANGE_PARSER_COMPATIBILITY_GAP` 已做最小 source-owner remediation：`scripts/import_sermons.py::title_parts()` 仅扩展 spoken range separator 支持 `至`，并仅在紧跟 `至` 时允许首个 `节` 省略；未重写 parser、未 special-case article/package/operation identity。
- test chronology 保留：首轮仅加 `到|至` 后 targeted tests FAIL（1 failure + 1 error）；随后收窄修正后 targeted 5/5 PASS，全部 Python scripts tests 55/55 PASS。
- exact `罗马书12章1至2节` -> `罗马书 12:1-2`；既有 `到`、colon、跨章 range 不回归；exact P5 body 不再产生 `body=罗马书 12` false conflict；genuine conflict 仍 `SystemExit / Scripture conflict detected` fail-closed。
- separate read-only counterexample-oriented verification process PASS；同一 CodexPro session，非独立 LLM context。文章正文、metadata、package、fidelity、Scripture Gate 均未修改/重开；未执行第二次 Website dry-run，未创建新 operation id；build/publish/push/deploy=not_run，notification=suppressed_not_run，production mutation=false，side_effects=[]，commit/push=0/0。返回 P5 Parent redecision。

## 2026-09-11 — P5 successor preflight PASS; exactly one fixed dry-run consumed and fail-closed on Scripture conflict

- Hermes path-only successor SHA=`07c11adfead2b98c3143769434f6c1d657c46e7ed71e2725cc727b8001ddaa5b` 已 fresh-read，并按 current path-boundary 要求 byte-exact复制为 Website task-local carrier；carrier SHA同值，byte equality=true。
- 完整 WEBSITE_CONSUMER_PREFLIGHT=`PASS`：prepublish/official_chinese/English source 均在 RonnieCross content-root 内且 SHA current；staged corrected child SHA exact；metadata.website_source、tags current policy、production_publish_authorized=false、notification_policy=suppress、scope均通过。
- fresh operation id=`p5-same-article-shadow-successor-20260911-v1` 被 exactly one fixed non-production dry-run实际消费；dry-run terminal=`FAIL_CLOSED_WEBSITE_DRY_RUN`，error_stage=`website_dry_run`，consumer stderr=`Scripture conflict detected; please confirm metadata manually: folder=罗马书 12:1-2; file=罗马书 12:1-2; body=罗马书 12`。未重试、未整改。
- website-publication-result/v1.1未创建；dry-run evidence SHA=`3c774594db0b35f4f54a1e371b7b52cb169a49f515b0c87dbbe5d85cdea498ea`；zero-side-effect evidence SHA=`e731e3cadecad217eb3411e76150b5c5cd736269ea0be5d406b003ee22e2702e`。build/publish/push/deploy均not_run，notification suppressed_not_run，production mutation=false，side_effects=[]，commit/push=0/0。正式返回 P5 Parent redecision，不宣告 global closure。

## 2026-09-11 — P5 Website targeted preflight remediation completed; requalification fail-closed on new reference boundary

- Parent-authorized exact blocker A/B remediation completed: Hermes package was copied byte-for-byte into Website task-local carrier; source/carrier SHA both=`8a4e5472daac057eb74e585fc0134c3997f0699af8206a8c8cbc843c4de5516a`, byte equality=true, no package semantic rebuild/re-serialization. Website task-local staged Chinese was replaced by corrected-child exact bytes, SHA=`e91d29548d1d9320927e4a86636eef933dbfac46802cc1ea37deee3916163ca9`; `metadata.website_source` locator unchanged.
- Full consumer preflight requalification then returned FAIL_CLOSED: current Website validator requires package references inside RonnieCross content-root, while unchanged package `prepublish.path` and `official_chinese.path` still point to Hermes. Because package semantic rewrite/rebuild is not authorized, fixed dry-run was not entered.
- actual Website operation id=`NOT_CREATED`, consumed=false; website-publication-result/v1.1 and dry-run evidence were not created. real publish/build/push/deploy=`not_run`, notification=`suppressed_not_run`, production mutation=false, production side_effects=[], commit/push=0/0.
- Formal return to `P5_HQ_SAME_ARTICLE_COMPATIBILITY_JOINT_PRODUCT_MASTER_CONTROL / ACTIVE_MASTER` for redecision on the newly exposed reference-boundary blocker; Website Owner does not declare P5 global closure.

## 2026-09-11 — P5 same-article Website non-production shadow preflight fail-closed

- P5 exact package SHA=`8a4e5472daac057eb74e585fc0134c3997f0699af8206a8c8cbc843c4de5516a` 与 corrected child SHA=`e91d29548d1d9320927e4a86636eef933dbfac46802cc1ea37deee3916163ca9` 已 fresh-read；interface/version、production_publish_authorized=false、notification_policy=suppress、scope 与 tags 均符合 Parent route，current tag policy PASS。
- WEBSITE_CONSUMER_PREFLIGHT=`FAIL_CLOSED`：current fixed dry-run surface要求 contract 位于 RonnieCross 内，exact package 位于 Hermes；机械 probe exit=2 / `contract_path`，operation directory 未创建、operation id 未消费。另 current website_source 的 staged Chinese 仍为 P4 SHA=`b4ce3d9d93f89dd341f6ab75ff2a4b13df1d74875b4495a0edba06998250316a`，未绑定 corrected child SHA。
- 按 frozen rule 未修包、未 staging mutation、未进入 fixed dry-run，因此 website-publication-result/v1.1 与 dry-run evidence 均未创建。real publish/build/push/deploy/notification/production mutation/commit/Git push 全部未运行；zero production side effects PASS。
- 正式返回 `P5_HQ_SAME_ARTICLE_COMPATIBILITY_JOINT_PRODUCT_MASTER_CONTROL / ACTIVE_MASTER` 做 redecision；Website Owner 不宣告 P5 global closure。

## 2026-09-08 — Publication Fast Lane / Construction Isolation Owner Adoption

- Website Owner 正式采用 `PUBLICATION_FAST_LANE + CONSTRUCTION_ISOLATION`：canonical business worktree 保持用于成熟文章发布；长期/并行建设承担 branch/worktree 隔离与后续 baseline requalification 成本。
- 本轮同时把 2026-09-06 已独立通过的 B-min/C-min presentation closure exact files 迁入当前 `main` worktree，保持 B-min SHA=`be9f36e48ae1c60c730a78b264acbef0247cdf6a8b274f6d6d81448798e93f6e`、C-min SHA=`f8d0132d7e97a333cfb46f5691ad054e822b34a70a6c8962d639a35a16272d6f` 不变。
- 本轮不改变 renderer/CSS/layout/已发布正文，不执行 deploy/notification；legacy 20260902 worktree 的物理 retirement 由 RonnieCross topology normalization 总控在零未分类内容后单独执行。

## 2026-09-06 — Sermon Publication Presentation Website Owner Closure

- RonnieCross `Sermon Publication Presentation Minimal Owner Closure` 已完成正式闭环；首轮独立审计曾因 B-min `F-01` false-positive 裁决 `FAIL`，随后只做该 finding 的最小定向修复，并经新的 targeted independent re-audit `PASS`。历史 FAIL chronology 保留。
- 当前正式 Website Owner closure identities 固定为：
  - B-min Gate：`scripts/validate_sermon_presentation.mjs`，SHA-256=`be9f36e48ae1c60c730a78b264acbef0247cdf6a8b274f6d6d81448798e93f6e`；
  - C-min Rendering Binding：`docs/sermon-content-rendering-binding.md`，SHA-256=`f8d0132d7e97a333cfb46f5691ad054e822b34a70a6c8962d639a35a16272d6f`。
- 当前状态：`OWNER_CLOSURE_COMPLETE / NO_FURTHER_WEBSITE_REMEDIATION_REQUIRED_NOW`。
- 为保持已接受 closure identity，本阶段不再修改上述 B-min/C-min 实体，即使文件内部保留形成 candidate 时的历史状态文字，也不得仅为更新状态标签而改变已验收 SHA。
- 当前不修改 Website renderer/CSS/layout，不新增 sermon-only TOC，不重做/扩大 B-min checks，不建立通用 Markdown/presentation framework，不扫描历史 sermon，不修改/部署《属于基督》。

## 2026-09-06 — 《属于基督》发布稿排版与中文文风整改

- 根因：首次发布漏掉 publication-presentation gate；fidelity PASS 不能替代发布排版/中文编辑验收。
- independently verified semantic baseline SHA=`c738a9705aaf6ae2da7f76b8b9344e3cc21ebd2827ae71e397d2a8d6805eef06`。
- presentation-style revision SHA=`9d92ef8ff7e8fdc0ad66372378ac1b33c939774938cec4f6e1ca83024059ffad`；95/95 semantic-loss diff gate PASS；controlled scripture text unchanged。
- Website revision commit=`6eae292deaf61956b6f43096cbd66bb6c1b60eb3` 已 push/deployed；deployment builtAt=`2026-09-06T02:31:51.856Z`。
- live presentation verify：三大点/小组分享/荣耀颂均为 H2；10 个 scripture blockquote；115 paragraphs；max paragraph=134 chars；stage-direction markers=0。
- 更新既有文章，不属于新增 post；Email workflow run `34006652657` success，未重复发送订阅邮件。
- 本地正式中文稿、Website raw/processed/post、NAS archived Chinese 已同步到 SHA `9d92ef8f...`。

## 2026-09-06 — 《属于基督》正式发布完成

- 当前状态：COMPLETE_COMMITTED_PUSHED_DEPLOYED_NOTIFIED / LIVE_VERIFY_PASS。
- production commit=`ca3d87bd6ed275151441f10e2ed8933daa7dce9f`；`main...origin/main` clean。
- Cloudflare `deployment.json` 已确认 exact commit=`ca3d87bd6ed275151441f10e2ed8933daa7dce9f`，builtAt=`2026-09-06T01:53:45.682Z`；文章 live HTTP 200。
- GitHub Actions `Email published posts` run `34005008294` success：postCount=1、recipientCount=2、successCount=2、failedCount=0、skippedSlugs=[]。
- Website publication result v1.1 已更新为 status=`deployed`、push_status=`pushed`、deployment_status=`deployed`、notification_status=`sent`。
- 讲道 NAS 三文件归档由内容侧 RonnieCross registry/task 记录为 `archived`。

## 2026-09-05 — 《耶稣为何自称人子》正式发布完成

- 当前状态：COMPLETE_COMMITTED_PUSHED_DEPLOYED_NOTIFIED / LIVE_VERIFY_PASS。
- website-publication-package/v1.2 contract plan/dry-run PASS；本篇 raw、processed、post 已生成，slug=2026-09-05-why-jesus-called-himself-son-of-man，articleId=post-3ae5349dbe24efc3。
- 发现全站 17 个既有 body drift 后，独立机械追溯确认 17/17 的正式 post 最后正文修改均来自 H8 commit 15a99304d878608213c88dfd00783dba169c0a49，而 processed mirror 未同步；本轮只将 H8 已批准 post 正文机械同步到对应 processed mirror，不改正式 post。修复后 mirror 588/588 PASS。
- 三个已授权 commits 已 normal non-force fast-forward push 到 origin/main；fresh readback 确认 remote main exact SHA=f553ec4fb75478622f971a07ac9e390e08bad20b，本地与 origin/main=0/0。
- Cloudflare /deployment.json 已确认 commit=f553ec4fb75478622f971a07ac9e390e08bad20b，builtAt=2026-09-05T06:39:16.146Z。线上文章 HTTP 200；标题、canonical、正文指纹“枯骨复活与五旬节”及“人子来，为要寻找拯救失丧的人”均 PASS。
- GitHub Actions Email published posts run 33950361513 成功：postCount=1、recipientCount=2、successCount=2、failedCount=0、skippedSlugs=[]。
- 最终本地验证：articleId 294/294 PASS；mirror 588/588 PASS；Knowledge 294 篇 0 errors / 0 warnings；Astro build 336 pages PASS；git diff --check PASS。

最后更新：2026-09-05 +09:00

## 当前状态

- 2026-08-30 `website-publication-package/v1.2` 已进入 lifecycle/default-write adoption write-set successor candidate：当前 candidate truth=`contract_stable / default write`，validator/controlled consumer 按现有 version-bound 实现消费 v1.1/v1.2；v1.1 保留为 `contract_stable / non_default / compatibility-preserved`，并继续拒绝 max-audit literal。网站未复制或解释讲道 max-audit 业务语义；publish 仍需既有显式授权。该状态待独立 lifecycle adoption audit。
- 项目：使用 Astro 构建的中文文章网站，部署目标为 Cloudflare Pages。
- 当前分支：`main`。
- 当前任务入口：`docs/tasks/current.md`。
- 当前有效业务/生产事实：《希伯来书 11:23-29｜摩西的信心之旅》已完成网站 commit/push、Cloudflare 部署与自动邮件通知；正式 `website-publication-result/v1.1` 记录 commit=`a72f499f67be090dc407f0185b8f9946bee80ea4`、`push_status=pushed`、`deployment_status=deployed`、`notification_status=sent`。该文章不再存在待执行的 commit/push/deploy/notify 动作。
- current-over-history precedence：正常 cold-start 以本文件顶部 current truth、`docs/tasks/current.md` 顶部 current-effective 区及 fresh formal task/evidence 为准；下方历史 chronology 中旧 `ACTIVE/PENDING` 只代表原执行 epoch，不得据此恢复已完成的生产动作。若没有新的正式网站业务任务，不为了填充 current 状态伪造 ACTIVE production task。

## 统一 Tag Pipeline 建设（2026-08-02）

- 已建立 `assets/admin/tag-rules.json` 单一权威规则源、Python/浏览器双运行时，并接入分享、讲道、Custom Admin 和备用 Decap Admin 的新写入边界。
- 讲道导入不再默认生成 `讲道`、`教会讲道` 或讲员姓名；规则不足时 fail closed 并要求人工 `--tags`。
- `website-publication-package/v1.1` 未升级，兼容可选 `metadata.tags` 保持不变；历史 content schema 和历史文章未修改。
- 验证：Python 21 tests PASS；浏览器 fixture 17/17；Admin Save Flow 0 errors；Knowledge Layer 286 篇、0 errors、0 warnings；整站 Astro build PASS；`git diff --check` PASS。
- 未执行真实文章发布、GitHub Admin 保存、部署、通知或 NAS。用户后续明确批准 Git 操作后，实现提交 `d47bf6e` 已推送到 `origin/main`。
- 权威任务包：`tasks/current/content-workflow-tag-pipeline-construction/`。建设阶段曾进入 `CONSTRUCTION_COMPLETE_PENDING_INDEPENDENT_REVIEW`；后续独立复审与 P1 修复状态见下节。

### 独立复审 P1 定向修复

- 独立安全与合同复审正式裁决 `FAIL`：人工标签 alias map 遗漏 `books[*].aliases`，Python/Browser 会一致地把 `1 John` 等别名原样写入。
- 已最小修复两端 alias map；`1 John`、`John`、`约一`、`Genesis` 均进入标准书卷规范化，且与 scripture 自动书卷二次去重。
- 原失败探针现返回 `['信心', '约翰一书', '恩典']`。
- 回归：Python 21 tests、Browser 21/21、Admin 0 errors、Knowledge 286 篇 0/0、Astro build 全部 PASS。
- 修复未修改规则 JSON、历史文章、Knowledge Layer 或 publication contract；未 commit、未 push、未部署、未发布、未操作 NAS。
- 当前状态：`TARGETED_REMEDIATION_COMPLETE_PENDING_NEW_INDEPENDENT_REVIEW`。

### P1 修复后复审与第二次定向修复

- 修复后独立复审再次裁决 `FAIL`：alias map 算法已正确，但权威字典缺少 `First John`。
- 已在单一 JSON 权威源中为所有编号书卷补齐 First/Second/Third 英文序数全称，不在 Python/Browser 写特例。
- 新增 6 个跨运行时 fixture；已确认 First/Second/Third John 和 First Peter 规范化，且中英 scripture/人工别名交叉去重后保留 scripture evidence。
- 定向回归：Python 21 tests PASS，Browser fixtures 27/27 PASS。完整验证记录见任务 `verification.md`。
- 第二次修复后独立复审报告正式裁决 `PASS`，P0/P1/P2 均无，独立确认 17/17 编号书卷矩阵与全部回归通过。
- 剩余风险仅为未来可将 17 卷矩阵全部固化为持久 fixture；不影响本次 `PASS`。
- 关闭前远程同步检查为 `0 0`；闭环主提交 `2fab73d fix: close tag pipeline alias remediation` 已成功推送到 `origin/main`。
- 当前状态：`COMPLETE_INDEPENDENT_REVIEW_PASS_COMMITTED_PUSHED`。

## Search Console canonical alternate 修复（2026-08-01）

- `www` 域名与旧 `/posts/?category=...&focus=...` 的既有 301 逻辑保持不变。
- 已删除的《马太福音 21:19｜为什么耶稣要咒诅无花果树？》详情 URL 及其旧 `focus` URL 改为 HTTP 410，并输出 `X-Robots-Tag: noindex, follow`。
- 新增自定义 `404.astro`；Astro 本地预览已确认未知路径返回 HTTP 404，带 `noindex,follow`且无 canonical。
- robots.txt 已取消 `/posts/?*` 抓取屏蔽，使 Googlebot 可读取旧参数 URL 的 301/410 响应；`/admin/`、`/api/`和 `/search/?*` 仍保持屏蔽。
- 验证：`node scripts/test-search-console-middleware.mjs` 通过；`node --check functions/_middleware.js` 通过；`npm run build -- --force` 通过，327 pages built；Search Console 列出的 34 个 `focus` slug 中 33 个均存在对应生成文章，唯一缺失项为预期返回 410 的已删除无花果树文章；`git diff --check` 通过。
- 实现提交 `15b3dc957f21fb8e7bc692fc0d747fefe6e53e46` 已 push 到 `origin/main` 并由 Cloudflare Pages 自动部署；`/deployment.json` 已确认线上版本与该提交一致。
- 线上验收通过：首页与 RSS 返回 200；`www/about/` 返回 301 到正式域名；普通 `focus` URL 返回 301 到正式文章；已删除文章详情与 `focus` URL 返回 410；未知路径返回 404、`noindex,follow` 且无 canonical；robots.txt 和 sitemap 符合新规则。
- 本轮未直接操作 Google Search Console；后续按任务交接中的步骤重新提交 sitemap 并验证修复。
- 长期规则和 Search Console 操作清单已收敛到 `SEO.md`；部署后 HTTP 验收要求已同步到 `DEPLOY.md`；阶段背景与生产证据保留在 `docs/tasks/search-console-canonical-indexing-phase2.md`。

## Search Console robots.txt 屏蔽修复（2026-08-01）

- 对 Search Console 列出的 27 个 URL 完成分类：23 个 `focus` URL、2 个纯 `category` URL、1 个搜索模板 URL 和 1 个订阅 API URL。
- 23 个 `focus` 中 22 个存在正式文章并按既有规则 301；`2026-06-12-test` 是已于 2026-06-13 删除的测试文章，现登记为 410。
- 两个纯 `category` URL 已在上一轮解除 robots 屏蔽，分别 301 到稳定分类页。
- 移除 robots.txt 中 `/search/?*` 屏蔽，使 Googlebot 可读取页面既有 `noindex,follow`；同时从 `WebSite` JSON-LD 移除已停用的 `SearchAction` / `{search_term_string}`。
- `/api/subscribe` 继续受 `/api/` robots 规则保护，这是预期行为；该接口已输出 `X-Robots-Tag: noindex, nofollow`，不属于可索引网页。
- 本地验证：middleware 测试、语法检查、Knowledge Layer 285 篇 0 错误/0 警告、强制构建 327 pages 和 `git diff --check` 全部通过。
- 实现提交 `7b78d7e04a0e85f25cb60fc6ad07be5ed8e036be` 已 push 到 `origin/main` 并由 Cloudflare Pages 自动部署；`/deployment.json` 确认 `builtAt=2026-08-01T14:01:02.084Z` 且线上 commit 与实现提交一致。
- 直接逐 URL 线上抽查因本地外部访问审批器误拒绝而未完成；已部署的精确提交与本地完整构建/生成物验收一致，后续由 Search Console 实际网址测试和验证流程补齐 Googlebot 视角证据。

## 当前事实源

接手项目时按以下顺序读取：

1. `README.md`
2. `AGENTS.md`
3. `STATUS.md`
4. `docs/tasks/current.md`
5. 与具体任务相关的 workflow、decision 或专项任务文档

`docs/tasks/archive/` 保存历史任务；`.ai-bridge/` 不得保存唯一长期事实。

## 当前发布与接口边界

- 正式内容位于 `src/content/posts/`，网站 raw 与 processed 镜像分别位于 `data/raw/` 和 `data/processed/`。
- 网站拥有 current default `website-publication-package/v1.2` 的消费、v1.1 compatibility 消费，以及 `website-publication-result/v1.1` 的生成职责。
- v1.2 当前 adoption candidate=`contract_stable / default write`；v1.1=`contract_stable / non_default / compatibility-preserved`。这些接口状态不等于自动发布，也不等于 `production_acceptance_passed`。
- 网站写入、构建、push、Cloudflare 部署和邮件发送必须按任务授权和发布流程执行。
- 已发布讲道正文修正不得改变 slug、articleId、日期、作者、分类、经文等锁定身份字段，除非任务明确授权。

## 最近已验证基线

最近一次完整生产验收为 2026-07-22 的 Psalm 7 分享文章：

- `npm run check:knowledge`：282 篇，0 错误，0 警告；
- Python 发布契约测试：12 tests OK；
- `npm run build -- --force`：323 pages built；
- 网站 `main` 已推送到 `e09641e79d885db971e5f569c3f2eacf43eea5d7`；
- Cloudflare deployment commit 与网站 HEAD 一致；
- 首次邮件 workflow `29927545169` 为 1 篇、3 名收件人、3 次成功、0 次失败；
- 幂等 workflow `29928285307` 为 0 篇、0 收件人，并安全 skip 已发布 slug。

该批次已通过 V2 production acceptance，正式证据位于 `workspace-control/acceptance-runs/20260722-v2-production-acceptance-thessalonica-01/`。

## 当前阻断与待办

- 当前无阻断项。
- 最近一次发布为《我们真能遵行基督的命令吗？》：网站提交 `78f569bce58e9d44efb7a6be47237c6a1f7287f8` 已 push，Cloudflare `/deployment.json` 已部署到该提交，线上正文指纹通过；GitHub Actions run `29986161978` 邮件发送成功，1 篇文章、3 名收件人、3 次成功、0 失败。
- 后续真实修改前仍应先同步 `origin/main`，确认 Admin 或其他入口没有产生远端新内容。

## 历史说明

2026-07-13 以前及其后累积在旧 `STATUS.md` 中的阶段过程、邮件 MVP、访问量修复、source 路径审计和迁移记录，应完整归档为历史状态快照，不再保留在当前 STATUS 中。正式归档后，当前状态只由本文件替换后的 `STATUS.md` 表达。

## RonnieAutomation治理接入边界（2026-07-28）

RonnieAutomation已登记为外部编排参与者，不是网站Owner。网站正式文章、raw/processed/posts、Git、build、Cloudflare和邮件事实仍由本项目拥有。

两个automation-business-operation/v1接口当前仅为`draft`，受控业务代理和网站自动化调用均未实现。未来写入仍必须通过网站正式发布契约、显式授权和本项目Gate；RonnieAutomation不得直接写网站仓库或自我声明发布成功。
