# 当前任务

## 当前任务状态（2026-08-02，统一 Tag Pipeline 建设）

状态：`CONSTRUCTION_COMMITTED_PUSHED_PENDING_INDEPENDENT_REVIEW`

已按 `tasks/current/content-workflow-tag-pipeline-construction/task.md` 完成统一标签架构设计和建设。新增单一 JSON 权威规则源、Python/浏览器双运行时，并接入分享、讲道、Custom Admin 草稿/发布和备用 Decap preSave；讲道不再默认输出 `讲道`、`教会讲道` 或讲员姓名。CLI/Admin 人工标签继续保留，统一执行书卷、确定性规则、别名、去重、generic、歧义、字符、context-only 和 2–6 fail-closed Gate。

接口边界：未修改 `website-publication-package/v1.1`，`metadata.tags` 继续兼容可选；未收紧全局 content schema，未迁移历史文章。未修改 posts、raw、processed、Knowledge Layer、RonnieAutomation、n8n 或 NAS。

验证：`python3 -m unittest discover -s scripts/tests` 为 21 tests PASS；`npm run check:tags` 为 17/17；`npm run check:admin-save` 为 0 errors；`npm run check:knowledge` 为 286 篇、0 errors、0 warnings；`npm run build` PASS；Python/Node 语法和 `git diff --check` PASS。

用户在建设完成后明确批准 commit 和 push。实现与任务资料提交为 `d47bf6e`（`feat: unify content tag pipeline`），已成功推送到 `origin/main`。未进行真实发布、部署、通知、NAS 或其它生产副作用。完整设计、文件清单、验证、剩余风险和复审攻击面见 `tasks/current/content-workflow-tag-pipeline-construction/`。

下一步：停止建设会话，仅由新的、完全独立会话执行建设后复审。不得自动进入修复、AI 标签、历史标签迁移或生产发布。

---

## 当前任务状态（2026-08-02，Grayson《信仰的殿堂：雅各》整理发布）

已从 NAS 讲道收件读取 8 页双语 PDF《Final - Hebrews 11_21 JACOB-2.pdf》，按完整讲章模式整理 Grayson 的《希伯来书 11:21、39-40｜信仰的殿堂：雅各》。已保留雅各从抓取到安息的生命脉络、信心的姿态/实践/眼光/悖论四个主点、Bryan Johnson、高山右近和阿拉斯加狗拉雪橇的全部例证、创世记 48:12-20 的交叉祝福、福音邀请、两道分组问题和结尾祷告邀请，没有摘要化。原始 PDF、英文提取稿、中文定稿与 metadata 已进入 raw，中文定稿已归档 NAS，并生成 processed 与正式 post。文章使用 6 个精准 SEO/GEO 标签，作者为 Grayson，日期为 2026-08-02。

验证结果：npm run check:knowledge 通过，286 篇、0 错误、0 警告；npm run build 通过，328 个页面构建完成。正文与发布记录提交为 f62ff19；push 与线上部署结果将在完成后补记。

---

## 当前任务状态（2026-08-01，Search Console robots.txt 屏蔽收敛）

状态：`done`

已对 Search Console 列出的 27 个“已被 robots.txt 屏蔽” URL 完成分类与修复：23 个 `focus` URL 中 22 个对应正式文章、已按既有 middleware 301，`2026-06-12-test` 为已删除测试文章并新增 410；2 个纯 `category` URL 按既有规则 301 到稳定分类页；`/search/?q={search_term_string}` 解除 robots 屏蔽以读取 `noindex,follow`，并从 JSON-LD 移除已停用的 `SearchAction`；`/api/subscribe` 继续屏蔽且不索引，属预期行为。

修改文件：`assets/robots.txt`、`functions/_middleware.js`、`src/lib/knowledge/schema.ts`、`src/layouts/BaseLayout.astro`、`scripts/test-search-console-middleware.mjs`、`scripts/check-knowledge-layer.mjs`、`scripts/audit_seo_urls.mjs`、`SEO.md`、`DEPLOY.md`、`STATUS.md`、`docs/tasks/current.md`、`docs/tasks/search-console-robots-blocked-remediation-2026-08.md`。

验证：`npm run sync` 通过；Search Console middleware 测试通过；`node --check functions/_middleware.js` 通过；`npm run check:knowledge` 为 285 篇、0 errors、0 warnings；`npm run build -- --force` 通过，327 pages built；生成 HTML 不含 `SearchAction` / `search_term_string`；robots.txt 仅保留 `/admin/` 和 `/api/` 屏蔽；23 个 `focus` slug 只有预期删除的 `2026-06-12-test` 无生成页；`git diff --check` 通过。

