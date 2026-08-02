# Tag Pipeline Design

## 状态

`IMPLEMENTED_PENDING_INDEPENDENT_REVIEW`

本设计基于 2026-08-02 对现有 Python、Custom Admin、备用 Decap Admin、发布契约消费路径、SEO/内容规范和相关测试的只读审查。实现必须遵循本设计；若实现阶段发现必须改变跨项目接口或扩大范围，应停止并记录阻断，不得用复制规则规避。

## 1. 现状审查结论

### 1.1 Python 发布路径

- `scripts/content_workflow.py` 是分享、讲道和 `publish-contract` 的统一命令入口，但当前只负责转发参数，没有统一标签 Gate。
- `scripts/consume_publication_package.py` 将 `website-publication-package/v1.1` 中兼容可选的 `metadata.tags` 转发给现有入口；本任务不把该字段升级为跨项目必填字段。
- `scripts/import_shares.py` 内置 `build_seo_tags()`：要求 `--tags`，只补一个按空格切出的书卷名，维护局部 generic 集合并做 2–6 个数量检查；没有别名、规则推断、多书卷或统一字符校验。
- `scripts/import_sermons.py` 没有 `--tags`，固定生成 `讲道`、`教会讲道` 和讲员姓名，违反当前 SEO 规范和本任务合同。
- 两个导入器都可被直接执行，因此最终写入 Gate 必须位于导入器共享模块，而不能只放在 `content_workflow.py`。

### 1.2 Admin 路径

- `assets/admin/editor.js`（Custom Admin）从输入框读取人工标签，只用本地 `GENERIC_TAGS`、正则提取单一书卷并在正式发布时检查 2–6 个；草稿保存与正式发布不共享完整统一规则。
- `assets/admin/decap.js`（备用 Decap Admin）当前 preSave 只补 `articleId` 和 description，没有统一标签 Gate。
- `assets/admin/config.yml` 保留人工标签输入，但没有别名、规则推断或 fail-closed 说明。
- 两个 Admin 都直接写 GitHub，因此必须在各自最终 pre-save/save 边界调用同一浏览器 Tag Pipeline；只修改 Custom Admin 不足以覆盖现有入口。

### 1.3 现有测试与漂移风险

- `scripts/check-admin-save-flow.mjs` 当前只做源码护栏和 Markdown round-trip，没有执行标签算法。
- Python 现有测试主要覆盖发布契约消费、验证和结果写回，没有分享/讲道标签真实入口回归。
- Python 与浏览器各自硬编码书卷和 generic 集合是当前主要漂移来源。

## 2. 架构边界

### 2.1 单一权威规则源

新增 `assets/admin/tag-rules.json`，作为 Python 与浏览器共同读取的唯一规则数据源。该文件同时由 Astro 的 `publicDir=./assets` 发布为 `/admin/tag-rules.json`，不复制生成第二份配置。

规则源包含：

- `schema_version` 与规则版本；
- 最终数量上下界；
- 标签字符/长度约束参数；
- 完整标准书卷表及中英文别名；
- generic tag 集合；
- 标准人物、地点、事件和主题标签；
- 每个标准标签的中英文人工输入别名；
- 仅用于确定性标题/副标题推断的匹配词；
- 显式歧义词登记，例如 `以色列`，不得作为 `雅各` 的无条件别名。

JSON 只保存数据，不保存可执行代码，不接入网络或 AI。

### 2.2 运行时实现

- `scripts/tag_pipeline.py`：Python 独立模块。分享、讲道和契约消费最终都会在导入器写 frontmatter 前调用它。
- `assets/admin/tag-pipeline.js`：浏览器独立模块。Custom Admin 和 Decap Admin 在保存前加载同一 JSON 并调用它。
- 两端实现相同的版本校验、规范化、选择顺序、错误码和证据结构。
- `scripts/check_tag_pipeline_parity.mjs` 与固定 fixture 对 Python/JavaScript 结果做逐项一致性检查；规则版本不匹配、输出不同或错误码不同即失败。

## 3. 输入与输出合同

### 3.1 输入

统一输入对象：

