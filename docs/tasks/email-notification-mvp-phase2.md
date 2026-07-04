# 新文章邮件提醒系统 MVP 第二阶段：手动发送新文章提醒

## 一、任务背景

第一阶段已经完成并通过线上测试：

```text
1. /about/ 订阅入口正常。
2. 订阅后确认邮件发送正常。
3. 点击确认链接后，D1 中订阅者状态可变为 confirmed。
4. 点击退订链接后，D1 中订阅者状态可变为 unsubscribed。
5. About 页邮件提醒卡片深浅模式透明效果已验收。
```

第二阶段目标是在不引入 Cron、不做自动检测、不做复杂统计的前提下，实现一个可控的“手动发送新文章提醒”MVP。

本阶段仍然以安全、克制、可回滚为原则。不要一次性实现完整 newsletter 系统。

## 二、阶段目标

实现管理员可以手动触发某一篇文章的更新提醒邮件：

```text
1. 管理员选择或输入文章 slug。
2. 管理员调用后台 API。
3. 系统检查该文章是否存在。
4. 系统检查该文章是否已经发送过提醒。
5. 系统只向 status = confirmed 的订阅者发送邮件。
6. 邮件正文只包含温和提示与跳转链接。
7. 发送完成后记录本次发送结果。
8. 同一篇文章默认只能发送一次，避免重复打扰读者。
```

## 三、本阶段必须实现

```text
1. 新增 D1 migration：email_post_sends 表。
2. 新增 D1 migration：email_send_logs 表，记录每个邮箱的发送结果。
3. 扩展 functions/_utils/email.js，新增发送文章提醒邮件的方法。
4. 新增后台 API：POST /api/admin/email/send-post。
5. API 必须有管理员保护。
6. API 必须支持 dryRun，先预览发送目标数量，不真实发信。
7. API 必须防重复发送：同一 slug 成功发送后，默认不能再发第二次。
8. API 发送时只选择 confirmed 订阅者。
9. 发送完成后更新 email_subscribers.last_sent_at。
10. 更新 docs/tasks/current.md 与 STATUS.md。
```

## 四、本阶段不要实现

```text
1. 不要实现 Cron 自动发送。
2. 不要实现自动检测新文章。
3. 不要实现后台 UI 页面，先用 API 或命令测试。
4. 不要实现邮件打开率统计。
5. 不要实现点击率统计。
6. 不要实现 /go/post/<neutral_id> 跳转追踪。
7. 不要实现分类订阅。
8. 不要批量导入外部邮箱。
9. 不要把未确认、已退订邮箱加入发送。
10. 不要在邮件正文中放完整文章内容。
```

## 五、数据库设计

新增 migration：

```text
scripts/migrations/0005_create_email_post_sends.sql
```

建议内容：

```sql
CREATE TABLE IF NOT EXISTS email_post_sends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_slug TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',
  subject TEXT NOT NULL,
  recipient_count INTEGER NOT NULL DEFAULT 0,
  success_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  sent_at TEXT,
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_email_post_sends_post_slug
ON email_post_sends(post_slug);

CREATE INDEX IF NOT EXISTS idx_email_post_sends_status
ON email_post_sends(status);
```

新增 migration：

```text
scripts/migrations/0006_create_email_send_logs.sql
```

建议内容：

```sql
CREATE TABLE IF NOT EXISTS email_send_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_send_id INTEGER NOT NULL,
  subscriber_id INTEGER NOT NULL,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  resend_id TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL,
  sent_at TEXT,
  FOREIGN KEY (post_send_id) REFERENCES email_post_sends(id),
  FOREIGN KEY (subscriber_id) REFERENCES email_subscribers(id)
);

CREATE INDEX IF NOT EXISTS idx_email_send_logs_post_send_id
ON email_send_logs(post_send_id);

CREATE INDEX IF NOT EXISTS idx_email_send_logs_subscriber_id
ON email_send_logs(subscriber_id);

CREATE INDEX IF NOT EXISTS idx_email_send_logs_status
ON email_send_logs(status);
```

说明：

```text
1. email_post_sends 记录“一篇文章的一次发送任务”。
2. email_send_logs 记录“每个订阅者的发送结果”。
3. post_slug 使用站内真实 slug，但只保存在后台 D1，不在公开邮件里暴露额外追踪参数。
4. 本阶段不做点击追踪，所以不需要 neutral_id。
```

## 六、后台 API 设计

新增：

```text
functions/api/admin/email/send-post.js
```

请求方式：

```text
POST /api/admin/email/send-post
```

请求 JSON：

```json
{
  "slug": "2026-07-04-示例文章/index",
  "dryRun": true
}
```

或者：

```json
{
  "slug": "2026-07-04-示例文章",
  "dryRun": false
}
```

API 行为：