部署：实现提交 `7b78d7e04a0e85f25cb60fc6ad07be5ed8e036be` 已 push 到 `origin/main`；Cloudflare Pages `/deployment.json` 确认线上 commit 与该提交一致，`builtAt=2026-08-01T14:01:02.084Z`。本地外部访问审批器误拒绝了最后的批量线上 URL 抽查，但线上部署身份与已通过完整验收的本地生成物一致。

未完成：需由用户在 Search Console 启动“已被 robots.txt 屏蔽”验证，并用“测试实际网址”补齐 Googlebot 视角的线上证据。

## 当前任务状态（2026-08-01，Search Console canonical alternate 收敛修复）

状态：`done`

已完成 Search Console 列出的 36 个 canonical alternate URL 的本地核查与修复。既有 `www` 与旧 `focus` URL 的 301 已确认正常；对已于 2026-06-14 删除的《马太福音 21:19｜为什么耶稣要咒诅无花果树？》，其详情 URL 和旧 `focus` URL 现返回 HTTP 410，不再以 HTTP 200 返回首页。新增自定义 404 页保证其他未知路径返回真正的 HTTP 404。robots.txt 已解除 `/posts/?*` 屏蔽，以便 Googlebot 重新抓取并读取 301/410 信号。

修改文件：

- `functions/_middleware.js`
- `assets/robots.txt`
- `scripts/test-search-console-middleware.mjs`
- `src/pages/404.astro`
- `SEO.md`
- `STATUS.md`
- `docs/tasks/current.md`

验证结果：`npm run sync` 通过且远程已是最新；Search Console middleware 测试通过；middleware 语法检查通过；`npm run build -- --force` 通过，327 pages built；Astro 本地预览中未知路径确认返回 HTTP 404；生成 sitemap 不包含 404 或已删除文章；Search Console 列出的 34 个 `focus` slug 中 33 个均存在对应生成文章，唯一缺失项为预期返回 410 的已删除无花果树文章；`git diff --check` 通过。

部署结果：实现提交 `15b3dc957f21fb8e7bc692fc0d747fefe6e53e46` 已 push 到 `origin/main`，Cloudflare Pages 已自动部署到该提交。线上验收确认首页/RSS 200、`www/about/` 301、普通 `focus` URL 301、已删除文章详情与 `focus` URL 410、未知路径 404 + `noindex,follow` + 无 canonical，robots.txt 已允许抓取 `/posts/?*`，sitemap 仍只包含正式 URL。

未完成：需由用户在 Google Search Console 重新提交 sitemap，对正式文章请求编入索引，并在“备用网页（有适当的规范标记）”报告中启动验证。

文档闭环：长期判定规则与 Search Console 固定操作已写入 `SEO.md`，部署后 301/404/410/robots/sitemap 验收已写入 `DEPLOY.md`，问题背景、实现结论和生产证据已写入 `docs/tasks/search-console-canonical-indexing-phase2.md`。本轮只修改文档，没有改动网站源码或生产配置；复用本次功能提交已通过的 327 pages 构建和线上验收，不重复触发构建。

## 当前任务状态（2026-07-26，Nathan《没有道路时的信心》整理发布）

已从 NAS 讲道收件读取 13 页双语 PDF《Heb. 11 Abraham 26-07-26 (side-by-side).pdf》，按完整讲章模式整理 Nathan 的《希伯来书 11:8-11、17-19｜没有道路时的信心》。已保留亚伯拉罕蒙召、等候以撒、献以撒三个主要事件，南加州迁往中西部的个人例证、立约仪式说明、现实需要应用、福音邀请、教会劝勉和完整结束祷告均已译出，没有摘要化。原始 PDF、英文提取稿、中文定稿与 metadata 已进入 raw，中文定稿已归档 NAS，并生成 processed 与正式 post。文章使用 6 个精准 SEO/GEO 标签，作者为 Nathan，日期为 2026-07-26。

验证结果：npm run check:knowledge 通过，285 篇、0 错误、0 警告；npm run build 通过，326 个页面构建完成。正文与发布记录提交为 14c73d4；push 与线上部署结果将在完成后补记。

---

> 历史任务记录已按月份归档，参见：
> - [2026年7月任务归档](archive/2026-07.md)

以下仅保留最近 5 条已完成记录以及仍未完成的任务，新的任务开始时应在此处登记目标、范围、状态和下一步；正式状态值遵循 `../../../workspace-control/TASK_STATUS_POLICY.md`。

## 当前任务状态（2026-07-23，我们真能遵行基督的命令吗 分享文章整理发布）

