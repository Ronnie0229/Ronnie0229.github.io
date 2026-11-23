# Hermes RETEST-02 分块清单独立核验

- 源文 `data/raw/分享/How Do We Grow in the Grace and Knowledge of Christ.en.txt`，8062 bytes、7958 字符、126 行，独立 SHA-256 `5142dc2fc01ba2afb9cc70bb9f6c2da8c2f17a5bcbf4e0c1a339f5c76a88c2e1`。
- 实际文件 `hermes-gemma4-retest-02/manifest.json` 存在，626 bytes，SHA-256 `017df95b4319130689bad4a4452454246a991099494ab8d154d41d54836e56c3`。
- `manifest.json` 所填源 SHA `50f1db48355d355608deb32f39b948ed7548ed3cd80912df6576be73bcd23b80` 与真实文件不符，FAIL。
- 分块行范围 1–32、33–75、76–126 完整且顺序无重复；按 `splitlines(keepends=True)` 拼接可无损恢复源文，PASS。
- 每块含换行符的实际字符数依次为 2073、2634、3251，与 manifest 填写的 2067、2624、3240 均不一致，FAIL。
- 原 task-03 自报不构成 PASS；`CHUNK_MANIFEST_VALIDATION_FAIL`。未发现中文分块候选或全部合并译文。保留已产生的 manifest 和失败 chronology；由 Hermes Telegram 自行调用工具修复源身份及计数，再检验、继续翻译。不可由 Website Owner 代修或代译。
