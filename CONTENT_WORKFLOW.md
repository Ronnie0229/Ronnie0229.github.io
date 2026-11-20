# CONTENT_WORKFLOW.md

本文件是 RonnieCross 内容整理与发布的项目级入口。详细脚本步骤见 `docs/统一内容整理与发布流程.md`，风格规则见 `docs/content-style.md`，Codex 专项流程见 `skills/article-workflow.md`。


## 统一分享与讲道发布治理（Stage D）

新内容统一遵循 `content-presentation/v1` 与 `website-publication-package/v1.3` 治理合同。统一的是 source/fidelity（发生翻译时）/Project Bible/presentation identity/package/Website rendered-structure/import safety gates，不统一两类内容的正文结构。

- Share：保留原文章标题、段落、列表、引文、对话、祷告、问题和结尾（原文存在时）；不得强加讲道三点大纲或 Full Sermon Mode。默认作者 Ronnie 仅作 fallback，明确来源/Owner 作者优先；分类「灵命成长」；`archive_status=not_applicable`，终态 `SHARE_ARCHIVE_NOT_APPLICABLE`，严禁访问 NAS archive path。
- Sermon：保留 Full Sermon Mode 与现有讲道专属结构 Gate。默认讲员 Patrick 仅作 fallback，明确来源/Owner speaker 优先；分类「教会讲道」；继续执行受保护 NAS append-only archive。
- 两类内容的收件入口分别为 `NAS/分享收件` 与 `NAS/讲道收件`。除入口、默认人员和归档外，不另设较弱的 Share 发布质量路径。
- 任何源语言→中文翻译均使用讲道整理 Owner 的现有通用 fidelity state machine；Website 不重新裁决 fidelity 或 Project Bible。正文经文 TTS 显示规范化必须在 candidate SHA freeze 前完成；随后冻结 candidate SHA 与 structured/paired records，再进行独立 fidelity 审核/修复 release gate，之后才进入 Project Bible/CUVMPS gate。不连续/歧义/未受控英文书卷引用 fail-closed，机器 metadata 可保留紧凑格式。
- 正式链路顺序：source extraction → TTS scripture normalization → frozen Chinese candidate SHA + structured/paired records →（发生翻译时）通用 fidelity loop 与独立审核/修复 release gate → Project Bible/CUVMPS gate → body-only presentation artifact + `content-presentation/v1` identity → v1.3 package → Website package consumer / profile-aware rendered structure gate → controlled import。
- v1.0/v1.1/v1.2 与历史 `sermon-presentation/v1` 保持原有兼容；不迁移/重写历史文章、package、URL、articleId 或历史审核 chronology。
- Stage D 仅完成文档与入口对齐。Stage F 前，现行生产入口/default 不变；v1.3 只允许显式 plan/dry-run/受控验收，non-dry-run 必须 fail-closed。Stage E 合成端到端验收和 Stage F 生产启用是独立阶段。

详见本任务 `STAGE_D_IMPLEMENTATION_PLAN.md` 与 Sermon Owner canonical `DESIGN.md`。


## v1.3 统一 package consumer 入口（Stage D）

对新 Share / Sermon 的统一合同验证，使用 Website 的 `publish-contract` 入口：

```shell
python3 scripts/content_workflow.py publish-contract --contract <website-publication-package-v1.3.json> --schema contracts/website-publication-package-v1.3.schema.json --content-root <package-content-root> --mode plan
python3 scripts/content_workflow.py publish-contract --contract <website-publication-package-v1.3.json> --schema contracts/website-publication-package-v1.3.schema.json --content-root <package-content-root> --mode dry-run
```

`plan` / `dry-run` 只验证并预览 SHA-bound package、presentation identity、profile、archive semantics 与 Website import/render gates。Stage F 前不得执行 `--mode publish`；consumer 必须 fail-closed。现有 `publish share|sermon` 是迁移期间保持现行生产路径的版本绑定兼容入口，不代表 v1.3 已成为生产默认，也不得用它绕过 package-bound v1.3 gates。底层 direct importer 的 package/source/metadata 验证继续独立生效。

