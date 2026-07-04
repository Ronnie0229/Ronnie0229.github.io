# 新文章邮件提醒系统 MVP 第一阶段：订阅、确认、退订

## 一、任务背景

本站 `ronniecross.com` 是 Astro 静态内容网站，当前部署在 Cloudflare Pages，并已使用 Cloudflare Pages Functions 与 D1 数据库。

本阶段只实现：

```text
用户订阅
发送确认邮件
用户点击确认
用户退订
```

本阶段不实现：

```text
新文章提醒发送
手动发送文章通知
Cron 自动检测
newsletter 模板
打开率统计
点击统计
分类订阅
后台管理页面
```

邮件发送服务使用 Resend。Cloudflare Pages 环境变量已经准备好：

```text
RESEND_API_KEY
EMAIL_FROM
EMAIL_ADMIN_SECRET
SITE_URL
```

其中本阶段只需要使用：

```text
RESEND_API_KEY
EMAIL_FROM
SITE_URL
```

`EMAIL_ADMIN_SECRET` 留给第二阶段手动发送新文章提醒使用。

## 二、当前环境信息

项目类型：

```text
Astro 静态站
Cloudflare Pages
Cloudflare Pages Functions
Cloudflare D1
```

已有 D1 绑定：

```text
COMMENTS_DB
```

第一阶段复用这个 D1 数据库和 `COMMENTS_DB` binding，不新建数据库。

Resend 发信域名已经验证：

```text
updates.ronniecross.com
```

发信地址：

```text
RonnieCross <notice@updates.ronniecross.com>
```

Resend 送达测试结果：Yahoo Japan、Gmail、Outlook、QQ 均已收到测试邮件。

## 三、第一阶段目标

实现最小可用邮件订阅流程：

```text
1. 读者在网站订阅表单输入邮箱
2. 网站调用 /api/subscribe
3. 系统写入 D1，状态为 pending
4. 系统通过 Resend 发送确认邮件
5. 读者点击确认链接
6. /api/confirm 将状态改为 confirmed
7. 读者以后可以通过退订链接退订
8. /api/unsubscribe 将状态改为 unsubscribed
```

## 四、必须实现

```text
1. D1 migration：email_subscribers 表
2. POST /api/subscribe
3. GET /api/confirm?token=...
4. GET /api/unsubscribe?token=...
5. /subscribe/confirmed/ 静态成功页面
6. /subscribe/unsubscribed/ 静态退订页面
7. SubscribeForm 组件
8. 在首页或关于页加入订阅入口
9. 使用 Resend 发送确认邮件
10. 基础防滥用措施：邮箱格式校验、honeypot、重复邮箱处理
```

## 五、不要实现

```text
1. 不要实现新文章邮件提醒发送
2. 不要实现 /api/admin/email/send-post
3. 不要实现 /go/post/<neutral_id>
4. 不要实现 email_post_sends
5. 不要实现 email_send_logs
6. 不要实现 Cron
7. 不要做邮件打开率、点击率追踪
8. 不要加入文章标题、摘要、经文推送逻辑
9. 不要改 RSS 自动发送逻辑
```

## 六、数据库设计

新增 migration 文件，沿用项目现有 `scripts/migrations/` 习惯：

```text
scripts/migrations/0004_create_email_subscribers.sql
```

表结构：

```sql
CREATE TABLE IF NOT EXISTS email_subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',
  confirm_token TEXT NOT NULL UNIQUE,
  unsubscribe_token TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  confirmed_at TEXT,
  unsubscribed_at TEXT,
  last_sent_at TEXT
);
```

状态只需要：`pending`、`confirmed`、`unsubscribed`。

## 七、API 设计

### POST `/api/subscribe`

接收 JSON：

```json
{
  "email": "reader@example.com",
  "website": ""
}
```

处理要求：

```text
1. 只允许 POST
2. 解析 JSON body
3. honeypot 字段 website 有值时，返回成功样式响应，但不写库、不发信
4. 校验 email：必须存在、trim、转小写、基础格式校验、长度不超过 254
5. 不存在：插入 pending，生成 confirm_token / unsubscribe_token，发送确认邮件
6. pending：更新 confirm_token，重新发送确认邮件
7. confirmed：不重复订阅，不暴露邮箱是否存在，可不发邮件
8. unsubscribed：改回 pending，生成新的 confirm_token，清空 unsubscribed_at，重新发送确认邮件
9. 返回统一 JSON，不泄露邮箱是否已存在
```

