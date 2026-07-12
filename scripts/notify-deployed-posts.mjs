import { readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const siteUrl = String(process.env.SITE_URL || "https://ronniecross.com").replace(/\/$/, "");
const secret = String(process.env.EMAIL_AUTOMATION_SECRET || "");
const eventPath = process.env.GITHUB_EVENT_PATH;
const manualPostSlugs = String(process.env.MANUAL_POST_SLUGS || "");
const automationPath = String(process.env.EMAIL_AUTOMATION_PATH || "/api/email/auto-send");
const checkOnly = String(process.env.EMAIL_CHECK_ONLY || "").toLowerCase() === "true";

async function loadGitHubEvent() {
  if (!eventPath) {
    throw new Error("GITHUB_EVENT_PATH is required.");
  }
  const event = JSON.parse(await readFile(eventPath, "utf8"));
  const before = String(event.before || "");
  const after = String(event.after || process.env.GITHUB_SHA || "");
  if (!after) {
    throw new Error("Unable to determine the pushed commit SHA.");
  }
  return { before, after };
}

function changedPostSlugs({ before, after }) {
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
    ? ["show", "--pretty=format:", "--name-only", "--diff-filter=A", "-z", after]
    : ["diff", "--name-only", "--diff-filter=A", "-z", `${before}..${after}`];
  const output = execFileSync("git", args, { encoding: "utf8" });
  return Array.from(
    new Set(
      output
        .split("\0")
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

const SEND_RETRY_DELAYS_MS = [10000, 30000];

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
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
    await sleep(15000);
  }
  throw new Error(`A deployment containing ${commit} was not observed within 15 minutes.`);
}

function formatAttemptResult(data, attempt) {
  return {
    attempt,
    postCount: data.postCount,
    recipientCount: data.recipientCount,
    successCount: data.successCount,
    failedCount: data.failedCount,
    skippedSlugs: data.skippedSlugs || []
  };
}

function formatCheckOnlyResult(data) {
  return {
    checkOnly: data.checkOnly,
    requestedSlugs: data.requestedSlugs || [],
    resolvedSlugs: data.resolvedSlugs || [],
    existingSends: data.existingSends || [],
    hasSentOrSuccess: data.hasSentOrSuccess === true
  };
}

async function requestEmailAutomation({ slugs, checkOnly }) {
  if (!secret) {
    throw new Error("EMAIL_AUTOMATION_SECRET is required.");
  }
  const response = await fetch(`${siteUrl}${automationPath}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "X-Email-Automation-Secret": secret
    },
    body: JSON.stringify({ slugs, checkOnly })
  });
  const data = await response.json().catch(() => ({}));

  if (!response.ok || !data.ok) {
    throw new Error(data.error || `Email automation request failed with ${response.status}.`);
  }
  return data;
}

export async function notifyWithRetries({
  slugs,
  checkOnly = false,
  request = requestEmailAutomation,
  wait = sleep,
  retryDelaysMs = SEND_RETRY_DELAYS_MS,
  log = console.log
}) {
  if (checkOnly) {
    const data = await request({ slugs, checkOnly: true });
    log(JSON.stringify(formatCheckOnlyResult(data), null, 2));
    if (data.hasSentOrSuccess === true) {
      throw new Error("D1 already contains a sent/success record for the target slug.");
    }
    return data;
  }

  let lastData = null;
  const maxAttempts = retryDelaysMs.length + 1;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const data = await request({ slugs, checkOnly: false });
    lastData = data;
    log(JSON.stringify(formatAttemptResult(data, attempt), null, 2));

    if (Number(data.failedCount || 0) === 0) return data;
    if (attempt < maxAttempts) {
      const delay = retryDelaysMs[attempt - 1];
      log(`Attempt ${attempt} still has ${data.failedCount} failed recipient(s); retrying in ${delay / 1000}s.`);
      await wait(delay);
    }
  }

  throw new Error(`Email automation still has ${lastData.failedCount} failed recipient(s) after ${maxAttempts} attempts.`);
}

async function main() {
  const { before, after } = await loadGitHubEvent();
  const slugs = changedPostSlugs({ before, after });
  if (!slugs.length) {
    console.log("No changed published posts were found in this push.");
    return;
  }

  console.log(`Waiting for deployment ${after} before ${checkOnly ? "checking" : "sending"} ${slugs.length} post notification(s).`);
  await waitForDeployment(after);
  await notifyWithRetries({ slugs, checkOnly });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
