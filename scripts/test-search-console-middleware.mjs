import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { onRequest } from "../functions/_middleware.js";

async function runMiddleware(url) {
  let nextCalled = false;
  const response = await onRequest({
    request: new Request(url),
    next() {
      nextCalled = true;
      return new Response("next", { status: 200 });
    },
  });

  return {
    response,
    nextCalled,
    status: response.status,
    location: response.headers.get("location"),
  };
}

async function assertRedirect(url, expectedLocation, message) {
  const result = await runMiddleware(url);
  assert.equal(result.nextCalled, false, `${message}: should not call next`);
  assert.equal(result.status, 301, `${message}: status`);
  assert.equal(result.location, expectedLocation, `${message}: location`);
}

async function assertNext(url, message) {
  const result = await runMiddleware(url);
  assert.equal(result.nextCalled, true, `${message}: should call next`);
  assert.equal(result.status, 200, `${message}: status`);
  assert.equal(result.location, null, `${message}: location`);
}

async function assertGone(url, message) {
  const result = await runMiddleware(url);
  assert.equal(result.nextCalled, false, `${message}: should not call next`);
  assert.equal(result.status, 410, `${message}: status`);
  assert.equal(result.location, null, `${message}: location`);
  assert.match(
    result.response.headers.get("x-robots-tag") || "",
    /noindex/i,
    `${message}: x-robots-tag`
  );
}

await assertRedirect(
  "https://www.ronniecross.com/",
  "https://ronniecross.com/",
  "www root canonicalizes to apex HTTPS"
);

await assertGone(
  "https://ronniecross.com/posts/2026-06-13-%E9%A9%AC%E5%A4%AA%E7%A6%8F%E9%9F%B3-2119%E4%B8%BA%E4%BB%80%E4%B9%88%E8%80%B6%E7%A8%A3%E8%A6%81%E5%92%92%E8%AF%85%E6%97%A0%E8%8A%B1%E6%9E%9C%E6%A0%91/",
  "permanently removed post returns gone"
);

await assertGone(
  "https://ronniecross.com/posts/?category=%E7%81%B5%E5%91%BD%E6%88%90%E9%95%BF&focus=2026-06-12-test",
  "legacy focus URL for removed test post returns gone"
);

await assertGone(
  "https://ronniecross.com/posts/?category=%E7%81%B5%E5%91%BD%E6%88%90%E9%95%BF&focus=2026-06-13-%E9%A9%AC%E5%A4%AA%E7%A6%8F%E9%9F%B3-2119%E4%B8%BA%E4%BB%80%E4%B9%88%E8%80%B6%E7%A8%A3%E8%A6%81%E5%92%92%E8%AF%85%E6%97%A0%E8%8A%B1%E6%9E%9C%E6%A0%91",
  "legacy focus URL for removed post returns gone"
);

await assertRedirect(
  "https://www.ronniecross.com/about/",
  "https://ronniecross.com/about/",
  "www about canonicalizes and keeps path"
);

await assertRedirect(
  "https://ronniecross.com/posts/?category=%E6%95%99%E4%BC%9A%E8%AE%B2%E9%81%93",
  "https://ronniecross.com/posts/category/sermons/",
  "legacy sermons category query redirects"
);

await assertRedirect(
  "https://ronniecross.com/posts/?category=%E6%95%99%E4%BC%9A%E8%AE%B2%E9%81%93&focus=2026-07-12-%E5%B8%8C%E4%BC%AF%E6%9D%A5%E4%B9%A6-11-1-4%E5%83%8F%E4%BA%9A%E4%BC%AF%E4%B8%80%E6%A0%B7%E7%9A%84%E4%BF%A1%E5%BF%83#post-2026-07-12-%E5%B8%8C%E4%BC%AF%E6%9D%A5%E4%B9%A6-11-1-4%E5%83%8F%E4%BA%9A%E4%BC%AF%E4%B8%80%E6%A0%B7%E7%9A%84%E4%BF%A1%E5%BF%83",
  "https://ronniecross.com/posts/2026-07-12-%E5%B8%8C%E4%BC%AF%E6%9D%A5%E4%B9%A6-11-1-4%E5%83%8F%E4%BA%9A%E4%BC%AF%E4%B8%80%E6%A0%B7%E7%9A%84%E4%BF%A1%E5%BF%83/",
  "focus query takes precedence over category query"
);

await assertNext(
  "https://ronniecross.com/about/",
  "canonical normal URL passes through"
);

await assertNext(
  "https://ronniecross.com/posts/?utm_source=search-console",
  "unknown posts query passes through"
);

const robotsTxt = readFileSync(new URL("../assets/robots.txt", import.meta.url), "utf8");
assert.doesNotMatch(
  robotsTxt,
  /^Disallow:\s*\/posts\/\?\*/m,
  "legacy posts query URLs must remain crawlable so Google can process redirects"
);
assert.doesNotMatch(
  robotsTxt,
  /^Disallow:\s*\/search\/\?\*/m,
  "search result URLs must remain crawlable so Google can process noindex"
);

console.log("Search Console middleware tests passed");
