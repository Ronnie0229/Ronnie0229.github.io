#!/usr/bin/env node
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const editorPath = path.join(rootDir, "assets", "admin", "editor.js");
const decapPath = path.join(rootDir, "assets", "admin", "decap.js");
const editorHtmlPath = path.join(rootDir, "assets", "admin", "editor.html");
const decapHtmlPath = path.join(rootDir, "assets", "admin", "decap.html");
const tagPipelinePath = path.join(rootDir, "assets", "admin", "tag-pipeline.js");
const tagRulesPath = path.join(rootDir, "assets", "admin", "tag-rules.json");
const tagFixturesPath = path.join(rootDir, "scripts", "tests", "fixtures", "tag_pipeline_cases.json");
const tmpDir = path.join(rootDir, "tmp", "admin-save-flow");
const fixturePath = path.join(tmpDir, "2026-06-27-phase-7-admin-save-test.md");

const errors = [];

function addError(message) {
  errors.push(message);
}

function slugify(value) {
  const slug = value
    .normalize("NFKC")
    .trim()
    .toLowerCase()
    .replace(/[\\/:*?"<>|]/g, "")
    .replace(/[、，,；;：:\s]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 90);
  return slug || "article-test";
}

function yamlValue(value) {
  if (Array.isArray(value)) return JSON.stringify(value);
  if (typeof value === "boolean") return String(value);
  if (value === null || value === undefined) return '""';
  return JSON.stringify(String(value));
}

function serializeMarkdown(data, body) {
  const order = [
    "articleId",
    "title",
    "description",
    "date",
    "publishedAt",
    "tags",
    "category",
    "scripture",
    "author",
    "reviewed",
    "draft",
    "source"
  ];
  const keys = [...order, ...Object.keys(data).filter((key) => !order.includes(key))];
  const lines = keys
    .filter((key) => data[key] !== undefined)
    .map((key) => `${key}: ${yamlValue(data[key])}`);
  return `---\n${lines.join("\n")}\n---\n\n${body.trim()}\n`;
}

function parseValue(value) {
  const trimmed = value.trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed.startsWith("[") && trimmed.endsWith("]")) return JSON.parse(trimmed);
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) return JSON.parse(trimmed);
  return trimmed;
}

function parseMarkdown(raw) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: raw };
  const data = {};
  for (const line of match[1].split(/\r?\n/)) {
    const field = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/);
    if (field) data[field[1]] = parseValue(field[2]);
  }
  return { data, body: match[2] };
}

function validatePost(data, body, draft) {
  const validationErrors = [];
  if (!data.title) validationErrors.push("missing title");
  if (!data.date) validationErrors.push("missing date");
  if (!data.category) validationErrors.push("missing category");
  if (!draft && !body.trim()) validationErrors.push("missing body");
  if (!draft && !data.description) validationErrors.push("missing description");
  return validationErrors;
}

