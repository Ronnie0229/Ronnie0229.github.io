# Amendment — P1B-pre Targeted Architecture Gap Remediation

日期：2026-10-07

正式目标：只关闭 independent audit 的 Finding A / Finding B，并冻结 implementation 前 runtime state root。原已通过架构边界继续有效，不重开。

## A. Generation authorization one-time atomic claim — FROZEN

### A1. Immutable authorization identity

每一个 explicit generation authorization 必须有 immutable `authorization_ref` 与 `generation_epoch`。Website authorization claim 只约束“一次用户授权最多绑定一个 logical generation identity”；它不替代 VOICE_AI N6 的 provider request exactly-once authority。

当前 Pilot 冻结：
- authorization_ref = `article-read-aloud-pilot-generation-authorization-20261007-a1`
- generation_epoch = `pilot-20261007-a1`
- authorization state at this remediation closure = `UNCLAIMED / NOT_CONSUMED`

### A2. Canonical immutable logical job descriptor

descriptor schema：`ronniecross-readaloud-generation-operation/v1`

字段集合固定且必须全部参与 identity：
- schema
- authorization_ref
- generation_epoch
- operation_id
- article_id
- render_sha256
- voice_contract_id

当前 Pilot：
- operation_id = `article-read-aloud-pilot-post-32d30724d859c99c`
- article_id = `post-32d30724d859c99c`
- render_sha256 = `5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`
- voice_contract_id = `VOICE_AI_LOCAL_HTTP_V1`

canonical serialization 固定为 UTF-8 JSON：keys 按字典序排序、无多余空白、ASCII escaped，即 Python 等价语义 `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)`。

当前 Pilot canonical descriptor exact bytes 对应文本：
`{"article_id":"post-32d30724d859c99c","authorization_ref":"article-read-aloud-pilot-generation-authorization-20261007-a1","generation_epoch":"pilot-20261007-a1","operation_id":"article-read-aloud-pilot-post-32d30724d859c99c","render_sha256":"5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a","schema":"ronniecross-readaloud-generation-operation/v1","voice_contract_id":"VOICE_AI_LOCAL_HTTP_V1"}`

descriptor SHA-256 = `49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`

deterministic request_id derivation：
`request_id = "rc-readaloud-v1:" + sha256(canonical_descriptor_bytes).hexdigest()`

当前 Pilot exact request_id：
`rc-readaloud-v1:49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005`

该 request_id 长度 80，满足 VOICE_AI current request_id regex。

### A3. Atomic claim primitive

选择最小 primitive：**Website-local atomic exclusive-create claim file**。不使用 lease、数据库、Redis、Celery、distributed lock。

claim key 仅由 `authorization_ref + generation_epoch` 决定；同一 authorization epoch 永远映射同一个 claim pathname。首次 submit 在任何 provider POST 之前，必须使用 OS-level exclusive create 语义创建该 claim；只有一个 caller 能成功。

claim 内容至少固定：authorization_ref、generation_epoch、descriptor_sha256、request_id、operation_id、article_id、render_sha256、voice_contract_id。

规则：
1. exclusive create 成功后，该 authorization 永久视为 bound；不会因 caller disconnect、worker crash/restart、host restart、provider busy/not-ready 自动释放。
2. exclusive create 失败且 claim 已存在：读取 existing claim。
3. existing claim 与当前 immutable descriptor + request_id exact 相同：返回 existing job identity；不得产生新 request_id，也不产生第二 authorization right。
4. existing claim 任一 identity 字段不同、claim 不完整、无法解析、权限异常或 identity 不可证明：fail-closed / operator-required；provider POST=0。
5. claim 不允许 delete-and-retry、TTL expiry、timeout release、lease takeover 或自动生成新 generation_epoch。
6. 新 logical generation 只能来自新的 explicit user authorization + new generation_epoch。

### A4. Crash-safe invariant and job ordering

最小顺序冻结：
1. materialize immutable job descriptor candidate；
2. atomic exclusive-create authorization claim；
3. claim 完整写入并 durability sync 后，才允许把同一 existing job 标记为 runnable；
4. provider POST 只能来自已证明 exact claim binding 的 runnable job。

若 crash 发生：
- claim 创建前：authorization 仍未 claim，可由同一 descriptor 重新 submit；provider POST=0。
- claim 已创建但内容不完整/未能证明 durable completion：该 authorization 保持占用并 fail-closed，必须人工 resolution；绝不自动释放。
- claim 已完整但 job 尚未 runnable：同一 descriptor 重复 submit 可恢复同一 existing job 到 runnable，不创建新 request_id。

因此 safety 优先于 availability：crash 最坏使该 authorization 暂停人工处理，不会使同一 authorization 获得第二 logical generation identity。

## B. Exact Render View binding before every possible provider POST — FROZEN

### B1. Bounded render_ref

