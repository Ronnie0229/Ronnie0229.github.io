# Ronnie Personal Homepage

Ronnie 的个人主页与讲道文章站，使用 Astro 构建，文章内容使用 Markdown 管理。

## 本地预览

```powershell
npm.cmd install
npm.cmd run dev
```

打开：

```text
http://127.0.0.1:4321
```

## 添加文章

在 `src/content/posts/` 目录中新建 Markdown 文件，并填写标题、摘要、日期和标签。

也可以把原始讲道资料放在 `教会讲道/`，然后运行：

```powershell
& "C:\Users\caoyi\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" scripts\import_sermons.py
```

脚本会把整理后的 Markdown 输出到 `整理后的讲道文章/`，并同步到网站文章目录。

## 构建

```powershell
npm.cmd run build
```
