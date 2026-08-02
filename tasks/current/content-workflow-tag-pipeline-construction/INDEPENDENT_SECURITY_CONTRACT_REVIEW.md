# RonnieCross Content Workflow Tag Pipeline 独立安全与合同复审

## 1. 复审性质

本报告记录对 RonnieCross Content Workflow Tag Pipeline 建设结果的全新、完全独立、缺陷优先复审。

被审计正式状态：

`CONSTRUCTION_COMPLETE_PENDING_INDEPENDENT_REVIEW`

本会话不是建设续跑、修复、历史标签迁移、AI Tag Provider 建设或生产发布会话。

复审期间未修改被审计生产实现、测试、Tag Dictionary、历史文章、历史 tags、Knowledge Layer、publication contract 或建设产物；未 commit、未 push、未部署、未发布、未操作 NAS。

## 2. 审计范围

直接审查了以下范围：

- 单一权威规则源：`assets/admin/tag-rules.json`；
- Python Pipeline：`scripts/tag_pipeline.py`；
- Browser Pipeline：`assets/admin/tag-pipeline.js`；
- 分享入口：`scripts/import_shares.py`；
- 讲道入口：`scripts/import_sermons.py`；
- 统一命令入口：`scripts/content_workflow.py`；
- Publication Package 消费入口：`scripts/consume_publication_package.py`；
- Custom Admin 保存/发布路径：`assets/admin/editor.js`；
- Decap preSave 路径：`assets/admin/decap.js`；
- 相关 HTML/config、fixtures、parity tests、Admin Save Flow 检查与长期文档；
- Git 工作树与受保护范围。

重点复核：

1. 所有现有发布入口是否经过统一 Tag Pipeline；
2. 是否仍存在直接拼装或写入 tags 的旁路；
3. Python 与浏览器是否读取同一权威规则源；
4. Dictionary、Alias、Generic、歧义和字符/数量规则是否一致；
5. 规则加载和标签不足时是否 fail closed；
6. 分享、讲道、Admin、Publication Package 是否符合统一合同；
7. 是否存在规则漂移、隐藏默认值或旧式 fallback；
8. 是否修改历史文章、Knowledge Layer、publication contract 或其它范围外实现；
9. 验证是否可独立重跑。

## 3. 独立验证结果

### 3.1 Python 全套测试

```shell
python3 -m unittest discover -s scripts/tests
```

结果：PASS，21 tests。

### 3.2 浏览器 Tag Pipeline fixtures

```shell
npm run check:tags
```

结果：PASS，17/17。

### 3.3 Admin Save Flow

```shell
npm run check:admin-save
```

结果：PASS，Errors: 0。

### 3.4 Knowledge Layer

```shell
npm run check:knowledge
```

结果：PASS，Posts checked: 286，Errors: 0，Warnings: 0。

### 3.5 Astro 整站构建

```shell
npm run build
```

结果：PASS，328 pages built。

### 3.6 工作树

复审前及构建后工作树均无生产实现改动。新增本报告前，`show_changes` 返回无变更。

### 3.7 独立攻击性探针

执行：

```shell
python3 -c "from scripts.tag_pipeline import build_tags; print(build_tags(title='Faith', scripture='', manual_tags=['1 John','Grace']).tags)"
```

实际输出：

```text
['信心', '1 John', '恩典']
```

预期合同行为：`1 John` 应依据书卷英文别名规范化为权威标准书卷标签，而不是作为未规范化自由标签直接写入。

## 4. 发现的问题

### [P1] 将书卷 aliases 纳入人工标签的统一 alias map — `scripts/tag_pipeline.py:107-116` / `assets/admin/tag-pipeline.js:79-90`

Python 与浏览器的规则校验都把 `books[*].aliases` 声明为全局唯一且有效的 Tag Dictionary alias，但实际构造 alias map 时，书卷只登记 canonical，完全忽略 `books[*].aliases`。因此 `1 John`、`John`、`Genesis` 等书卷英文别名作为 CLI/Admin/Publication Package 人工标签输入时不会映射为标准中文书卷标签，而会作为任意自由标签通过字符与数量 Gate 并写入 frontmatter。

这违反以下正式合同：

- Tag Dictionary 必须支持书卷名中英文别名；
- 人工标签必须经过同一别名映射；
- Python 与 Admin 应输出标准标签；
- 设计明确规定普通人工书卷标签可规范化为标准书卷名。

该缺陷同时存在于 Python 与浏览器实现，所以现有 parity tests 会得到一致的错误结果，不能证明合同正确。当前 17 个 fixture 未覆盖“书卷 alias 作为 manual_tags 输入”的场景。

影响入口包括：

- 分享 CLI `--tags`；
- 讲道 CLI `--tags`；
- `content_workflow.py` 转发路径；
- Publication Package 的 `metadata.tags`；
- Custom Admin 保存与发布；
- Decap preSave。

建议修复时让两端 alias map 对书卷与普通标签采用相同的 `[canonical, ...aliases]` 登记方式，并增加至少以下跨运行时 fixture：

- `1 John` → `约翰一书`；
- `John` → `约翰福音`；
- 一个中文书卷别名；
- 书卷 alias 与 scripture 自动生成同一 canonical 后的二次去重。

## 5. 其它复审结论

- 分享和讲道写入 frontmatter 前均调用 Python Tag Pipeline；未发现讲道恢复 `讲道`、`教会讲道` 或讲员姓名默认标签。
- Custom Admin 的草稿保存与正式发布在生成保存数据前调用 Browser Pipeline；失败会在 GitHub PUT 前中止。
- Decap preSave 等待规则加载并调用 Browser Pipeline；规则加载或验证失败会拒绝 preSave。
- Python 与 Browser 直接读取同一个 `assets/admin/tag-rules.json`；未发现第二份生产规则配置。
- Generic、歧义、数量上下界和旧式 fallback 的既有测试均可独立重跑。
- 未发现 `src/content/posts/`、`data/raw/`、`data/processed/`、`src/lib/knowledge/`、content schema、publication contract、RonnieAutomation、n8n 或 NAS 的范围外修改。
- 现有验证全部通过，但不能覆盖上述共享实现缺陷，因此不能据此判定合同通过。

## 6. 最终正式裁决

`FAIL`

理由：统一 Tag Dictionary 的书卷 alias 合同未在人工标签路径真实生效，且该缺陷横跨所有 Python 与 Admin 写入入口。Python/浏览器 parity 只能证明两端一致，不能证明两端正确；当前两端在该路径上一致地违反权威合同。

## 7. 后续建议

开启新的、独立授权的最小定向修复会话，仅修复 Python/Browser alias map 对 `books[*].aliases` 的遗漏，并补齐跨运行时与入口回归测试。修复后必须再由新的独立会话复审；本会话不进入修复阶段。
