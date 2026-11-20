# Stage C Website Consumer Remediation 01 — Independent Re-Audit Report

- Task: `20261115-unified-share-sermon-publication-governance`
- Role: `INDEPENDENT_AUDITOR`
- Audit mode: independent read-only re-audit
- Audit date: 2026-11-17
- Website construction workspace: `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-unified-publication-stage-a-20261116`
- Branch: `task/unified-share-sermon-publication-stage-a-20261116`
- HEAD: `09ce7eb588a21745d0286d3eec6a890c16a26aea`
- Frozen baseline: exact match
- **Verdict: FAIL**
- Stage C: `REMEDIATED_WITH_RESIDUAL_BLOCKERS`
- Stage D: **BLOCKED**
- Stage F: **DISABLED**

## 1. Executive conclusion

本轮整改已经修复了首轮 FAIL 中最直接的 package bypass：直接调用 Share importer 时，不提供 publication package 已不能进入 presentation import；底层 importer 也会独立执行 v1.3 package validator，且 Stage F 前拒绝非 dry-run。

但本轮仍未满足合同规定的 source selector 精确身份绑定：

1. **F-01（P1）部分修复，仍 FAIL：** importer 只比较解析后文件的 basename，而不是 package-bound source 的规范相对路径。直接 CLI 可以用指向 raw 子目录文件的路径或仓库内 symlink alias 通过校验。临时目录实测 symlink alias 被接受。
2. **F-02（P2）部分修复，仍 FAIL：** workflow 同样只比较 basename。带有不同目录的 caller source selector（例如 `sub/sample.txt`）会通过身份检查，并继续调用 renderer 和 importer；它没有按合同要求在 renderer/importer 前拒绝 source mismatch。

因此，原首轮 F-01 的“无 package 直接导入”漏洞已关闭，但新的/残留 source identity bypass 仍处于同一 importer 安全边界中；F-02 的 metadata mismatch 防护已明显补齐，但 source selector 的 exact-match 条件仍未成立。不能给 Stage C PASS，也不能启动 Stage D/E/F。

## 2. Workspace isolation and chronology

### Website construction worktree

- Exact root、branch、HEAD 均与复审请求一致。
- 审核前状态：6 个 tracked modified paths、27 个 untracked paths，0 staged。
- 审核报告是本轮唯一新增的 workspace 文件；实施代码、测试、schema、计划、状态文档和历史报告均未修改。
- 原始 Stage C 首轮 FAIL 报告 SHA-256 重新计算结果：

`967cc403d54d27efedc02dc8b50870aedcb5ec1a597178ff4fd77ac2e41e8d47`

与复审请求完全一致，原报告未变。

### Canonical Website / Sermon Owner

- Canonical Website `/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目`：`main...origin/main`，HEAD 为 `09ce7eb588a21745d0286d3eec6a890c16a26aea`，clean；show_changes 为 0 changed files。
- Canonical Sermon `/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理`：仍为 `master...origin/master [ahead 2]`，既有 modified/untracked dirty lineage 保持；本轮只读打开和检查，未写入。
- Sermon construction worktree：branch `task/unified-share-sermon-publication-stage-a-20261116`，HEAD `812ace500102bac54cb54cb0fa2249341118a3da`；既有 Stage A/B dirty lineage 未修改。
- Stage B accepted Re-Audit 01 report SHA-256 复算为 `9a4616989cd8cbdd390158dca14b40cd27f6ccff885a4b0c164604c0bbaed0ea`，与请求完全一致。
- Stage B Remediation 01 implementation report SHA-256：`3a0842e98471407849f3603b57240b850e72d8f7dec98db9c1af09e53e49cd55`。
- Website 与 Sermon Owner 的两份 schema、共享 invariant helper 均逐字节一致：
  - `content-presentation-v1.schema.json`: `359b443c5a407c490027084651dc201aa1f90cb10c4536499d3b949919639ad5`
  - `website-publication-package-v1.3.schema.json`: `6c3b07bb67c4c223d5da9480a6b94a6a1af37c1aaafce6f3448553132b07670e`
  - `publication_contract_invariants.py`: `b6e74359e5dc64411ad7870e22a6e04bddf577f63ab070ee718c9b0b5b6734e0`

历史 Stage A/B chronology、Stage B accepted PASS 与 Stage C 首轮 FAIL 均保留，未被覆盖或重新分类。

## 3. F-01 — direct importer entrypoint security

**Disposition: PARTIAL / FAIL — 原始无 package bypass 已修复，source identity bypass 仍存在。**

### 已确认修复

`scripts/import_shares.py`：

