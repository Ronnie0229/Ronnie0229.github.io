# Current Task: Post-Deploy Verification and Worktree Cleanup

## 背景

当前主工作区：

```text
C:\Users\caoyi\Projects\各人网页项目
```

当前主分支：

```text
main
```

Bible Knowledge Layer v1 已经完成、合并并推送到远程：

```text
commit: 879d81d feat: add Bible Knowledge Layer v1
branch: main
remote: origin/main
```

已完成的能力：

```text
Phase 0: docs/knowledge/ARCHITECTURE.md 与 ROADMAP.md
Phase 1: src/lib/knowledge/ 核心 helper
Phase 2: JSON-LD builder 抽离到 src/lib/knowledge/schema.ts
Phase 3: 文章页接入 buildPostKnowledge
Phase 4: 书卷页、search-index、sitemap 接入 Knowledge Layer；RSS 保持兼容
Phase 5: Admin description fallback 与 articleId preSave 逻辑增强
Phase 6: scripts/check-knowledge-layer.mjs 与 check:knowledge 脚本
```

用户已在 main 工作区完成并确认：

```text
git merge feature/bible-knowledge-layer
Fast-forward d669b3d..879d81d

npm.cmd run check:knowledge
Posts checked: 158
Errors: 0
Warnings: 0

npm.cmd run build
188 page(s) built
[build] Complete!

git status --short
空

git push
45c184d..879d81d main -> main
```

## 本次任务目标

这一步不是继续开发新功能，而是做发布后的低风险验证与清理准备：

1. 确认 main 本地状态干净。
2. 确认 Knowledge Layer 检查仍通过。
3. 确认 Astro build 仍通过。
4. 检查 `dist/` 中关键输出文件是否存在。
5. 生成一份本地验证记录。
6. 准备清理临时 worktree / feature 分支的手顺，但不要擅自删除，等待用户确认。

## 本次允许操作

允许读取：

```text
package.json
scripts/check-knowledge-layer.mjs
docs/knowledge/ARCHITECTURE.md
docs/knowledge/ROADMAP.md
docs/tasks/current.md
src/lib/knowledge/
src/pages/search-index.json.ts
src/pages/sitemap.xml.ts
src/pages/rss.xml.ts
assets/admin/config.yml
assets/admin/decap.js
```

允许运行：

```powershell
git status --short
git log --oneline -5
git branch --show-current
git worktree list
npm.cmd run check:knowledge
npm.cmd run build
```

可以检查这些构建产物是否存在：

```text
dist/index.html
dist/search-index.json
dist/sitemap.xml
dist/rss.xml
dist/bible/index.html
```

允许新增或更新：

```text
docs/tasks/current.md
docs/knowledge/ROADMAP.md
```

如果需要记录验证结果，可以新增：

```text
docs/knowledge/POST_DEPLOY_CHECK.md
```

## 本次不允许操作

- 不修改文章。
- 不修改前台页面。
- 不修改 CSS。
- 不修改 Admin 逻辑。
- 不修改 Knowledge Layer 代码。
- 不新增功能。
- 不调用外部 API。
- 不访问外部网络。
- 不部署。
- 不 push。
- 不删除 worktree。
- 不删除 feature 分支。
- 不自动提交 commit，除非用户明确要求。

## 验收标准

必须确认：

- `git status --short` 为空。
- 当前分支是 `main`。
- `npm.cmd run check:knowledge` 通过。
- `npm.cmd run build` 通过。
- 构建页数仍为 188 或合理接近。
- `dist/search-index.json`、`dist/sitemap.xml`、`dist/rss.xml` 存在。
- 没有越界修改。
- 给出是否可以清理 worktree 的建议。

## 建议的清理手顺

只有在用户确认线上部署正常后，才执行：

```powershell
cd C:\Users\caoyi\Projects\各人网页项目
git worktree list
git worktree remove C:\Users\caoyi\Projects\各人网页项目-bible-knowledge
git branch -d feature/bible-knowledge-layer
```

如果 `git worktree remove` 提示目录有未清理文件，不要强制删除，先汇报。

## 完成后汇报格式

完成后请汇报：

1. 当前分支和 git 状态。
2. `check:knowledge` 结果。
3. build 结果。
4. 关键 dist 文件是否存在。
5. 是否发现问题。
6. 是否建议清理 worktree。
7. 清理命令建议。

不要提交、不要 push、不要删除 worktree，等待用户确认。