统一成功返回：

```json
{
  "ok": true,
  "message": "如果邮箱地址有效，我们会发送一封确认邮件。请前往邮箱完成确认。"
}
```

### GET `/api/confirm?token=...`

处理要求：

```text
1. token 不存在：302 到 /subscribe/confirmed/?status=invalid
2. token 找不到：302 到 /subscribe/confirmed/?status=invalid
3. token 找到：status 改为 confirmed，confirmed_at 写入当前 ISO 时间，unsubscribed_at = NULL
4. 成功：302 到 /subscribe/confirmed/
```

### GET `/api/unsubscribe?token=...`

处理要求：

```text
1. token 不存在：302 到 /subscribe/unsubscribed/?status=invalid
2. token 找不到：302 到 /subscribe/unsubscribed/?status=invalid
3. token 找到：status 改为 unsubscribed，unsubscribed_at 写入当前 ISO 时间
4. 成功：302 到 /subscribe/unsubscribed/
```

## 八、Resend 发信逻辑

建议新增工具文件：

```text
functions/_utils/email.js
```

必须使用环境变量：

```text
RESEND_API_KEY
EMAIL_FROM
SITE_URL
```

确认邮件标题：

```text
确认订阅 RonnieCross 更新提醒
```

确认邮件正文保持简单纯文本，可同时提供简单 HTML。不要加入文章标题、经文、摘要。

## 九、前端组件和页面

新增：

```text
src/components/SubscribeForm.astro
src/pages/subscribe/confirmed.astro
src/pages/subscribe/unsubscribed.astro
```

第一阶段只在 `src/pages/about.astro` 底部加入订阅入口。不要全站弹窗，不要强提醒，不要浮动订阅框。

## 十、安全与防滥用要求

```text
1. 邮箱格式校验
2. honeypot 字段
3. 不暴露邮箱是否已存在
4. 订阅必须 double opt-in
5. confirmed 之前不加入正式发送列表
6. 所有 token 使用 crypto 随机生成
7. 不把 RESEND_API_KEY 写入代码
8. 不在日志里输出完整 token 或 API Key
9. API 出错时不要返回内部堆栈
```

## 十一、Cloudflare / D1 注意事项

本阶段直接使用：

```js
env.COMMENTS_DB
```

不要新增 binding。代码完成后给出 D1 migration 执行命令或说明。不要擅自部署生产数据库，除非用户明确要求。

## 十二、验证要求

至少运行：

```powershell
npm.cmd run build
```

如果项目已有其他检查脚本，也运行：

```powershell
npm.cmd run check:admin-save
npm.cmd run check:knowledge
```

## 十三、上线前功能测试清单

```text
1. 访问订阅表单页面
2. 输入无效邮箱，应该提示错误
3. 输入有效 Yahoo 邮箱，应该提示确认邮件已发送
4. 邮箱收到确认邮件
5. 点击确认链接
6. 跳转到 /subscribe/confirmed/
7. D1 中 status 变为 confirmed
8. 使用同一邮箱再次订阅，不应重复创建多条记录
9. 点击退订链接
10. 跳转到 /subscribe/unsubscribed/
11. D1 中 status 变为 unsubscribed
12. 退订后同一邮箱再次订阅，应重新进入 pending 并发送确认邮件
13. honeypot 字段有值时，不应写库、不应发信，但前端不暴露拦截
```

## 十四、不要触碰的范围

```text
1. src/pages/rss.xml.ts
2. scripts/import_sermons.py
3. scripts/import_shares.py
4. 文章 Markdown 内容
5. 现有评论功能
6. 现有 GitHub 登录 / Admin 功能
7. 现有 COMMENTS_DB 绑定名称
8. 现有 Cloudflare Access 配置
9. 现有 SEO / sitemap 逻辑
```

## 十五、第二阶段预告，但本次不要实现

```text
1. email_post_sends 表
2. email_send_logs 表
3. /api/admin/email/send-post
4. /go/post/<neutral_id>
5. 手动触发新文章提醒
6. 同一 slug 只能发送一次
7. 邮件正文不包含文章标题、摘要、经文、真实 slug
```