```text
title: string
subtitle: string (optional)
scripture: string (optional)
category: string (context only)
author: string (context only; speaker maps to author)
manual_tags: string[]
```

规则：

- `category`、内容类型、`author/speaker` 只用于判定上下文标签集合是否无效，不自动生成标签。
- CLI `--tags` 与两个 Admin 的标签字段均转为 `manual_tags`。
- `metadata.tags` 缺失仍可通过 v1.1 契约验证；进入网站写入边界后由流水线推断，无法得到足够精准标签则 fail closed。

### 3.2 成功输出

```text
tags: string[]              # 2–6 个标准标签
evidence: object[]          # 每个标签的来源：scripture / rule / manual
rules_version: string
```

frontmatter 只写 `tags`，evidence 仅用于测试、dry-run 解释和错误诊断，不新增跨项目字段。

### 3.3 失败输出

流水线抛出/返回稳定错误码及中文明确消息：

- `RULES_INVALID`
- `TAG_EMPTY`
- `TAG_INVALID_CHARACTER`
- `TAG_TOO_LONG`
- `TAG_GENERIC`
- `TAG_AMBIGUOUS`
- `TAG_CONTEXT_ONLY`
- `TAG_COUNT_TOO_LOW`
- `TAG_COUNT_TOO_HIGH`

任何错误均 fail closed；不得回退到 `讲道`、`教会讲道`、分类或讲员姓名。

## 4. 三层处理数据流

```text
结构化 scripture
  -> 识别所有明确书卷并按经文出现顺序加入

title + subtitle + scripture
  -> 只执行字典中显式、确定、可解释的 inference terms
  -> 生成人物、地点、事件、主题标准标签

CLI/Admin 人工标签
  -> NFKC/空白规范化
  -> 精确别名映射
  -> 歧义词 Gate

三层合并
  -> 标准化后二次去重
  -> generic/context/字符/长度检查
  -> 2–6 Gate
  -> 成功输出或 fail closed
```

## 5. 规范化、别名与歧义

- 输入先执行 Unicode NFKC、首尾空白清理和连续空白折叠。
- 英文别名使用 Unicode case-insensitive 精确匹配；中文别名使用规范化后的精确匹配。
- 别名映射后再次去重；例如 `Jacob`、`雅各` 最终只保留 `雅各`。
- `Abram`、`Abraham`、`亚伯兰` 统一为 `亚伯拉罕`；`Noah`、`Cain`、`Paul` 等按字典统一。
- `以色列` 保持为歧义词：不得无条件映射成 `雅各`。作为人工标签出现时，除非未来增加显式语境规则，本阶段返回 `TAG_AMBIGUOUS`；标题明确写 `雅各` 时才生成 `雅各`。
- 书卷别名只在 `scripture` 字段用于识别书卷；普通人工标签 `雅各书` 可规范化为标准书卷名，但 `雅各` 不映射为书卷。

## 6. 生成优先级与溢出策略

最终顺序固定为：

1. scripture 中按出现顺序识别出的标准书卷；
2. 标题/副标题规则按字典声明顺序生成的人物、地点、事件、主题；
3. 人工标签按用户输入顺序追加。

所有层在加入时去重，但最后仍做一次标准化后二次去重。

- 少于 2 个：`TAG_COUNT_TOO_LOW`，提示补充精准人工标签。
- 多于 6 个：`TAG_COUNT_TOO_HIGH`，列出当前候选并要求人工减少；不得静默截断，因为截断会隐藏书卷或丢弃人工意图。
- 多段经文产生多个书卷时全部保留，除非总数超过 6；超过时同样 fail closed。

## 7. Generic 与上下文标签规则

初始 generic 集合严格覆盖任务合同：

```text
分享
灵命成长
讲道
教会讲道
文章
查经
生命反思
信仰
基督教
```

generic 检查在别名规范化后执行，任何 generic 标签都直接失败，不静默删除。

分类、内容类型或 author/speaker 不自动加入。若最终候选除书卷外只由 category/author 等上下文字段构成，则返回 `TAG_CONTEXT_ONLY`；由此防止用讲员姓名和分类凑足数量。

