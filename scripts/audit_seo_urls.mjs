import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const REPORT_PATH = path.join(ROOT, "docs", "seo-url-audit.csv");
const BASE_URL = process.env.SEO_AUDIT_BASE_URL ?? "https://ronniecross.com";
const SITEMAP_URL = new URL("/sitemap.xml", BASE_URL);
const EXTRA_URLS = [
  "https://ronniecross.com/search/?q=%7Bsearch_term_string%7D",
  "https://ronniecross.com/search/?q=test",
  "https://ronniecross.com/api/comments",
  "https://ronniecross.com/api/views",
  "https://ronniecross.com/api/visits",
  "https://www.ronniecross.com/cdn-cgi/l/email-protection"
];

function csvEscape(value) {
  const text = value == null ? "" : String(value);
  if (/[",\n\r]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

function extractLocs(xml) {
  return [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1].trim());
}

function findMetaRobots(html) {
  const match = html.match(/<meta\s+[^>]*name=["']robots["'][^>]*>/i);
  if (!match) return "";
  const content = match[0].match(/content=["']([^"']+)["']/i);
  return content ? content[1] : "";
}

function findCanonical(html) {
  const match = html.match(/<link\s+[^>]*rel=["']canonical["'][^>]*>/i);
  if (!match) return "";
  const href = match[0].match(/href=["']([^"']+)["']/i);
  return href ? href[1] : "";
}

async function inspectUrl(url) {
  const response = await fetch(url, { redirect: "follow" });
  const contentType = response.headers.get("content-type") ?? "";
  const xRobotsTag = response.headers.get("x-robots-tag") ?? "";
  let canonical = "";
  let metaRobots = "";

  if (contentType.includes("text/html")) {
    const html = await response.text();
    canonical = findCanonical(html);
    metaRobots = findMetaRobots(html);
  }

  return {
    requested_url: url,
    status: response.status,
    final_url: response.url,
    redirected: response.url === url ? "no" : "yes",
    canonical,
    canonical_matches_final_url: canonical && canonical === response.url ? "yes" : "no",
    meta_robots: metaRobots,
    x_robots_tag: xRobotsTag
  };
}

async function main() {
  const sitemapResponse = await fetch(SITEMAP_URL);
  if (!sitemapResponse.ok) {
    throw new Error(`Failed to fetch sitemap: ${sitemapResponse.status} ${sitemapResponse.statusText}`);
  }

  const sitemapXml = await sitemapResponse.text();
  const sitemapUrls = extractLocs(sitemapXml);
  const urls = [...new Set([...sitemapUrls, ...EXTRA_URLS])];
  const rows = [];

  for (const url of urls) {
    try {
      rows.push(await inspectUrl(url));
    } catch (error) {
      rows.push({
        requested_url: url,
        status: "fetch_error",
        final_url: "",
        redirected: "",
        canonical: "",
        canonical_matches_final_url: "",
        meta_robots: "",
        x_robots_tag: "",
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  const headers = [
    "requested_url",
    "status",
    "final_url",
    "redirected",
    "canonical",
    "canonical_matches_final_url",
    "meta_robots",
    "x_robots_tag",
    "error"
  ];
  const csv = [headers.join(","), ...rows.map((row) => headers.map((header) => csvEscape(row[header])).join(","))].join("\n") + "\n";
  fs.writeFileSync(REPORT_PATH, "\ufeff" + csv, "utf8");

  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Sitemap URLs: ${sitemapUrls.length}`);
  console.log(`Audited URLs: ${rows.length}`);
  console.log(`Report: ${path.relative(ROOT, REPORT_PATH).replace(/\\/g, "/")}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
