# URL Encoding Guidelines

## 目的

本项目存在中文路径，例如：

```text
/bible/罗马书/
```

这些中文 URL 在浏览器中可以正常访问，但在 Windows PowerShell、Codex、某些终端、任务文档读取或自动化检查中，可能因为编码处理不一致而出现 mojibake 乱码，例如：

```text
/bible/鄂鈴ｩｬ荵ｦ/
```

这种乱码通常不是网站路由、构建或部署问题，而是命令行 / 工具链在处理中文 URL 时发生的编码转换问题。

## 基本规则

以后凡是让 Codex、PowerShell、curl、自动化脚本或外部验证任务检查中文 URL 时，必须优先使用百分号编码 URL。

不要在命令行验证中直接使用：

```text
https://ronniecross.com/bible/罗马书/
```

应使用：

```text
https://ronniecross.com/bible/%E7%BD%97%E9%A9%AC%E4%B9%A6/
```

该 URL 是 `/bible/罗马书/` 的 UTF-8 百分号编码形式。

## 推荐检查方式

PowerShell / Codex 中检查中文 URL 时，优先使用：

```powershell
curl.exe -I "https://ronniecross.com/bible/%E7%BD%97%E9%A9%AC%E4%B9%A6/"
curl.exe -L "https://ronniecross.com/bible/%E7%BD%97%E9%A9%AC%E4%B9%A6/"
```

检查通过标准：

```text
HTTP 200 或最终跳转后 200
返回内容不是首页 fallback
HTML 中能看到目标页面标题或关键词，例如：罗马书
```

## 不要误判为部署问题

如果自动化检查中出现类似：

```text
https://ronniecross.com/bible/鄂鈴ｩｬ荵ｦ/
```

不要立即判断为线上部署失败。应先确认：

1. 原目标是否是中文 URL。
2. 是否发生了 mojibake 乱码。
3. 正确的百分号编码 URL 是否能访问。
4. sitemap / search-index / 浏览器直接访问是否正常。

只有在正确的百分号编码 URL 也访问失败时，才需要继续调查网站路由、构建或部署问题。

## 何时需要真正修复网站

只有出现以下情况，才考虑作为网站问题处理：

```text
浏览器点击中文 URL 也打不开
sitemap.xml 中中文路径本身乱码
search-index.json 中书卷名变乱码
Google Search Console 报大量乱码 URL
真实用户访问中文书卷页经常进入乱码路径
```

当前 Bible Knowledge Layer v1 的线上验证中，正确编码 URL 已确认正常：

```text
https://ronniecross.com/bible/%E7%BD%97%E9%A9%AC%E4%B9%A6/
HTTP 200
页面标题：罗马书 | 圣经书卷 | Ronnie
不是首页 fallback
```

因此，当前不需要修改网站代码或部署配置。

## 长期改进候选

如果未来希望彻底避免中文路径在工具链中产生编码问题，可以单独规划 URL 规范化任务，把书卷页 URL 改成英文 slug，例如：

```text
/bible/romans/
/bible/john/
/bible/acts/
/bible/genesis/
```

页面显示仍然保留中文：

```text
罗马书
约翰福音
使徒行传
创世记
```

该方案会改变公开 URL，需要同时处理：

```text
旧中文 URL 到新英文 URL 的重定向
sitemap.xml 更新
search-index.json 更新
内部链接更新
Google Search Console 观察
```

因此，这应作为独立任务执行，不应混入 Bible Knowledge Layer v1 的收尾工作。