- CLI 已增加 `--publication-package` 与 `--content-root`（约 242–245 行）。
- presentation import 缺少 package 或 content root 时，在输出目录创建前拒绝（442–445 行、529–540 行）。
- importer 自己调用 `validate_publication_package_v13.py` 并要求 validator PASS（447–462 行），不依赖 workflow 先运行。
- package 必须是 v1.3 Share（447–449 行）。
- presentation artifact 必须与 package binding 指向同一解析路径（480–485 行）；validator 同时验证 artifact SHA。
- prepublish author/date/category/contentType 与 package metadata 对齐；title/description/scripture/tags/author/date/slug 的显式 caller 值与 bound 值比较（473–517 行）。
- Stage F 前 direct non-dry-run 在输出目录创建前拒绝（515–516 行；输出目录创建在 541–544 行之后）。
- valid package-bound direct dry-run 实际运行成功，且不创建 processed/posts/report 输出。
- legacy Share path（无 `--presentation-file`）测试仍通过。

### 残留 blocker：source selector 只按 basename 绑定

- `resolve_source_file()`（250–266 行）先对 caller path 执行 `resolve()`，再仅检查解析结果是否位于 `SOURCE_DIR` 内。它允许 raw 目录内部的嵌套路径和指向目录内部文件的 symlink alias。
- `validate_v13_import_identity()`（486–489 行）构造的 expected source 是 `data/raw/分享/{source.name}`，比较的也是解析后 `source.name`，没有要求 caller 输入本身解析为 package 指定的根目录文件，也没有拒绝 symlink alias。

### 独立临时目录攻击验证

使用合法 v1.3 Share package，其 SHA-bound prepublish source 为：

`data/raw/分享/sample.txt`

在临时 raw 目录建立：

`raw/sub/sample.txt`

以及：

`raw/alias.txt -> raw/sub/sample.txt`

直接调用真实 `import_shares.main()`，传入 `--source-file alias.txt`、合法 package、合法 artifact、content root 和 `--dry-run`。结果：

- importer 接受该 symlink alias；
- 实际解析目标为 `raw/sub/sample.txt`；
- 返回 `Imported shares: 1`；
- processed/posts/report 目录均未创建（dry-run）。

另一个直接调用探针以 `sub/sample.txt` 为 source selector，也被真实 importer 接受并完成 dry-run。

这证明直接 importer 仍可让一个与 package 声明的根路径不同的 raw 文件通过 source identity gate。虽然当前 v1.3 非 dry-run 仍被 Stage F gate 禁止，且正文 body 仍取自绑定的 presentation artifact，但 source provenance/filename-based checks 已可基于错误 raw 文件继续执行。该路径必须在 Stage F 前收紧。

**F-01 结论：** 无 package 直接导入的原始漏洞已修复；但复审合同明确要求“valid package + different source selector must fail closed”，当前实现未满足，故 F-01 不能关闭。

## 4. F-02 — underlying workflow identity binding

**Disposition: PARTIAL / FAIL — metadata binding 已补齐，source selector exact-match 仍未补齐。**

### 已确认修复

`scripts/content_workflow.py`：

- workflow 独立重验 package（192–220 行）。
- prepublish author/date/category/contentType 与 package metadata 对齐（226–240 行）。
- title、description、scripture、tags、author、publish_date、slug 的 caller 显式值逐项比较（241–255 行）。
- 未提供的值从 bound prepublish/package 派生（258–265 行）。
- package path 与 content root 被传给底层 importer（316–320 行）。
- v1.3 non-dry-run 仍被禁用（266–267 行）。

8 类 metadata/source mismatch 的既有测试中，title、description、scripture、tags、author、publish date、slug 以及不同 basename 的 source 均在 renderer/importer 前失败。

### 残留 blocker：source selector 只比较 basename

- `content_workflow.py:232–235` 使用 `Path(source_file).name` 构造 expected path，只比较 basename，没有验证 caller source 的完整规范路径。
- `content_workflow.py:258` 随后将 source_file 改写为 bound source 的 basename。
- renderer 在 300–315 行调用，故不匹配的 caller source 仍可先进入 renderer。

### 独立实际 workflow 调用验证

使用合法 Share package，其 bound source 为 `data/raw/分享/sample.txt`；真实调用 `content_workflow.publish()`，传入 caller source `sub/sample.txt`，其余 metadata 均为正确值，并拦截 subprocess 以记录边界调用。结果：

1. package validator 被调用；
2. renderer 被调用；
3. importer 被调用；
4. importer command 最终收到 `sample.txt`（workflow 已把 caller path 归一化为 basename）。

