import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createMarkdownProcessor } from "@astrojs/markdown-remark";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SERMON_VALIDATOR = path.join(ROOT, "scripts", "validate_sermon_presentation.mjs");

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  if (!args.source) throw new Error("--source is required");
  if (!args["candidate-id"]) throw new Error("--candidate-id is required");
  if (!["share_article", "sermon"].includes(args.profile)) {
    throw new Error("--profile must be share_article or sermon");
  }
  return args;
}

function stripFrontmatter(markdown) {
  const normalized = markdown.replace(/^\uFEFF/, "");
  if (!normalized.startsWith("---\n") && !normalized.startsWith("---\r\n")) return normalized;
  const lines = normalized.split(/\r?\n/);
  for (let index = 1; index < lines.length; index += 1) {
    if (lines[index].trim() === "---") return lines.slice(index + 1).join("\n");
  }
  throw new Error("frontmatter is not closed");
}

function plainText(html) {
  return html.replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();
}

function countMatches(value, regex) {
  return [...value.matchAll(regex)].length;
}

function sourceBlockquoteCount(lines) {
  let count = 0;
  let inQuote = false;
  for (const line of lines) {
    const quoted = /^\s*>/.test(line);
    if (quoted && !inQuote) count += 1;
    inQuote = quoted;
  }
  return count;
}

async function validateShare(sourcePath, source, candidateId) {
  const body = stripFrontmatter(source);
  const lines = body.split(/\r?\n/);
  const sourceHeadings = [...body.matchAll(/^\s*(#{2,3})\s+(.+?)\s*$/gm)]
    .map((match) => ({ depth: match[1].length, text: match[2].trim() }));
  const sourceListItems = countMatches(body, /^\s*(?:[-+*]|\d+[.)])\s+\S/gm);
  const sourceBlockquotes = sourceBlockquoteCount(lines);
  const internalNoteFailures = [];
  for (let index = 0; index < lines.length; index += 1) {
    if (/(?:NEEDS_METADATA|PENDING_METADATA|待元数据(?:最终)?确认|待补元数据)/i.test(lines[index])) {
      internalNoteFailures.push({ line: index + 1, text: lines[index].trim() });
    }
  }

  const processor = await createMarkdownProcessor({});
  const rendered = await processor.render(body);
  const html = rendered.code;
  const renderedHeadings = [...html.matchAll(/<h([23])\b[^>]*>([\s\S]*?)<\/h\1>/gi)]
    .map((match) => ({ depth: Number(match[1]), text: plainText(match[2]) }));
  const renderedListItems = countMatches(html, /<li\b/gi);
  const renderedBlockquotes = countMatches(html, /<blockquote\b/gi);
  const renderedParagraphs = countMatches(html, /<p\b/gi);
  const renderedTextChars = plainText(html).replace(/\s+/g, "").length;

  const failures = [];
  if (!renderedTextChars) failures.push({ kind: "empty_rendered_body" });
  if (JSON.stringify(sourceHeadings) !== JSON.stringify(renderedHeadings)) {
    failures.push({ kind: "heading_render_integrity", source: sourceHeadings, rendered: renderedHeadings });
  }
  if (sourceListItems !== renderedListItems) {
    failures.push({ kind: "list_render_integrity", source_list_items: sourceListItems, rendered_list_items: renderedListItems });
  }
  if (sourceBlockquotes !== renderedBlockquotes) {
    failures.push({ kind: "blockquote_render_integrity", source_blockquotes: sourceBlockquotes, rendered_blockquotes: renderedBlockquotes });
  }
  if (internalNoteFailures.length) failures.push({ kind: "internal_workflow_notes", items: internalNoteFailures });

  const sourceParagraphBlocks = body.split(/\n\s*\n/).filter((block) => {
    const trimmed = block.trim();
    if (!trimmed) return false;
    return !/^(?:#{1,6}\s|>|(?:[-+*]|\d+[.)])\s|---\s*$|\x60{3}|~~~|\|.*\|$)/.test(trimmed);
  }).length;
  const nonListQuoteHtml = html
    .replace(/<blockquote\b[^>]*>[\s\S]*?<\/blockquote>/gi, "")
    .replace(/<(?:ul|ol)\b[^>]*>[\s\S]*?<\/(?:ul|ol)>/gi, "");
  const renderedPlainParagraphs = countMatches(nonListQuoteHtml, /<p\b/gi);
  if (sourceParagraphBlocks !== renderedPlainParagraphs) {
    failures.push({
      kind: "paragraph_boundary_integrity",
      source_paragraph_blocks: sourceParagraphBlocks,
      rendered_plain_paragraphs: renderedPlainParagraphs
    });
  }

  return {
    gate: "content-publication-presentation-structure/v1",
    profile: "share_article",
    candidate_id: candidateId,
    status: failures.length ? "CONTENT_PRESENTATION_STRUCTURE_FAIL" : "CONTENT_PRESENTATION_STRUCTURE_PASS",
    completion_ceiling: failures.length ? "publication_structure_blocked" : "publication_structure_ready",
    source: { path: sourcePath, sha256: sha256(source) },
    rendered_html: { engine: "@astrojs/markdown-remark/createMarkdownProcessor", sha256: sha256(html) },
    metrics: {
      source_heading_count: sourceHeadings.length,
      rendered_heading_count: renderedHeadings.length,
      source_list_item_count: sourceListItems,
      rendered_list_item_count: renderedListItems,
      source_blockquote_count: sourceBlockquotes,
      rendered_blockquote_count: renderedBlockquotes,
      rendered_paragraph_count: renderedParagraphs,
      rendered_text_chars: renderedTextChars
    },
    failures
  };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
    const sourcePath = path.resolve(args.source);
    const source = fs.readFileSync(sourcePath, "utf8");

    if (args.profile === "sermon") {
      const result = spawnSync(process.execPath, [SERMON_VALIDATOR, "--source", sourcePath, "--candidate-id", args["candidate-id"]], {
        cwd: ROOT, encoding: "utf8"
      });
      if (result.error) throw result.error;
      let payload;
      try { payload = JSON.parse(result.stdout); }
      catch { throw new Error(result.stderr || "sermon validator returned invalid JSON"); }
      payload.profile = "sermon";
      console.log(JSON.stringify(payload, null, 2));
      process.exitCode = result.status ?? 2;
      return;
    }

    const report = await validateShare(sourcePath, source, args["candidate-id"]);
    console.log(JSON.stringify(report, null, 2));
    process.exitCode = report.status === "CONTENT_PRESENTATION_STRUCTURE_PASS" ? 0 : 1;
  } catch (error) {
    console.error(JSON.stringify({ gate: "content-publication-presentation-structure/v1", error: error.message }, null, 2));
    process.exitCode = 2;
  }
}

main();
