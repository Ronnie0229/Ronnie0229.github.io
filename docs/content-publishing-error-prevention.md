# 内容整理发布防错清单

本文件记录 2026-06-21 Patrick 讲道发布过程中暴露的问题、原因和固定整改。以后处理“分享”或“讲道”时，必须把这里当作完成前检查的一部分，避免重复消耗额度在同类错误上。

## 1. PDF 提取可能丢句或错序

问题：双语 PDF 的普通 `page.extract_text()` 会把英文、日文列混在一起；按 CJK 字符截断时，还会把英文段落中的日文引用误判为日文正文，导致英文源稿页尾丢句。

原因：PDF 是视觉排版，不是线性文本。双栏、双语、页眉页码和引用短语会破坏普通文本抽取顺序。

整改：

- 不要直接把 `*.extracted.txt` 当作翻译底稿或发布源。
- 先抽取并人工检查源语言底稿，确认每页开头、页尾、经文引用和例子都完整。
- 双语 PDF 优先确认翻译源语言；若用户没有指定，先明确说明本次依据哪一种语言。
- 对双栏 PDF，必要时按坐标抽取源语言区域；但抽取结果必须再人工通读，不能只看字符数。
- 最终中文 TXT 必须来自校订后的源语言底稿，不来自机器提取的混排文本。

## 2. 翻译不能变成摘要或主题整理

问题：讲道翻译如果只提炼主题，会遗漏原文论证、例子、过渡和重复强调。

原因：整理文章的习惯容易覆盖翻译任务；但讲道发布需要保留原文信息负载。

整改：

- sermon fidelity 的业务真值不再由本网站文档定义。Full Sermon Mode、E1、经文/ending fidelity、审核/修复轮次、Attempt 3 final repair 与 max-audit release semantics 一律引用 `../../讲道整理/docs/end-to-end-content-publishing-workflow.md §4.4.1/§4.4.2/§4.4.3`、`../../讲道整理/docs/translation-fidelity-quality-control.md`、`../../讲道整理/docs/sermon-independent-audit-orchestration.md`。
- 网站默认接受 `website-publication-package/v1.2` 交付的讲道 Owner 已成立正式稿 identity/SHA、publication-facing fidelity status/evidence 与发布元数据；v1.1 继续用于历史、已生成、在途 package 与显式兼容。不得用网站 build、mirror、SHA 或 JSON 检查替代 fidelity approval。
- 网站继续负责自身的 Markdown/rendering 可读性、正文经文 TTS-friendly display normalization、frontmatter/SEO/scripture metadata 机器格式、import fail-closed、raw/processed/posts 一致性以及后续 build/deploy/SEO/Git/notification Gate。
- 如果 package、identity/SHA、metadata 或网站显示/导入 Gate 不满足要求，网站应 fail-closed；但不得因此自行发明或重判 sermon fidelity verdict。

## 3. 跨项目文档同步防漏规则

问题：只在讲道整理项目或只在个人网页项目更新流程规则，会导致新对话或切换账号后读取到不一致的规则。

整改：

- 讲道 Owner 的 fidelity 规则变化时，不再要求两个项目同步复制相同业务规则正文。网站侧只检查 sermon canonical reference 与 current default `website-publication-package/v1.2`（以及需要时的 v1.1 compatibility）consumer/contract compatibility。
- 只有网站自己的消费、display/metadata、import、raw/processed/posts、build、Git、deploy、SEO、notification Gate 受影响时，才更新对应网站文档或实现；讲道 fidelity truth 始终回到讲道 Owner canonical authority fresh-read。
- 新开对话或切换新账号处理讲道发布时，网站应先读本项目 `AGENTS.md`、`CONTENT_WORKFLOW.md` 与相关发布文档，并按其中 canonical reference fresh-read 讲道 Owner authority；不得把网站旧规则副本当作 sermon truth。

## 4. 摘要 description 容易截断

问题：导入脚本默认从正文开头截取摘要，页面上会出现半句话，尤其是讲道文章开头通常先重复标题和问安。

原因：自动截取固定长度不知道句子边界，也不一定能抓住文章核心。

整改：

- 发布前必须人工检查 frontmatter 的 `description`。
- `description` 用 1 句完整中文概括文章核心，不能停在半句话。
- 讲道文章建议包含讲员、经文和主题，例如：`Patrick 分享罗马书 15:1-13，说明……`。
- 不接受以正文前 80 字作为重要文章的最终摘要。

