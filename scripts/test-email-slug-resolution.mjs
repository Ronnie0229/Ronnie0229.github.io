import assert from "node:assert/strict";

import { canonicalSlugKey, resolvePublishedSlugs } from "../functions/api/admin/email/auto-send.js";

const fileSlug = "2026-07-12-希伯来书-11-1-4｜像亚伯一样的信心";
const publishedSlug = "2026-07-12-希伯来书-11-1-4像亚伯一样的信心";

assert.equal(canonicalSlugKey(fileSlug), canonicalSlugKey(publishedSlug));

assert.deepEqual(
  resolvePublishedSlugs([fileSlug], [{ slug: publishedSlug }]),
  {
    resolved: [publishedSlug],
    missing: [],
    ambiguous: []
  },
  "filename slug with punctuation resolves to the single published slug"
);

assert.deepEqual(
  resolvePublishedSlugs([publishedSlug], [{ slug: publishedSlug }]),
  {
    resolved: [publishedSlug],
    missing: [],
    ambiguous: []
  },
  "exact slug match resolves without canonical fallback"
);

assert.deepEqual(
  resolvePublishedSlugs(["2026-07-12-不存在的文章"], [{ slug: publishedSlug }]),
  {
    resolved: [],
    missing: ["2026-07-12-不存在的文章"],
    ambiguous: []
  },
  "unknown slug is reported as missing"
);

assert.deepEqual(
  resolvePublishedSlugs([fileSlug], [
    { slug: publishedSlug },
    { slug: "2026-07-12-希伯来书-11-1-4像亚伯一样的信心!" }
  ]),
  {
    resolved: [],
    missing: [],
    ambiguous: [
      {
        requested: fileSlug,
        matches: [
          publishedSlug,
          "2026-07-12-希伯来书-11-1-4像亚伯一样的信心!"
        ]
      }
    ]
  },
  "canonical key collision is ambiguous and never auto-selected"
);

console.log("Email slug resolution tests passed.");
