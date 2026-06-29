# SEO.md

本文件是 RonnieCross 网站 SEO 规范入口。SEO 修改必须兼顾搜索引擎、RSS、站内搜索、读者分享和长期可维护性。

## 基本原则

1. 每篇正式文章必须有清晰标题。
2. 每篇正式文章必须有准确 description。
3. 每篇文章必须有稳定 slug / 文件名。
4. 每篇文章必须有日期。
5. 分类和标签要帮助读者理解内容，不要堆砌关键词。
6. 页面 H1 只出现一次。
7. H2 / H3 用于正文结构，不要只为视觉效果乱用标题。
8. 图片必须有有意义的 alt。
9. 不创建大量重复页面。
10. 不为了 SEO 牺牲文章真实性和可读性。

## 标题规范

推荐：

- `罗马书 12:9-21：真诚的爱如何活出来`
- `在焦虑中重新学习信靠`
- `约翰福音 8:31-36：真正的自由从哪里来`

避免：

- `讲章整理`
- `主日信息`
- `一些感想`
- `文章1`

## Description 规范

description 建议 80-160 个中文字符，准确概括文章，不要堆叠关键词。

示例：

```text
本文从罗马书 12:9-21 出发，思想真诚的爱如何在真实生活中被操练，并反思信仰如何更新我们与人相处的方式。
```

避免：

- 太短：`罗马书文章。`
- 太空泛：`这是一篇非常好的文章，希望大家喜欢。`
- 关键词堆砌：`罗马书, 圣经, 基督教, 讲道, 信仰, 爱, 教会...`

## Slug / 文件名规范

文章文件建议：

```text
YYYY-MM-DD-short-topic.md
```

例如：

```text
2026-06-20-romans-12-genuine-love.md
```

原则：

- 使用小写英文、数字、连字符。
- 不使用空格。
- 不使用中文文件名作为正式发布 slug，除非项目已明确支持并验证。
- 发布后不要轻易改 slug，避免旧链接失效。

## 分类和标签

分类用于大方向，标签用于细分主题。

分类示例：

- 信仰随笔
- 讲道整理
- 圣经学习
- 生命反思
- 读书笔记

标签示例：

- 罗马书
- 约翰福音
- 焦虑
- 爱
- 祷告
- 盼望

原则：

- 标签数量适中，通常 2-6 个。
- 不为 SEO 堆砌无关标签。
- 同一概念尽量使用统一写法。

## 网站级 SEO 文件

相关页面和文件：

- `src/pages/sitemap.xml.ts`
- `src/pages/rss.xml.ts`
- `src/pages/search-index.json.ts`
- `src/pages/deployment.json.ts`
- `assets/robots.txt`
- `assets/site.webmanifest`
- `src/layouts/BaseLayout.astro`

修改 SEO 时，应检查这些文件是否与当前站点结构一致。

## Favicon / 搜索结果图标规则

搜索结果前的网站图标通常来自页面 head 中的 favicon 声明，以及站点 manifest / app icon 相关资源。处理搜索结果图标时必须遵守品牌资产规则：

1. 不得为了修正搜索图标而临时新建、AI 重绘或重新设计 favicon。
2. favicon、apple-touch-icon、manifest icons 必须使用用户确认过的正式 Logo，或从正式 Logo 等比例裁切 / 缩放生成尺寸版本。
3. 修改前必须检查 `src/layouts/BaseLayout.astro`、`assets/site.webmanifest` 和 `assets/images/` 中实际被引用的图标文件。
4. 修改后必须确认浏览器标签页显示的是正式 Logo，因为浏览器标签页和搜索结果可能使用同一 favicon 入口。
5. 搜索结果图标不会在发布后立即刷新；需要等待搜索引擎重新抓取，也可在 Search Console 请求首页重新编入索引。

## 文章页 SEO 检查

- [ ] title 是否准确。
- [ ] description 是否完整。
- [ ] date 是否正确。
- [ ] category 是否正确。
- [ ] tags 是否相关。
- [ ] URL 是否稳定。
- [ ] 页面是否只有一个 H1。
- [ ] 正文标题层级是否合理。
- [ ] RSS 是否能包含文章。
- [ ] sitemap 是否能包含文章。
- [ ] 站内搜索索引是否能包含文章。

## Google Search Console 问题处理

如果 Search Console 提示：

- 备用网页（有适当的规范标记）
- 网页会自动重定向
- 由于遇到其他 4xx 问题而被屏蔽

处理时先判断是否为预期行为。

检查顺序：

1. 页面是否应该被索引。
2. URL 是否有重复版本。
3. 是否有 canonical。
4. 是否发生重定向。
5. 页面是否返回 200。
6. 是否被 robots 或 noindex 阻止。
7. sitemap 是否包含正确 URL。
8. 内链是否指向最终 URL，而不是旧 URL。

不要为了消除 Search Console 提示而把不该索引的后台、API、重复页暴露给搜索引擎。

## 修改 SEO 后的验证

- [ ] `npm run build` 通过。
- [ ] 生成的 sitemap 正常。
- [ ] RSS 正常。
- [ ] 站内搜索索引正常。
- [ ] 文章页 title / description 正常。
- [ ] 不影响后台、Functions 或 API。

## Frontmatter 最低要求

发布文章时，至少要检查这些字段：

| 字段 | 作用 | 要求 |
| --- | --- | --- |
| `title` | 页面主标题和列表标题 | 清楚、具体，不要只写笼统主题。 |
| `description` | 搜索摘要和分享摘要 | 1 到 2 句话说明文章核心内容。 |
| `date` | 发布时间和排序依据 | 使用稳定日期格式，避免随意改动历史文章日期。 |
| `tags` | 主题标签 | 少量精准标签即可，不要堆砌。 |
| `category` | 文章分类 | 必须使用站点已有分类，新增分类前先确认。 |

如果新增字段或调整 schema，要同步检查 `src/content/config.ts`、文章列表页和构建结果。

## Search Console 索引规则

- `https://ronniecross.com/` 是正式首页，`http://` 和 `www` 版本自动重定向属于正常现象，不需要单独收录。
- 正文文章应使用 `/posts/<slug>/` 这类稳定地址进入 sitemap，并让 Google 索引这个地址。
- `/posts/?category=...`、`/posts/?focus=...` 只是列表页筛选和返回定位，canonical 指向 `/posts/`，属于备用页，不作为独立索引页。
- `/search/?q=...` 只是站内搜索结果页，不作为独立索引页。
- `/api/`、`/admin/`、`/deployment.json`、`/search-index.json` 这类接口或后台数据不作为网页索引对象。
- robots.txt 应持续屏蔽 `/admin/`、`/api/`、`/posts/?*`、`/search/?*`，避免 Google 把接口和参数页当成网页抓取。
- 站内链接、sitemap、RSS 只放正式可索引 URL，不放筛选参数、focus 参数、API 地址。