Sermon producer 端通过 `generate_prepublish_md.py --contract-version 1.3`、`build_website_publication_package.py --contract-version 1.3 --content-presentation-manifest ...` 与 `export_to_website_project.py --publication-package ...` 生成/验证/导出 package；export 默认 dry-run。Share 与 Sermon 必须分别使用 `share_article` / `sermon` profile，不能互换。

## 内容类型

项目主要处理：

1. 分享文章
2. 讲道资料
3. 信仰随笔
4. 圣经学习笔记
5. 翻译整理稿
6. 公众号迁移稿
7. 网站正式 Markdown / Content Collections 文章

## 重要目录

| 路径 | 用途 |
| --- | --- |
| `\\RonnieNAS\tmp\分享` | 分享收件目录 |
| `\\RonnieNAS\tmp\讲道` | 讲道收件目录 |
| `data/raw/分享/` | 分享原始资料 |
| `data/raw/教会讲道/` | 讲道原始资料 |
| `data/processed/整理后的分享文章/` | 分享中间稿 |
| `data/processed/整理后的讲道文章/` | 讲道中间稿 |
| `src/content/posts/` | 正式网站文章 |
| `docs/内容整理报告/` | 目录、审计、待确认报告 |

## 跨项目文档同步规则

讲道整理项目与个人网页项目共同维护讲道发布流程。以后只要新增或修改讲道整理、讲道翻译、讲道发布、NAS 归档、日期、元数据、发布前 MD、导出或质量门禁相关规则，都要同步检查两个项目的对应文档。

对应文档至少包括讲道整理项目的 AGENTS.md 和 docs 下相关工作流文档，以及个人网页项目的 AGENTS.md、CONTENT_WORKFLOW.md、docs/统一内容整理与发布流程.md、docs/content-publishing-error-prevention.md、skills/article-workflow.md。若只更新其中一个项目，最终汇报必须说明另一个项目尚未同步及原因。

## 内容事实来源优先级

处理内容时，按以下优先级判断：

1. 原始资料本身。
2. 用户本次明确要求。
3. `docs/统一内容整理与发布流程.md`。
4. `docs/content-style.md`。
5. `skills/article-workflow.md`。
6. 过去聊天记录或旧草稿。

## 讲道 Owner 输入与网站消费 Gate

讲道翻译、Full Sermon Mode、E1、经文/ending fidelity、审核/修复轮次、Attempt 3 final repair 和 max-audit release semantics 不由网站项目定义。当前 sermon canonical authority 统一引用：`../讲道整理/docs/end-to-end-content-publishing-workflow.md §4.4.1/§4.4.2/§4.4.3`、`../讲道整理/docs/translation-fidelity-quality-control.md`、`../讲道整理/docs/sermon-independent-audit-orchestration.md`。

Stage F 启用统一流程前，现行生产入口保持不变：讲道继续通过 `website-publication-package/v1.2` 接收讲道 Owner 已成立的正式中文稿/英文源 identity 与 SHA、publication-facing fidelity status/evidence、发布前 Markdown 和发布元数据；分享继续使用既有批准的 Share 路径。v1.1 继续用于历史、已生成、在途 package 与显式兼容。Stage C 新增的 `website-publication-package/v1.3` consumer 仅供显式 plan/dry-run/受控验收，publish 模式在 Stage F 前强制禁用。v1.3 Share presentation import 的 package 安全边界同时强制于 `content_workflow.py` 与底层 `import_shares.py`：底层 importer 必须独立校验 package、presentation artifact、source 和 metadata 身份；直接调用不能绕过 package，也不能在 Stage F 前写入。source selector 必须是 Share raw root 下的单一文件名，并与 package 中唯一规范相对路径 `data/raw/分享/<filename>` 精确绑定；workflow 与 direct importer 都必须确认目标是实际存在的普通文件，missing file、directory、broken symlink、nested path、绝对路径、路径穿越及任何 symlink alias 均 fail closed，workflow 必须在 renderer/importer 前拒绝。初始路径解析与 package-bound identity 校验使用 Website-local `scripts/share_source_identity.py` 的不同函数；严格 package-bound helper 必须显式提供有效 `expected_source`，不得省略或传入 `None`。`scripts/publication_contract_invariants.py` 仅保留与 Sermon Owner byte-identical 的跨文档合同不变量。不得用 build、mirror、SHA、JSON 计数或网站自身判断替代 sermon fidelity approval。

