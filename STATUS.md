# 项目状态

最后更新：2026-06-30 +09:00

## 当前结论

内容整理收尾已完成：不发布清单已从发布队列清理，待神学事实复核的两篇已整理为已复核状态并通过本地构建。

```text
正式开发目录：C:\Users\caoyi\Projects\个人网页项目
当前主分支：main
最近构建结果：npm.cmd run build 成功，192 page(s) built
当前任务状态：内容整理收尾完成，待提交/推送后进行线上验证
```

## 本次内容整理收尾

已按用户判断完成：

1. `docs/内容整理报告/待确认版权.csv` 中的文章不发布，待确认记录已清空。
2. `docs/内容整理报告/待补经文.csv` 中的 `属世的谎言.docx` 不发布，已从分享文章目录和 processed 中间稿清理。
3. `docs/内容整理报告/待神学事实复核.csv` 中的两篇已判断完毕：
   - `20230503_假信仰与假平安.docx`
   - `和睦相处荣耀神.docx`
4. 两篇正式文章已修正 `description`，并将 `reviewed` 标为 `true`。
5. 对应 processed 中间稿同步更新。

## 最近验证结果

已完成：

```powershell
node scripts/add_article_ids.mjs --check
npm.cmd run build
```

结果：

```text
检查完成：161 篇文章，0 篇缺少 articleId。
192 page(s) built
[build] Complete!
```

构建前曾因 Astro 缓存权限和 Duplicate id 缓存警告失败；已清理 `.astro` 与 `node_modules/.astro` 构建缓存后重建成功。

## 已知注意事项

1. 本次没有删除 `data/raw` 原始资料。
2. `待确认版权.csv`、`待补经文.csv`、`待神学事实复核.csv` 现在只保留表头，表示当前无待处理条目。
3. 需要完成提交、推送和正式域名线上验证后，才算网站线上发布闭环完成。