## 8. 各入口迁移方案

### 8.1 分享

- 删除 `import_shares.py` 的局部 `build_seo_tags()`。
- 写 frontmatter 前调用 Python Tag Pipeline。
- 保留 `--tags`，但允许规则已经生成足够精准标签时省略；不足时明确要求补充。
- 自动支持多书卷、别名、generic、duplicate、字符与数量 Gate。

### 8.2 讲道

- 删除 `讲道/教会讲道/讲员` 默认标签。
- 新增并保留 `--tags` 人工补充入口，由 `content_workflow.py` 转发。
- 从 scripture 和标题生成确定标签；不足即失败，要求 `--tags`。

### 8.3 发布契约

- 不修改 `website-publication-package/v1.1` Schema，不把 `metadata.tags` 改为跨项目必填。
- 有 tags 时继续转发；无 tags 时由网站内部 Tag Pipeline 推断并在网站写入边界 Gate。

### 8.4 Custom Admin

- 保留人工输入框。
- `formData/savePost` 在草稿保存和正式发布前都调用浏览器 Tag Pipeline。
- 成功时将标准化结果回填输入框；失败时显示稳定中文错误且不调用 GitHub PUT。

### 8.5 备用 Decap Admin

- preSave 异步加载相同 JSON，调用同一浏览器 Tag Pipeline，并写回标准化 tags。
- 失败时拒绝 preSave；不允许备用入口绕过 Gate。

## 9. 历史兼容与非迁移证明

- 不收紧 `src/content/config.ts` 的全局 schema；历史文章继续允许读取已有 tags 数量和写法。
- 不扫描后回写 `src/content/posts/`、`data/raw/` 或 `data/processed/`。
- 2–6、generic 和规则推断只在分享/讲道新生成及 Admin 新保存/新发布边界执行。
- 完成前用 Git diff/status 证明 `src/content/posts/`、`data/raw/`、`data/processed/` 和 GEO Knowledge Layer 实现无修改。

## 10. 测试与回归矩阵

### Python 单元与入口测试

- scripture 单书卷和多书卷；
- 分享规则生成、人工追加、generic、duplicate、alias、数量边界；
- 讲道不产生旧式默认标签、精准推断、不足 fail closed、多段经文；
- 非法字符、空值、规范化后二次重复、歧义词；
- 固定 fixture：雅各、亚伯拉罕、挪亚、人物/地点/主题分享、只有通用上下文。

### Admin 与跨运行时测试

- Custom Admin 和 Decap 都加载同一规则文件并在保存前调用流水线；
- 浏览器端 fixture 覆盖书卷、人工标签、generic、数量和错误消息；
- Python/JavaScript 对同一 fixture 的 tags、evidence source 和错误码完全一致；
- 规则 schema/version 不一致时失败。

### 回归

```text
python3 -m unittest discover -s scripts/tests
npm run check:admin-save
npm run check:knowledge
npm run build
git diff --check
```

Knowledge Layer 只运行既有检查，不修改其实现或历史文章以消除失败。

## 11. 明确未实现范围

- AI Tag Provider 或模型推断；
- 历史文章标签迁移、补正或批量重写；
- GEO Knowledge Layer 修改；
- RonnieAutomation、n8n、NAS、生产发布、部署或通知；
- 新跨项目接口版本；
- 未来 API/移动端/自动同步的具体实现。未来入口只登记为必须先调用 Tag Pipeline 的治理约束。

## 12. 实现后核对

实现与本设计一致：单一规则源、Python/浏览器双运行时、分享/讲道/Custom Admin/Decap 接入、契约兼容、fail-closed、历史读取兼容和跨运行时 fixture 均已落地。实现没有要求升级 `website-publication-package/v1.1`，没有修改全局 content schema，也没有修改历史文章或 Knowledge Layer。

独立复审仍应攻击：规则加载失败、Decap 异步 preSave、书卷别名重叠、别名规范化后 generic/author 绕过、超过 6 个候选时的静默截断风险，以及任何仍可直接写 tags 的入口。