状态：`done`

已完成《我们真能遵行基督的命令吗？》本地整理、网站导入、构建、push、Cloudflare 部署、线上正文验证和邮件发送。文章 `articleId=post-445e95aa051161aa`，slug 为 `2026-07-23-obey-christ-commands`，网站提交 `78f569bce58e9d44efb7a6be47237c6a1f7287f8` 已推送到 `origin/main`。

验证结果：`npm run sync` 通过；`website-publication-package/v1.1` 只读消费校验通过；`python3 scripts/content_workflow.py publish share ... --dry-run` 通过；`node scripts/add_article_ids.mjs --check` 为 284 篇、0 缺失；`python3 scripts/check_content_mirrors.py` 通过，568 项、0 errors；`node scripts/check-knowledge-layer.mjs` 为 284 篇、0 error、0 warning；`npm run build` 通过，325 pages。

线上与通知：Cloudflare `/deployment.json` 已更新为 `78f569bce58e9d44efb7a6be47237c6a1f7287f8`，builtAt=`2026-07-23T06:49:10.179Z`；线上页面标题、canonical、经文、描述和正文指纹均通过。GitHub Actions `Email published posts` run `29986161978` 成功，`postCount=1`、`recipientCount=3`、`successCount=3`、`failedCount=0`、`skippedSlugs=[]`。

备注：本轮还补齐了上一批《工作与安息的七个圣经真理》processed mirror 缺失的 `articleId=post-8a24724dfa8dc662`，使 mirror gate 恢复通过。

## 当前任务状态（2026-07-23，工作与安息分享文章整理发布）

已按 RonnieCross V3 统合后的 manifest-only intake 和 `website-publication-package/v1.1` 受控消费流程，完成《马太福音 11:28-30｜工作与安息的七个圣经真理》整理发布。

输入 PDF 已在 `讲道整理` 项目完成英文抽取、中文逐项整理和忠实度检查；网站新增 raw、processed、post 与本批契约消费记录。文章 `articleId=post-8a24724dfa8dc662`，内容提交 `aa6538a` 已普通 push 到 `origin/main`。

验证结果：Knowledge Layer 283 篇、0 error、0 warning；Python 单测 12 项通过；Astro 强制构建 324 pages。正式页面 HTTP 200，标题以及“在耶稣里可以找到安息”“神的子民将来还有安息”正文指纹均通过。GitHub Actions `Email published posts` run `29980947391` 成功，`postCount=1`、`recipientCount=3`、`successCount=3`、`failedCount=0`。分享文章不适用教会讲道 NAS 归档，`archive_status=not_applicable`。

---

## 当前任务状态（2026-07-22，Psalm 7 V2 生产验收发布）

已完成《诗篇 7:1-17｜大卫为何称自己为义》的真实生产发布和 V2 完整验收。网站 `main` 已推送到 `e09641e79d885db971e5f569c3f2eacf43eea5d7`，Cloudflare deployment 与该 commit 一致；线上页面 HTTP 200、最终 URL 和正文指纹均通过。首次邮件 workflow `29927545169` 为 1 篇、3 名收件人、3 次成功、0 次失败；幂等 workflow `29928285307` 为 0 篇、0 收件人并安全跳过已发布 slug。知识检查为 282 篇 0 error/0 warning，12 项单测通过，构建 323 pages。

输入 PDF 文件名指向 Thessalonica，但正文证据实际为 Psalm 7，元数据已按正文确定。验收结束后已补齐正常 intake move：源文件通过 manifest `--apply` 从 `NAS/分享收件` 移入本批 `讲道整理/原始资料/share/`，分享收件已清空，目标与 immutable snapshot SHA 一致。

---

## 当前任务状态（2026-07-21，分享收件帖撒罗尼迦 PDF 拆分发布）

已按讲道整理流程重新处理 `NAS/分享收件/What Is the Significance of Thessalonica in the Bible.pdf`。复核确认 PDF 抽取源稿实际包含三篇文章，已拆分发布为三篇 `灵命成长` 分享文章：

```text
使徒行传 17:1-9｜帖撒罗尼迦：在逼迫中持守福音的教会
帖撒罗尼迦前书 5:17｜不住地祷告是什么意思
帖撒罗尼迦前书 4:16｜在基督里死了的人必先复活是什么意思
```

