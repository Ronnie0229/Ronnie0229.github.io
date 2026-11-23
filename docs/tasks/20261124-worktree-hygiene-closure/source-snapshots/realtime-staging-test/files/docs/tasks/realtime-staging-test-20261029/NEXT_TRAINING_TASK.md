# REALTIME_STAGING_TEST_20261029 — STEP_18 纠正来源身份与视觉来源准入

角色：HERMES_STAGING_SOURCE_IDENTITY_REMEDIATION_EXECUTOR；汇报给 Project Owner。

正式工作区必须 exact open `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目` 并 fresh-read 当前相关 authority；实际 root 不一致则停止，不借用其它工作区。

**任务背景：** STEP_17 报告声称英文候选 7958 bytes、SHA `0942846b042153088366e0856b23b645f3101195e7c71559c463d6e00814e88a`。Project Owner 独立核验：PDF SHA `7e98a87c3a359ec4abb4f270b93ed669c692ae4582d3a57e7fd4c590cd94c0ab`；候选为 7958 个 Unicode 字符、8062 bytes、SHA `5142dc2fc01ba2afb9cc70bb9f6c2da8c2f17a5bcbf4e0c1a339f5c76a88c2e1`；PDF 4 页 PyMuPDF 文本分别 2107、2212、1963、1676 字符；候选字节解码与四页原始 `page.get_text()` 串接完全相等。原执行报告的 SHA/bytes FAIL，先前机械内容流一致 PASS，两种 chronology 都保留。

**本轮必须连续完成，不能每一步问用户：**

1. 重新读取 PDF 和 `.en.txt` 两文件，独立复算 SHA、bytes、chars 和 4 页字符数量；若不符合上面的现场身份，BLOCKED 并报告实际差异；不得修改原始 PDF/候选。
2. **本轮已生成视觉证据，无需重复渲染。** 读取 `pdf-visual-evidence/manifest.json` 和 `page-01.png` 至 `page-04.png`，先回算每张 PNG 的 SHA 和尺寸（150dpi、1240×1754）；必须由具备实际视觉能力的独立 reviewer 逐页对照原始 PDF 可见正文顺序、列序、标题、引语、署名、经文、末段以及 `.en.txt`，提供逐页 PASS/FAIL 证据。图片生成不等于视觉审阅；不能看图时 `BLOCKED_VISUAL_REVIEW_REQUIRED`，不要伪称 PASS。
3. 将前次执行者的错误身份按原始 FAIL + 更正 PASS chronology 写到新的 `STEP18_RESULT.md`，包含两个文件确切绝对路径、SHA/bytes/chars、每页结果、视觉证据 manifest、未解决差异。不能改写原 STEP17 报告来掩盖失败。
4. 只有原 PDF 页面视觉审查通过、文本流与候选完全一致及文档身份无漂移，才提请 Owner 冻结该 `.en.txt` 为正式英文源稿。如果有提取顺序或缺漏，只报告并提出最小修复，不自作主张改写原始引语或经文。
5. 输出唯一下一步，不进行中文翻译、网站发布、通知、部署、Git push、NAS 移动/覆盖；不得声称产生了未真正完成的独立 reviewer PASS。

**Project Owner 已验证的内容：** PDF 4 页均有文本块 (33/33/32/28)，没有 image blocks、`get_images()` 图像或注释；这是视觉审查风险较低的信号，并非视觉审查完成。候选首页确有 2 Peter 3:18 与 Charles Spurgeon 开头引语；末页包含 Philippians 1:6b 与 `And so, go and grow by the power of the Lord’s Spirit working in you.`。以上不是页内完整视觉审核的替代品。
