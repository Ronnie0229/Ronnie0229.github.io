#!/usr/bin/env node
/* Deterministic TTS render view from an exact post. No standard scripture retranslation. */
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { unified } from "unified";
import remarkParse from "remark-parse";

function fail(code) { throw new Error(code); }
const digest = b => crypto.createHash("sha256").update(b).digest("hex");
function inline(n) {
  if (n.type === "text" || n.type === "inlineCode") return n.value || "";
  if (n.type === "break") return "\n";
  if (n.type === "link" || n.type === "linkReference") return (n.children || []).map(inline).join("");
  if (n.type === "image" || n.type === "imageReference") return n.alt || "";
  if (["strong","emphasis","delete","paragraph","heading","root","blockquote","listItem"].includes(n.type)) return (n.children || []).map(inline).join("");
  fail("UNSUPPORTED_INLINE_NODE_" + n.type);
}
function blocks(n, output) {
  if (["paragraph","heading"].includes(n.type)) {
    const value = (n.children || []).map(inline).join("").trim();
    if (value) output.push(value);
    return;
  }
  if (n.type === "root" || n.type === "blockquote" || n.type === "list" || n.type === "listItem") {
    for (const c of n.children || []) blocks(c, output);
    return;
  }
  if (n.type === "thematicBreak") return;
  if (n.type === "code" || n.type === "html" || n.type === "table" || n.type === "definition") fail("MANUAL_RENDER_REVIEW_REQUIRED_" + n.type);
  fail("UNSUPPORTED_BLOCK_NODE_" + n.type);
}
export function renderPost(raw) {
  if (!raw.startsWith("---\n")) fail("FRONTMATTER_MISSING");
  const stop = raw.indexOf("\n---\n", 4);
  if (stop < 0) fail("FRONTMATTER_NOT_CLOSED");
  const frontmatter = raw.slice(4, stop);
  const body = raw.slice(stop + 5);
  const articleId = frontmatter.match(/^articleId:\s*["']?(post-[a-zA-Z0-9-]+)["']?\s*$/m)?.[1];
  if (!articleId) fail("ARTICLE_ID_MISSING");
  if (/^audioUrl:\s*\S/m.test(frontmatter)) fail("AUDIO_ALREADY_BOUND");
  const tree = unified().use(remarkParse).parse(body);
  const paragraphs = [];
  blocks(tree, paragraphs);
  if (!paragraphs.length) fail("RENDER_EMPTY");
  const text = paragraphs.join("\n\n") + "\n";
  if (Buffer.byteLength(text, "utf8") > 262144) fail("TTS_RENDER_BYTE_LIMIT");
  return { article_id: articleId, post_sha256: digest(raw), render_sha256: digest(text), text, paragraph_count: paragraphs.length };
}
if (process.argv[1] && fs.realpathSync(path.resolve(process.argv[1])) === fs.realpathSync(fileURLToPath(import.meta.url))) {
  const file = process.argv[2];
  if (!file) fail("POST_ARGUMENT_REQUIRED");
  const content = file === "-" ? fs.readFileSync(0, "utf8") : fs.readFileSync(file, "utf8");
  const rendered = renderPost(content);
  // No implicit files, provider requests or production effects.
  console.log(JSON.stringify(rendered));
}
