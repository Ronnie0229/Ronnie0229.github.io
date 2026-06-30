import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const POSTS_DIR = path.join(ROOT, "src", "content", "posts");
const REPORT_DIR = path.join(ROOT, "docs", "内容整理报告");
const REPORT_PATH = path.join(REPORT_DIR, "live-vs-local-posts.csv");
const LIVE_INDEX_URL = process.env.LIVE_INDEX_URL ?? "https://ronniecross.com/search-index.json";

function csvEscape(value) {
  const text = value == null ? "" : String(value);
  if (/[",\n\r]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function cleanMarkdown(markdown) {
  return (markdown ?? "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/[*_~|>#-]/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

function hashText(text) {
  return crypto.createHash("sha256").update(text, "utf8").digest("hex").slice(0, 16);
}

function parseFrontmatter(text) {
  const normalizedText = String(text ?? "").replace(/^\uFEFF/, "");
  const match = normalizedText.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  const data = {};
  let body = normalizedText;
  if (!match) return { data, body };
  body = normalizedText.slice(match[0].length);
  for (const line of match[1].split(/\r?\n/)) {
    const item = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/);
    if (!item) continue;
    const key = item[1];
    let value = item[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (value === "true") value = true;
    if (value === "false") value = false;
    data[key] = value;
  }
  return { data, body };
}

function normalizeDate(value) {
  if (!value) return "";
  const text = String(value);
  const match = text.match(/^\d{4}-\d{2}-\d{2}/);
  return match ? match[0] : text;
}

function compareKey(slug) {
  return String(slug ?? "")
    .normalize("NFC")
    .replace(/[｜|、，,？?：:；;]/g, "")
    .trim();
}

function localPosts() {
  const posts = [];
  for (const file of fs.readdirSync(POSTS_DIR).filter((name) => name.endsWith(".md")).sort()) {
    const fullPath = path.join(POSTS_DIR, file);
    const raw = fs.readFileSync(fullPath, "utf8");
    const { data, body } = parseFrontmatter(raw);
    const cleanedBody = cleanMarkdown(body);
    posts.push({
      slug: file.replace(/\.md$/, ""),
      file: path.relative(ROOT, fullPath).replace(/\\/g, "/"),
      title: data.title ?? "",
      date: normalizeDate(data.date),
      category: data.category ?? "",
      scripture: data.scripture ?? "",
      description: data.description ?? "",
      draft: data.draft === true,
      bodyHash: hashText(cleanedBody),
      bodyLength: cleanedBody.length,
    });
  }
  return posts;
}

function comparePost(local, live) {
  if (!local && live) return { status: "live_only", note: "Article exists on live site but no local markdown file has the same slug." };
  if (local && !live) return { status: "local_only", note: local.draft ? "Local draft is not expected to appear on live site." : "Local markdown exists but live search index has no same slug." };

  const diffs = [];
  if ((local.title ?? "") !== (live.title ?? "")) diffs.push("title");
  if (normalizeDate(local.date) !== normalizeDate(live.date)) diffs.push("date");
  if ((local.category ?? "") !== (live.category ?? "")) diffs.push("category");
  if ((local.scripture ?? "") !== (live.scripture ?? "")) diffs.push("scripture");
  if ((local.description ?? "") !== (live.description ?? "")) diffs.push("description");
  if (local.bodyHash !== hashText(live.body ?? "")) diffs.push("body");

  if (!diffs.length) return { status: "same", note: "" };
  if (diffs.length === 1 && diffs[0] === "body") return { status: "content_diff", note: "Cleaned body text differs." };
  if (diffs.every((item) => item !== "body")) return { status: "metadata_diff", note: `Different fields: ${diffs.join(", ")}` };
  return { status: "metadata_and_content_diff", note: `Different fields: ${diffs.join(", ")}` };
}

async function main() {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
  const response = await fetch(LIVE_INDEX_URL, { headers: { "Accept": "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to fetch ${LIVE_INDEX_URL}: ${response.status} ${response.statusText}`);
  }
  const livePosts = await response.json();
  if (!Array.isArray(livePosts)) {
    throw new Error(`Live index is not an array: ${LIVE_INDEX_URL}`);
  }

  const localBySlug = new Map(localPosts().map((post) => [compareKey(post.slug), post]));
  const liveBySlug = new Map(livePosts.map((post) => [compareKey(post.slug), {
    slug: post.slug,
    title: post.title ?? "",
    date: normalizeDate(post.date),
    category: post.category ?? "",
    scripture: post.scripture ?? "",
    description: post.description ?? "",
    body: post.body ?? "",
    bodyLength: (post.body ?? "").length,
  }]));

  const keys = Array.from(new Set([...localBySlug.keys(), ...liveBySlug.keys()])).sort();
  const rows = [];
  const counts = new Map();
  for (const key of keys) {
    const local = localBySlug.get(key);
    const live = liveBySlug.get(key);
    const result = comparePost(local, live);
    counts.set(result.status, (counts.get(result.status) ?? 0) + 1);
    rows.push({
      compare_key: key,
      local_slug: local?.slug ?? "",
      live_slug: live?.slug ?? "",
      status: result.status,
      local_file: local?.file ?? "",
      live_url: live ? `https://ronniecross.com/posts/${live.slug}/` : "",
      local_title: local?.title ?? "",
      live_title: live?.title ?? "",
      local_date: local?.date ?? "",
      live_date: live?.date ?? "",
      local_category: local?.category ?? "",
      live_category: live?.category ?? "",
      local_scripture: local?.scripture ?? "",
      live_scripture: live?.scripture ?? "",
      local_description: local?.description ?? "",
      live_description: live?.description ?? "",
      local_body_length: local?.bodyLength ?? "",
      live_body_length: live?.bodyLength ?? "",
      note: result.note,
    });
  }

  const headers = [
    "compare_key", "local_slug", "live_slug", "status", "local_file", "live_url", "local_title", "live_title", "local_date", "live_date",
    "local_category", "live_category", "local_scripture", "live_scripture", "local_description", "live_description", "local_body_length", "live_body_length", "note"
  ];
  const csv = [headers.join(","), ...rows.map((row) => headers.map((header) => csvEscape(row[header])).join(","))].join("\n") + "\n";
  fs.writeFileSync(REPORT_PATH, "\ufeff" + csv, "utf8");

  console.log(`Live index: ${LIVE_INDEX_URL}`);
  console.log(`Local posts: ${localBySlug.size}`);
  console.log(`Live posts: ${liveBySlug.size}`);
  for (const [status, count] of Array.from(counts.entries()).sort()) {
    console.log(`${status}: ${count}`);
  }
  console.log(`Report: ${path.relative(ROOT, REPORT_PATH).replace(/\\/g, "/")}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
