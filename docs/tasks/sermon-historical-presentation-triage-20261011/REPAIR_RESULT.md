# 81 篇历史讲道排版修复正式结果（2026-10-11）

## 执行顺序、范围与结果

正式工作区：`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`。按用户明确批准的 `P1 → P2 → P3` 顺序，对上轮已列出的 81 篇网站讲道正文做定向排版修复；没有更改讲道 Owner 的冻结英文/中文源、Project Bible、NAS、音频、原文件或翻译 E1 结论。

- P1：19/19 已处理，19/19 **SERMON_PRESENTATION_STRUCTURE_PASS**。清理制作阶段幻灯片标记、修复中文提纲伪列表、目录的重复编号、少量经文标签与讨论问题结构。
- P2：34/34 已处理，34/34 **SERMON_PRESENTATION_STRUCTURE_PASS**。拆分原本混在同一行的 `1）2）3）` 视觉列表、规范编号、相关章节标题和经文标签。
- P3：28/28 已处理，28/28 **SERMON_PRESENTATION_STRUCTURE_PASS**。仅规范独立经文引用标签的全角冒号，未改变引用原句或经文对应文本。
- 当前此前 FAIL 分母共 81/81 回归为机械 Gate PASS；原始 220 篇中 139 篇此前通过且本次未改动，因此**当前总数应为 220/220 结构 Gate PASS**（非 220 篇真实 iPhone 人工视觉 PASS）。
- `python3 scripts/check_content_mirrors.py`：604/604 PASS；81 篇每篇 post 和 processed 的**正文相同**；逐文件比较旧 `HEAD`，**81×2 frontmatter 完全未变化**，包括 slug 所在路径、articleId、日期、作者、经文和分类。
- 保留文字核验：81/81 篇中文与英文字符序列在排除批准移除的 `[幻灯片]` 等制作标记后与原 Git HEAD 相同；未通过整体重写、缩减正文或改动语义让 Gate 通过。经文字符未变，只更新独立标签后面的格式标点。
- Astro 最终构建 346 页 PASS；20/20 presentation regression、27/27 Tag Pipeline、Knowledge Layer 302 篇 0 错误 0 警告均 PASS；`git diff --check` PASS。

## 现场与真实渲染

- P1 `2026-07-09-马太福音-5-13-16｜盐和光.md`：最终 Astro 页面中三个并列要点存在，并以真实 Chrome headless 390px 页面核对三项各对应唯一 `<li>`、同一个 `<ul>`，`scrollWidth=375 < 390`，无横向溢出。
- P2 `2025-05-04-使徒行传-17-16-24｜未知之神.md`：最终 Astro 页面中的三项编号正确显示，真实 Chrome headless 390px 核验三项为独立 `<li>`、同一 `<ul>`，无横向溢出。
- P3 `2021-01-09-彼得前书-1-3-4｜福音的恢复.md`：最终 Astro HTML 中已显示 `彼得前书1章4节：`，未更改经文原文。
- Chrome 截图与 DOM JSON 保存在本地非 Git 证据目录：`logs/sermon-historical81-repair-20261011/`。本次对 P1/P2 做代表性实际窄屏浏览器检查；不声称已人工逐篇在 iPhone Safari 检查 81 篇。

## 历史时间线与发布边界

- 原历史盘点：220 篇中 139 PASS / 81 FAIL（触发新旧校验规则），仅作缺陷发现，没有批量修改。
- 本次真实修复 chronology：P1 19 PASS → P2 34 PASS → P3 28 PASS；详细文件与新旧 SHA 见 `P1-repair-changes.json`、`P2-repair-changes.json`、`P3-repair-changes.json`；81 篇逐篇原始命中位置见 `REPORT.md` 和 `report.json`。
- 网站邮件通知脚本 `scripts/notify-deployed-posts.mjs` 以 Git `--diff-filter=A` 识别新增文章，而本次 write-set **只有修改现有 posts**，没有增加新文章；本次不得发送新文章邮件、不执行 `workflow_dispatch`。若推送后 GitHub workflow 因路径被触发，它应检测不到新增文章并安全退出。
- 本次只改 81×2 网站 `processed/posts` 文件和本盘点报告文件，不更改其 raw 中文底稿或受保护 NAS 源。
- 正式 Git commit / push 与远端回读需要以本次实际执行记录为准；文档写入不等于已经部署成功，生产页面最终 live readback 另验。
