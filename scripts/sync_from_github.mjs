import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function runGit(args, capture = false) {
  const result = spawnSync("git", ["-C", projectRoot, ...args], {
    encoding: "utf8",
    stdio: capture ? "pipe" : "inherit",
  });
  if (result.error) {
    throw new Error(`Git could not be started: ${result.error.message}`);
  }
  return result;
}

const status = runGit(["status", "--porcelain"], true);
if (status.status !== 0) {
  throw new Error(status.stderr.trim() || "Unable to read the Git status.");
}

if (status.stdout.trim()) {
  console.error("Local changes were found. Sync stopped to avoid overwriting them.");
  console.error(status.stdout.trimEnd());
  process.exit(2);
}

console.log("Rebasing local main onto the latest website changes from GitHub...");
const pull = runGit(["pull", "--rebase", "origin", "main"]);
if (pull.status !== 0) {
  throw new Error("Sync failed. Check the network, GitHub credentials, or rebase conflicts.");
}

console.log("Sync complete. The local project is rebased onto origin/main.");
