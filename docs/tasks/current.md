# 当前任务

## 任务名称

2026-06-28 Patrick 讲道整理发布。

## 当前目标

整理并发布用户放入讲道目录的 Patrick 讲道 PDF。严格执行本地修改前先同步远端、双语 PDF 防错、逐句忠实翻译、发布后构建和线上验证的流程。

## 本任务范围

已修改并准备交接的文件：

```text
src/content/posts/2026-06-28-romans-15-14-33-gospel-reminder.md
data/processed/整理后的讲道文章/2026-06-28-romans-15-14-33-gospel-reminder.md
docs/内容整理报告/讲道文章目录.csv
scripts/add_article_ids.mjs
STATUS.md
docs/tasks/current.md
```

本机 raw 资料和 NAS 归档：

```text
data/raw/教会讲道/20260628罗马书15：14-33福音的提醒_Patrick/
\\RonnieNAS\share\教会讲道\20260628罗马书15：14-33福音的提醒_Patrick
```

未修改：

```text
functions/
assets/
wrangler.jsonc
其他旧文章正文
```

## 已完成

1. 启动前执行远端同步：`git pull --rebase origin main`，结果为最新。
2. 检查讲道收件目录，确认只有今天 Patrick 的 PDF。
3. 入库 PDF，生成 `*.extracted.txt`，并确认机器提取稿只作辅助。
4. 因 PDF 为英日双语，确认以英文为翻译源。
5. 生成英文源稿，按英文逐句完整翻译为中文 TXT，没有用摘要代替翻译。
6. 复制到 `\\RonnieNAS\share\教会讲道` 受保护归档区，归档校验通过：3 个正式文件，761116 字节。
7. 生成网站文章和 processed 文章，并手动修正：
   - `description` 为完整句。
   - `scripture` 为 `罗马书 15:14-33`。
   - `author` 为 `Patrick`。
   - slug 为稳定英文 `2026-06-28-romans-15-14-33-gospel-reminder`。
   - `articleId` 非空。
8. 发现并处理发布脚本批量重写旧文问题：恢复 2026-06-14 旧文改动，删除 2026-06-21 重复文件，只保留今天文章。
9. 修复 `scripts/add_article_ids.mjs` 对 UTF-8 BOM 历史文件的 frontmatter 识别问题。
10. 构建和线上验证均完成。

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

内容提交已推送：

```text
a8f0503 Publish Patrick sermon on Romans 15 14-33
```

线上验证通过：

```text
https://ronniecross.com/posts/2026-06-28-romans-15-14-33-gospel-reminder/
```

验证项：HTTP 200、标题、经文、讲员、摘要关键句、正文代表句均存在。

## 下一步

1. 后续讲道发布仍需先 `git pull --rebase origin main`。
2. 后续讲道发布后必须检查 diff，当前 `publish sermon` 仍会批量处理旧目录。
3. 如果要减少后续人工清理，建议单独改造 `scripts/import_sermons.py`，让它支持只发布指定讲道目录。