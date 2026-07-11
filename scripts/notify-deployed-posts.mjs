import { readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";

const siteUrl = String(process.env.SITE_URL || "https://ronniecross.com").replace(/\/$/, "");
const secret = String(process.env.EMAIL_AUTOMATION_SECRET || "");
const eventPath = process.env.GITHUB_EVENT_PATH;
const manualPostSlugs = String(process.env.MANUAL_POST_SLUGS || "");
const automationPath = String(process.env.EMAIL_AUTOMATION_PATH || "/api/email/auto-send");

if (!secret) {
  throw new Error("EMAIL_AUTOMATION_SECRET is required.");
}

if (!eventPath) {
  throw new Error("GITHUB_EVENT_PATH is required.");
}

const event = JSON.parse(await readFile(eventPath, "utf8"));
const before = String(event.before || "");
const after = String(event.after || process.env.GITHUB_SHA || "");

if (!after) {
  throw new Error("Unable to determine the pushed commit SHA.");
}

function changedPostSlugs() {
  if (manualPostSlugs.trim()) {
    return Array.from(
      new Set(
        manualPostSlugs
          .split(",")
          .map((slug) => slug.trim())
          .filter(Boolean)
      )
    );
  }

  const emptyBefore = /^0+$/.test(before);
  const args = emptyBefore
    ? ["show", "--pretty=format:", "--name-only", after]
    : ["diff", "--name-only", `${before}..${after}`];
  const output = execFileSync("git", args, { encoding: "utf8" });
  return Array.from(
    new Set(
      output
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => /^src\/content\/posts\/.+\.md$/i.test(line))
        .map((line) => line.replace(/^src\/content\/posts\//, "").replace(/\.md$/i, ""))
    )
  );
}

function commitIsDeployed(targetCommit, deployedCommit) {
  if (!deployedCommit) return false;
  if (deployedCommit === targetCommit) return true;

  try {
    execFileSync("git", ["fetch", "origin", "main", "--quiet"], { stdio: "ignore" });
    execFileSync("git", ["merge-base", "--is-ancestor", targetCommit, deployedCommit], {
      stdio: "ignore"
    });
    return true;
  } catch {
    return false;
  }
}

async function waitForDeployment(commit) {
  const deadline = Date.now() + 15 * 60 * 1000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${siteUrl}/deployment.json?commit=${encodeURIComponent(commit)}&time=${Date.now()}`, {
        headers: { Accept: "application/json" },
        cache: "no-store"
      });
      if (response.ok) {
        const deployment = await response.json();
        if (commitIsDeployed(commit, String(deployment.commit || ""))) return;
      }
    } catch {
      // Cloudflare Pages may be unavailable briefly while the deployment is switching.
    }
    await new Promise((resolve) => setTimeout(resolve, 15000));
  }
  throw new Error(`A deployment containing ${commit} was not observed within 15 minutes.`);
}

const slugs = changedPostSlugs();
if (!slugs.length) {
  console.log("No changed published posts were found in this push.");
  process.exit(0);
}

console.log(`Waiting for deployment ${after} before sending ${slugs.length} post notification(s).`);
await waitForDeployment(after);

const response = await fetch(`${siteUrl}${automationPath}`, {
  method: "POST",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-Email-Automation-Secret": secret
  },
  body: JSON.stringify({ slugs })
});
const data = await response.json().catch(() => ({}));

if (!response.ok || !data.ok) {
  throw new Error(data.error || `Email automation request failed with ${response.status}.`);
}

console.log(
  JSON.stringify(
    {
      postCount: data.postCount,
      recipientCount: data.recipientCount,
      successCount: data.successCount,
      failedCount: data.failedCount,
      skippedSlugs: data.skippedSlugs || []
    },
    null,
    2
  )
);

if (data.failedCount > 0) {
  process.exitCode = 1;
}