## 5. 经文字段、标题和 slug 需要人工校正

问题：自动导入可能把 `罗马书 15:1-13` 识别成 `罗马书 15`，中文文件名生成的 URL 也可能不清晰或丢标点。

原因：导入脚本的中文经文解析和 slugify 对冒号、竖线、中文标题不稳定。

整改：

- 发布前必须检查 `title`、`scripture`、`date`、`category`、`tags`、`author`、`source`。
- `scripture` 必须保留完整章/节范围，例如 `罗马书 15:1-13`。
- 正式文章文件名优先使用稳定英文 slug，例如 `2026-06-21-romans-15-1-13-gospel-harmony.md`。
- 重命名文章文件后，必须同步 processed 版本和目录报告。
- 重命名后重新计算或确认 `articleId`，避免空值或与旧 slug 不一致。

## 6. 导入脚本可能重写旧文章

问题：运行 `python scripts/content_workflow.py publish sermon` 时，会重新生成同类所有讲道文章，可能覆盖用户手动修订过的旧文章。

原因：当前导入器是批量导入，不是只导入本次新增文件。

整改：

- 每次 publish 后立即运行 `git status --short` 和 `git diff --stat`。
- 如果出现非本次文章的 Markdown 改动，必须先检查原因。
- 对无关旧文章覆盖，恢复到任务开始前状态；不要把无关旧文覆盖混进提交。
- 提交前确认只包含本次目标类别和目标文章的变更。

## 7. Astro 内容缓存会导致新文章不出现或 Duplicate id

问题：新文章源文件存在，但 `dist/posts` 没生成；或重命名后出现 Duplicate id 警告。

原因：`.astro` 是本地内容缓存，删除或重命名文章后可能残留旧内容索引。

整改：

- 新文章未出现在构建产物、搜索索引或 sitemap 时，先清理 `.astro` 后重建。
- 如果只清 `.astro/data-store.json` 无效，清整个 `.astro` 目录后重建。
- `.astro` 是本地构建缓存，不是源内容；清理它不等于删除文章。
- 最终构建必须无新增 Duplicate id 警告。

## 8. 线上验证用正式域名

问题：GitHub Pages 默认域名可能返回 404，但正式域名已经可访问。

原因：项目使用正式域名 `ronniecross.com` 作为公开访问入口，GitHub Pages 域名不一定代表最终线上状态。

整改：

- 线上验证优先使用 `https://ronniecross.com/`。
- 验证新文章 URL 返回 200。
- 页面必须包含标题、分类、经文、讲员/作者、完整摘要关键句和正文代表句。
- 如正式域名未更新，再查看 GitHub Actions 状态；不要只凭 GitHub Pages 默认域名 404 判定失败。

## 9. 提交和交接必须分清内容提交与交接提交

问题：内容发布完成后，还需要更新 `STATUS.md` 和 `docs/tasks/current.md`，否则下一个账号无法准确接手。

原因：线上验证结果通常要等推送后才知道，不能完全写在内容提交之前。

整改：

- 内容文章先提交推送并线上验证。
- 验证完成后更新 `STATUS.md` 和 `docs/tasks/current.md`。
- 交接文档可以单独提交，记录构建结果、提交号、线上 URL、归档校验和剩余未跟踪文件。
- 最终回复必须说明：改了哪些文件、构建结果、线上验证、当前 Git 状态和注意事项。

## 10. 正文段落空行不能被压扁

问题：Admin 编辑区能看到换行，但公开文章页没有分段，正文像一整段连续文字。

原因：Markdown/Astro 需要段落之间有空行；只有单换行时，前台渲染会把多行合并到同一个 `<p>` 中。Admin 文本编辑器显示换行，不等于公开页面会分段。

整改：

- 中文原稿合并、发布前 Markdown 生成、导出到网站三个阶段都必须保留段落空行。
- 允许压缩三个以上连续空行为一个空行，但不得删除所有空行。
- 发布前抽查 `src/content/posts/<文章>.md`，确认正文段落之间存在空行。
- 线上验证时检查公开页面正文是否有正常段落间距。

## 11. 讲稿/投影片标记不得进入正文

问题：`[WD]`、`[SLIDE]`、`[slide]`、`[SLIDE - ...]`、`[TIMELINE SLIDE - ...]` 等源文件制作标记进入中文稿和网站正文。

