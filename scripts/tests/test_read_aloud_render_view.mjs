import test from "node:test";
import assert from "node:assert/strict";
import { renderPost } from "../read_aloud_render_view.mjs";

test("keeps semantic paragraphs, heading, quote, parallel list and prayer", () => {
  const source = '---\narticleId: "post-demo"\ntitle: "测试"\n---\n讲道题目\n\n> 经文全文。\n\n今天有三个要点。\n\n- 一、第一\n- 二、第二\n- 三、第三\n\n**祷告**：阿们。\n';
  const out = renderPost(source);
  assert.equal(out.article_id, "post-demo");
  for (const text of ["讲道题目","经文全文。","今天有三个要点。","一、第一","二、第二","三、第三","祷告：阿们。"]) assert.ok(out.text.includes(text));
  assert.equal(out.paragraph_count, 7);
});

test("fail-closed for code, oversized and already audio bound", () => {
  const base = '---\narticleId: "post-demo"\n---\n正文。\n';
  assert.throws(() => renderPost(base.replace("正文。", "~~~js\nalert(1)\n~~~")), /MANUAL_RENDER_REVIEW_REQUIRED_code/);
  assert.throws(() => renderPost(base.replace("正文。", "中".repeat(90000))), /TTS_RENDER_BYTE_LIMIT/);
  assert.throws(() => renderPost(base.replace('articleId: "post-demo"', 'articleId: "post-demo"\naudioUrl: "https://audio.example/a.mp3"')), /AUDIO_ALREADY_BOUND/);
});
