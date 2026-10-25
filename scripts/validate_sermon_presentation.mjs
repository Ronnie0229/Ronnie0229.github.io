import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createMarkdownProcessor } from "@astrojs/markdown-remark";
import projectBibleBooks from "./project_bible_book_aliases.json" with { type: "json" };

const GATE_ID = "sermon-publication-presentation-structure/v2";
const PASS_STATUS = "SERMON_PRESENTATION_STRUCTURE_PASS";
const FAIL_STATUS = "SERMON_PRESENTATION_STRUCTURE_FAIL";
const COMPLETION_CEILING_PASS = "publication_structure_ready";
const COMPLETION_CEILING_FAIL = "publication_structure_blocked";

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for --${key}`);
    }
    args[key] = value;
    index += 1;
  }
  if (!args.source) throw new Error("--source is required");
  if (!args["candidate-id"]) throw new Error("--candidate-id is required");
  return args;
}

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function stripFrontmatter(markdown) {
  const normalized = markdown.replace(/^\uFEFF/, "");
  if (!normalized.startsWith("---\n") && !normalized.startsWith("---\r\n")) {
    return normalized;
  }
  const lines = normalized.split(/\r?\n/);
  for (let index = 1; index < lines.length; index += 1) {
    if (lines[index].trim() === "---") {
      return lines.slice(index + 1).join("\n");
    }
  }
  return normalized;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const controlledBookNames = [...new Set(
  projectBibleBooks.books.flatMap((book) => [book.book_name, book.book_abbr]).filter(Boolean)
)].sort((a, b) => b.length - a.length);
const scriptureLabelPattern = new RegExp(
  `^(?:${controlledBookNames.map(escapeRegExp).join("|")})\\s*\\d{1,3}\\s*章\\s*\\d{1,3}\\s*节(?:\\s*到\\s*(?:\\d{1,3}\\s*章\\s*)?\\d{1,3}\\s*节)?\\s*([：:]?)$`
);

const productionResiduePatterns = [
  /^\s*\[(?:WD|MAP)\](?:\s|$)/i,
  /^\s*\[(?:SLIDE|TIMELINE\s+SLIDE|PAGE)(?:[^\]]*)\](?:\s|$)/i,
  /^\s*\[幻灯片(?:[^\]]*)\](?:\s|$)/i,
  /^\s*(?:Page\s+\d+|第\s*\d+\s*页)\s*$/i
];

// Public-content hygiene: publishing metadata belongs in frontmatter, not the sermon body.
const internalWorkflowNotePattern = /(?:默认规则.{0,16}待元数据(?:最终)?确认|待元数据(?:最终)?确认|NEEDS_METADATA|PENDING_METADATA)/i;
const duplicateSermonLeadPattern = /^(?:#{1,3}\s*)?(?:《?[^\n]{0,45}》?\s*)?(?:腓立比书|罗马书|希伯来书|雅各书|哥林多前书|哥林多后书|诗篇|马太福音|约翰福音)\s*\d{1,3}\s*章[^\n]{0,90}$/;

const itemizedSectionPattern =
  /(重点|要点|主要论点|提纲|小组讨论|讨论问题|反思问题|key\s*points?|reflection\s*questions?|discussion(?:\s*questions?)?|wakachiai)/i;
const listItemPattern = /^\s*(?:[-+*]|\d+[.)])\s+\S/;
const pseudoOrderedListLinePattern = /^\s*(\d+)[）、．]\s*\S/;
const pseudoOrderedListInlinePattern = /(?:^|\s)(\d+)[）、．]\s*\S/g;
const nonPublicSmallGroupHeadingPattern =
  /^\s*#{2,3}\s+(?:小组分享.*WAKACHIAI.*|WAKACHIAI(?:\s.*)?)\s*$/i;

function collectPseudoOrderedListFailures(lines) {
  const failures = [];
  let run = [];

  function flushRun() {
    if (run.length >= 2) {
      failures.push({
        kind: "consecutive_pseudo_ordered_list_lines",
        lines: run.map((entry) => entry.line),
        text: run.map((entry) => entry.text).join(" | ")
      });
    }
    run = [];
  }

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const lineMatch = line.match(pseudoOrderedListLinePattern);
    if (lineMatch) {
      const number = Number(lineMatch[1]);
      const expected = run.length ? run[run.length - 1].number + 1 : number;
      if (run.length && number !== expected) flushRun();
      run.push({ line: index + 1, number, text: line.trim() });
    } else if (line.trim()) {
      flushRun();
    }

    const inlineNumbers = [...line.matchAll(pseudoOrderedListInlinePattern)].map((match) =>
      Number(match[1])
    );
    if (inlineNumbers.length >= 2) {
      failures.push({
        kind: "inline_pseudo_ordered_list",
        line: index + 1,
        numbers: inlineNumbers,
        text: line.trim()
      });
    }
  }
  flushRun();
  return failures;
}

// Fail closed on Chinese outline siblings split between headings/plain lines,
// or presented as visual-only lines. Scope to contiguous sequential markers,
// not isolated section headings in the body.
const chineseOutlineNumbers = "一二三四五六七八九十";
function chineseOutlineOrdinal(line) {
  const trimmed = line.trim();
  const m = trimmed.match(/^(?:(#{2,3})\s+)?(?:(?:[-+*]|\d+[.)])\s+)?(?:([一二三四五六七八九十])\s*[、．.]|[（(]([一二三四五六七八九十])[）)]|第([一二三四五六七八九十])(?:个|项|点|部分|方面)[：:]\s*)\S/);
  if (!m) return null;
  return { number: chineseOutlineNumbers.indexOf(m[2] || m[3] || m[4]) + 1,
    structured: Boolean(m[0].match(/^\s*(?:[-+*]|\d+[.)])\s+/)),
    heading: Boolean(m[1]), text: trimmed };
}
function collectChineseOutlineFailures(lines) {
  const failures = [];
  let index = 0;
  while (index < lines.length) {
    const first = chineseOutlineOrdinal(lines[index]);
    if (!first || first.number !== 1) { index++; continue; }
    const run = [{ ...first, line: index + 1 }];
    let cursor = index + 1;
    while (cursor < lines.length) {
      if (!lines[cursor].trim()) { cursor++; continue; }
      const next = chineseOutlineOrdinal(lines[cursor]);
      if (!next || next.number !== run.length + 1) break;
      run.push({ ...next, line: cursor + 1 });
      cursor++;
    }
    if (run.length >= 2 && !run.every(item => item.structured)) {
      failures.push({kind:"chinese_outline_not_uniform_markdown_list",
        items:run, expected:"every parallel point must be a standard Markdown list item"});
    }
    // When an immediately preceding introduction explicitly promises N points,
    // the number of sibling records must match. Do not infer a number from unrelated prose.
    const introduction = lines.slice(Math.max(0, index - 4), index).join(" ");
    const declared = introduction.match(/(?:今天有|下面有|共有|分为|以下有).{0,24}?([两二三四五六七八九十])(?:个)?(?:要点|重点|方面|问题|部分)/);
    const expectedCount = declared ? chineseOutlineNumbers.indexOf(declared[1]) + 1 : null;
    if (expectedCount && run.length !== expectedCount) {
      failures.push({ kind: "declared_outline_count_mismatch", declared_count: expectedCount,
        actual_count: run.length, items: run });
    }
    index = Math.max(index + 1, cursor);
  }
  return failures;
}

function collectThreePointHeadingFailures(lines) {
  const failures = [];
  for (let i = 0; i < lines.length - 2; i += 1) {
    const a = lines[i].match(/^1\.\s+(.+)/);
    const b = lines[i + 1].match(/^2\.\s+(.+)/);
    const c = lines[i + 2].match(/^3\.\s+(.+)/);
    if (!a || !b || !c) continue;
    const intro = lines.slice(Math.max(0, i - 5), i).join(" ");
    const scriptureOutline = [a[1], b[1], c[1]].every(x => /第.{1,12}节/.test(x));
    if (!/(?:今天|下面|以下|全文|本篇).{0,20}(?:有|分为|包括)(?:三个|三项|三点)|(?:共有|分为)(?:三个|三项|三点)/.test(intro) && !scriptureOutline) continue;
    const normalize = x => x.replace(/\*\*/g, "").trim();
    const titles = [a[1], b[1], c[1]].map(normalize);
    const headings = lines.filter(line => /^##\s+/.test(line)).map(line => normalize(line.replace(/^##\s+/, "")));
    for (const title of titles) {
      if (!headings.includes(title)) failures.push({kind:"missing_three_point_h2", title, outline_line:i+1});
    }
  }
  return failures;
}

function collectItemizedSections(lines) {
  const sections = [];
  for (let index = 0; index < lines.length; index += 1) {
    const heading = lines[index].match(/^\s*(#{2,3})\s+(.+?)\s*$/);
    if (!heading || !itemizedSectionPattern.test(heading[2])) continue;
    const content = [];
    for (let cursor = index + 1; cursor < lines.length; cursor += 1) {
      if (/^\s*#{2,3}\s+/.test(lines[cursor])) break;
      content.push(lines[cursor]);
    }
    const listItems = content.filter((line) => listItemPattern.test(line));
    const nonBlankContent = content.filter((line) => line.trim());
    const unstructuredInlineTails = [];
    let consecutiveListItems = 0;
    for (let contentIndex = 0; contentIndex < content.length; contentIndex += 1) {
      const line = content[contentIndex];
      if (!line.trim()) {
        consecutiveListItems = 0;
        continue;
      }
      if (listItemPattern.test(line)) {
        consecutiveListItems += 1;
        continue;
      }
      if (consecutiveListItems >= 2) {
        unstructuredInlineTails.push({
          line: index + contentIndex + 2,
          text: line.trim()
        });
      }
      consecutiveListItems = 0;
    }
    sections.push({
      heading: heading[2].trim(),
      depth: heading[1].length,
      sourceListItemCount: listItems.length,
      nonBlankLineCount: nonBlankContent.length,
      unstructuredInlineTails
    });
  }
  return sections;
}

function plainTextFromHtml(value) {
  return value
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();
}

function renderedListEvidence(html, section) {
  const headingRegex = /<h([23])\b[^>]*>([\s\S]*?)<\/h\1>/gi;
  const headings = [];
  let match;
  while ((match = headingRegex.exec(html)) !== null) {
    headings.push({
      depth: Number(match[1]),
      text: plainTextFromHtml(match[2]),
      start: match.index,
      end: headingRegex.lastIndex
    });
  }
  const targetIndex = headings.findIndex(
    (heading) => heading.depth === section.depth && heading.text === section.heading
  );
  if (targetIndex < 0) {
    return { foundHeading: false, renderedListItemCount: 0, hasListBlock: false };
  }
  const start = headings[targetIndex].end;
  const end = headings[targetIndex + 1]?.start ?? html.length;
  const segment = html.slice(start, end);
  const listMatch = segment.match(/<(ol|ul)\b[^>]*>([\s\S]*?)<\/\1>/i);
  if (!listMatch) {
    return { foundHeading: true, renderedListItemCount: 0, hasListBlock: false };
  }
  const renderedListItemCount = (listMatch[2].match(/<li\b/gi) ?? []).length;
  return { foundHeading: true, renderedListItemCount, hasListBlock: true };
}

function makeCheck(id, failures, detail) {
  return {
    id,
    status: failures.length === 0 ? "PASS" : "FAIL",
    failures,
    detail
  };
}

function collectRenderedStructureMetrics(body, html) {
  const sourceHeadingCount = (body.match(/^\s*#{2,3}\s+\S/gm) ?? []).length;
  const renderedParagraphCount = (html.match(/<p\b/gi) ?? []).length;
  const renderedListItemCount = (html.match(/<li\b/gi) ?? []).length;
  const renderedBlockquoteCount = (html.match(/<blockquote\b/gi) ?? []).length;
  const renderedHeadingCount = (html.match(/<h[23]\b/gi) ?? []).length;
  const renderedTextChars = plainTextFromHtml(html).replace(/\s+/g, "").length;
  const contentBlockCount =
    renderedParagraphCount + renderedListItemCount + renderedBlockquoteCount + renderedHeadingCount;
  return {
    source_heading_count: sourceHeadingCount,
    rendered_heading_count: renderedHeadingCount,
    rendered_paragraph_count: renderedParagraphCount,
    rendered_list_item_count: renderedListItemCount,
    rendered_blockquote_count: renderedBlockquoteCount,
    rendered_text_chars: renderedTextChars,
    rendered_content_block_count: contentBlockCount
  };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(JSON.stringify({ gate: GATE_ID, error: error.message }, null, 2));
    process.exitCode = 2;
    return;
  }

  const sourcePath = path.resolve(args.source);
  let source;
  try {
    source = fs.readFileSync(sourcePath, "utf8");
  } catch (error) {
    console.error(JSON.stringify({ gate: GATE_ID, error: error.message }, null, 2));
    process.exitCode = 2;
    return;
  }

  const body = stripFrontmatter(source);
  const lines = body.split(/\r?\n/);

  const residueFailures = [];
  for (let index = 0; index < lines.length; index += 1) {
    if (productionResiduePatterns.some((pattern) => pattern.test(lines[index]))) {
      residueFailures.push({ line: index + 1, text: lines[index].trim() });
    }
  }

  const internalNoteFailures = [];
  for (let index = 0; index < lines.length; index += 1) {
    if (internalWorkflowNotePattern.test(lines[index])) {
      internalNoteFailures.push({ line: index + 1, text: lines[index].trim() });
    }
  }
  // Narrowly detect the incident shape: duplicate title followed by speaker/event labels.
  const lead = lines.filter((line) => line.trim()).slice(0, 4);
  const duplicateLeadFailures = [];
  if (lead.length >= 2 && duplicateSermonLeadPattern.test(lead[0].trim()) &&
      /^讲员\s*[：:]/.test(lead[1].trim())) {
    duplicateLeadFailures.push({ kind: "body_title_and_speaker_duplicate", text: lead.slice(0, 3).join(" | ") });
  }
  if (lead.some((line) => /^场合\s*[：:]/.test(line.trim()))) {
    duplicateLeadFailures.push({ kind: "internal_event_label_in_body", text: lead.slice(0, 4).join(" | ") });
  }

  const scriptureFailures = [];
  for (let index = 0; index < lines.length; index += 1) {
    const trimmed = lines[index].trim();
    const scriptureMatch = trimmed.match(scriptureLabelPattern);
    if (scriptureMatch && scriptureMatch[1] !== "：") {
      scriptureFailures.push({ line: index + 1, text: trimmed });
    }
  }

  const headingFailures = [];
  const smallGroupHeadingFailures = [];
  for (let index = 0; index < lines.length; index += 1) {
    const match = lines[index].match(/^\s*#{2,3}\s+(\d+)\s*[.、．)]\s*\S/);
    if (match) headingFailures.push({ line: index + 1, text: lines[index].trim() });
    if (nonPublicSmallGroupHeadingPattern.test(lines[index])) {
      smallGroupHeadingFailures.push({ line: index + 1, text: lines[index].trim() });
    }
  }

  const pseudoOrderedListFailures = collectPseudoOrderedListFailures(lines);
  const chineseOutlineFailures = collectChineseOutlineFailures(lines);
  const threePointHeadingFailures = collectThreePointHeadingFailures(lines);
  const itemizedSections = collectItemizedSections(lines);
  const sourceStructureFailures = itemizedSections
    .filter(
      (section) =>
        section.sourceListItemCount < 2 || section.unstructuredInlineTails.length > 0
    )
    .map((section) => ({
      heading: section.heading,
      source_list_item_count: section.sourceListItemCount,
      non_blank_line_count: section.nonBlankLineCount,
      unstructured_inline_tails: section.unstructuredInlineTails
    }));

  const processor = await createMarkdownProcessor({});
  const rendered = await processor.render(body);
  const renderedHtml = rendered.code;
  const renderedSectionEvidence = itemizedSections.map((section) => ({
    ...section,
    ...renderedListEvidence(renderedHtml, section)
  }));
  const renderedStructureFailures = renderedSectionEvidence
    .filter(
      (section) =>
        section.sourceListItemCount >= 2 &&
        (!section.foundHeading ||
          !section.hasListBlock ||
          section.renderedListItemCount < section.sourceListItemCount)
    )
    .map((section) => ({
      heading: section.heading,
      expected_list_items: section.sourceListItemCount,
      rendered_list_items: section.renderedListItemCount,
      found_heading: section.foundHeading,
      has_list_block: section.hasListBlock
    }));

  const structureMetrics = collectRenderedStructureMetrics(body, renderedHtml);
  const paragraphCollapseFailures = [];
  if (
    structureMetrics.rendered_text_chars >= 1200 &&
    structureMetrics.rendered_paragraph_count <= 1 &&
    structureMetrics.rendered_list_item_count === 0
  ) {
    paragraphCollapseFailures.push({
      rendered_text_chars: structureMetrics.rendered_text_chars,
      rendered_paragraph_count: structureMetrics.rendered_paragraph_count,
      rendered_list_item_count: structureMetrics.rendered_list_item_count
    });
  }

  const renderedBlockDensityFailures = [];
  if (
    structureMetrics.rendered_text_chars >= 2000 &&
    structureMetrics.rendered_content_block_count < 6
  ) {
    renderedBlockDensityFailures.push({
      rendered_text_chars: structureMetrics.rendered_text_chars,
      rendered_content_block_count: structureMetrics.rendered_content_block_count,
      minimum_required_blocks: 6
    });
  }

  const headingRenderIntegrityFailures = [];
  if (structureMetrics.source_heading_count !== structureMetrics.rendered_heading_count) {
    headingRenderIntegrityFailures.push({
      source_heading_count: structureMetrics.source_heading_count,
      rendered_heading_count: structureMetrics.rendered_heading_count
    });
  }

  if (args["rendered-output"]) {
    const renderedPath = path.resolve(args["rendered-output"]);
    fs.mkdirSync(path.dirname(renderedPath), { recursive: true });
    fs.writeFileSync(renderedPath, renderedHtml, "utf8");
  }

  const checks = [
    makeCheck(
      "production_residue",
      residueFailures,
      "Blocks incident-proven PDF/page/slide production residue patterns only."
    ),
    makeCheck("internal_workflow_note_in_public_body", internalNoteFailures,
      "Rejects recognized internal metadata-confirmation and staging markers in public sermon body."),
    makeCheck("duplicate_sermon_body_metadata_header", duplicateLeadFailures,
      "Blocks duplicated sermon title/speaker or event labels at the start of public article body; website frontmatter owns title and speaker."),
    makeCheck(
      "scripture_label_fullwidth_colon",
      scriptureFailures,
      "Checks controlled TTS-style scripture label lines end with Chinese full-width colon; does not judge scripture text exactness."
    ),
    makeCheck(
      "toc_heading_duplicate_numbering_risk",
      headingFailures,
      "Current Website TOC is an ordered list over H2/H3; source H2/H3 must not carry an Arabic list-number prefix."
    ),
    makeCheck(
      "pseudo_ordered_list_requires_markdown_list",
      pseudoOrderedListFailures,
      "Two or more ordered items written as Chinese visual markers such as 1）/2） are not stable Markdown list blocks and must be normalized to standard Markdown list syntax before publication."
    ),
    makeCheck(
      "chinese_parallel_outline_structure",
      chineseOutlineFailures,
      "Chinese parallel outline items (一、二、三、 / （一）（二） / 第一、第二) must use uniform Markdown list syntax; mixed H2 and plain-line siblings are forbidden."
    ),
    makeCheck("three_point_outline_h2_presence", threePointHeadingFailures,
      "An explicit three-part sermon outline must have exactly corresponding visible H2 chapter boundaries."),
    makeCheck(
      "small_group_heading_public_label",
      smallGroupHeadingFailures,
      "Public sermon presentation uses the exact Chinese heading 小组分享; source-language helper label WAKACHIAI must not remain in the public H2/H3 heading."
    ),
    makeCheck(
      "itemized_section_source_structure",
      sourceStructureFailures,
      "Recognized key-point/discussion sections require standard Markdown list items; after two or more consecutive list items, an immediately adjacent plain-text tail without a blank-line boundary is incomplete itemized structure."
    ),
    makeCheck(
      "itemized_section_rendered_blocks",
      renderedStructureFailures,
      "Renders this exact source candidate with Astro's Markdown processor and requires independent rendered <li> blocks."
    ),
    makeCheck(
      "paragraph_collapse_guard",
      paragraphCollapseFailures,
      "Long-form sermon content must not collapse into a single rendered paragraph."
    ),
    makeCheck(
      "rendered_block_density",
      renderedBlockDensityFailures,
      "Long-form sermon content requires a minimum rendered block density so multi-thousand-character bodies cannot pass as a few giant blocks."
    ),
    makeCheck(
      "heading_render_integrity",
      headingRenderIntegrityFailures,
      "Every source H2/H3 presentation boundary must survive Markdown rendering as an H2/H3 boundary."
    )
  ];

  const passed = checks.every((check) => check.status === "PASS");
  const status = passed ? PASS_STATUS : FAIL_STATUS;

  const result = {
    gate: GATE_ID,
    candidate_id: args["candidate-id"],
    status,
    legacy_mechanical_status: passed ? "MECHANICAL_PRESENTATION_PASS" : "MECHANICAL_PRESENTATION_FAIL",
    completion_ceiling: passed ? COMPLETION_CEILING_PASS : COMPLETION_CEILING_FAIL,
    source: {
      path: sourcePath,
      sha256: sha256(source)
    },
    rendered_html: {
      engine: "@astrojs/markdown-remark/createMarkdownProcessor",
      sha256: sha256(renderedHtml),
      output_path: args["rendered-output"] ? path.resolve(args["rendered-output"]) : null
    },
    checks,
    rendered_structure_metrics: structureMetrics,
    rendered_section_evidence: renderedSectionEvidence
  };

  console.log(JSON.stringify(result, null, 2));
  process.exitCode = status === PASS_STATUS ? 0 : 1;
}

main().catch((error) => {
  console.error(JSON.stringify({ gate: GATE_ID, error: error.message }, null, 2));
  process.exitCode = 2;
});
