# 当前任务

> 历史任务记录已按月份归档，参见：
> - [2026年7月任务归档](archive/2026-07.md)

当前无活动任务。以下仅保留最近 5 条已完成记录，新的任务开始时应在此处登记目标、范围、状态和下一步；正式状态值遵循 `../../../workspace-control/TASK_STATUS_POLICY.md`。

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

RonnieCross 三个跨项目接口已经完成 v1.1 治理闭环：`translation-candidate-package/v1.1`、`website-publication-package/v1.1`、`website-publication-result/v1.1`。三个接口的 v1.1 状态均为 `stable`；v1.0 仍保留为 `legacy-compatible`，只用于读取既有记录，不再作为新产物默认版本。

三套不同真实文章已完成全接口 v1.1 连续独立验收，验收计数为 3/3：《记念耶稣》、《为什么受洗》、《耶和华是我的牧者》。个人网页项目已接入发布契约只读验证、受控消费入口和发布结果原子写回。网站正式写入仍必须显式授权；stable 不等于自动发布。

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
