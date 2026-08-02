# Verification

## Status

`PASS_PENDING_INDEPENDENT_REVIEW`

以下只记录本建设会话实际执行的本地验证。没有执行真实文章发布、GitHub Admin 写入、部署、通知、NAS、commit 或 push。

## Focused Tag Pipeline

### Python 全套测试

```shell
python3 -m unittest discover -s scripts/tests
```

结果：PASS，21 tests。

覆盖：

- Python Tag Pipeline 单元测试；
- 分享入口人工标签、规则生成和 generic 拒绝；
- 讲道入口无旧式默认标签、实际 Markdown frontmatter、标签不足 fail closed；
- `content_workflow.py` 向 sermon 转发 `--tags`；
- 既有发布契约验证、消费和结果写回回归；
- Python/JavaScript 对同一 fixture 的 tags、evidence 和错误码一致性。

### 浏览器固定 fixture

```shell
npm run check:tags
```

结果：PASS，17/17。

覆盖：雅各、亚伯拉罕、挪亚、分享人物/地点/主题、多书卷、英文编号书卷、generic、duplicate、中文/英文 alias、Israel/以色列歧义、author alias context-only、空标签、非法字符、超长、数量上下界。

### Admin 保存检查

```shell
npm run check:admin-save
```

结果：PASS，Errors: 0。

检查 Custom Admin 与 Decap 都加载 `/admin/tag-pipeline.js`、调用同一规则文件、保存前运行 Pipeline；同时保留既有 Admin Markdown round-trip 与保存护栏。

## Syntax

```shell
python3 -m py_compile scripts/tag_pipeline.py scripts/import_shares.py scripts/import_sermons.py scripts/content_workflow.py scripts/consume_publication_package.py
node --check assets/admin/tag-pipeline.js
node --check assets/admin/editor.js
node --check assets/admin/decap.js
node --check scripts/check-admin-save-flow.mjs
node --check scripts/run_tag_pipeline_fixtures.mjs
```

结果：全部 PASS。

## Knowledge Layer

```shell
npm run check:knowledge
```

结果：PASS，Posts checked: 286，Errors: 0，Warnings: 0。

未修改 Knowledge Layer 实现或历史文章来消除失败。

## Full Build

```shell
npm run build
```

结果：PASS，Astro 静态构建成功。

构建产物规则文件一致性：

```text
tag-rules.json    source/dist SHA-256 = 052a827ed0e65b473d98981bdf49433f7cbceca856cae7e8071bebed3f9f757c
tag-pipeline.js   source/dist SHA-256 = 0a5bdde65f5ccf58b0a78edbbe12f98343e8e9a70d386b8316de885735654f3d
```

证明 Admin 构建产物携带与 Python 读取相同的权威 JSON 和已测试浏览器实现。

## Scope And Diff

```shell
git diff --check
git diff --name-only -- src/content/posts data src/lib/knowledge scripts/check-knowledge-layer.mjs
```

结果：PASS；第二条无输出。历史 posts、raw、processed 和 Knowledge Layer 均未修改。

## Deliberately Not Run

- 真实分享/讲道生产 dry-run 或 publish：本任务禁止真实内容发布，测试使用固定 fixture 和临时 TXT。
- 真实 Custom Admin/Decap GitHub PUT：会产生外部写入，未获授权。
- Cloudflare 部署、线上验收、邮件、NAS：均在禁止范围。
- commit/push：未获授权且任务要求停止等待独立复审。
