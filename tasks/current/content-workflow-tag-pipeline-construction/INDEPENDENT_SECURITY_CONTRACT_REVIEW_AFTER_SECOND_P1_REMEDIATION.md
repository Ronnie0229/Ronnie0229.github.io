# RonnieCross Content Workflow Tag Pipeline 第二次 P1 修复后独立安全与合同复审

## 1. 复审性质与被审计状态

本报告记录对 RonnieCross Content Workflow Tag Pipeline 第二次 P1 最小定向修复结果的全新、完全独立、缺陷优先安全与合同复审。

被审计正式状态：

`SECOND_TARGETED_REMEDIATION_COMPLETE_PENDING_INDEPENDENT_REVIEW`

本会话不是第二次修复续跑、建设续跑、第三次修复、AI Tag Provider 建设、历史标签迁移或生产发布会话。

复审期间未修改被审计生产实现、测试、Tag Dictionary、历史文章、历史 tags、Knowledge Layer、publication contract 或两份历史独立审计报告；未 reset、checkout、clean、stash、commit、push、部署、发布或操作 NAS。除本报告外未新增或修改生产文件。

历史正式裁决保持不变：

- 首次独立安全与合同复审：`FAIL`；
- 第一次 P1 修复后独立复审：`FAIL`。

## 2. 审计范围

直接审查了：

- `assets/admin/tag-rules.json`；
- `scripts/tag_pipeline.py`；
- `assets/admin/tag-pipeline.js`；
- `scripts/tests/fixtures/tag_pipeline_cases.json`；
- `scripts/tests/test_tag_pipeline.py`；
- `scripts/run_tag_pipeline_fixtures.mjs`；
- 分享、讲道、`content_workflow.py`、Publication Package 消费入口；
- Custom Admin 草稿保存/正式发布与 Decap preSave；
- 当前完整工作树 diff、构建产物和受保护范围。

重点独立检查：

1. Python 与 Browser alias 行为是否一致且正确；
2. canonical 与 aliases 是否完整、唯一、无覆盖；
3. 规则版本 `2026-08-02.2` 是否统一；
4. First/Second/Third John、数字英文名、英文缩写和中文简称映射；
5. John 与约翰书信边界；
6. 17 卷编号书卷英文序数全称逐项映射；
7. scripture/manual canonical 二次去重与 scripture evidence 优先；
8. Unicode NFKC、大小写、连续空白与排序；
9. 2–6、Generic、歧义、字符、长度和 fail-closed 回归；
10. Admin、分享、讲道、Publication Package 统一入口及受保护范围。

## 3. 实现与字典审查

### 3.1 单一权威规则源与版本

`assets/admin/tag-rules.json` 的：

- `schema_version` 为 `1.0`；
- `rules_version` 为 `2026-08-02.2`；
- Python 与 Browser 均直接读取/接收该同一规则结构；
- 构建后的 `dist/admin/tag-rules.json` 与 source SHA-256 一致；
- 构建后的 `dist/admin/tag-pipeline.js` 与 source SHA-256 一致。

### 3.2 Alias 注册与冲突防护

Python 与 Browser 均对每个书卷和普通标签登记：

```text
[canonical, ...aliases]
```

两端规则校验均对规范化后的 lookup key 执行全局唯一性检查。当前字典通过校验，没有发现：

- canonical 重复；
- alias 重复；
- 大小写冲突；
- 中文简称冲突；
- 后写覆盖；
- 书卷 alias 与普通 tag alias 冲突。

### 3.3 John 边界

独立探针确认：

- `John` → `约翰福音`；
- `First John` / `1 John` / `1 Jn` / `约一` → `约翰一书`；
- `Second John` / `2 John` / `2 Jn` / `约二` → `约翰二书`；
- `Third John` / `3 John` / `3 Jn` / `约三` → `约翰三书`。

`John` 未被任何书信别名覆盖或误映射。

## 4. 17 卷编号书卷逐项核对

预期值由审计探针硬编码，不从被测字典动态生成。逐项结果如下：

