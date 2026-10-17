# 历史文章有声阅读 Phase 0.5：审核凭据恢复和源路径核验

日期：2026-10-14；模式：只读原有材料 + 写入报告；无 TTS、无发布、无原文修改。

## 一、299 篇逐篇交叉核验结果

- Phase 0 分母：303 篇正式文章，4 篇已有 audioUrl，**299 篇待音频**。本轮关联 299/299，不改变分母。
- 分类：{'教会讲道': 219, '灵命成长': 80}。
- 严格证据级别分母：**3 篇符合“静态及 reviewed 标志足以进入单篇最终门”的条件，但本轮没有证明任何文章已完成此次历史 TTS 专用的经文/语义/音质最终审查。**

| Phase 0.5 处理类别 | 篇数 | 意义 |
|---|---:|---|
| 单篇最终质量门候选 | **3** | 仅能排队单篇核验，不代表自动批量 TTS 许可 |
| 需要人工/独立审核凭据核对 | **286** | reviewed 和已有登记不足以证明当前正文忠实度 |
| 暂缓：结构风险 | **10** | 编号或正文问题先检查，可能是静态误判 |
| 暂缓：硬门 | **0** | 草稿、正文空等需先解决 |

**合计 299 篇。任何未找到确证的历史审核不能自动设为 PASS。**

## 二、现有正式历史索引的可恢复信息

- 在 299 篇中匹配到 sermon-import-registry：**106** 篇。导入记录带原始 source SHA / post path，但状态 imported 只证明导入，不等于 fidelity PASS。
- 精确标题匹配分享目录：**73** 篇；“已完成基础校订”不能取代完整源对照。
- 匹配旧 source-path-check：**284** 篇；历史 missing/ok 可能是旧 Windows 或旧归档位置，不能据此断言当前 NAS 缺失。
- processed 文件可定位：**299**；正文与网站正文逐字相同（移除 frontmatter 后粗比）：**299**。双副本一致不证明对英文原文忠实。
- 'reviewed: true'：**5**；false：**294**。该布尔字段不是独立审核报告。

## 三、关于“167 个 source 不可解析”的裁决

Phase 0 的 `SOURCE_PATH_MISSING_OR_UNAVAILABLE` 标记为 **167 篇**；本轮汇总 `source_exists=NO` 为 **168 篇**，其中 **1 篇根本没有声明 source**（Phase 0 单列 `MISSING_SOURCE`），所以两个口径并不矛盾。原 Phase 0 静态扫描中的 source 不可解析只表示“当时声明的 repo-relative 路径没有对应实体”。本轮并列输出声明路径、历史 source-path-check、导入登记/文件 SHA、processed 镜像是否存在，以帮助后续定向追踪。不能把 import registry / source check 的文件名匹配视为已找回原始字节；跨项目、NAS 或旧 Windows 资料需在 source Owner 合法 read-only 范围内再做哈希对照。

## 四、优先级与建议试运行

1. 先针对候选 3 篇（希伯来书讲道：挪亚、雅各、没有道路时的信心），读取其当前正式 fidelity 及 Project Bible 审核证据，进行“单篇最终质量门”后才可能 TTS。
2. 同步挑选灵命成长短文（历史目录有基础校订记录者优先）作内容/来源对照审核，目标补齐 2 篇分享，与讲道构成 3–5 篇 Pilot。
3. 结构风险 10 篇先复核原样 Markdown 在 Render View 下是否真会导致语义/朗读问题，再最小修改，绝不依据纯 regex 批量改。
4. 其余按来源定位证据、已有 fidelity 审核凭据的确定性关联度及长度分组。所有历史 TTS 必须单篇 request ID、once-only、独立工件哈希与逐篇发布 gate。

## 五、禁止误用和边界

- 本报告只读文章/历史索引，不修改 reviewed 标志、不补写或改写原稿、不触发 Telegram/TTS/NAS/R2/邮件、不 commit/push。
- 原因标注仅是可观察证据与缺失证据，不对真实语义忠实度和人工听感作结论。
- 299 篇批量回填依然受现行 authority 暂停约束；后续要有针对历史 backfill 的新授权、正式任务和有限批次。
- 保留 Phase 0 判定而不覆盖：此前 3 初步符合 / 286 待确认 / 10 结构风险的初筛历史仍有效；Phase 0.5 只增补独立证据层。

## 六、文件与复现

- 完整逐篇表：`EVIDENCE_RECONCILIATION_299.csv`（含 flags、source、registry status、镜像比较、最终核验类别）。
- 输入：`docs/tasks/historical-read-aloud-phase0-20261014/inventory_299.csv`、`docs/内容整理报告/{sermon-import-registry.csv,分享文章目录.csv,source-path-check.csv}`、现行 `src/content/posts` 和 `data/processed`。
- 不允许自动根据本报告签发生产权限。
