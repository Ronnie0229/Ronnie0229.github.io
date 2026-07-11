# 新文章邮件提醒系统 MVP 第三阶段：发布后自动发送与订阅邮箱一览

## 当前目标

第三阶段实现以下功能：

```text
1. 文章通过 Admin 编辑器发布，并确认 Cloudflare Pages 已部署成功后，自动发送新文章提醒邮件。
2. 短时间内连续发布多篇文章时，把多篇文章的中性阅读链接合并到同一封邮件。
3. Admin 增加只读的订阅邮箱一览页。
4. 清理第二阶段文档中的过时状态，避免误判真实发送尚未执行。
```

## 自动发送触发机制

Admin 编辑器原有流程会在文章提交 GitHub 后轮询 `/deployment.json`。只有线上部署返回的 commit 与本次 GitHub commit 完全一致时，页面才显示“发布成功”。

第三阶段新增：

```text
assets/admin/auto-email.js
functions/api/admin/email/auto-send.js
```

`auto-email.js` 在原编辑器脚本之前加载，并完成：

```text
1. 捕获写入 src/content/posts 的 GitHub PUT 请求。
2. 草稿不会进入邮件队列。
3. 正式文章写入成功后，将文章 slug 放入 localStorage 持久队列。
4. 监听 /deployment.json，只有 commit 完全一致时才启动邮件发送。
5. 部署成功后等待 12 秒，合并这段时间内连续发布的多篇文章。
6. 调用 POST /api/admin/email/auto-send，一次向每个 confirmed 订阅者发送一封邮件。
7. 发送成功后清空队列；失败时保留队列，下一次打开文章管理页会重试。
```

## 批量邮件规则

```text
1. 一篇文章：邮件标题保持“RonnieCross 新文章提醒”。
2. 多篇文章：邮件标题显示“RonnieCross 新文章提醒（N篇）”。
3. 邮件正文列出每篇文章的中性 URL。
4. 不显示文章标题、经文、摘要或真实 slug。
5. 每个订阅者仍单独发送，避免泄露其他邮箱。
6. 每篇文章仍分别写入 email_post_sends，防止重复发送。
7. 一批邮件的逐邮箱发送日志锚定到该批第一篇文章的 post_send_id；同批其他文章的 email_post_sends 同步记录相同成功数和失败数。
```

## Admin 订阅邮箱一览

新增：

```text
functions/api/admin/email/subscribers.js
assets/admin/subscribers.html
assets/admin/subscribers.js
```

页面地址：

```text
/admin/subscribers.html
```

页面只读显示：

```text
邮箱
订阅状态
订阅时间
确认或退订时间
最近发送时间
全部、已确认、待确认、已退订数量
```

页面和 API 均复用现有 Cloudflare Access 管理员保护，不提供修改、删除、手工确认或批量导入功能。

## GitHub push 统一自动触发

为了覆盖 Codex 整理发布、本地 Git push、GitHub 网页提交和 Admin 发布，第三阶段增加 GitHub Actions 统一触发器：

```text
.github/workflows/email-published-posts.yml
scripts/notify-deployed-posts.mjs
```

触发规则：

```text
1. main 分支 push 中只要包含 src/content/posts/*.md 的新增或修改，就启动工作流。
2. 工作流读取本次 push 中所有变动的文章 slug。
3. 等待线上 /deployment.json 的 commit 等于本次文章 push，或属于包含该文章 push 的后续 main 提交。
4. 这样即使 Codex 在文章提交后继续提交状态文档，也不会因为线上已经部署到更新 commit 而错过邮件。
5. 部署确认后，一次调用 /api/admin/email/auto-send。
5. 同一次 push 中多篇文章合并为一封邮件。
6. 已发送过提醒的文章由 D1 记录自动跳过。
7. API 使用 EMAIL_AUTOMATION_SECRET 机器鉴权；该值必须同时配置为 Cloudflare Pages secret 和 GitHub Actions repository secret。
8. 如果某次文章 push 已经被后续 main 提交包含并部署，工作流仍视为部署完成，避免错过发送窗口。
9. 支持 `workflow_dispatch` 受控补发，输入明确 slug 后只补发指定文章；密钥仍仅从 GitHub Actions secret 注入，不在本地输出。
10. GitHub Actions 默认调用 `/api/email/auto-send`，避免 Cloudflare Access 对 `/api/admin/...` 后台路径的登录拦截；Admin 浏览器仍可继续使用 `/api/admin/email/auto-send`。
11. 如果某篇文章已有 `partial_failed` 发送记录，再次触发同一 slug 时只重试上一批失败且当前仍 confirmed 的订阅者，并复用原 `email_post_sends` 记录，避免 `post_slug` 唯一约束冲突和给已成功邮箱重复发送。
```

因此，Codex 整理文章并完成 commit / push 后，不需要再手工调用邮件 API。

## 当前边界

```text
1. Admin 浏览器发布仍保留 localStorage 队列作为即时触发和失败重试机制。
2. GitHub Actions 是覆盖 Codex、本地 Git 和 GitHub 网页发布的统一触发器。
3. 如果只在本地生成文章但没有 push 到 main，不会发送邮件。
4. 如果 GitHub Actions secret 或 Cloudflare Pages secret 未配置，统一自动触发不会成功。
5. 不实现 Cron、Cloudflare Queues、点击率、打开率、分类订阅或订阅者编辑功能。
6. 自动发送上线后必须先使用可控测试邮箱发布测试文章验证，不应直接用大量真实订阅者做首次测试。
```

## 验证结果

```text
node --check functions/api/admin/email/auto-send.js：通过
node --check assets/admin/auto-email.js：通过
node --check assets/admin/subscribers.js：通过
npm run build：通过，310 page(s) built，Build Complete
```

## 上线后验证

```text
1. 打开 /admin/subscribers.html，确认只能由管理员访问，邮箱列表与 D1 一致。
2. 发布一篇测试文章，确认部署成功后自动发出一封邮件。
3. 短时间连续发布两篇测试文章，确认只收到一封包含两个中性 URL 的邮件。
4. 检查 email_post_sends：每篇文章各有一条 sent 或 partial_failed 记录。
5. 检查 email_send_logs：每位订阅者每批只有一条实际发送结果。
6. 确认草稿保存不会发邮件。
7. 确认已经发送过的文章不会重复发送。
8. 确认退订邮箱和待确认邮箱不会收到邮件。
```