| 英文序数全称 alias | 预期 canonical | 结果 |
|---|---|---|
| First Samuel | 撒母耳记上 | PASS |
| Second Samuel | 撒母耳记下 | PASS |
| First Kings | 列王纪上 | PASS |
| Second Kings | 列王纪下 | PASS |
| First Chronicles | 历代志上 | PASS |
| Second Chronicles | 历代志下 | PASS |
| First Corinthians | 哥林多前书 | PASS |
| Second Corinthians | 哥林多后书 | PASS |
| First Thessalonians | 帖撒罗尼迦前书 | PASS |
| Second Thessalonians | 帖撒罗尼迦后书 | PASS |
| First Timothy | 提摩太前书 | PASS |
| Second Timothy | 提摩太后书 | PASS |
| First Peter | 彼得前书 | PASS |
| Second Peter | 彼得后书 | PASS |
| First John | 约翰一书 | PASS |
| Second John | 约翰二书 | PASS |
| Third John | 约翰三书 | PASS |

汇总：`17/17 PASS`，没有遗漏或错误目标。

现有 fixture 只用 `First Peter` 代表其它编号书卷政策，因此 fixture 本身没有逐项覆盖全部 17 卷；本次通过独立硬编码探针补足了审计验证。该缺口属于测试覆盖剩余风险，不构成当前实现缺陷。

## 5. Alias 攻击性探针

### 5.1 单项输入

Python 与 Browser 对以下输入输出完全一致：

- First John；
- 1 John；
- 1 Jn；
- 约一；
- John；
- Second John；
- 2 John；
- 2 Jn；
- 约二；
- Third John；
- 3 John；
- 3 Jn；
- 约三；
- Genesis；
- 创世记。

### 5.2 Unicode、大小写和空白

以下变体均规范化为 `约翰一书`：

- `first john`；
- `FIRST   JOHN`；
- `１ John`；
- `First　John`。

这验证了 NFKC、英文大小写、连续 ASCII 空白和全角空格在两端的一致行为。

### 5.3 组合与顺序

独立验证通过：

1. scripture `约翰一书 1:1` + manual `First John`；
2. scripture `约翰二书 1:1` + manual `Second John`；
3. scripture `约翰三书 1:1` + manual `Third John`；
4. scripture 同时含约翰福音、约翰一书、约翰二书、约翰三书；
5. manual 同时含 John、First John、Second John、Third John；
6. scripture 自动书卷与 canonical、英文序数全称、数字英文名、英文缩写、中文简称重复混合；
7. 多卷、多语言和简称组合。

顺序稳定遵循：scripture → rule → manual。规范化后重复书卷只保留一次。

### 5.4 数量 fail closed

超过 6 个最终标签的探针在 Python 与 Browser 均返回：

`TAG_COUNT_TOO_HIGH`

没有静默截断。

## 6. Scripture / Manual 二次去重与 Evidence

确认以下三组均只输出一个 canonical 书卷标签：

- scripture `约翰一书 1:1` + manual `First John`；
- scripture `约翰二书 1:1` + manual `Second John`；
- scripture `约翰三书 1:1` + manual `Third John`。

对应 evidence 均保留：

```text
书卷标签 / scripture
信心 / rule
```

人工重复 alias 不产生第二个 manual evidence。多卷混合输入同样保持 scripture evidence 优先和确定顺序。

## 7. Fixtures 与检查脚本审查

现有 27 个 fixtures 已真实覆盖：

- First John；
- Second John；
- Third John；
- scripture 与人工 alias 交叉去重；
- scripture evidence 优先；
- John 与约翰书信边界；
- First Peter 作为其它编号书卷政策代表。

`test_tag_pipeline.py` 与 Browser runner 均对可选 expected evidence 执行精确比较。

现有 fixture 未逐项覆盖全部 17 个英文序数全称 alias。任务文档中的“17/17 完整性探针”没有作为持久测试脚本出现在 diff 中，因此本次没有依赖其自证结论，而是使用硬编码预期映射独立验证。建议后续在独立授权下把该硬编码矩阵固化为回归测试，但当前实现本身已逐项正确。

## 8. 独立验证命令与真实结果

