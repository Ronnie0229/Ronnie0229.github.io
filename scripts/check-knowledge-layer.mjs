#!/usr/bin/env node
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const postsDir = path.join(rootDir, "src", "content", "posts");
const bibleDataPath = path.join(rootDir, "src", "data", "bible.ts");
const schemaPath = path.join(rootDir, "src", "lib", "knowledge", "schema.ts");
const adminScriptPath = path.join(rootDir, "assets", "admin", "decap.js");

const errors = [];
const warnings = [];

function addError(file, message) {
  errors.push({ file: path.relative(rootDir, file), message });
}

function addWarning(file, message) {
  warnings.push({ file: path.relative(rootDir, file), message });
}

async function listMarkdownFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...await listMarkdownFiles(fullPath));
    if (entry.isFile() && entry.name.endsWith(".md")) files.push(fullPath);
  }
  return files;
}

function stripQuotes(value) {
  const trimmed = String(value ?? "").trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function parseScalar(value) {
  const trimmed = String(value ?? "").trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed === "[]") return [];
  if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
    return trimmed.slice(1, -1).split(",").map((item) => stripQuotes(item)).filter(Boolean);
  }
  return stripQuotes(trimmed);
}

function parseFrontmatter(markdown, file) {
  markdown = String(markdown || "").replace(/^\uFEFF/, "");
  if (!markdown.startsWith("---")) {
    addError(file, "missing frontmatter block");
    return { data: {}, body: markdown };
  }
  const end = markdown.indexOf("\n---", 3);
  if (end === -1) {
    addError(file, "frontmatter block is not closed");
    return { data: {}, body: markdown };
  }
  const rawFrontmatter = markdown.slice(3, end).replace(/^\r?\n/, "");
  const bodyStart = markdown.indexOf("\n", end + 1);
  const body = bodyStart === -1 ? "" : markdown.slice(bodyStart + 1);
  const data = {};
  const lines = rawFrontmatter.split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (!line.trim() || line.trimStart().startsWith("#")) continue;
    const match = /^(\w+):\s*(.*)$/.exec(line);
    if (!match) continue;
    const [, key, rawValue] = match;
    if (rawValue === "") {
      const list = [];
      while (index + 1 < lines.length && /^\s+-\s+/.test(lines[index + 1])) {
        index += 1;
        list.push(stripQuotes(lines[index].replace(/^\s+-\s+/, "")));
      }
      data[key] = list;
    } else {
      data[key] = parseScalar(rawValue);
    }
  }
  return { data, body };
}

