# 2026-10-11 讲道网站排版质量门专项整改 — RESULT

## 任务、范围与当前结论

任务：杜绝 Patrick《活着就是基督》式中文并列提纲变形重复进入正式网站发布。正式工作区 `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`。**只改现有 Website presentation validator、唯一 canonical sermon importer 的前置硬门、测试夹具及发布流程文档；不改原文翻译、Project Bible、NAS、既有文章正文或部署基础设施。**

结论：**结构质量门代码完成 / 单篇真实负向准入验证 PASS / 20 项回归测试 PASS / 390px + 360px 实际浏览器布局 DOM PASS / 已构建 346 页 PASS**。人眼已查看 390px 窄屏截图中 3 个独立要点和自然换行。其余历史文章不在本轮修复 write-set。不要把此结果称为新的隔离独立 E1 审核。

## 为什么此前重复漏检

2026-09-13《为爱心祷告》事故已经确立“伪编号需变成真正 Markdown list、实际 Astro 渲染检查”规则；此前 `scripts/validate_sermon_presentation.mjs` 主要处理 `1）/2）`、重点 section、heading 与段落数量，没有检查 **中文 `一、二、三、` 是否为同一语义层级的并列提纲**。2026-10-11 Patrick 文本在 `今天有三个要点` 后误成 `## 一、` + 普通行 `二、` + 普通行 `三、`，结构 Gate 误报 PASS；网站并未完成必要的手机窄屏实际目视审核。根因同时涉及 Gate 覆盖漏洞和执行环节缺失。

## 定向修复

1. `scripts/validate_sermon_presentation.mjs` 新增 `chinese_parallel_outline_structure` 检查，识别连续 `一、二、三、`、`（一）（二）（三）`、`第一点：第二点：第三点：`；同一组并列项必须全部是标准 Markdown 列表项。对“今天有三个要点”这类紧邻声明，核实实际项数与声明一致。独立正常章节标题之间有正文时不判为同组提纲。
2. `scripts/import_sermons.py` canonical direct importer、dry-run 与真正 publish 共用同一 prewrite 检验：以 Node/Astro 真实渲染器得到 `SERMON_PRESENTATION_STRUCTURE_PASS` 且 `completion_ceiling=publication_structure_ready` 才进入任何 raw→processed/posts 写入。错误、invalid JSON 与 unavailable Node 全 fail-closed。
3. 真实负向 smoke：`python3 scripts/content_workflow.py publish sermon --folder <exact existing folder> --presentation-file scripts/tests/fixtures/sermon_presentation/fail-chinese-outline-heading-mix.md --dry-run ...` 返回 `SERMON_PRESENTATION_STRUCTURE_FAIL`、exit=1、没有生成文章或修改已有 post。
4. `scripts/tests/test_sermon_presentation_gate.mjs` 新增 6 条 fail/pass regression：Patrick 事故、中文括号序号、第一点序号、声明数量短缺，以及正确列表与正常章节标题正例；与 2026-09-13 既有列表问题共同验收，`20/20 PASS`。
5. 实际 Astro 构建 `npm run build` exit=0 / 346 pages，Tag Pipeline fixtures `27/27 PASS`；本次没有打开旧文章重新导入/批量修复。

## 实际浏览器窄屏证据

测试来源：本次 Astro `dist/posts/2026-10-11-腓立比书-1-20-30活着就是基督/index.html`，Mac Chrome headless 经 localhost 加载网站静态 JS/CSS，而非仅 Markdown/HTML 字符串。截图和解析的 DOM 几何 JSON 保存在 **非 Git 的本地 evidence**：

`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目/logs/sermon-presentation-hardening-20261011/`

- 390px：`innerWidth=390`，`scrollWidth=375`，横向 overflow=false，`面对死亡/生活中/面对苦难` 各恰好匹配一个 `li`，均为同一个 `ul` 的子元素；截图 `mobile-390.png` 已目视查看，均为独立列表行。
- 360px：`innerWidth=360`，`scrollWidth=345`，overflow=false，三项仍恰好匹配独立 `li` 和相同 `ul`；截图 `mobile-360.png` 和 `mobile-360.json` 已保存。未将 headless Chrome 模拟等同于用户实际 iPhone Safari 验收。
- 视觉 Gate 不应只靠截图文件存在：以后每次讲道发布，都要在人或浏览器视觉审阅后附实际截屏/DOM 证据；不允许以构建成功冒充移动端视觉 PASS。缺此步骤必须在正式 Git 发布前停止并报告。

## 范围与 chronology

本轮不触及两份通过 E1 的源/译文 SHA，不重发文章邮件。Patrick 原发布与修复提交的历史记录、之前反复发生的排版事故、旧 CHECK FAIL 均保留。当前任务只完成发布质量门整改，下一次实际新文章发布仍需单篇校验与新截图 evidence，不能用本轮截图充作其他文章的验收。

全量只读兼容性扫描：**220 篇**现有讲道逐一经新网站结构 Gate 验证，**139 PASS / 81 FAIL / 0 invalid**；81 个是按当前严格合同发现的既有历史内容问题，不是本次代码引起 81 篇新修改。其中 **12 篇被新增中文并列提纲规则识别**（两份抽样原文确有“一、二、三”普通行而非真正 Markdown list），其余主要为已有脚本会阻断的旧标签、幻灯片残留、伪列表等。详细只读逐文件结果见 `logs/sermon-presentation-hardening-20261011/legacy-sermon-scan.json`，该文件不加入 Git。12 个新结果并未全部完成人工复核，不得直接宣称 12 篇均存在已确认缺陷。本任务不批量重写 220 篇旧文章；若需历史修复应单独批准逐篇清单，保留新旧 Gate chronology。

最终 Git commit / push 与 remote readback 以本轮实际执行日志为准，不能预填 PASS。