```shell
python3 -m unittest discover -s scripts/tests
```

结果：PASS，21 tests。

```shell
npm run check:tags
```

结果：PASS，27/27 browser fixtures。

```shell
npm run check:admin-save
```

结果：PASS，Errors: 0。

```shell
npm run check:knowledge
```

结果：PASS，Posts checked: 286，Errors: 0，Warnings: 0。

```shell
npm run build
```

结果：PASS，328 pages built。

```shell
python3 -m py_compile scripts/tag_pipeline.py scripts/import_shares.py scripts/import_sermons.py scripts/content_workflow.py scripts/consume_publication_package.py
```

结果：PASS。

```shell
node --check assets/admin/tag-pipeline.js
node --check assets/admin/editor.js
node --check assets/admin/decap.js
node --check scripts/check-admin-save-flow.mjs
node --check scripts/run_tag_pipeline_fixtures.mjs
```

结果：全部 PASS。

```shell
git diff --check
```

结果：PASS。

Source/dist SHA-256：

```text
tag-rules.json  85d4862acd63af34a11e3d2b5511a7f3d6659e826ec60bd5031f81e07d7b23f7
tag-pipeline.js 580c7090e128b30d12caad74cfaf0ab8e75f96363f5af67f426abdefdc0823fb
```

source 与 dist 分别一致。

## 9. Generic、Validator、Admin、Knowledge 与入口回归

- Generic Tag 拒绝、歧义拒绝、空标签、非法字符、长度和 2–6 Gate 的既有测试全部通过；
- 没有放宽 Validator；
- 没有允许自由书卷 alias 绕过 canonical 规范化；
- Custom Admin 草稿保存和正式发布仍在写入前调用 Browser Tag Pipeline；
- Decap preSave 仍调用同一 Browser Tag Pipeline；
- 分享、讲道、`content_workflow.py` 和 Publication Package 消费路径仍使用统一 Python Tag Pipeline；
- 未发现恢复 `讲道`、`教会讲道`、讲员姓名、category 或其它旧式默认标签；
- Knowledge Layer 检查保持 0 errors / 0 warnings；
- Astro build 成功。

## 10. 受保护范围与 Diff

当前生产 diff 仅包含：

- Python/Browser alias map 的第一次 P1 修复；
- `tag-rules.json` 的第二次 P1 英文序数全称补齐和版本更新；
- fixtures/runner/evidence 断言；
- 状态与任务文档。

未发现修改：

- `src/content/posts/`；
- `data/raw/`；
- `data/processed/`；
- `src/lib/knowledge/`；
- content schema；
- sitemap、RSS、canonical、相关文章逻辑；
- publication contract；
- RonnieAutomation、n8n 或 NAS；
- 两份历史独立审计报告内容。

## 11. 新发现的问题

### P0

无。

### P1

无。

### P2

无。

### P3

无实现缺陷。

测试覆盖剩余风险：持久 fixtures 没有逐项覆盖全部 17 个编号书卷英文序数全称，仅以 First Peter 代表同类政策。本次已通过独立硬编码矩阵逐项验证 17/17 正确；建议未来固化该矩阵，防止后续字典编辑回归。

## 12. 最终正式裁决

`PASS`

理由：第二次修复的 alias 合同真实生效；17 卷编号书卷英文序数全称逐项映射正确；无 alias 冲突、覆盖或错误目标；Python 与 Browser 在 fixtures 外的大小写、空白、NFKC、组合、顺序和 overflow 探针中一致且正确；scripture/manual 二次去重及 scripture evidence 优先正确；Generic、Validator、Admin、Knowledge、构建和统一写入入口无回归；规定验证全部通过；受保护范围未被修改；不存在影响统一写入入口的 P0、P1 或 P2 缺陷。

## 13. 后续建议

在独立授权的后续维护中，将本报告使用的 17 卷硬编码 expected alias→canonical 矩阵固化为 Python/Browser 持久回归测试。该建议不改变本次 `PASS` 裁决，也不授权本会话继续修改实现、commit、push、AI 标签、历史迁移或生产发布。
