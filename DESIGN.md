# DESIGN.md

本文件是 RonnieCross 网站设计规范的项目级入口。详细设计规格和素材见：`风格重新设计素材/ronniecross_astro_design_spec.md`。

## 设计定位

RonnieCross 是信仰随笔、圣经学习、讲道整理和长文阅读类网站。设计目标是安静、柔和、适合阅读，而不是企业官网、科技博客、图片墙或强视觉营销页。

关键词：

- 圣经学习
- 深蓝
- 白底
- 圆润
- 安静
- 长文阅读
- 书桌 / 灯光 / 笔记
- 少量金色点缀

避免：

- 绿色田园风作为主视觉
- 强科技感 / 霓虹色
- 大量文章缩略图
- 复杂动画
- 高对比刺眼配色

## 布局原则

桌面端优先使用左侧 Sidebar + 主内容区布局：

- Sidebar：Logo、站点名、导航、简短说明或引用。
- Main：顶部导航、Hero、最新文章、辅助卡片、Footer。

移动端应转为单列结构：

- 顶部 Logo + 站点名 + 导航入口
- Hero
- 文章列表
- 关于 / 分类 / 辅助信息

## 深色主题

深色主题方向：Blue Bible Study。

特征：

- 深海蓝背景
- 打开的圣经 / 书桌 / 暖色台灯氛围
- 白色或浅灰正文
- 圆润卡片
- 少量金色点缀

金色只用于：

- 当前导航下划线
- 小图标
- 按钮强调
- 引用符号
- 少量状态点

不要大面积使用金色。

推荐 token 以 `风格重新设计素材/ronniecross_astro_design_spec.md` 为准，核心颜色包括：

- 背景：`#061625`、`#0A1D30`
- 卡片：`rgba(12, 31, 50, 0.82)`
- 正文：`#F5F7FA`
- 次级文字：`#B8C4D4`
- 金色：`#D7A84F`

## 浅色主题

浅色主题方向：White Bible Study。

特征：

- 白底
- 深蓝色正文和按钮
- 少量金色点缀
- 圣经学习书桌背景
- 清爽、安静、适合长文阅读

浅色版不要变成绿色系风格。

核心颜色包括：

- 背景：`#FFFFFF`
- 次背景：`#F7F9FC`
- 正文：`#0A1D30`
- 次级文字：`#516070`
- 主色：`#0E3A67`
- 金色：`#D7A84F`

## Logo 规范

使用用户确认的 R + Cross Logo，不要用 AI 重新绘制 Logo。

现有素材：

- `assets/images/ronniecross-logo-theme-dark.jpg`
- `assets/images/ronniecross-logo-theme-light.jpg`
- `assets/images/ronniecross-logo-theme-dark-transparent.png`
- `assets/images/ronniecross-logo-theme-light-transparent.png`
- `assets/images/ronniecross-mark.png`
- `风格重新设计素材/深色logo.jpg`
- `风格重新设计素材/浅色logo.jpg`

原则：

1. 深浅色只调整颜色与背景，不改变 Logo 的比例、粗细和构图。
2. 不要重新生成形状不同的 R 或十字架。
3. Logo、favicon、apple-touch-icon、manifest icons 都属于受保护品牌资产；不得 AI 重绘、临时新建替代图标或重新设计图标。
4. favicon / app icon 只能使用用户确认过的正式 Logo 文件，或从正式 Logo 等比例裁切、缩放生成尺寸版本，不得改变构图、颜色逻辑或视觉风格。
5. 修改 favicon 前必须先确认浏览器标签页会显示哪个文件，避免把搜索结果图标修正误做成重新设计 favicon。
6. 组件层面优先修改 `src/components/Logo.astro`，不要复制多个失控版本。

## 图片和背景

背景应服务阅读，不应抢正文注意力。

可使用：

- 圣经学习书桌
- 打开的圣经
- 温暖灯光
- 笔记本 / 手写笔记
- 柔和虚化背景

避免：

- 与信仰随笔无关的装饰图
- 过亮、过花、对比过强的背景
- 让正文可读性下降的图片

## 卡片、圆角和玻璃感

当前偏好的视觉包括：

- 圆润卡片
- 柔和阴影
- 轻微磨砂 / 玻璃感
- 悬浮层次
- 不夸张的立体感

推荐：

- 小圆角：12px
- 中圆角：18px
- 大圆角：24px
- 超大圆角：32px

磨砂效果要克制，不能牺牲文字清晰度。

## 主题切换

网站应支持深浅模式，并优先允许自动跟随设备系统设置。

建议逻辑：

1. 用户手动选择时，优先使用用户选择。
2. 用户未选择时，跟随 `prefers-color-scheme`。
3. 主题切换不要造成页面闪烁。

相关组件：

- `src/components/ThemeToggle.astro`
- `src/layouts/BaseLayout.astro`
- `src/styles/tokens.css`
- `src/styles/global.css`

## 修改设计时的检查清单

- [ ] 是否仍然符合“安静、柔和、适合长文阅读”。
- [ ] 深色版是否仍为深蓝圣经学习氛围。
- [ ] 浅色版是否仍为白底深蓝阅读风格。
- [ ] 金色是否只是点缀，而非大面积主色。
- [ ] Logo 是否没有被重绘变形。
- [ ] 移动端是否可读。
- [ ] 文章页正文宽度、行距、段距是否舒适。
- [ ] `npm run build` 是否通过。

## 设计事实来源

设计相关事实来源优先级：

1. 当前代码实现和现有素材。
2. `DESIGN.md`。
3. `docs/ui-spec.md`。
4. `风格重新设计素材/ronniecross_astro_design_spec.md`。
5. 过去聊天记录或效果图描述。

## 已有设计素材

当前仓库里已经有这些设计参考，后续改版应优先复用，不要重新发明一套风格：

| 文件 | 用途 |
| --- | --- |
| `风格重新设计素材/ronniecross_astro_design_spec.md` | Astro 站点视觉规范与页面改造说明。 |
| `风格重新设计素材/深色效果图.PNG` | 深色主题视觉参考。 |
| `风格重新设计素材/浅色效果图.PNG` | 浅色主题视觉参考。 |
| `assets/images/ronniecross-logo-theme-dark.jpg` | 深色主题 Logo 素材。 |
| `assets/images/ronniecross-logo-theme-light.jpg` | 浅色主题 Logo 素材。 |

设计任务开始前，先确认这些素材是否仍是最新基准；只有用户明确要求时，才另起一套视觉方向。