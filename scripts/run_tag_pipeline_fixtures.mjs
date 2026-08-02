#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
await import(path.join(rootDir, "assets", "admin", "tag-pipeline.js"));

const rules = JSON.parse(await readFile(path.join(rootDir, "assets", "admin", "tag-rules.json"), "utf8"));
const cases = JSON.parse(
  await readFile(path.join(rootDir, "scripts", "tests", "fixtures", "tag_pipeline_cases.json"), "utf8")
);

const results = cases.map((fixture) => {
  try {
    const result = globalThis.RonnieTagPipeline.buildTags(fixture.input, rules);
    return { name: fixture.name, ok: true, result };
  } catch (error) {
    return { name: fixture.name, ok: false, error: { code: error.code || "UNEXPECTED", message: error.message } };
  }
});

if (process.argv.includes("--json")) {
  console.log(JSON.stringify(results));
} else {
  let failures = 0;
  for (const [index, fixture] of cases.entries()) {
    const actual = results[index];
    if (fixture.expected_error) {
      if (actual.ok || actual.error.code !== fixture.expected_error) failures += 1;
    } else if (
      !actual.ok
      || JSON.stringify(actual.result.tags) !== JSON.stringify(fixture.expected.tags)
      || (fixture.expected.evidence
        && JSON.stringify(actual.result.evidence) !== JSON.stringify(fixture.expected.evidence))
    ) {
      failures += 1;
    }
  }
  console.log(`Tag Pipeline browser fixtures: ${cases.length - failures}/${cases.length} passed`);
  process.exitCode = failures ? 1 : 0;
}