async function checkSourceGuards() {
  const [editorSource, decapSource, editorHtml, decapHtml] = await Promise.all([
    readFile(editorPath, "utf8"),
    readFile(decapPath, "utf8"),
    readFile(editorHtmlPath, "utf8"),
    readFile(decapHtmlPath, "utf8")
  ]);

  const requiredEditorSnippets = [
    "function savePost(draft)",
    "function serializeMarkdown(data, body)",
    "function slugify(value)",
    ".toLowerCase()",
    "currentFrontmatter = { articleId:",
    "validatePost(data, draft)",
    "firstPublication",
    "publishedAt: new Date().toISOString()",
    "findGithubFile(path)",
    "existingArticle.data.articleId === data.articleId",
    "payload.sha = targetSha",
    "method: \"PUT\"",
    "await tagRulesPromise",
    "RonnieTagPipeline.buildTags"
  ];

  for (const snippet of requiredEditorSnippets) {
    if (!editorSource.includes(snippet)) addError(`editor.js missing required save-flow snippet: ${snippet}`);
  }

  const listenerCount = (decapSource.match(/registerEventListener\s*\(/g) ?? []).length;
  if (listenerCount !== 1) addError(`decap.js expected one preSave listener, found ${listenerCount}`);
  for (const snippet of ["name: \"preSave\"", "articleId", "createArticleId", "description", "generateFallbackDescription"]) {
    if (!decapSource.includes(snippet)) addError(`decap.js missing preSave snippet: ${snippet}`);
  }
  for (const snippet of ["await tagRulesPromise", "RonnieTagPipeline.buildTags", "nextData.set(\"tags\""]) {
    if (!decapSource.includes(snippet)) addError(`decap.js missing Tag Pipeline snippet: ${snippet}`);
  }
  if (!editorHtml.includes("/admin/tag-pipeline.js")) addError("editor.html does not load Tag Pipeline before saving");
  if (!decapHtml.includes("/admin/tag-pipeline.js")) addError("decap.html does not load Tag Pipeline before preSave");
  if (editorSource.includes("const GENERIC_TAGS")) addError("editor.js still contains a local generic-tag authority");
  if (editorSource.includes("const COMMON_TAGS")) addError("editor.js still contains a local tag-preset authority");
}

async function checkTagPipelineFixtures() {
  await import(tagPipelinePath);
  const [rules, fixtures] = await Promise.all([
    readFile(tagRulesPath, "utf8").then(JSON.parse),
    readFile(tagFixturesPath, "utf8").then(JSON.parse)
  ]);
  globalThis.RonnieTagPipeline.validateRules(rules);
  for (const fixture of fixtures) {
    try {
      const result = globalThis.RonnieTagPipeline.buildTags(fixture.input, rules);
      if (fixture.expected_error) {
        addError(`${fixture.name}: expected ${fixture.expected_error}, but Tag Pipeline succeeded`);
      } else if (JSON.stringify(result.tags) !== JSON.stringify(fixture.expected.tags)) {
        addError(`${fixture.name}: unexpected tags ${JSON.stringify(result.tags)}`);
      }
    } catch (error) {
      if (!fixture.expected_error || error.code !== fixture.expected_error) {
        addError(`${fixture.name}: unexpected Tag Pipeline error ${error.code || error.message}`);
      }
    }
  }
}

async function checkLocalFixtureRoundTrip() {
  const title = "Phase 7 Admin Save Test";
  const slug = slugify(title);
  const date = "2026-06-27";
  const data = {
    articleId: "post-phase-7-admin-save-test",
    title,
    description: "Local fixture for verifying the Phase 7 admin article save flow.",
    date,
    tags: ["admin-test", "phase-7"],
    category: "灵命成长",
    scripture: "罗马书 8:1-4",
    author: "Ronnie",
    reviewed: false,
    draft: true,
    source: "local-admin-save-flow-fixture"
  };
  const body = "This temporary fixture verifies frontmatter serialization for the admin save flow.";
  const expectedFileName = `${date}-phase-7-admin-save-test.md`;
  const raw = serializeMarkdown(data, body);

  if (slug !== "phase-7-admin-save-test") addError(`slugify produced ${slug}`);
  if (path.basename(fixturePath) !== expectedFileName) addError("fixture path does not use expected slug");

  await rm(tmpDir, { recursive: true, force: true });
  await mkdir(tmpDir, { recursive: true });
  await writeFile(fixturePath, raw, "utf8");
  const parsed = parseMarkdown(await readFile(fixturePath, "utf8"));
  await rm(tmpDir, { recursive: true, force: true });

  for (const [key, value] of Object.entries(data)) {
    const parsedValue = parsed.data[key];
    if (JSON.stringify(parsedValue) !== JSON.stringify(value)) {
      addError(`round-trip mismatch for ${key}`);
    }
  }

  if (parsed.body.trim() !== body) addError("round-trip body mismatch");
  const validationErrors = validatePost(parsed.data, parsed.body, false);
  if (validationErrors.length) addError(`published validation failed: ${validationErrors.join(", ")}`);
}

await checkSourceGuards();
await checkTagPipelineFixtures();
await checkLocalFixtureRoundTrip();

console.log("Admin Save Flow Check");
console.log(`Errors: ${errors.length}`);
for (const error of errors) console.error(`ERROR ${error}`);
process.exit(errors.length ? 1 : 0);