网站自己的消费与显示 Gate 继续生效：

- 导入时核对 package、正式稿 identity/SHA、metadata 与目标路径，异常时 fail-closed。
- 正文 Markdown 的标题、小标题、编号列表、引文、对话、祷告、讨论问题等必须保持可读层级；网站导入器继续负责自身 Markdown/rendering 规范。
- 网站正文经文显示继续执行受控书卷全名 + `章/节/到` 的 TTS-friendly rendering；frontmatter、SEO 和 `scripture` metadata 继续允许紧凑机器格式。该项是网站 display/import 责任，不构成网站对 sermon scripture fidelity 的重新判断。
- raw/processed/posts、metadata、slug/articleId、build、Git、deploy、SEO、notification 与线上发布事实继续归网站 Owner。

若讲道 Owner 的 fidelity 规则发生变化，网站不复制新的规则正文；只检查 canonical reference 与当前生产 `website-publication-package/v1.2`、Stage C 的受控 v1.3 候选 consumer（以及需要时的 v1.1 compatibility）contract compatibility，并在确有网站侧兼容需求时调整消费或显示 Gate。v1.3 只有在 Stage C/D/E 独立验收通过、Owner 接受后由 Stage F 明确启用，才可替代现行生产入口。

### 已发布讲道正文修正模式

对已经发布的讲道进行批量复核时，必须使用正文修正模式：

1. 逐篇以英文原稿为准人工对照，只修改正文内容和必要的中文分段。
2. 锁定既有 slug、标题、日期、articleId、作者、分类、经文范围和 source，不得因重译生成新文章或改变 URL。
3. 禁止调用邮件发送、补发、订阅通知、`workflow_dispatch` 或任何会触发读者提醒的流程。
4. 修正必须覆盖 raw、processed 和原 slug 对应 post 的正文，并验证三处内容一致。
5. frontmatter 仅允许补正 `tags`。标签通常 2-6 个，优先包含相关圣经书卷和 1-5 个核心主题；必须精准、统一，不得为 SEO/GEO 堆砌无关词。
6. 每篇必须保留独立审计记录，确认无遗漏、无摘要化、无未确认语境缺口、中文自然可读、标签准确后才能完成。

## 信仰文章整理原则

适合网站发布的信仰文章，应当：

- 保持神学核心不变。
- 语气温和、清楚、可读。
- 保留经文逻辑和核心论证。
- 避免无必要的攻击性表达。
- 不把文章改成空泛鸡汤。
- 对公众平台版本，可在不改变核心意义的前提下调整表达。

## 正文 Markdown 规范

网站正文必须使用标准 Markdown 段落：段落之间保留一个空行。只有单换行、没有空行时，Astro/Markdown 前台会把多行合并成同一个段落；Admin 编辑区虽然能看到换行，但公开页面不会显示为分段。

讲道、分享、翻译稿进入 `data/processed/` 或 `src/content/posts/` 前，必须清理只用于讲稿制作或投影片提示的标记，例如：

```text
[WD]
[SLIDE]
[slide]
[SLIDE - ...]
[TIMELINE SLIDE - ...]
[MAP]
[PAGE ...]
```

如果标记独占一行，整行删除；如果标记后面还有正文，只删除标记，保留正文。清理规则必须同时应用在中文原稿合并、发布前 Markdown 生成、导出到网站三个阶段，避免任一入口漏掉。

## 网站文章 frontmatter

正式文章位于 `src/content/posts/`。具体字段以 `src/content/config.ts` 为准。新增文章前必须先查看当前 schema。

