# Article Read-Aloud — REAL_USAGE Minimal Device Acceptance Checklist

日期：2026-10-10
模式：`REAL_USAGE / MAINTENANCE / ISSUE_DRIVEN_REPAIR`

本清单只用于现有生产功能的真实人工验收，不触发新功能建设、批量生成或自动发布。

## 当前已机械确认

- 两篇生产文章都存在 `audioUrl`。
- 线上页面实际渲染原生 `<audio controls preload="metadata">`。
- Pilot 1 R2：Range `206`，`Content-Type=audio/mpeg`，总 bytes=`7337901`。
- Pilot 2 R2：Range `206`，`Content-Type=audio/mpeg`，总 bytes=`4848045`。
- 5 分钟 thin tick LaunchAgent：interval=`300s`，last exit=`0`。
- 当前 durable workflow：`COMPLETE`，cleanup=`CLEANUP_ELIGIBLE`，open_repairs=`0`。

## 最小人工验收矩阵

优先使用两篇现有生产文章，不新增测试文章：

1. iPhone Safari
   - 页面能看到“听文章”播放器；
   - 点击播放后能正常出声；
   - 暂停后保持当前位置；
   - 向前 seek 约 1–2 分钟后能继续播放；
   - 向后 seek 后能继续播放；
   - 锁屏/切后台后回到 Safari，播放器没有异常重置；
   - 连续播放至少 10 分钟，无无故停止、重复、跳段或明显卡死。

2. macOS Safari
   - 播放 / 暂停正常；
   - seek 到中段正常；
   - seek 接近结尾正常；
   - 连续播放至少 10 分钟；
   - 刷新页面后允许按浏览器默认行为重置，不要求自定义记忆进度。

3. Chrome（macOS 或 iPhone 可用环境）
   - 播放 / 暂停正常；
   - seek 正常；
   - 连续播放至少 10 分钟；
   - 无跨域、媒体格式、Range 或加载错误。

## 建议先验收两篇中的至少一篇完整矩阵

- Pilot 1：《基督徒不应该做计划吗？》
- Pilot 2：《骆驼穿过针眼是什么意思》

若第一篇在 iPhone Safari + macOS Safari + Chrome 全部通过，再用第二篇做快速交叉确认：播放、seek、5–10 分钟连续播放即可。

## 判定

`PASS_REAL_DEVICE_ACCEPTANCE`：
- 上述三个浏览器/设备面均可播放、暂停、seek；
- 至少一次真实连续播放 >=10 分钟；
- 无重复生成、无音频 URL 错绑、无明显兼容性故障。

`ISSUE_DRIVEN_REPAIR_REQUIRED`：
- 只有出现可复现的真实兼容性缺陷时才进入代码修复；
- 记录设备、OS、浏览器版本、文章、发生时间点、现象；
- 优先做最小修复，不扩建播放器框架、监控平台或调度系统。

## 人工验收结果 — 2026-10-10

PROJECT_OWNER 已明确确认上述实机验收项目全部通过。

正式判定：`PASS_REAL_DEVICE_ACCEPTANCE`。

已通过：
- iPhone Safari：播放器可见、播放/暂停正常、前后 seek 正常、锁屏/后台返回后无异常重置、连续播放至少 10 分钟正常；
- macOS Safari：播放/暂停、中段 seek、接近结尾 seek、连续播放至少 10 分钟正常；
- Chrome：播放/暂停、seek、连续播放至少 10 分钟正常，未发现媒体/CORS/Range 加载异常；
- 无重复生成、无音频 URL 错绑、无明显兼容性故障。

## 剩余质量保留项

- Pilot 2 完整人工整篇试听仍保持现有 `PROVISIONAL_PROJECT_OWNER_PASS_NO_FULL_LISTENING` 状态；本次设备矩阵 PASS 不等于 Pilot 2 全文内容/发音完整试听 PASS。