这没有证明错误文件最终写入——实际传给 importer 的 basename 又回到了 package 声明的文件名。但它明确证明 caller 提供的不同 source selector 没有按合同要求在 renderer/importer 前 fail closed。F-02 的 source identity proposition 因此仍不通过。

**F-02 结论：** metadata mismatch 防护有实质进展；source selector 必须比较完整规范路径/固定根目录下的 exact relative path，并在 renderer 前拒绝 alias、nested path、traversal 与 symlink alias。

## 5. Package identity / profile / compatibility

| Proposition | Result | Evidence |
|---|---|---|
| Package version/content_type、schema validation、bound file existence/SHA | PASS（代码与现有 validator tests） | importer 独立调用 v1.3 validator；validator 负向测试覆盖 missing/out-of-root refs、SHA drift、schema/profile 等 |
| Presentation artifact exact path + SHA | PASS | importer 比较解析路径；package validator 校验 artifact SHA |
| Prepublish body 与 bound artifact 一致 | PASS（validator） | validator 334–352 行 |
| Importer 不对冻结 presentation body 做 legacy normalization/formatting | PASS（代码） | 560–566 行读取 artifact；606 行 presentation path 直接使用 body |
| Share/Sermon profile、category/archive/fidelity semantics | PASS（schema/validator） | Owner schema mirror + v1.3 validator |
| Stage F 前 v1.3 non-dry-run disabled | PASS | workflow 266–267 行；importer 515–516 行；相关 consumer tests |
| v1.0/v1.1/v1.2 legacy compatibility | PASS | legacy suite 25/25 |
| Source traversal / symlink alias fail-closed | **FAIL** | raw 目录内 nested source 和 symlink alias 被 direct importer 接受 |

注意：本轮对 package-bound file references 的路径保护与 raw Share source selector 的路径保护作了区分。validator 对 package 内文件引用的 root containment / symlink escape 检查正常；本轮发现的是 importer 对 raw Share source 的 basename-only 检查。

## 6. Regression and test quality

所有指定命令均退出码 0：

| Check | Exact result | Exit |
|---|---:|---:|
| Full Python suite | 258/258 PASS | 0 |
| Stage C five-module focused command | 57 test executions PASS | 0 |
| Focused suite distinct tests after overlap accounting | 40 unique tests | 0 |
| Legacy compatibility suite | 25/25 PASS | 0 |
| Share Tag Pipeline | 27/27 PASS | 0 |
| Python compile (5 modules) | PASS | 0 |
| Node syntax check | PASS | 0 |
| `git diff --check` | PASS | 0 |

Focused command的 57 次执行中有 17 次重复：`test_import_share_presentation.py` 将 `PublicationPackageV13ConsumerValidationTests` 作为模块级 import 引入，unittest 又收集了该 TestCase；逐模块运行得到 4 + 17 + 8 + 6 + 5 = 40 个 distinct tests。报告不把 57 次执行误称为 57 个独立测试。

新增测试有真实调用 `import_shares.main()` 并断言拒绝路径零输出；但 direct importer 测试尚未覆盖 nested raw source / internal symlink alias、source mismatch、wrong version/content_type、malformed package 与 missing package-bound file 的完整入口攻击矩阵。validator 自身的部分负向测试不能代替 importer entrypoint 的组合验证。

## 7. Side effects and final disposition

本轮未执行：

- dependency install/upgrade；
- production import 或任何真实文章写入；
- Astro build；
- NAS access/read/write；
- notification/email；
- commit、push、merge、deploy；
- Stage D、Stage E 或 Stage F。

攻击验证均使用临时目录，测试结束后清理；没有在 Website raw/processed/posts 或 canonical worktree 中创建内容。Python compile 命令执行期间可能刷新被 Git 忽略的 `__pycache__` 字节码缓存；Git 可见的审核前变更集合未因该操作增加。除此以外，没有修改授权报告以外的项目文件。

**最终裁决：FAIL。** F-01 原始 package bypass 已修复，但 direct importer 的 raw source selector 仍可被 nested path / symlink alias 绕过；F-02 metadata binding 已补齐，但 caller source basename alias 仍能越过 workflow mismatch gate 并进入 renderer/importer。请 Master 将这两项聚合为一次最小 source-identity hardening remediation，再进行新的独立复审。Stage C 在 Master 接受新的独立 PASS 前不予接受；Stage D 保持 BLOCKED，Stage F 保持 DISABLED。

本报告 SHA-256 在文件写入并 read-back 后由 Master handback 单独提供；不将自引用 hash 写入报告正文。
