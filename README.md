# Ronnie 个人文章站

使用 Astro 构建的中文文章网站，部署到 Cloudflare Pages。

## 本地运行

```powershell
npm.cmd install
npm.cmd run dev
```

浏览器打开 `http://127.0.0.1:4321`。

## 构建

```powershell
npm.cmd run build
```

构建结果输出到 `dist/`。

## 内容维护

- 网站正式文章：`src/content/posts/`
- 原始讲道资料：`data/raw/教会讲道/`
- 原始分享资料：`data/raw/分享/`
- 整理后的中间文章：`data/processed/`
- 整理报告：`docs/内容整理报告/`
- 导入脚本：`scripts/import_sermons.py`、`scripts/import_shares.py`
- 数据库迁移：`scripts/migrations/`

完整目录用途参见 `docs/目录说明.md`。
