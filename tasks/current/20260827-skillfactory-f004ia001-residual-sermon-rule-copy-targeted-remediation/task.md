# task｜F-F004IA-001 网站 current 文档残留 sermon fidelity rule copy 定向整改

状态：`ACTIVE / READY_FOR_EXECUTOR / NOT_EXECUTED`

角色：`SKILLFACTORY_F004IA001_WEBSITE_RESIDUAL_RULE_COPY_TARGETED_REMEDIATION_EXECUTOR`

交回：`SKILL_FACTORY_CROSS_PROJECT_MASTER_CONTROL`

## 背景

F-P0-004 首轮联合独立审核正式结果为：

`FAIL / F004IA-01..F004IA-08 = 7/8 PASS`

唯一 blocker：

`F-F004IA-001 / CURRENT_WEBSITE_DOC_RETAINS_SERMON_FIDELITY_RULE_COPY`

位置：`个人网页项目/docs/统一内容整理与发布流程.md:59-72`。

独立审核确认新的 Owner/consumer 边界总体正确，但该 current-effective 段落仍直接维护“全文逐段 v2 E1 审计 → finding 后修复/重新全文审计 → independently_verified 后发布”的 sermon-owned workflow 正文，与同文件前文“不再复制 sermon fidelity 规则正文”冲突。

## 目标价值 Gate

`CONTINUE_BUSINESS_NECESSARY`

这是正常维护者会直接读到的 current-effective authority placement 问题，不是只有恶意篡改才成立。整改只需收敛一个已定位段落，不需要 schema、validator、runtime、service/database/watcher 或新流程。

## 本轮唯一目标

只定向修复 `个人网页项目/docs/统一内容整理与发布流程.md` 中“剩余46篇重译项目四阶段门禁”残留的 sermon-owned fidelity workflow copy：

- 网站不得继续正文定义 E1/独立审核/修复/重新审核/sermon terminal semantics；
- 应改为引用 `讲道整理` Owner 的 current canonical authority / 该 46 篇 Owner authority；
- 网站只保留自己真正拥有的 D 阶段 consumer/publishing responsibilities，例如 raw/processed/posts、frontmatter/slug identity、build/Git/deploy/notification/线上验证等；
- 不得改变历史 archive，不得追溯改写首轮独立审核 FAIL。

## 固定执行分母

`F004R-01..F004R-06 = 6/6`

1. `F004R-01` fresh-read RonnieCross root governance、网站 current authority、F004 两侧 executor result、首轮 independent audit RESULT/AUDIT_EVIDENCE/NEXT_HANDOFF，以及讲道 Owner 对应 46 篇 current authority。
2. `F004R-02` 确认 write-set 只限本 finding 必需的网站 current authority 与本 task-local result/evidence/handoff；不得顺手 cleanup 其他历史表述。
3. `F004R-03` 将 `docs/统一内容整理与发布流程.md:59-72` 的 sermon-owned E1/audit/repair/re-audit/terminal rule body 收敛为 Owner canonical reference，不再形成第二 authority。
4. `F004R-04` 保留网站真正拥有的 consumer/display/publishing/identity/build/Git/deploy/notification/online verification Gate，不把网站职责误删或推给讲道 Owner。
5. `F004R-05` 不修改讲道 Owner、`website-publication-package/v1.1` schema/interface、validator/runtime/article body，不运行 build/reviewer/model/provider/n8n/production，不进入其他 finding。
6. `F004R-06` 形成 `PASS_CANDIDATE`、`FAIL` 或 `BLOCKED_CURRENT_TRUTH_MOVED` 的正式 RESULT/VERIFICATION/NEXT_HANDOFF；保留首轮 7/8 FAIL 历史，不自行执行独立复审或宣布 F004 closure。

## 禁止范围

不得修改讲道 Owner；不得新建 schema/validator/service/database/watcher；不得修改历史 archive；不得 build、commit、push、deploy、notify、NAS；不得进入 F-P0-005、Owner amendment adoption、L4、P2、Skill build/release。

## 停止

达到 `PASS_CANDIDATE / F004R-01..F004R-06=6/6`、`FAIL` 或 `BLOCKED_CURRENT_TRUTH_MOVED` 后立即停止并交回 `SKILL_FACTORY_CROSS_PROJECT_MASTER_CONTROL`。