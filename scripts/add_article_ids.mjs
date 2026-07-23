import { createHash } from "node:crypto";
import { access, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const projectRoot = path.resolve(import.meta.dirname, "..");
const postsDirectory = path.join(projectRoot, "src", "content", "posts");
const processedDirectories = [
  path.join(projectRoot, "data", "processed", "整理后的分享文章"),
  path.join(projectRoot, "data", "processed", "整理后的讲道文章"),
];
if (process.argv.includes("--help") || process.argv.includes("-h")) {
  console.log("Usage: node scripts/add_article_ids.mjs [--check]");
  process.exit(0);
}
const checkOnly = process.argv.includes("--check");
const files = (await readdir(postsDirectory))
  .filter((name) => name.endsWith(".md"))
  .sort((a, b) => a.localeCompare(b, "zh-CN"));
const seenIds = new Set();
let changed = 0;
let processedChanged = 0;

async function exists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

function frontmatterArticleId(content) {
  return content.match(/^---\r?\n(?:[\s\S]*?\r?\n)?articleId:\s*"?([^"\r\n]+)"?/m);
}

function setArticleId(content, articleId) {
  const existing = frontmatterArticleId(content);
  const lineEnding = content.startsWith("---\r\n") ? "\r\n" : "\n";
  return existing
    ? content.replace(/^articleId:\s*"?\s*"?\s*$/m, `articleId: "${articleId}"`)
    : content.replace(
        `---${lineEnding}`,
        `---${lineEnding}articleId: "${articleId}"${lineEnding}`
      );
}

async function syncProcessedArticleId(fileName, articleId) {
  for (const directory of processedDirectories) {
    const filePath = path.join(directory, fileName);
    if (!(await exists(filePath))) {
      continue;
    }
    const rawContent = await readFile(filePath, "utf8");
    const content = rawContent.replace(/^\uFEFF/, "");
    if (!content.startsWith("---\n") && !content.startsWith("---\r\n")) {
      throw new Error(`processed mirror 缺少 Frontmatter：${filePath}`);
    }
    const existing = frontmatterArticleId(content);
    const current = existing?.[1]?.trim();
    if (current && current !== articleId) {
      throw new Error(`processed mirror articleId 不一致：${filePath}`);
    }
    if (current === articleId) {
      continue;
    }
    processedChanged += 1;
    if (!checkOnly) {
      await writeFile(filePath, setArticleId(content, articleId), "utf8");
    }
  }
}

for (const fileName of files) {
  const filePath = path.join(postsDirectory, fileName);
  const rawContent = await readFile(filePath, "utf8");
  const content = rawContent.replace(/^\uFEFF/, "");
  const existing = frontmatterArticleId(content);

  if (existing) {
    const articleId = existing[1].trim();
    if (articleId) {
      if (seenIds.has(articleId)) {
        throw new Error(`发现重复 articleId：${articleId}`);
      }
      seenIds.add(articleId);
      await syncProcessedArticleId(fileName, articleId);
      continue;
    }
  }

  if (!content.startsWith("---\n") && !content.startsWith("---\r\n")) {
    throw new Error(`文章缺少 Frontmatter：${fileName}`);
  }

  const slug = path.basename(fileName, ".md");
  const articleId = `post-${createHash("sha256").update(slug).digest("hex").slice(0, 16)}`;
  if (seenIds.has(articleId)) {
    throw new Error(`生成了重复 articleId：${articleId}`);
  }
  seenIds.add(articleId);
  changed += 1;

  if (!checkOnly) {
    await writeFile(filePath, setArticleId(content, articleId), "utf8");
  }
  await syncProcessedArticleId(fileName, articleId);
}

console.log(
  checkOnly
    ? `检查完成：${files.length} 篇文章，${changed} 篇缺少 articleId，${processedChanged} 个 processed mirror 缺少同步 articleId。`
    : `处理完成：${files.length} 篇文章，已为 ${changed} 篇补充 articleId，已同步 ${processedChanged} 个 processed mirror。`
);