一般文章至少应包含：

```yaml
title: "文章标题"
description: "文章摘要"
date: 2026-06-20
publishedAt: 2026-06-20T14:35:00+09:00
category: "分类"
tags:
  - 标签
draft: false
```

`date` 只用于日历日期、排序和归档；`publishedAt` 用于“xx前”，必须在文章首次公开发布时写入完整时间和时区。通过导入脚本或 Admin 发布时由系统自动生成；后续编辑既有文章时必须保留原值，不得改成修改时间。

如果项目当前使用 `articleId`，必须运行：

```shell
node scripts/add_article_ids.mjs
```

## 发布前远端同步规则

所有内容整理和发布任务，在开始修改、导入、导出、构建、提交或推送之前，必须先执行：

```shell
npm run sync
```

`npm run sync` 必须等价于 `git pull --rebase origin main`。如果本地已有未提交改动、同步失败或发生 rebase 冲突，必须暂停并与用户确认，不能跳过同步继续发布。

## Stage F 前现行生产兼容流程（Share / Sermon）

以下 Share / Sermon 操作步骤描述的是 Stage F 前必须保持不变的现行生产兼容路径：Share 仍走已批准的 legacy `publish share` 路径；Sermon 仍走现行 v1.2 / `sermon-presentation/v1` 路径。它们不是 v1.3 统一合同入口，也不得被用于绕过 package-bound v1.3 gates。新 v1.3 package 的唯一 Website 受控消费入口是上文 `publish-contract`，Stage F 前只允许 `plan` / `dry-run`，不执行生产写入。

## 分享流程摘要（Stage F 前 legacy production path）

0. 同步远端：`npm run sync`
1. 只读检查：`python scripts/content_workflow.py inspect share`
2. 入库：`python scripts/content_workflow.py ingest share`
3. 预览发布：`python scripts/content_workflow.py publish share --source-file "data/raw/分享/<file>" --dry-run --description "人工概括型摘要。" --tags "核心人物,核心地点,核心主题"`
4. 正式发布：`python scripts/content_workflow.py publish share --source-file "data/raw/分享/<file>" --description "人工概括型摘要。" --tags "核心人物,核心地点,核心主题"`
5. 检查文章、报告、Git 差异。
6. 运行 `node scripts/add_article_ids.mjs`（如需要）。
7. 运行 `npm run build`。
8. 更新 `docs/tasks/current.md`。

分享发布必须指定单个 `--source-file`，不得无参数全量扫描 `data/raw/分享/`。`description` 必须是人工概括型摘要，不能使用正文截取、模板句或占位符。统一 Tag Pipeline 会从 scripture 补入所有明确书卷，并按标题确定性规则推断人物、地点、事件和主题；`--tags` 保留为人工补充入口。人工标签与自动标签统一经过别名规范化、去重、generic 拒绝和最终 2–6 Gate。无法得到足够精准标签时必须 fail closed 并要求补充 `--tags`；不得使用 `分享`、`灵命成长` 等内容类型或分类词凑数。旧版 Share workflow/importer 在未提供作者时默认使用 `Ronnie`；显式 `--author` 仍优先。该默认只适用于 legacy 路径，v1.3 必须继续以 publication package 绑定的作者为准，不得让 legacy fallback 覆盖 package metadata。`--dry-run` 不写入 processed、posts、CSV 报告或审计摘录。

## 讲道流程摘要（Stage F 前 v1.2 legacy production path）

本节保留当前正式讲道生产路径；v1.3 producer/exporter/consumer 只用于显式受控 plan/dry-run/验收，Stage F 前不得替代本路径或执行 v1.3 production write。

