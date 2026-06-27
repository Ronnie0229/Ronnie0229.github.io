# 项目状态

最后更新：2026-06-28 +09:00

## 当前结论

已完成 2026-06-28 Patrick 讲道《罗马书 15:14-33｜福音的提醒》的整理、归档、发布、构建、推送和线上验证。

正式开发目录：

```text
C:\Users\caoyi\Projects\各人网页项目
```

本轮开始前已按规则执行远端同步：

```powershell
git pull --rebase origin main
```

结果：`Already up to date.`

## 本轮已完成

1. 检查讲道收件目录：

```text
\\RonnieNAS\tmp\讲道
```

发现 PDF：

```text
[TF] Romans 15_14-33 The Gospel Reminder - Google Docs.pdf
```

2. 将 PDF 入库到本地 raw 目录，并生成机器提取稿：

```text
data/raw/教会讲道/20260628罗马书15：14-33福音的提醒_Patrick/
```

3. 按防错流程处理双语 PDF：
   - 确认本次以英文为翻译源。
   - 机器提取稿只作为辅助，不直接发布。
   - 生成并检查英文源稿。
   - 按英文原文逐句完整翻译，生成中文译稿。
4. 复制到受保护归档区：

```text
\\RonnieNAS\share\教会讲道\20260628罗马书15：14-33福音的提醒_Patrick
```

归档结果：3 个正式文件，761116 字节；不包含 `*.extracted.txt`。

5. 发布网站文章：

```text
src/content/posts/2026-06-28-romans-15-14-33-gospel-reminder.md
data/processed/整理后的讲道文章/2026-06-28-romans-15-14-33-gospel-reminder.md
```

6. 更新讲道目录报告：

```text
docs/内容整理报告/讲道文章目录.csv
```

7. 修复 `scripts/add_article_ids.mjs`：让脚本兼容带 UTF-8 BOM 的历史 Markdown 文件，避免再次误报“文章缺少 Frontmatter”。

## 防重复错误处理记录

本轮发布脚本一度批量重写旧讲道文章，并生成 2026-06-21 的重复中文文件。已按 `docs/content-publishing-error-prevention.md` 处理：

- 恢复 2026-06-14 旧文和 processed 旧文改动。
- 删除脚本生成的 2026-06-21 重复文件。
- 恢复报告到原状态后，只追加 2026-06-28 正确记录。
- 今天文章使用稳定英文 slug。
- 手动校正 `description`、`scripture`、`author`、`articleId`、`source`。

## 验证结果

已运行：

```powershell
node scripts/add_article_ids.mjs --check
npm.cmd run build
```

结果：

```text
检查完成：160 篇文章，0 篇缺少 articleId。
190 page(s) built
[build] Complete!
```

内容提交：

```text
a8f0503 Publish Patrick sermon on Romans 15 14-33
```

线上验证：

```text
https://ronniecross.com/posts/2026-06-28-romans-15-14-33-gospel-reminder/
```

正式域名返回 200，并已确认页面包含标题、经文、讲员、完整摘要关键句和正文代表句。

## 已知注意事项

1. `data/raw/` 被 `.gitignore` 忽略，原始 PDF、英文源稿、中文译稿保存在本机 raw 目录和 NAS 受保护归档区，不随 Git 提交。
2. 讲道导入脚本仍是批量导入模式，后续发布讲道时仍必须检查 diff，防止旧文被重写。
3. 本轮已修复 `add_article_ids.mjs` 的 BOM 兼容问题。