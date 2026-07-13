import assert from "node:assert/strict";

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

await assertRedirect(
  "https://www.ronniecross.com/",
  "https://ronniecross.com/",
  "www root canonicalizes to apex HTTPS"
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

console.log("Search Console middleware tests passed");
