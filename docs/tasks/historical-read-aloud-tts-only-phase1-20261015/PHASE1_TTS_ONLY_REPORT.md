# 历史文章 TTS-only Phase 1：299 篇资格重新盘点与五篇 Pilot 生产前技术预检

日期：2026-10-15；性质：**只读技术预检及报告落盘**。本次无音频合成、NAS/R2、正文修改、邮件、Git commit/push。

## 一、结论与分母

- 基准：303 篇正式 Markdown 文章，其中 4 篇已有 audioUrl，剩余 **299 篇**。
- 已按生产当前 `scripts/read_aloud_render_view.mjs` 逐篇真实调用 `renderPost()`：**269 篇无标记通过、17 篇渲染成功但带编号结构提示、13 篇被当前渲染器拒绝**。
- `reviewed`、原文英文、E1、Project Bible 不是本轮 TTS 技术阻断项；旧 Phase 0/0.5 对这些条件的判定仅保留历史，不再作为本次放行标准。
- `PASS_RENDER_WITH_STRUCTURE_FLAG` 指渲染器成功，但正则发现中文编号结构，**不等于确认朗读损坏**；应对这些篇目做实际 Render View 结构抽检，避免擅自修复正文。

| TTS-only 分类 | 篇数 | 处理规则 |
|---|---:|---|
| 渲染通过，无提示 | 269 | 可排队单篇 once-only 任务准备 |
| 渲染通过，编号结构提示 | 17 | 先做朗读顺序/列表结构复核 |
| 当前渲染器阻断 | 13 | 须修复**渲染兼容性**或选择受控替代，无原文重审 |
| **合计** | **299** | **无 TTS 执行授权** |

## 二、13 篇真实阻断

- **11 篇旧式 `sermon-...` articleId**：现行渲染器限定 `post-...` 前缀，报 `ARTICLE_ID_MISSING`，但文章本身存在稳定 articleId。不能直接改动历史 articleId，应先提出兼容性最小修复和回归测试。
- **2 篇带 UTF-8 BOM 的 Markdown**：渲染器要求首字节即 `---`，报 `FRONTMATTER_MISSING`。不能修改正式正文绕过质量门；可以讨论在受控读取层支持 BOM。

| 阻断码 | 文章 |
|---|---|
| `FRONTMATTER_MISSING` | `2026-06-21-romans-15-1-13-gospel-harmony.md` |
| `FRONTMATTER_MISSING` | `2026-06-28-romans-15-14-33-gospel-reminder.md` |
| `ARTICLE_ID_MISSING` | `2026-07-02-创世记-3-1-10｜福音-堕落.md` |
| `ARTICLE_ID_MISSING` | `2026-07-02-腓立比书-2-6-11｜福音-救赎.md` |
| `ARTICLE_ID_MISSING` | `2026-07-03-马可福音-1-1-8｜服侍的君王.md` |
| `ARTICLE_ID_MISSING` | `2026-07-03-马可福音-1-35-45｜耶稣与麻风病人.md` |
| `ARTICLE_ID_MISSING` | `2026-07-03-马可福音-1-9-13｜神所爱的儿子.md` |
| `ARTICLE_ID_MISSING` | `2026-07-03-马可福音-2-1-12｜我们真正需要的是什么.md` |
| `ARTICLE_ID_MISSING` | `2026-07-04-马可福音-2-23-3-6｜安息日的主.md` |
| `ARTICLE_ID_MISSING` | `2026-07-04-马可福音-4-35-41｜耶稣平静风浪.md` |
| `ARTICLE_ID_MISSING` | `2026-07-04-马可福音-5-21-43｜绝望中的信心.md` |
| `ARTICLE_ID_MISSING` | `2026-07-04-马可福音-6-30-52｜好牧人的供应.md` |
| `ARTICLE_ID_MISSING` | `2026-07-05-罗马书-16-17-27｜被福音坚固.md` |

## 三、首批五篇 Pilot 技术预检

此前五篇的 source/E1 阻断不再适用于“已发布中文文章 TTS-only”。本轮直接对正式文章运行当前生产 Render View，并验证 articleId、post SHA、render SHA、无旧 audioUrl。

| Pilot | 作者 | Render View | 实际字数 | SHA |
|---|---|---|---:|---|
| 列王纪上 17:1-24｜以利亚与撒勒法寡妇：信靠神的供应 | Ronnie | **PASS_RENDER_READY** | 2160 | `d736091f42749fd3…` |
| 希伯来书 11:1-7｜信仰的殿堂：挪亚 | Akira | **PASS_RENDER_READY** | 5198 | `9595d571c66d539d…` |
| 帖撒罗尼迦前书 4:16｜在基督里死了的人必先复活是什么意思 | Ronnie | **PASS_RENDER_READY** | 2178 | `46523a1a5027e4b7…` |
| 希伯来书 11:8-11;17-19｜没有道路时的信心 | Nathan | **PASS_RENDER_READY** | 6387 | `5e534b6ae40633cc…` |
| 希伯来书 11:21、39-40｜信仰的殿堂：雅各 | Grayson | **PASS_RENDER_READY** | 5616 | `412426de24014456…` |

**五篇均为 Render View PASS**；尚未证明音频声学 QC、原文章内容是否存在历史错误，也尚未启动任何 TTS。正式 Pilot 生产仍需单篇冻结快照、授权和防重复执行检查。

## 四、Pilot 顺序与运行门

1. 先两篇短分享，再三篇长讲道；每篇独立 once-only request ID、脚本 SHA、运行时 claim 和产物回执，不使用全量自动循环。
2. 生产前再次 fresh-read live Git articleId、post SHA、Render View SHA、audioUrl 不存在和上一次网站发布 VERIFIED。
3. TTS 生成之后，WAV/MP3 全解码、异常啸音/静音、首尾完整性和必要试听；质量异常停在媒体上传前。
4. NAS WAV append-only、R2 单对象上传、SHA/Range 206、仅新增 audioUrl、构建与精确 push；本次 push 后 PENDING 收口，下一次发布前核验。
5. 不进行中英翻译重新审核，`reviewed: false` 不构成 TTS 阻断。

## 五、证据边界

- 本次代码执行返回的 299 条结果保存在 `tts_only_inventory_299.json` 和 `TTS_ONLY_INVENTORY_299.csv`。基准 Git HEAD：`67a68298a21c05ab27befd2b39c2a722a67bd851`。
- 十三篇属于实际现行渲染器拒绝，编号结构属于提示风险，两者不能混同。
- 此计划不是历史批量 299 篇自动执行授权；不得自动请求 TTS 或发布。