job descriptor/runtime record 保存 bounded `render_ref` + immutable `render_sha256`，不把完整文章复制进 job JSON/log。

当前 Pilot bounded render_ref 冻结为 Website workspace-relative path：
`docs/tasks/article-read-aloud-phase1a-20261007/tts-readaloud.txt`

当前 exact resolved evidence path：
`/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目-read-aloud-phase0-20261007/docs/tasks/article-read-aloud-phase1a-20261007/tts-readaloud.txt`

当前 fresh SHA-256 = `5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a`；UTF-8 bytes=10658；decode=PASS。

future implementation 必须把 render_ref 解析限制在 frozen Website project/worktree root 内。absolute path injection、`..` escape、symlink/rebinding ambiguity 都 fail-closed。

### B2. Pre-POST gate

每一次 worker 即将执行**任何可能进入 provider 的 POST**，无论首次 generation 还是 same-id reconcile replay，都必须：
1. 通过 bounded render_ref 打开并读取 exact file bytes 一次；
2. 对这同一 bytes object 计算 SHA-256；
3. require exact SHA == immutable render_sha256；
4. 用严格 UTF-8 decode 把这同一 bytes object 得到唯一 text string；decode failure fail-closed；
5. 不 trim、不 normalize、不 newline rewrite、不重新读取路径；
6. POST body 的 `text` 必须直接来自刚刚验证得到的同一内存 bytes/string instance；
7. request_id 必须是 descriptor 已冻结的 exact request_id。

以下任一情况：missing、unreadable、path escape、symlink/rebinding ambiguity、SHA mismatch、UTF-8 decode failure、descriptor/request_id mismatch，均必须在 Website 侧 fail-closed，provider POST=0。

frozen SHA 指 exact file-byte identity。即使文本肉眼或语义等价，只要 bytes 不同即 mismatch。

reconcile 若只读取 Website terminal state/result，不触发 provider POST，则无需重新读取全文；一旦 reconcile 可能 POST，就必须重新执行完整 B2 gate。

## C. Runtime state root — FROZEN BEFORE IMPLEMENTATION

exact root：
`/Users/ronnie/Library/Application Support/RonnieCross/read-aloud`

fresh parent evidence：
- current user=`ronnie`, uid=501
- parent=`/Users/ronnie/Library/Application Support`
- parent exists=true / directory=true / readable=true / writable=true
- parent owner uid=501
- parent mode=`0700`
- target root currently absent；本轮未创建

future implementation/installation contract：
- runtime root owner：`ronnie` (uid 501)
- runtime root mode：`0700`
- no root required
- local machine only
- no fallback path；root unavailable/untrusted => fail-closed
- Git repo 外、NAS 外、VOICE_AI workspace 外

固定子目录：
- `jobs/` — immutable descriptor + mutable orchestration state；dir 0700；files 0600
- `claims/` — authorization single-use claim files；dir 0700；files 0600
- `tmp/` — atomic state temp / partial artifact temp only；dir 0700；files 0600
- `artifact-cache/` — bounded retrieved artifact cache before downstream handoff；dir 0700；files 0600
- `logs/` — bounded lifecycle/error metadata；dir 0700；files 0600

logs/job/claim 默认不得复制完整 TTS text；只记录必要 ref/hash/identity/status/failure。artifact-cache 不是 publication/NAS/R2 storage。

## D. Dual-truth boundary

- Website authorization claim = user authorization consumption/binding truth。
- Website job state = orchestration truth。
- VOICE_AI N6 persisted state = provider generation exactly-once/result truth。

Website 不得把自身 claim/job state解释成“provider 已生成”；只有 N6 terminal result 才能证明 provider result identity。反向也一样：N6 的同 request_id exactly-once 不替代 Website 对一次用户 authorization 的 single-use claim。

## E. Hidden second-generation path exclusion

以下全部禁止：
- same authorization 派生不同 request_id；
- timeout/restart/busy 自动新 epoch；
- claim 删除后重试；
- render mismatch 后自动改文本或换 request_id；
- provider unknown/in-progress 时另建 job；
- launchd restart 触发 regeneration。

## F. Current Pilot disposition

本轮仅冻结 identity/contract；没有执行 claim、submit 或 provider POST。

`GENERATION_AUTHORIZATION_NOT_CONSUMED` 继续成立。

当前 Pilot proof rule：因为 authorization_ref + generation_epoch 的 claim pathname 唯一且只能 exclusive-create 一次，claim 内容又绑定 exact descriptor_sha256 + exact request_id，所以同一 authorization 无法合法绑定第二个不同 request_id。任何不同 descriptor/request_id 都在 provider POST 前 fail-closed。

## G. Remediation verdict

`PASS_TARGETED_ARCHITECTURE_REMEDIATION / READY_FOR_FRESH_REAUDIT`