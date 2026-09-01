# task｜F-P0-004 网站 Owner sermon authority reference 最小整改

状态：`ESTABLISHED / WAITING_FOR_SERMON_OWNER_RESULT / NOT_EXECUTED`

角色：`SKILLFACTORY_F004_WEBSITE_SERMON_AUTHORITY_REFERENCE_REMEDIATION_EXECUTOR`

交回：`SKILL_FACTORY_CROSS_PROJECT_MASTER_CONTROL`

## 最初需求与目标

个人网页项目必须继续拥有网站正式文章、display/metadata、raw/processed/posts、build、Git、deploy、SEO、notification 等网站 truth；但不得把 `讲道整理` Owner 的 Full Sermon Mode、E1、fidelity、scripture/ending、repair/max-audit 等业务规则正文维护成网站自己的第二 authority。

F-P0-004 的网站侧目标是：把 current-effective 的 sermon-owned rule copies 收敛为 **Owner canonical reference + website-owned consumption/display Gate**，让新会话只从讲道 Owner 获取 sermon fidelity truth，同时保留网站真正需要的发布消费与显示规则。

## 启动前置条件

本任务现在只建立，**不得立即执行**。

必须先由下列讲道 Owner 任务形成正式终态，并由本执行者 fresh-read 其 actual result/current authority：

`讲道整理/tasks/current/20260827-skillfactory-f004-sermon-canonical-consumer-reference-remediation/task.md`

若 sermon Owner `FAIL`、`BLOCKED_CURRENT_TRUTH_MOVED`，或没有形成可机械定位的 canonical consumer reference，本任务必须 `BLOCKED_UPSTREAM_SERMON_REFERENCE_NOT_READY`，不得自行替 sermon Owner 发明 reference。

## 当前已知 fresh truth

任务建立时，网站 current-effective 文档仍直接复制 sermon-owned hard rules，至少包括：

- `个人网页项目/AGENTS.md`；
- `个人网页项目/CONTENT_WORKFLOW.md`；
- `个人网页项目/docs/统一内容整理与发布流程.md`；
- `个人网页项目/docs/content-publishing-error-prevention.md`；
- `个人网页项目/skills/article-workflow.md`。

这些文档当前直接出现 Full Sermon Mode、忠实翻译、E1/独立审核、scripture/CUV/TTS、ending、repair/audit separation 等规则正文；同时 `AGENTS.md` 又明确网站不得吸收 sermon fidelity 业务逻辑，形成 current authority placement 冲突。

`workspace-control/PROJECT_REGISTRY.json`、`DATA_OWNERSHIP.md` 和 `INTERFACE_REGISTRY.md` 已明确：fidelity final approval 归 `讲道整理`，网站消费 `website-publication-package/v1.1`，网站拥有后续正式文章和技术发布事实。

以上只是建立任务时的定位信息。执行者必须 fresh-read current files，若现场已变化，以 current authority 为准。

## 本轮唯一目标

在不改变网站发布功能和不重写 sermon 业务规则的前提下：

1. 将网站 current-effective 文档中的 sermon-owned 规则正文替换/收敛为对讲道 Owner canonical consumer reference 的明确引用；
2. 保留网站自己的 consumer Gate：只接收通过正式 `website-publication-package/v1.1` 提供的官方稿、identity/SHA、允许的 fidelity terminal/evidence 和发布元数据；
3. 保留网站自己的 display/metadata/scripture rendering/import fail-closed/build/deploy/SEO/Git/notification 等职责；
4. 明确网站不重新判定 Full Sermon Mode、E1、repair/max-audit、fidelity release semantics；
5. 把“两个项目同步复制业务规则”改成“Owner 规则变化时检查 consumer reference/contract 兼容性”，避免 future copy drift。

## 最小必要 write-set 上限

只有 fresh-read 确认仍为 current-effective duplicate 的文件才允许修改：

- `个人网页项目/AGENTS.md`
- `个人网页项目/CONTENT_WORKFLOW.md`
- `个人网页项目/docs/统一内容整理与发布流程.md`
- `个人网页项目/docs/content-publishing-error-prevention.md`
- `个人网页项目/skills/article-workflow.md`
- 本任务自己的 result / verification / files-changed / progress / NEXT_HANDOFF

不得为了“统一风格”顺带清理历史 archive、旧任务记录或无关 content docs。

## 固定整改分母

- `F004W-01`：fresh-read root + website current authority + sermon upstream result；确认 canonical reference 有效且 current truth 未移动。
- `F004W-02`：对 current-effective website rule copies 做完整定向 inventory；历史 archive 只记录不追溯改写。
- `F004W-03`：移除/收敛 website 对 Full Sermon Mode/E1/fidelity/repair/max-audit 等 sermon-owned规则正文的第二 authority 表达。
- `F004W-04`：网站文档统一指向 sermon Owner canonical consumer reference 和既有 `website-publication-package/v1.1`；不复制新的完整业务规则。
- `F004W-05`：保留 website-owned display/metadata/import/build/deploy/SEO/Git/notification 与 locked identity 等规则，不把网站职责推回 sermon。
- `F004W-06`：将旧“跨项目规则双边同步复制”语义收敛为 Owner change 后检查 consumer reference/contract compatibility，不建立双 truth。
- `F004W-07`：不修改 schema/validator/runtime/业务正文，不运行生产，不处理无关 finding。

## 明确非目标

不得：

- 修改 `讲道整理` 文件；
- 新建或升级 publication schema/interface；
- 重写网站 validator 或新增 sermon fidelity validator；
- 修改正式文章正文、raw/processed/posts；
- build、commit、push、Cloudflare、邮件、NAS 或真实发布；
- 处理 F-P0-005、Owner amendment adoption、L4、P2、Skill build/release；
- 清理历史 task/archive。

## 过度建设检查

`PASS_MINIMAL_AND_ALIGNED`

现有 `website-publication-package/v1.1` 已能承载 Owner→consumer handoff；本轮只修正 current authority placement/reference，不需要新增接口或实现。

## 完成与停止状态

允许终态：

- `PASS_CANDIDATE / F004W-01..F004W-07 = 7/7`
- `NO_ACTION_REQUIRED_CURRENT_WEBSITE_AUTHORITY_ALREADY_SEPARATED`
- `FAIL`
- `BLOCKED_UPSTREAM_SERMON_REFERENCE_NOT_READY`
- `BLOCKED_CURRENT_TRUTH_MOVED`

到达任一终态后立即停止，不得自行执行独立审核或进入下一 finding；把结果正式交回 `SKILL_FACTORY_CROSS_PROJECT_MASTER_CONTROL`。
