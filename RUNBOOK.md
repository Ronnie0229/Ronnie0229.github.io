# RUNBOOK.md

## 用途

本文件是 RonnieCross 项目的日常操作手册。任何账号接手项目后，如果需要运行、构建、预览、整理内容或排查常见问题，应优先阅读本文件。

## 工作目录

正式工作目录：

```text
C:\Users\caoyi\Projects\各人网页项目
```

不要在 NAS 路径中运行 Git、Node、Astro、Codex 或文件监听。

## 初次准备

安装 Node 依赖：

```shell
npm install
```

安装 Python 依赖：

```shell
python -m pip install -r requirements.txt
```

## 日常开发命令

启动本地开发服务器：

```shell
npm run dev
```

默认访问：

```text
http://127.0.0.1:4321
```

构建网站：

```shell
npm run build
```

预览构建结果：

```shell
npm run preview
```

从 GitHub 同步：

```shell
npm run sync
```

## 内容处理命令

只读检查分享收件目录：

```shell
python scripts/content_workflow.py inspect share
```

导入分享资料：

```shell
python scripts/content_workflow.py ingest share
```

发布分享文章：

```shell
python scripts/content_workflow.py publish share
```

只读检查讲道收件目录：

```shell
python scripts/content_workflow.py inspect sermon
```

导入讲道资料：

```shell
python scripts/content_workflow.py ingest sermon --date YYYYMMDD --title "经文与标题" --speaker "讲员"
```

归档讲道资料：

```shell
python scripts/content_workflow.py archive-sermon --folder "data/raw/教会讲道/<folder>"
```

发布讲道文章：

```shell
python scripts/content_workflow.py publish sermon
```

补充文章 ID：

```shell
node scripts/add_article_ids.mjs
```

## 每次任务完成前的最低验证

一般任务至少执行：

```shell
npm run build
```

如果本轮只改纯文档，可以根据情况不运行构建，但必须在 `docs/tasks/current.md` 写明原因。

如果涉及内容导入或文章发布，必须检查：

- `data/raw/` 是否保留原始资料。
- `data/processed/` 是否生成对应中间稿。
- `src/content/posts/` 是否只出现预期文章变更。
- `docs/内容整理报告/` 是否更新。
- `node scripts/add_article_ids.mjs` 是否已运行。
- `npm run build` 是否通过。

## Git 工作建议

开始前：

```shell
git status
git branch
```

不建议直接在 `main` 上做大规模修改。更安全的方式是使用任务分支：

```shell
git checkout main
git pull
git checkout -b task/<task-name>-YYYYMMDD
```

任务完成后，更新：

- `docs/tasks/current.md`
- 必要时更新 `STATUS.md`
- 必要时更新对应专项文档

## 常见问题

### Astro 内容缓存异常

如果删除或重命名文章后，构建提示重复 ID 或内容未刷新，可能是本地 `.astro/data-store.json` 缓存问题。确认不是源码问题后，可以清除本地缓存再构建。

### Windows 中文乱码

Windows 控制台可能显示中文乱码。检查文件内容时，优先使用支持 UTF-8 的编辑器或工具。

### NAS 安全边界

`\\RonnieNAS\share` 是受保护归档区，只允许新增和读取。不要移动、删除、重命名或覆盖其中资料。

### 原始资料保护

`data/raw/` 是原始资料保存区，不能随意改写。遇到同名目标时应停止并检查，不要自动覆盖。

## 任务结束前最低检查清单

1. 运行 `git status --short`，确认改动范围符合任务要求。
2. 如果是文档任务，确认没有修改 `src/`、`functions/`、`assets/`、`scripts/`、`data/raw/`、`data/processed/`、`wrangler.jsonc`。
3. 至少运行 `npm run build`，并把结果写入 `STATUS.md` 和 `docs/tasks/current.md`。
4. 不在未授权情况下执行 `git push`、`npm run deploy` 或 `wrangler deploy`。
5. 需要人工确认的事项要写清楚，不要藏在对话里。

## 后端与 Cloudflare 提醒

Cloudflare Pages、Functions、D1、环境变量和 `wrangler.jsonc` 属于部署与后端边界。涉及这些内容时，要先说明风险和验证方法。普通文档任务默认只记录说明，不改配置。