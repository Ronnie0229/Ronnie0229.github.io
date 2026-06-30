import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CHECK_REPORT = path.join(ROOT, "docs", "内容整理报告", "source-path-check.csv");
const REPAIR_REPORT = path.join(ROOT, "docs", "内容整理报告", "source-path-repair-plan.csv");
const RAW_ROOT = path.join(ROOT, "data", "raw");

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

function listFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  const result = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...listFiles(full));
    else result.push(full);
  }
  return result;
}

function normalizeForMatch(value) {
  return String(value ?? "")
    .normalize("NFKC")
    .toLowerCase()
    .replace(/\.[a-z0-9]+$/i, "")
    .replace(/[\s_\-｜|、，,。？?：:；;（）()\[\]【】「」『』《》“”"'’‘·‗–—]/g, "")
    .replace(/第/g, "")
    .replace(/章/g, "")
    .trim();
}

function tokenSet(value) {
  const normalized = normalizeForMatch(value);
  const tokens = new Set();
  for (const part of normalized.split(/[\/\\]+/)) {
    if (part) tokens.add(part);
  }
  const chinese = normalized.match(/[\u3400-\u9fff]{2,}/g) ?? [];
  for (const item of chinese) tokens.add(item);
  const numbers = normalized.match(/\d{4,8}|\d{1,3}/g) ?? [];
  for (const item of numbers) tokens.add(item);
  return tokens;
}

function scoreCandidate(row, candidateRel) {
  const sourceBase = path.basename(row.source || "");
  const articleBase = path.basename(row.article || "", ".md");
  const sourceNorm = normalizeForMatch(sourceBase);
  const candidateBaseNorm = normalizeForMatch(path.basename(candidateRel));
  const candidateFullNorm = normalizeForMatch(candidateRel);
  const articleNorm = normalizeForMatch(articleBase);

  let score = 0;
  const reasons = [];
  if (sourceNorm && candidateBaseNorm === sourceNorm) {
    score += 100;
    reasons.push("same_basename");
  }
  if (sourceNorm && candidateFullNorm.includes(sourceNorm)) {
    score += 60;
    reasons.push("source_name_in_candidate");
  }
  if (articleNorm && candidateFullNorm.includes(articleNorm)) {
    score += 40;
    reasons.push("article_name_in_candidate");
  }
  const sourceTokens = tokenSet(sourceBase);
  const articleTokens = tokenSet(articleBase);
  const candidateTokens = tokenSet(candidateRel);
  let tokenHits = 0;
  for (const token of new Set([...sourceTokens, ...articleTokens])) {
    if (token.length >= 2 && candidateTokens.has(token)) tokenHits += 1;
  }
  if (tokenHits) {
    score += tokenHits * 8;
    reasons.push(`token_hits_${tokenHits}`);
  }
  const sourceDate = (row.source.match(/\d{8}|\d{4}-\d{2}-\d{2}/) ?? [""])[0].replace(/-/g, "");
  const articleDate = (row.article.match(/\d{4}-\d{2}-\d{2}/) ?? [""])[0].replace(/-/g, "");
  const candidateDate = (candidateRel.match(/\d{8}|\d{4}-\d{2}-\d{2}/) ?? [""])[0].replace(/-/g, "");
  if (candidateDate && sourceDate && candidateDate === sourceDate) {
    score += 20;
    reasons.push("source_date_match");
  } else if (candidateDate && articleDate && candidateDate === articleDate) {
    score += 15;
    reasons.push("article_date_match");
  }
  return { score, reasons };
}

function categoryFor(row, candidates) {
  const source = row.source || "";
  if (row.status === "ok") {
    return { category: "ok", action: "none", confidence: "confirmed", suggested: source, note: "Source path exists." };
  }
  if (row.status === "no_source") {
    return { category: "no_source", action: "manual_review", confidence: "low", suggested: "", note: "Article has no source field value." };
  }

  const expectedPath = path.join(ROOT, source);
  const expectedDir = path.dirname(expectedPath);
  const expectedDirRel = path.relative(ROOT, expectedDir).replace(/\\/g, "/");
  const ext = path.extname(source).toLowerCase();
  const inShare = source.includes("data/raw/分享/");
  const inSermon = source.includes("data/raw/教会讲道/");
  const dirExists = fs.existsSync(expectedDir);
  const isBroadShareDir = expectedDirRel === "data/raw/分享";
  const isBroadSermonDir = expectedDirRel === "data/raw/教会讲道";

  if (dirExists && !isBroadShareDir && !isBroadSermonDir) {
    const sameDirCandidates = candidates.filter((candidate) => path.dirname(candidate.rel) === expectedDirRel);
    if (sameDirCandidates.length === 1) {
      return { category: "directory_exists_single_candidate", action: "manual_confirm_then_fix", confidence: "medium", suggested: sameDirCandidates[0].rel, note: "Expected source directory exists but target filename differs; one file exists in that directory." };
    }
    if (sameDirCandidates.length > 1) {
      return { category: "directory_exists_multiple_candidates", action: "manual_review", confidence: "medium", suggested: sameDirCandidates.map((item) => item.rel).join(" | "), note: "Expected source directory exists but target filename differs; multiple files exist." };
    }
    return { category: "directory_exists_no_candidate", action: "manual_review", confidence: "low", suggested: "", note: "Expected source directory exists but no files were found inside." };
  }

  const scored = candidates
    .map((candidate) => ({ ...candidate, ...scoreCandidate(row, candidate.rel) }))
    .filter((candidate) => candidate.score > 0)
    .sort((a, b) => b.score - a.score);
  const best = scored[0];
  const second = scored[1];
  if (best && best.score >= 100 && (!second || best.score - second.score >= 30)) {
    return { category: "unique_high_confidence_candidate", action: "manual_confirm_then_fix", confidence: "high", suggested: best.rel, note: `Best candidate score ${best.score}: ${best.reasons.join("+")}` };
  }
  if (best && best.score >= 50) {
    return { category: "possible_candidate", action: "manual_review", confidence: "medium", suggested: scored.slice(0, 3).map((item) => `${item.rel} (${item.score})`).join(" | "), note: "Potential candidates found but not safe enough for automatic repair." };
  }

  if (inShare && ext === ".docx") {
    return { category: "missing_share_docx", action: "recover_raw_file", confidence: "none", suggested: source, note: "Legacy share article points to a docx that is not present under data/raw." };
  }
  if (inShare) {
    return { category: "missing_share_raw", action: "recover_raw_file_or_manual_review", confidence: "none", suggested: source, note: "Share article source is missing under data/raw/分享." };
  }
  if (inSermon) {
    return { category: "missing_sermon_raw_directory", action: "recover_raw_directory", confidence: "none", suggested: source, note: "Sermon article source directory is not present under data/raw/教会讲道." };
  }
  return { category: "missing_other", action: "manual_review", confidence: "none", suggested: source, note: "Missing source path does not match known raw source conventions." };
}

function main() {
  const rows = parseCsv(fs.readFileSync(CHECK_REPORT, "utf8"));
  const rawFiles = listFiles(RAW_ROOT).map((full) => ({
    full,
    rel: path.relative(ROOT, full).replace(/\\/g, "/"),
  }));
  const output = [];
  const counts = new Map();
  for (const row of rows) {
    const result = categoryFor(row, rawFiles);
    counts.set(result.category, (counts.get(result.category) ?? 0) + 1);
    output.push({
      article: row.article,
      current_source: row.source,
      check_status: row.status,
      category: result.category,
      suggested_source: result.suggested,
      confidence: result.confidence,
      action: result.action,
      note: result.note,
    });
  }

  const headers = ["article", "current_source", "check_status", "category", "suggested_source", "confidence", "action", "note"];
  const csv = [headers.join(","), ...output.map((row) => headers.map((header) => csvEscape(row[header])).join(","))].join("\n") + "\n";
  fs.writeFileSync(REPAIR_REPORT, "\ufeff" + csv, "utf8");

  console.log(`Input: ${path.relative(ROOT, CHECK_REPORT).replace(/\\/g, "/")}`);
  console.log(`Raw files indexed: ${rawFiles.length}`);
  console.log(`Rows: ${output.length}`);
  for (const [category, count] of Array.from(counts.entries()).sort()) {
    console.log(`${category}: ${count}`);
  }
  console.log(`Report: ${path.relative(ROOT, REPAIR_REPORT).replace(/\\/g, "/")}`);
}

main();