0. **先核验上一次发布**：确认上一轮 production commit/deployment、公开 canonical URL、RSS/Sitemap 与 notification result 已 PASS；上一轮仍 pending/FAIL 时先闭合上一轮，不开始本轮发布写动作。
1. 同步远端：`npm run sync`。
2. 只读检查：`python scripts/content_workflow.py inspect sermon`。
3. 确认日期、经文标题和讲员。
4. 入库：`python scripts/content_workflow.py ingest sermon --date YYYYMMDD --title "经文与标题" --speaker "讲员"`。
5. 检查 PDF 提取稿。
6. 逐句完整翻译并校订中文 TXT；该 TXT 是 frozen fidelity candidate，不是 Website presentation artifact。
7. Fidelity release + Project Bible Gate PASS 后，由讲道 Owner 生成 body-only `presentation-prepared.md`；只允许空行、H2/H3、标准 Markdown list、blockquote、whole-record emphasis 等白名单 presentation transformation，并生成 `sermon-presentation/v1` manifest，机械证明去掉 presentation markup 后 frozen records 的文字与顺序完全一致。
8. 新 v1.2 sermon package 必须绑定该 manifest/artifact。Website read-only validator 可兼容历史无 binding package，但 sermon dry-run/publish 对无 binding package 必须返回 `PRESENTATION_ARTIFACT_REQUIRED`。
9. 归档：`python scripts/content_workflow.py archive-sermon --folder "data/raw/教会讲道/<folder>"`。
10. 预览发布：`python scripts/content_workflow.py publish sermon --folder "data/raw/教会讲道/<folder>" --presentation-file "<presentation-prepared.md>" --dry-run --description "人工概括型摘要。"`。
11. 正式发布：同上移除 `--dry-run`；canonical importer 直接消费已验证 presentation Markdown，不再对 plain TXT 执行 paragraph guessing/`normalize_body()`。
12. 正式写入前必须运行 `scripts/validate_sermon_presentation.mjs`；唯一可作为结构准入的 terminal 是 `SERMON_PRESENTATION_STRUCTURE_PASS` 且 `completion_ceiling=publication_structure_ready`。`MECHANICAL_PRESENTATION_PASS` 仅保留为 legacy compatibility 字段，不得再解释为完整排版验收。 canonical `import_sermons.py` 已内嵌此 Gate，直接导入也不允许跳过；中文并列提纲要在渲染后呈现相同层级的独立条目，不能把 H2/普通行混在一组。
13. 如需更新同一 source folder 对应的既有文章，必须显式加 `--update-existing`，且只能复用 registry 中的既有 slug/path。
14. 检查文章、报告、Git 差异并运行构建；在**首次 Git 发布前**实际查看手机 360/390px 视觉效果并记录截图/DOM 结构、审阅结果。缺视觉证据或出现并列项合并/横向溢出等问题，停留在发布前，不得以 build PASS 代替。
15. 当前 frozen publication object 一旦获得一次 `授权发布`，该授权覆盖标准 Publication Fast Lane 的 Website write → build → commit → push → deployment trigger → notification trigger → NAS append-only archive → registry/status/Git closure。除真实 blocker 外，不再为 commit、push、deploy、email、NAS 分别暂停并重复索权。
16. 本轮不等待本次 deployment/live/email 终态；记录 `PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY` 后结束。下一次发布从第 0 步核验本次结果。

讲道发布同样可用 `--tags "核心人物,核心地点,核心主题"` 补充人工标签。导入器不再默认生成 `讲道`、`教会讲道` 或讲员姓名；它从 scripture 与标题执行确定性生成，不足 2 个精准标签时停止并要求人工补充。所有标签规则与分享、Admin 共用 `assets/admin/tag-rules.json`。

讲道发布必须指定单个 `--folder`，不得无参数全量扫描 `data/raw/教会讲道/`。脚本会记录 `docs/内容整理报告/sermon-import-registry.csv`，用于固定 source folder、slug、source SHA-256 与正式文章路径。经文识别若在 folder、文件名、正文前部之间冲突，会停止并要求人工确认。

讲员身份必须按**显式完整值**处理。目录、package 或 metadata 已提供 speaker 时，该值就是当前 publication object 的 speaker identity；不得再用 substring/contains 规则把它归并到较短名字。`Patrick` 与 `Patrick父亲` 是两个独立 identity，除非存在用户明确确认的 alias mapping。历史 `SPEAKER_TAGS` 只允许在“没有显式 speaker”时作为 legacy fallback，不得覆盖显式 speaker。