```text
1. 只允许 POST。
2. 必须通过管理员权限验证。
3. 解析 slug，trim，禁止空值。
4. 读取站内文章清单，确认 slug 对应文章存在。
5. 查询 confirmed 订阅者数量。
6. dryRun = true 时，只返回预览信息，不写 email_post_sends，不发邮件。
7. dryRun = false 时：
   - 检查 email_post_sends 中该 post_slug 是否已存在 sent/sending/success 状态。
   - 如已发送过，返回 409，提示该文章已经发送过提醒。
   - 创建 email_post_sends 记录。
   - 向 confirmed 订阅者逐个发送邮件。
   - 写入 email_send_logs。
   - 更新 email_post_sends 的 success_count / failed_count / status / sent_at。
   - 更新成功发送订阅者的 email_subscribers.last_sent_at。
8. 返回 JSON 结果。
```

返回示例：

```json
{
  "ok": true,
  "dryRun": true,
  "post": {
    "slug": "...",
    "title": "...",
    "url": "https://ronniecross.com/posts/.../"
  },
  "recipientCount": 12
}
```

实际发送返回示例：

```json
{
  "ok": true,
  "dryRun": false,
  "postSlug": "...",
  "recipientCount": 12,
  "successCount": 12,
  "failedCount": 0
}
```

## 七、管理员权限保护

优先复用现有后台鉴权：

```text
functions/_lib/admin-auth.js
```

如果该 API 放在 `/api/admin/...` 下，应与现有 Admin API 一致：

```text
1. 只有通过 Cloudflare Access 的管理员可以调用。
2. 不要把 EMAIL_ADMIN_SECRET 暴露到前端。
3. 如果决定使用 EMAIL_ADMIN_SECRET 作为额外保护，只能从 env 读取，不能写入代码或文档真实值。
```

建议本阶段优先使用 `requireAdmin(request, env)`，不要另造一套权限系统。

## 八、文章信息来源

需要确认 Astro 内容在 Cloudflare Functions 运行时是否容易读取。

推荐优先方案：

```text
1. 构建期生成一个轻量 JSON 索引，例如 /email-post-index.json 或内部静态 JSON。
2. 内容包括 slug、title、description、date、url。
3. 后台发送 API 根据 slug 从该索引获取文章信息。
```

替代方案：

```text
1. 如果现有 search-index.json 已包含足够文章信息，可以复用。
2. 但要确认 search-index.json 字段稳定，且不会包含不适合发邮件的草稿或隐藏内容。
```

本阶段不要直接在 Functions 运行时读取 `src/content/posts` 文件系统，因为 Cloudflare Pages Functions 线上环境不适合依赖源码文件路径。

## 九、邮件内容要求

邮件必须克制，不要像营销 newsletter。

标题建议：

```text
RonnieCross 有一篇新文章更新
```

正文建议：

```text
你好，

RonnieCross 刚刚有一篇新文章更新。

你可以点击下面链接前往阅读：

{postUrl}

如果你不想继续收到提醒，可以点击下面链接退订：

{unsubscribeUrl}
```

HTML 版本可包含：

```text
1. 简短问候。
2. 文章标题。
3. 阅读按钮。
4. 退订链接。
```

注意：

```text
1. 邮件里可以包含文章标题和正常文章 URL。
2. 不放完整文章正文。
3. 不放过多摘要。
4. 不添加追踪跳转链接。
5. 必须包含退订链接。
```

## 十、发送策略

MVP 阶段订阅者数量少，可以逐个发送。

要求：

```text
1. 每个收件人单独发送，不要把多个邮箱放进同一个 to 数组。
2. 避免泄露订阅者邮箱。
3. 单封失败不应中断整个批次。
4. 每个失败写入 email_send_logs.error_message。
5. API 最终返回 success_count 与 failed_count。
```

如订阅者未来变多，再考虑队列、分批、Cron 或 Cloudflare Queues。本阶段不要提前引入。

## 十一、验证要求

本地代码验证：

```powershell
npm.cmd run build
npm.cmd run check:admin-save
npm.cmd run check:knowledge
```

远程 D1 migration 需要用户确认后执行：

```powershell
npx.cmd wrangler d1 execute ronniecross-comments --remote --file scripts/migrations/0005_create_email_post_sends.sql
npx.cmd wrangler d1 execute ronniecross-comments --remote --file scripts/migrations/0006_create_email_send_logs.sql
```

API 线上验证建议先 dryRun：

```powershell
# 具体命令需根据 Cloudflare Access 登录态或后台调用方式确定
```

实际发送前必须确认：

```text
1. confirmed 订阅者数量正确。
2. 测试邮箱仍是自己可控邮箱。
3. dryRun 返回的文章标题和 URL 正确。
4. 退订链接在邮件中存在。
5. 不会发送给 unsubscribed 邮箱。
```

## 十二、提交要求

完成代码后：

```text
1. 不要自动执行远程 D1 migration，除非用户明确同意。
2. 不要自动触发真实邮件发送，除非用户明确同意。
3. 不要提前实现第三阶段。
4. 通过 build 与检查脚本后再提交。
5. 提交后更新 STATUS.md 和 docs/tasks/current.md。
```

推荐 commit message：

```text
feat: add manual email post notification flow
```

## 十三、后续第三阶段预告，不在本阶段实现

```text
1. 后台 UI：选择文章并点击发送。
2. 更友好的发送历史页面。
3. 失败重试。
4. 定时检测新文章。
5. Cloudflare Queues 或分批发送。
6. 分类订阅。
7. 统计报表。
```
