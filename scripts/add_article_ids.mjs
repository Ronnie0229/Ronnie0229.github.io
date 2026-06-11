import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const projectRoot = path.resolve(import.meta.dirname, "..");
const postsDirectory = path.join(projectRoot, "src", "content", "posts");
const checkOnly = process.argv.includes("--check");
const files = (await readdir(postsDirectory))
  .filter((name) => name.endsWith(".md"))
  .sort((a, b) => a.localeCompare(b, "zh-CN"));
const seenIds = new Set();
let changed = 0;

for (const fileName of files) {
  const filePath = path.join(postsDirectory, fileName);
  const content = await readFile(filePath, "utf8");
  const existing = content.match(/^---\r?\n(?:[\s\S]*?\r?\n)?articleId:\s*"?([^"\r\n]+)"?/m);

  if (existing) {
    const articleId = existing[1].trim();
    if (seenIds.has(articleId)) {
      throw new Error(`发现重复 articleId：${articleId}`);
    }
    seenIds.add(articleId);
    continue;
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
    const lineEnding = content.startsWith("---\r\n") ? "\r\n" : "\n";
    const updated = content.replace(
      `---${lineEnding}`,
      `---${lineEnding}articleId: "${articleId}"${lineEnding}`
    );
    await writeFile(filePath, updated, "utf8");
  }
}

console.log(
  checkOnly
    ? `检查完成：${files.length} 篇文章，${changed} 篇缺少 articleId。`
    : `处理完成：${files.length} 篇文章，已为 ${changed} 篇补充 articleId。`
);
