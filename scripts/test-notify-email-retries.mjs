import assert from "node:assert/strict";

import { notifyWithRetries } from "./notify-deployed-posts.mjs";

function createLogger() {
  const lines = [];
  return {
    lines,
    log(message) {
      lines.push(String(message));
    }
  };
}

async function runScenario(responses, options = {}) {
  const calls = [];
  const waits = [];
  const logger = createLogger();
  let index = 0;

  const result = await notifyWithRetries({
    slugs: ["target-post"],
    checkOnly: options.checkOnly === true,
    retryDelaysMs: [10, 30],
    wait: async (ms) => {
      waits.push(ms);
    },
    log: logger.log,
    request: async (request) => {
      calls.push(request);
      const response = responses[index];
      index += 1;
      if (response instanceof Error) throw response;
      return response;
    }
  });

  return { result, calls, waits, logs: logger.lines };
}

const partialThenSuccess = await runScenario([
  { ok: true, postCount: 1, recipientCount: 3, successCount: 2, failedCount: 1, skippedSlugs: [] },
  { ok: true, postCount: 1, recipientCount: 1, successCount: 1, failedCount: 0, skippedSlugs: [] }
]);
assert.equal(partialThenSuccess.result.failedCount, 0);
assert.equal(partialThenSuccess.calls.length, 2);
assert.deepEqual(partialThenSuccess.waits, [10]);
assert.deepEqual(partialThenSuccess.calls.map((call) => call.checkOnly), [false, false]);
assert.match(partialThenSuccess.logs.join("\n"), /"attempt": 1/);
assert.match(partialThenSuccess.logs.join("\n"), /"attempt": 2/);

await assert.rejects(
  runScenario([
    { ok: true, postCount: 1, recipientCount: 3, successCount: 2, failedCount: 1, skippedSlugs: [] },
    { ok: true, postCount: 1, recipientCount: 1, successCount: 0, failedCount: 1, skippedSlugs: [] },
    { ok: true, postCount: 1, recipientCount: 1, successCount: 0, failedCount: 1, skippedSlugs: [] }
  ]),
  /still has 1 failed recipient/
);

const firstSuccess = await runScenario([
  { ok: true, postCount: 1, recipientCount: 3, successCount: 3, failedCount: 0, skippedSlugs: [] }
]);
assert.equal(firstSuccess.calls.length, 1);
assert.deepEqual(firstSuccess.waits, []);

const checkOnly = await runScenario(
  [
    {
      ok: true,
      checkOnly: true,
      requestedSlugs: ["target-post"],
      resolvedSlugs: ["target-post"],
      existingSends: [],
      hasSentOrSuccess: false
    }
  ],
  { checkOnly: true }
);
assert.equal(checkOnly.calls.length, 1);
assert.deepEqual(checkOnly.calls[0], { slugs: ["target-post"], checkOnly: true });
assert.deepEqual(checkOnly.waits, []);

console.log("Email notification retry tests passed.");
