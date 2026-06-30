import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const INPUT = path.join(ROOT, "docs", "内容整理报告", "source-path-repair-plan.csv");
const OUTPUT = path.join(ROOT, "docs", "内容整理报告", "source-raw-recovery-checklist.csv");

function csvEscape(value) {
  const text = value == null ? "" : String(value);
  if (/[",\n\r]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  const input = String(text ?? "").replace(/^\uFEFF/, "");
  for (let i = 0; i < input.length; i += 1) {
    const char = input[i];
    const next = input[i + 1];
    if (inQuotes) {
      if (char === '"' && next === '"') {
        field += '"';
        i += 1;
      } else if (char === '"') {
        inQuotes = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      inQuotes = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const [headers, ...body] = rows;
  return body.filter((item) => item.length === headers.length).map((item) => Object.fromEntries(headers.map((header, index) => [header, item[index] ?? ""])));
}

function priorityFor(category) {
  if (category === "missing_share_raw" || category === "no_source") return "P0";
  if (category === "missing_share_docx") return "P1";
  if (category === "missing_sermon_raw_directory") return "P2";
  return "P3";
}

function recoveryTargetFor(row) {
  if (row.category === "no_source") return "manual_source_identification";
  return row.current_source;
}

function recommendedSearchLocation(category) {
  if (category === "missing_share_raw") return "C:/Users/caoyi/Projects/讲道整理, \\\\RonnieNAS\\tmp\\分享, old ChatGPT/Codex export folders";
  if (category === "missing_share_docx") return "old share raw archive, backup, NAS share archive, previous content project";
  if (category === "missing_sermon_raw_directory") return "\\\\RonnieNAS\\share\\教会讲道, protected sermon archive, old data/raw/教会讲道";
  if (category === "no_source") return "local post history, live article, ChatGPT conversation, original source inbox";
  return "manual review";
}

function main() {
  const rows = parseCsv(fs.readFileSync(INPUT, "utf8"));
  const grouped = new Map();

  for (const row of rows) {
    if (row.category === "ok") continue;
    const key = `${row.category}\u0000${recoveryTargetFor(row)}`;
    if (!grouped.has(key)) {
      grouped.set(key, {
        priority: priorityFor(row.category),
        category: row.category,
        recovery_target: recoveryTargetFor(row),
        impacted_count: 0,
        impacted_articles: [],
        recommended_action: row.action,
        recommended_search_location: recommendedSearchLocation(row.category),
        status: "not_recovered",
        note: row.note,
      });
    }
    const item = grouped.get(key);
    item.impacted_count += 1;
    item.impacted_articles.push(row.article);
  }

  const output = Array.from(grouped.values()).sort((a, b) => {
    const priority = a.priority.localeCompare(b.priority);
    if (priority !== 0) return priority;
    const category = a.category.localeCompare(b.category);
    if (category !== 0) return category;
    return a.recovery_target.localeCompare(b.recovery_target);
  });

  const headers = [
    "priority",
    "category",
    "recovery_target",
    "impacted_count",
    "impacted_articles",
    "recommended_action",
    "recommended_search_location",
    "status",
    "note",
  ];
  const csv = [
    headers.join(","),
    ...output.map((row) => headers.map((header) => {
      if (header === "impacted_articles") return csvEscape(row.impacted_articles.join(" | "));
      return csvEscape(row[header]);
    }).join(",")),
  ].join("\n") + "\n";

  fs.writeFileSync(OUTPUT, "\uFEFF" + csv, "utf8");

  const counts = new Map();
  for (const item of output) counts.set(item.category, (counts.get(item.category) ?? 0) + 1);

  console.log(`Input: ${path.relative(ROOT, INPUT).replace(/\\/g, "/")}`);
  console.log(`Recovery targets: ${output.length}`);
  for (const [category, count] of Array.from(counts.entries()).sort()) {
    console.log(`${category}: ${count}`);
  }
  console.log(`Report: ${path.relative(ROOT, OUTPUT).replace(/\\/g, "/")}`);
}

main();