原因：这些标记属于讲稿制作、投影片切换或内部编辑提示，不是面向读者的正文；如果流程没有清洗，就会一路进入中文原稿、processed 和 posts。

整改：

- 清理 `[WD]`、`[SLIDE]`、`[slide]`、`[SLIDE - ...]`、`[TIMELINE SLIDE - ...]`、`[MAP]`、`[PAGE ...]` 等来源标记。
- 标记独占一行时删除整行；标记后面还有正文时只删除标记，保留正文。
- 清理必须至少覆盖中文原稿合并、发布前 Markdown 生成、导出到网站三个阶段。
- 提交前搜索本次新增/修改的中文稿、processed 和 posts，确认无残留。

## 12. 讲道日期一律使用整理发布日期

问题：旧流程曾允许补录旧讲道时使用历史讲道日期、文件名日期或用户确认旧日期作为网站 `date`，这会让新整理发布的讲道沉到旧时间线里，也容易诱导脚本从内容中判断日期。

原因：对网站文章而言，讲道类内容的 `date` 现在统一表示“整理发布到网站的日期”，不是实际讲道日期。

整改：

- 讲道内容的 frontmatter `date` 必须使用本次整理发布时的日期。
- 不得从原始文件名、讲道内容、历史讲道日期、文件修改时间或用户旧日期线索推断 `date`。
- 补录旧讲道也按整理发布当天进入网站时间线。
- 非讲道文章如用户明确指定发布日期，仍按对应内容流程处理。

## 13. 讲道整理项目导入不能绕过 NAS 归档

问题：从 `讲道整理` 项目生成发布前 MD 后，若直接导出到 `src/content/posts/` 并提交发布，可能绕过个人网页项目原有的 `archive-sermon` 归档步骤。

原因：讲道整理项目负责整理和发布前 MD，个人网页项目负责正式发布和 NAS 归档。直接复制 posts 文件会让网站文章上线，但 raw/source 交接、processed 副本和 NAS 受保护归档可能没有完成。

整改：

- 从讲道整理项目导入讲道时，必须确认 raw/source 资料、processed 副本、posts 文件和发布记录一致。
- 讲道内容默认必须执行 `archive-sermon` 或等价的只新增复制归档。
- NAS 实际归档内容只包含三类：原始文件、英文原稿文件、翻译后的中文原稿文件；不归档发布前 MD、审计报告、中间目录、网站 posts、processed 副本或脚本日志。
- NAS 归档目标目录已存在时停止并报告，不得合并、覆盖、重命名或清理旧资料。
- 若因环境权限无法完成归档，必须记录 `archive_status=pending`，不得把任务写成完整完成。
- 只有用户明确要求本次不归档时，才能记录 `archive_status=skipped_by_user`。

## 14. 多入口标签规则不得漂移

问题：分享、讲道、Custom Admin 和备用 Decap Admin 曾各自处理标签；讲道导入还会写入 `讲道`、`教会讲道` 和讲员姓名。

整改：

- 所有新生成、新保存和新发布必须调用统一 Tag Pipeline；规则唯一来源为 `assets/admin/tag-rules.json`。
- Python 与浏览器运行时必须通过同一 fixture 的结果和错误码一致性测试。
- scripture 自动补书卷；标题/副标题只按确定性规则推断；CLI/Admin 人工标签必须保留但不能绕过规范化与 Gate。
- generic、歧义、非法字符、少于 2 个或多于 6 个全部 fail closed，不得静默删除、截断或 fallback。
- 讲道不再默认生成内容类型、分类或讲员标签。dry-run 若报告标签不足，必须提供精准 `--tags` 后重跑。
- 不通过收紧全局 content schema 迁移历史文章；完成检查必须确认没有批量修改 `src/content/posts/`。

## 15. 文章目录层级与锚点跳转必须适配移动端 sticky header

问题：文章目录同时包含 H2/H3 时，如果使用同一套连续编号却又只给 H3 增加额外左缩进，会出现目录条目视觉不对齐；点击目录锚点后，如果目标标题没有为顶部 sticky header 预留滚动偏移，标题和正文首行会被导航栏遮挡。

原因：目录的“编号体系”和“视觉层级”属于同一个交互合同；不能一边把 H2/H3 当作同一连续编号列表，一边再用额外 margin 制造伪嵌套。锚点滚动则必须考虑桌面/移动端 sticky header 的实际占位和安全间距，不能只使用浏览器默认滚动位置。