## 公众号迁移稿

从公众号或聊天稿迁移到网站时：

1. 不要直接复制含平台格式的 HTML。
2. 转成清晰 Markdown。
3. 保留标题、小标题、经文、核心段落。
4. 删除与平台无关的引导语。
5. 根据网站分类和标签重设 frontmatter。
6. 检查公开表达是否温和、清楚、适合长期留存。

## 整理后 Markdown 命名规则

`data/processed/整理后的分享文章/` 和 `data/processed/整理后的讲道文章/` 中的整理后 Markdown 文件名，默认使用中文命名，格式保持为 `YYYY-MM-DD-经文-中文标题.md` 或项目现有中文命名风格。

正式网站文章位于 `src/content/posts/`，可以根据公开 URL、SEO 或稳定性需要另行使用英文 slug；但 processed 中间稿用于人工复查、追溯和对照原始资料，应优先保留中文可读文件名，不要为了统一 URL 把 processed 文件批量改成英文。

## data/raw 原始资料留存规则

`data/raw/` 是个人网页项目内的原始资料留存区，不是临时缓存目录。文章发布后，默认继续保留对应原始资料，以便后续追溯、复查和修订。

历史文章的 `source` 可能指向当前仓库中尚未恢复的 raw 文件或 raw 目录。遇到 `scripts/check_source_paths.py` 报告 missing 时，优先判断是否为历史 raw 未入库；不要把 `source` 批量改成 processed 文件、正式 posts 文件或其他不可验证路径。

当前 CodexPro 环境不能穿透 `C:\Users\caoyi\Projects\NAS` 下指向 `\\RonnieNAS\...` 的符号链接。除非用户明确提供文件到仓库内，或环境后续支持 NAS allowed roots，否则不要把 NAS raw 恢复作为本轮自动修复步骤。

讲道流程中的 `archive-sermon` 表示把 `data/raw/教会讲道/<folder>` 复制到 NAS 或其他受保护归档区；它不是移动，也不代表发布后删除 `data/raw` 里的源目录。NAS 讲道归档只保存三类内容：原始文件、英文原稿文件、翻译后的中文原稿文件。除上述三类以外，不归档发布前 MD、审计报告、中间目录、网站 posts、processed 副本、脚本日志、`*.extracted.txt` 或其他可再生成资料。

后续如需清理 `data/raw/`，必须先运行 source 路径检查：

```shell
python scripts/check_source_paths.py
```

然后确认：

```text
1. 对应 processed / posts 文章的 source 不再依赖该路径；或
2. 已同步更新 source 到新的受保护归档路径；并且
3. 用户明确同意清理。
```

检查报告输出到：

```text
docs/内容整理报告/source-path-check.csv
```

独立的 `讲道整理` 项目不得直接写入个人网页项目的 `data/raw/`。它应先在自身项目内生成 `发布前MD/待发布/` 或 `发布前MD/待补元数据/`，只有用户明确进入网站发布流程时，才由个人网页项目执行导入、发布和归档。

从 `讲道整理` 项目导入讲道时，不得只把发布前 MD 或导出后的 posts 文件复制进 `src/content/posts/` 就视为完整发布。个人网页项目必须确认 raw/source 资料交接、`data/processed/整理后的讲道文章/` 副本、正式 posts、`articleId`、构建、线上验证和 NAS 归档状态。讲道内容默认必须执行 `archive-sermon` 或等价的只新增复制归档，但 NAS 实际归档内容仅限原始文件、英文原稿文件、翻译后的中文原稿文件；若因权限或环境无法完成，必须记录 `archive_status=pending`，并在最终回复和交接文档中明确说明。

## 安全边界