本轮先提交既有网站发布契约治理改动 `4e98602 feat: add publication contract workflow`，再执行 `npm run sync`，随后只发布本次三篇分享文章。为保证干净 slug，`scripts/import_shares.py` 补充帖撒罗尼迦前后书经卷识别、三篇 metadata override，并清洗源稿中已有 Markdown 标题导致的重复 `##`。三篇均由 `content_workflow.py publish share --source-file ...` 生成 raw/processed/posts，`node scripts/add_article_ids.mjs` 已补 3 个 articleId。

验证结果：

```text
npm run sync：通过，Current branch main is up to date
三篇 dry-run：通过，标题/经文/slug 均正确
正式 publish share：三篇均 Imported shares: 1
node scripts/add_article_ids.mjs：处理 281 篇，补充 3 篇 articleId
npm run check:knowledge：281 篇，0 错误，0 警告
python3 -m unittest discover -s scripts/tests：12 tests OK
npm run build -- --force：322 page(s) built，Build Complete，无 duplicate id warning
git push origin main：通过，远端 main=c71740cd13ca769c5727bca6a1f56d9e7587960d
Cloudflare Pages：/deployment.json 已部署到 c71740cd13ca769c5727bca6a1f56d9e7587960d，builtAt=2026-07-21T14:10:51.571Z
线上验证：三篇 URL 均返回新标题、经文与正文关键词
Email published posts：GitHub Actions run 29837804445 成功，postCount=3，recipientCount=3，successCount=3，failedCount=0
```

未完成事项：无。注意本轮新增三篇文章后，网站自动邮件提醒流程已正常发送新文章提醒。

---

## 当前任务状态（2026-07-20，三接口 v1.1 治理闭环）

RonnieCross 三个跨项目接口已经完成 v1.1 治理闭环：`translation-candidate-package/v1.1`、`website-publication-package/v1.1`、`website-publication-result/v1.1`。三个接口的 v1.1 状态均为 `contract_stable`；v1.0 仍保留为 `legacy_compatible`，只用于读取既有记录，不再作为新产物默认版本。

三套不同真实文章已完成全接口 v1.1 连续独立验收，验收计数为 3/3：《记念耶稣》、《为什么受洗》、《耶和华是我的牧者》。个人网页项目已接入发布契约只读验证、受控消费入口和发布结果原子写回。网站正式写入仍必须显式授权；`contract_stable` 不等于自动发布。

C7–C9 恢复演练通过：C7 确认结果写入失败不会留下正式结果文件；C8 确认无效契约会在调用导入器前终止；C9 确认模拟部分网站写入失败后可以恢复原文件。

本次没有执行网站构建、Git 提交、Git push、Cloudflare 部署、邮件发送、NAS 写入或正式网站文章修改。

相关权威状态文件：`workspace-control/STATUS.md`、`workspace-control/INTERFACE_STABLE_ASSESSMENT.md`、`workspace-control/INTERFACE_REGISTRY.md`。

---

## 当前任务状态（2026-07-19，Akira《信仰的殿堂：挪亚》整理发布）

已从 NAS 讲道收件读取一份无扩展名 DOCX 双语讲稿，按完整讲章模式整理 Akira 的《希伯来书 11:1-7｜信仰的殿堂：挪亚》。已保留讲章三个主要论点、全部经文与交叉结构、福音邀请、两道分组分享问题、民数记 6:24-26 与哥林多后书 13:14 的祝祷，没有将正文摘要化。原始 DOCX、英文提取稿、中文定稿和 metadata 已进入 raw，中文定稿已归档 NAS，并生成 processed 与正式 post。文章使用 6 个精准 SEO/GEO 标签，作者为 Akira，日期为 2026-07-19。

验证结果：npm run check:knowledge 通过，276 篇、0 错误、0 警告；npm run build 通过，316 个页面构建完成。正文与发布记录提交为 701b698；push 与线上部署结果将在完成后补记。

---

## 当前任务状态（2026-07-18，分享文章 SEO 标签工作流修复）

已修复分享文章发布时使用通用标签的问题。分享发布现在必须提供精准主题标签，并自动补入经文书卷名、执行数量限制、去重和通用标签拦截。本次也已补正《该隐与挪得之地》的 processed 与正式文章标签，并同步更新 SEO 和发布流程文档。相关语法检查、标签测试、网站构建、知识层检查和后台保存流程检查均通过。

---

## 当前任务状态（2026-07-18，真实发布时间自动记录）

已补齐 publishedAt 的两个发布入口：Admin 新建文章直接发布或草稿首次转为公开时自动写入当前完整时间，后续编辑保留原值；import_shares.py 与 import_sermons.py 生成新正式文章时自动写入日本时区发布时间。旧文章继续在缺少 publishedAt 时回退到 date。已通过 Admin 保存流程检查、Python 语法检查和 315 页构建验证。