function cleanMarkdown(markdown) {
  return String(markdown || "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^>\s?/gm, "")
    .replace(/[\*_~|>#-]/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();
}

function trimTrailingPunctuation(text) {
  return text.replace(/[\u3002\uff01\uff1f\uff0c,\u3001\uff1b;\uff1a:\s]+$/u, "");
}

function generateFallbackDescription(markdownOrText, maxLength = 150) {
  const cleaned = cleanMarkdown(markdownOrText);
  if (!cleaned) return "";
  if (cleaned.length <= maxLength) return trimTrailingPunctuation(cleaned);
  const slice = cleaned.slice(0, maxLength + 1);
  const punctuationIndex = Math.max(
    slice.lastIndexOf("\u3002"),
    slice.lastIndexOf("\uff01"),
    slice.lastIndexOf("\uff1f"),
    slice.lastIndexOf(";"),
    slice.lastIndexOf("\uff1b")
  );
  if (punctuationIndex >= Math.floor(maxLength * 0.5)) return trimTrailingPunctuation(slice.slice(0, punctuationIndex + 1));
  return `${trimTrailingPunctuation(cleaned.slice(0, maxLength))}...`;
}

function countWords(text) {
  const cleaned = cleanMarkdown(text);
  if (!cleaned) return 0;
  const cjkMatches = cleaned.match(/[\u3400-\u9fff]/g) ?? [];
  const latinMatches = cleaned.replace(/[\u3400-\u9fff]/g, " ").match(/[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*/g) ?? [];
  return cjkMatches.length + latinMatches.length;
}

function extractArray(source, name) {
  const match = new RegExp(`export const ${name} = \\[([\\s\\S]*?)\\] as const`).exec(source);
  if (!match) return [];
  return [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]);
}

async function loadBibleBooks() {
  const source = await readFile(bibleDataPath, "utf8");
  const oldBooks = extractArray(source, "OLD_TESTAMENT_BOOKS");
  const newBooks = extractArray(source, "NEW_TESTAMENT_BOOKS");
  return { oldBooks, newBooks, allBooks: [...oldBooks, ...newBooks] };
}

function parseScripture(scripture, books) {
  const raw = String(scripture || "");
  const matchedBooks = books.allBooks.filter((book) => raw.includes(book));
  const hasOld = matchedBooks.some((book) => books.oldBooks.includes(book));
  const hasNew = matchedBooks.some((book) => books.newBooks.includes(book));
  const testament = hasOld && hasNew ? "mixed" : hasOld ? "old" : hasNew ? "new" : "unknown";
  return { raw, books: matchedBooks, testament, references: matchedBooks.map((book) => ({ raw: book, book })) };
}

const topicRules = {
  grace: ["\u6069\u5178"],
  faith: ["\u4fe1\u5fc3", "\u76f8\u4fe1"],
  prayer: ["\u7977\u544a"],
  gospel: ["\u798f\u97f3"]
};

function inferTopics(input) {
  const source = [input.title, input.description, input.scripture, ...(input.tags ?? []), cleanMarkdown(input.body ?? "")].filter(Boolean).join(" ");
  return Object.entries(topicRules).filter(([, words]) => words.some((word) => source.includes(word))).map(([topic]) => topic);
}

function buildPostKnowledge(post, books) {
  const data = post.data ?? {};
  const body = post.body ?? "";
  const fallbackDescription = generateFallbackDescription(body);
  const description = String(data.description || "").trim() || fallbackDescription;
  const scriptureKnowledge = parseScripture(data.scripture, books);
  const wordCount = countWords(body);
  return {
    slug: post.slug,
    articleId: data.articleId ?? "",
    title: data.title ?? "",
    description,
    fallbackDescription,
    date: data.date,
    author: data.author ?? "",
    category: data.category ?? "",
    tags: Array.isArray(data.tags) ? data.tags : [],
    scripture: data.scripture ?? "",
    scriptureKnowledge,
    bibleBooks: scriptureKnowledge.books,
    testament: scriptureKnowledge.testament,
    topics: inferTopics({ title: data.title, description, scripture: data.scripture, tags: data.tags, body }),
    wordCount,
    readingTimeMinutes: Math.max(1, Math.ceil(wordCount / 350))
  };
}

async function checkAdminScript() {
  const source = await readFile(adminScriptPath, "utf8");
  const listeners = source.match(/registerEventListener\s*\(/g) ?? [];
  if (listeners.length !== 1) addError(adminScriptPath, `expected exactly one preSave listener, found ${listeners.length}`);
  if (!source.includes('name: "preSave"')) addError(adminScriptPath, "missing preSave listener name");
  if (!source.includes("articleId") || !source.includes("createArticleId")) addError(adminScriptPath, "missing articleId generation logic");
  if (!source.includes("description") || !source.includes("generateFallbackDescription")) addError(adminScriptPath, "missing description fallback logic");
}

async function checkSchemaSource() {
  const source = await readFile(schemaPath, "utf8");
  for (const exportName of ["createWebSiteSchema", "createPersonSchema", "createBlogPostingSchema", "createSiteGraph"]) {
    if (!source.includes(`function ${exportName}`)) addError(schemaPath, `missing ${exportName}`);
  }
  try {
    JSON.stringify({ "@context": "https://schema.org", "@graph": [{ "@type": "WebSite" }] });
  } catch (error) {
    addError(schemaPath, `basic JSON-LD stringify failed: ${error.message}`);
  }
}

async function main() {
  const books = await loadBibleBooks();
  if (!books.allBooks.length) addError(bibleDataPath, "no Bible books parsed");
  const files = await listMarkdownFiles(postsDir);
  let checkedPosts = 0;
  for (const file of files) {
    const markdown = await readFile(file, "utf8");
    const { data, body } = parseFrontmatter(markdown, file);
    if (data.draft === true) continue;
    checkedPosts += 1;
    if (!String(data.title || "").trim()) addError(file, "missing title");
    if (!data.date || Number.isNaN(new Date(data.date).valueOf())) addError(file, "missing or invalid date");
    let knowledge;
    try {
      knowledge = buildPostKnowledge({ slug: path.basename(file, ".md"), data, body }, books);
    } catch (error) {
      addError(file, `buildPostKnowledge failed: ${error.message}`);
      continue;
    }
    if (!knowledge.description && !knowledge.fallbackDescription) addWarning(file, "missing description and fallback description is empty");
    if (knowledge.scripture && knowledge.bibleBooks.length === 0) addWarning(file, "scripture is present but no Bible book was detected");
    if (!Array.isArray(knowledge.topics)) addError(file, "topics was not generated as an array");
    if (!Number.isFinite(knowledge.wordCount) || knowledge.wordCount < 0) addError(file, "invalid wordCount");
    if (!Number.isFinite(knowledge.readingTimeMinutes) || knowledge.readingTimeMinutes < 1) addError(file, "invalid readingTimeMinutes");
  }
  await checkSchemaSource();
  await checkAdminScript();
  console.log("Knowledge Layer Check");
  console.log(`Posts checked: ${checkedPosts}`);
  console.log(`Errors: ${errors.length}`);
  console.log(`Warnings: ${warnings.length}`);
  for (const error of errors.slice(0, 20)) console.error(`ERROR ${error.file}: ${error.message}`);
  if (errors.length > 20) console.error(`ERROR ... ${errors.length - 20} more`);
  for (const warning of warnings.slice(0, 20)) console.warn(`WARNING ${warning.file}: ${warning.message}`);
  if (warnings.length > 20) console.warn(`WARNING ... ${warnings.length - 20} more`);
  process.exit(errors.length ? 1 : 0);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