- `data/raw/` 只新增，不直接改写或删除原始文件。
- NAS 受保护归档区默认只新增和读取，不移动、不删除、不覆盖。唯一例外是已发布讲道因漏译或概括性翻译而重译，且用户对当前重译任务明确授予临时覆盖权限时，可以只覆盖 `/Volumes/share/教会讲道/<对应目录>/` 中原有的最终中文 `.txt`。覆盖前后必须记录路径、大小和 SHA-256；PDF、英文原稿及其他文件仍禁止修改。未挂载时记录 `nas_overwrite_status=pending_mount`，不得创建同名本地目录冒充 NAS。
- 导入脚本不得清空 `src/content/posts/`。
- 不得因为整理某一类文章而删除另一类文章。
- 目标文件已存在时，停止并核对，不要自动覆盖。
- Stage F 前现行兼容生产路径：分享使用 `publish share --source-file ...`；讲道使用 `publish sermon --folder ... --presentation-file ...`。这些 legacy 路径不代表 v1.3 已启用，也不得作为 v1.3 package consumer 的旁路。Stage F 前 v1.3 只能通过 `publish-contract --mode plan|dry-run` 受控验证，`publish` 模式 fail-closed。无参数全量导入和 sermon plain-TXT presentation guessing 均已禁用。
- 正式发布前优先运行 `--dry-run`，确认目标路径、标题、经文、摘要和 Git diff 范围。
- `description` 必须由整理者人工概括正文主旨；脚本不得用正文前部、模板句或占位符代替。
- 讲道 `slug` 由 source folder 日期稳定生成，正式发布记录在 `sermon-import-registry.csv`；更新旧文必须显式使用 `--update-existing`。

## 完成前检查

- [ ] 原始资料是否已保留。
- [ ] 中间稿是否保留。
- [ ] 正式文章是否在 `src/content/posts/`。
- [ ] 讲道内容是否已执行 `archive-sermon` 或等价只新增复制归档；如未完成，是否记录 `archive_status=pending`。
- [ ] frontmatter 是否符合 `src/content/config.ts`。
- [ ] 标题、日期、分类、标签是否正确。
- [ ] 讲道内容的 `date` 是否使用本次整理发布日期；不得从文件名、讲道内容、历史讲道日期或旧日期线索推断。非讲道文章如用户明确指定日期，按对应内容流程处理。
- [ ] 翻译是否没有遗漏原文信息。
- [ ] 正文段落之间是否保留 Markdown 空行，前台不会合并成一整段。
- [ ] `[WD]`、`[SLIDE]` 等讲稿/投影片标记是否已从中文稿、processed 和 posts 中清理。
- [ ] 是否更新整理报告。
- [ ] 是否运行文章 ID 脚本。
- [ ] 是否运行 `npm run build`。
- [ ] 是否更新 `docs/tasks/current.md`。

## 发布防错清单

每次“分享”或“讲道”整理发布，都必须同时阅读并执行：

```text
docs/content-publishing-error-prevention.md
```

上次讲道发布暴露出的固定风险：

- 双语 PDF 普通文本提取可能丢句、错序，`*.extracted.txt` 只能作为辅助，不是最终翻译源。
- 讲道翻译必须逐句忠实，不能变成摘要、提纲或主题整理。
- `description` 不能由脚本硬截正文、不能用模板句凑数，也不能只抽取正文原句；必须由整理者阅读标题、经文和正文主旨后，写成一两句可独立阅读的大意摘要。
- 讲道文章的 frontmatter `date` 固定使用整理发布时的日期；不得从原始文件名、讲道内容、历史讲道日期、文件修改时间或用户旧日期线索推断。补录旧讲道也按整理发布当天进入网站时间线。非讲道文章如用户明确指定发布日期，仍按对应内容流程处理。
- 自动识别的 `scripture`、中文 slug 和 `articleId` 可能不准，提交前必须人工核对。
- 讲道 publish 脚本可能重写旧讲道文章，提交前必须检查并排除无关旧文覆盖。
- 新文章不出现在构建产物或出现 Duplicate id 时，优先清理 `.astro` 本地缓存后重建。
- 线上验证优先使用正式域名 `https://ronniecross.com/`，不要只凭 GitHub Pages 默认域名判断失败。
