# RonnieCross Content Workflow Tag Pipeline P1 修复后独立安全与合同复审

## 1. 复审性质

本报告记录对 RonnieCross Content Workflow Tag Pipeline P1 最小定向修复结果的全新、完全独立、缺陷优先复审。

被审计正式状态：

`TARGETED_REMEDIATION_COMPLETE_PENDING_NEW_INDEPENDENT_REVIEW`

本会话不是修复续跑、建设续跑、AI Tag Provider 建设、历史标签迁移或生产发布会话。

复审期间未修改被审计生产实现、测试、Tag Dictionary、历史文章、历史 tags、Knowledge Layer、publication contract 或既有建设/修复产物；未 reset、checkout、clean、stash、commit、push、部署、发布或操作 NAS。

## 2. 审计范围

直接审查并验证：

- `assets/admin/tag-rules.json` 的书卷 canonical 与 aliases；
- `scripts/tag_pipeline.py` 的 Python alias map、canonical 化与二次去重；
- `assets/admin/tag-pipeline.js` 的 Browser alias map、canonical 化与二次去重；
- `scripts/tests/fixtures/tag_pipeline_cases.json` 新增 alias fixtures；
- Python/Browser parity、Admin Save Flow、Knowledge Layer 与 Astro build；
- 修复 diff 和受保护范围。

重点边界：

- `1 John`；
- `First John`；
- `约一`；
- `John`；
- `Genesis`；
- `创世记`；
- 自动 scripture 标签与人工 alias 重复输入；
- 多卷书、多语言、简称组合；
- Generic、Validator、数量与 fail-closed 回归。

## 3. 实现审查结论

### 3.1 已正确修复的部分

Python 与 Browser 的 alias map 现均对书卷使用：

```text
[canonical, ...aliases]
```

因此已确认：

- `1 John` → `约翰一书`；
- `约一` → `约翰一书`；
- `John` → `约翰福音`，未误映射为 `约翰一书`；
- `Genesis` → `创世记`；
- `创世记` 保持 `创世记`；
- scripture 自动书卷与人工 alias 映射到同一 canonical 后只输出一次；
- scripture evidence 保持优先。

Python 与 Browser 的修复代码结构一致，并读取同一 `assets/admin/tag-rules.json`。

### 3.2 新发现的缺口

权威规则源中 `约翰一书` 当前为：

```json
{"canonical": "约翰一书", "aliases": ["1 John", "1 Jn", "约一"]}
```

没有登记本次复审合同明确要求统一处理的 `First John`。

因此两端虽然 alias 算法已经一致修复，但会一致地把 `First John` 当作自由标签原样接受，而不是规范化为 `约翰一书`。

## 4. 独立验证结果

### 4.1 Python 全套测试

```shell
python3 -m unittest discover -s scripts/tests
```

结果：PASS，21 tests。

### 4.2 Browser fixtures 与 parity

```shell
npm run check:tags
```

结果：PASS，21/21 fixtures。

现有 fixtures 覆盖 `1 John`、`John`、`约一`、`Genesis + scripture`，但未覆盖 `First John`。

### 4.3 Admin Save Flow

```shell
npm run check:admin-save
```

结果：PASS，Errors: 0。

### 4.4 Knowledge Layer

```shell
npm run check:knowledge
```

结果：PASS，Posts checked: 286，Errors: 0，Warnings: 0。

### 4.5 Astro 整站构建

```shell
npm run build
```

结果：PASS，328 pages built。

### 4.6 语法检查

```shell
python3 -m py_compile scripts/tag_pipeline.py scripts/import_shares.py scripts/import_sermons.py scripts/content_workflow.py scripts/consume_publication_package.py
node --check assets/admin/tag-pipeline.js
```

结果：PASS。

### 4.7 Diff 检查

```shell
git diff --check
```

结果：PASS。

修复 diff 仅涉及 Python/Browser alias map、4 个 fixtures 和状态/任务文档；未发现 `src/content/posts/`、`data/raw/`、`data/processed/`、Knowledge Layer、publication contract 或其它受保护范围修改。

### 4.8 Alias 独立攻击性探针

Python 结果：

```text
1 John      -> ['信心', '约翰一书', '恩典']
First John  -> ['信心', 'First John', '恩典']
约一         -> ['信心', '约翰一书', '恩典']
John        -> ['信心', '约翰福音', '恩典']
Genesis     -> ['信心', '创世记', '恩典']
创世记       -> ['信心', '创世记', '恩典']
```

Browser 对 `First John` 的实际结果同样为：

```text
['信心', 'First John', '恩典']
```

多卷书、多语言和重复组合：

```text
scripture = 创世记 1:1；约翰一书 1:1
manual_tags = Genesis, 1 John, Grace
```

结果：

```text
['创世记', '约翰一书', '信心', '恩典']
```

对应 evidence：两个书卷均保留 `scripture` 来源，没有重复人工书卷标签。

## 5. 新发现的问题

### [P1] 在权威 Tag Dictionary 中登记 `First John` 别名 — `assets/admin/tag-rules.json:84`

本次复审合同明确要求 `1 John`、`First John`、`约一` 均统一为 `约翰一书`。当前修复只修正了 alias map 的注册算法，但权威字典没有包含 `First John`。Python 与 Browser 因共享同一规则源，会一致地把该输入作为自由标签通过 Validator 并写入 frontmatter。

这意味着：

- Python 与 Browser 一致，但未满足本次明确 alias 合同；
- Tag Dictionary 仍不完整；
- parity tests 无法发现共享规则源中的同一遗漏；
- Custom Admin、Decap、CLI 与 Publication Package 路径都会受到影响；
- 现有 21 个 fixtures 没有覆盖本次要求的 `First John` 边界。

建议仅在新的最小定向修复会话中：

1. 将 `First John` 加入 `约翰一书` 的 aliases；
2. 同时核对 `Second John`、`Third John` 等同类英文序数形式是否应按一致策略登记；
3. 增加 Python/Browser fixture，明确 `First John` → `约翰一书`；
4. 增加与 scripture 自动 `约翰一书` 的二次去重和 evidence 优先测试。

## 6. 其它回归结论

- `John` 仍准确映射为 `约翰福音`，未被 `1 John` 覆盖。
- `1 John`、`约一`、`Genesis` 和 canonical 输入均工作正常。
- 自动 scripture 与人工别名二次去重正常。
- 多卷书与多语言组合顺序、canonical 和 evidence 正常。
- Generic Tag、Validator、数量上下界、歧义与 fail-closed 的既有测试未发生回归。
- 未发现历史文章、历史 tags、Knowledge Layer、publication contract 或其它受保护范围被修改。

## 7. 最终正式裁决

`FAIL`

理由：P1 的 alias 注册算法缺陷已经修复，但本次复审明确要求的 `First John` 仍未进入权威 Tag Dictionary，Python 与 Browser 会一致地输出非 canonical 自由标签。该问题影响所有统一写入入口，因此不能裁决 PASS。

## 8. 后续建议

开启新的、独立授权的最小定向修复会话，只补齐权威字典中的英文序数书卷别名及对应跨运行时 fixture。修复后再由新的独立会话复审；本会话不进入修复阶段。