整改：

- 如果文章目录使用 H2/H3 共用一套连续编号，所有目录项必须统一左对齐，不得仅因 heading depth 给其中一部分条目增加额外缩进。
- 如果未来改为真正的分层目录，必须同时改成明确的层级编号/结构（例如父项 + 子项），不能保留“连续平级编号 + 视觉嵌套”的混合状态。
- 文章正文中的 H2/H3 锚点必须统一设置足以避开 sticky header 的 `scroll-margin-top` 或等价机制，并分别验证桌面与移动端。
- 修改 header 高度、移动端导航结构、文章标题样式或 TOC 组件时，必须重新验证锚点 offset；不得假设旧数值永久有效。
- 不允许通过给单篇文章增加空行、空标题、假锚点或局部 margin 来规避导航遮挡；此类问题应在全局文章渲染层修复。
- TOC/锚点属于网站全局交互行为，修复后至少抽查 1 篇同时含 H2/H3 的长文章和 1 个移动端窄屏尺寸。

## 文章移动端视觉检查清单

文章发布、文章模板/CSS/TOC 修改或移动端导航修改后，至少执行以下人工或浏览器 smoke check。该检查不能只由 `npm run build` 代替：

- [ ] 以手机窄屏宽度打开文章，页面没有横向溢出，正文、引用、列表和长标题不会被裁切。
- [ ] 文章目录中的连续编号条目左侧对齐一致；如果存在真正的子层级，层级结构和编号表达一致，不出现“编号平级但视觉错位”。
- [ ] 点击目录中第一项、中间项和靠近文章末尾的一项，目标标题都完整停在 sticky header 下方，不被顶部导航遮挡。
- [ ] H2/H3 锚点跳转后，标题上方保留自然间距，不能只是勉强露出文字边缘。
- [ ] 正文中的 `1. / 2. / 3.`、讨论问题和其他列表项自上而下独立排列，没有因为 Markdown 规范化或 CSS 变成同一行。
- [ ] 长经文引用、TTS 友好的 `某书某章某节到某节`、中英文混排不会撑破容器或造成异常换行。
- [ ] 小组讨论、祝祷、荣耀颂、结束经文等文章末尾结构在手机端仍有清楚的标题层级和段落间距。
- [ ] 深色/浅色主题（若当前页面支持）下，目录、正文、链接和锚点目标均可读，没有因颜色或 sticky header 背景导致遮挡感。
- [ ] 若本次修改涉及 header 高度、safe-area、字体尺寸或 TOC CSS，必须重新确认移动端锚点 offset，而不是沿用旧截图结论。

## 发布前强制检查

- [ ] PDF/源资料已移动或复制到正确 raw 目录，并记录 SHA-256。
- [ ] 从讲道整理项目导入的讲道已完成 raw/source 交接，不能只复制 posts 文件。
- [ ] 讲道已完成 NAS 归档；若未完成，已记录 `archive_status=pending/skipped_by_user`。
- [ ] NAS 归档内容仅包含原始文件、英文原稿文件、翻译后的中文原稿文件，没有归档发布前 MD、审计目录、网站 posts 或 processed 副本。
- [ ] 讲道已生成完整中文 TXT，且不是 `*.extracted.txt`。
- [ ] 双语资料已说明翻译源语言。
- [ ] `description` 是完整句，不是正文截断。
- [ ] 正文段落之间保留 Markdown 空行，公开页面不会合并成一整段。
- [ ] `[WD]`、`[SLIDE]`、`[MAP]`、`[PAGE]` 等来源标记没有残留在中文稿、processed 或 posts。
- [ ] 讲道 frontmatter `date` 使用本次整理发布日期；不得使用旧讲道日期。非讲道文章如用户明确指定发布日期，按对应内容流程检查。
- [ ] `scripture` 包含完整经文范围。
- [ ] slug 稳定、可读，必要时使用英文 slug。
- [ ] `articleId` 非空，并与最终 slug 稳定对应。
- [ ] `git diff` 中没有无关旧文覆盖。
- [ ] 构建无新增 Duplicate id 警告。
- [ ] 已完成文章移动端视觉检查：TOC 对齐正确，目录锚点不会被 sticky header 遮挡，编号列表保持纵向独立排列。
- [ ] 正式域名线上 URL 通过 200 验证。
- [ ] `STATUS.md` 和 `docs/tasks/current.md` 已更新。
