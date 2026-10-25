# Patrick《基督的道路》2026-10-25 发布事故复盘与整改

## 审核结论
事故不是单点格式问题，而是五处连续控制缺口：1) Owner 将「（默认规则，待元数据最终确认）」内务元数据直接混入中文译文；2) frozen 65/65 逐句 E1 审核者对第一条混入内容判 complete，validator 只证明审计记录与 SHA 绑定，不证明语义结论正确；3) 发布结构门只审 H2/list/block density，未拦截内部备注以及「正文标题+讲员+场合」重复栏位，造成 iPhone Safari 中三行被普通 Markdown 换行合并；4) 首轮修复只改 Website processed/post，正式中文、raw、NAS 未同步；5) Git push 已完成但 Cloudflare 生产仍停旧 SHA，后来通过手动 Pages 发布才完成页面纠正，该次现场 deployment.json 曾为 `commit=local`，不可冒充 SHA 绑定自动生产发布。

## Chronology（保留每个阶段，不用后续 PASS 覆盖失败）
- 初版 PDF 来源检查 BLOCKED → 来源专项 PASS；正式翻译审核输入、产物落盘多次 BLOCKED，最终 canonical package + 65/65 paired-result 形式校验 PASS、Owner accept-paired-result PASS。
- 初次上线后用户发现内部备注 FAIL；仅 Website 两处修复 PARTIAL；用户报告线上仍旧内容，核对 Cloudflare production 的旧 SHA 和污染 HTML CONFIRMED；手动部署后重新核对线上污染备注已消失 PASS。
- 后续用户 iPhone 截图指出标题/讲员/场合黏连 FAIL；Website post/processed、正式中文、raw、NAS 五处 presentation-only 修正并 SHA readback PASS；网站结构门、349 页构建 PASS；Git `799a905` push PASS。本轮不把没有新一轮线上核验的内容声称已经部署完成。

## 本次工程整改
- 在 Website 已存在的 `scripts/validate_sermon_presentation.mjs` 硬门增加 incident-specific 两类 fail-closed 检查：内部元数据确认备注与文首「标题+讲员」重复；显式「场合：」正文栏位。基于 frontmatter/title+author 已自动展示、以及 sermon 原话应保留的边界，范围限定为正文开头及已知内部注释。
- `scripts/tests/test_sermon_prepublication_structure_gate.py` 加两项故障注入，证明同一网站 consumer 门禁实际阻止导入，不靠额外人工 Reviewer；原 3 项正常用例保持 PASS。
- Sermon Owner 文档独立澄清 E1 逐条判断中文是否有英文无依据的额外内容，以及全副本 SHA 回读清单。原配对/正式审计 evidence 一律保留不覆写。

## 后续发布的固定规则
1. 下一次文章/音频发布前 preflight 必须确认上一次 deployment identity、公开页面、通知/媒体状态；发现 `commit=local`、旧 SHA 或状态未知按原规则 fail-closed。
2. 当前次审核→排版→Website HTML 硬门→build→commit/push→触发部署→NAS/Registry/Git closure 后立即写 `PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY`，本次不等待本次 Cloudflare live/邮件结果。
3. 修复发布对象必须对 source、raw、processed、post、NAS archive 的实际 write-set 做一致性回读，严禁只修公开 Markdown 后宣称全完成。原 E1 审核证据和历史状态不追写。

## 边界
此为 incident-driven hardening，未引入新审核轮次、全局调度器、通用 house-style 系统或 TTS 改造。本结果未执行新一轮生产部署，也未更改无关历史有声阅读未跟踪任务。
