import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createMarkdownProcessor } from "@astrojs/markdown-remark";
import projectBibleBooks from "./project_bible_book_aliases.json" with { type: "json" };

const GATE_ID = "sermon-publication-presentation-mechanical/v1";
const COMPLETION_CEILING =
  "incident_proven_mechanical_checks_only_not_full_reader_quality_or_aesthetic_pass";

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
    )
  ];

  const status = checks.every((check) => check.status === "PASS")
    ? "MECHANICAL_PRESENTATION_PASS"
    : "MECHANICAL_PRESENTATION_FAIL";

  const result = {
    gate: GATE_ID,
    candidate_id: args["candidate-id"],
    status,
    completion_ceiling: COMPLETION_CEILING,
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
    rendered_section_evidence: renderedSectionEvidence
  };

  console.log(JSON.stringify(result, null, 2));
  process.exitCode = status === "MECHANICAL_PRESENTATION_PASS" ? 0 : 1;
}

main().catch((error) => {
  console.error(JSON.stringify({ gate: GATE_ID, error: error.message }, null, 2));
  process.exitCode = 2;
});
