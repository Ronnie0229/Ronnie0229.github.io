#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripture_reference_normalizer import normalize_scripture_references

ROOT = Path(__file__).resolve().parents[1]
FIXES = ROOT / "scripts/sitewide_display_reviewed_fixes_v1.json"
PROCESSED = ROOT / "data/processed"


def split_markdown(text: str) -> tuple[str, str]:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        _, frontmatter, body = core.split("---", 2)
        return bom + "---" + frontmatter + "---", body
    raise RuntimeError("markdown file missing canonical frontmatter")


def apply_body(body: str, replacements: list[list[str]], *, path: str) -> tuple[str, list[dict]]:
    report: list[dict] = []
    current = body
    for old, new in replacements:
        count = current.count(old)
        if count == 0:
            raise RuntimeError(f"reviewed replacement no longer matches {path}: {old[:100]}")
        current = current.replace(old, new)
        report.append({"old": old, "new": new, "count": count})
    current = normalize_scripture_references(current)
    return current, report


def processed_match(filename: str) -> Path:
    matches = list(PROCESSED.rglob(filename))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one processed mirror for {filename}, got {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    payload = json.loads(FIXES.read_text(encoding="utf-8"))
    result_items = []
    for item in payload["items"]:
        post = ROOT / item["path"]
        processed = processed_match(post.name)
        post_prefix, post_body = split_markdown(post.read_text(encoding="utf-8"))
        processed_prefix, processed_body = split_markdown(processed.read_text(encoding="utf-8"))

        post_new, post_replacements = apply_body(post_body, item["replacements"], path=item["path"])
        processed_new, processed_replacements = apply_body(
            processed_body,
            item["replacements"],
            path=str(processed.relative_to(ROOT)),
        )
        if post_new != processed_new:
            raise RuntimeError(f"post/processed body mismatch after reviewed remediation: {post.name}")

        if args.write:
            post.write_text(post_prefix + post_new, encoding="utf-8")
            processed.write_text(processed_prefix + processed_new, encoding="utf-8")

        result_items.append(
            {
                "post": item["path"],
                "processed": str(processed.relative_to(ROOT)),
                "post_replacements": post_replacements,
                "processed_replacements": processed_replacements,
                "body_changed": post_new != post_body,
            }
        )

    print(
        json.dumps(
            {
                "mode": "write" if args.write else "dry-run",
                "items": len(result_items),
                "changed": sum(1 for item in result_items if item["body_changed"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
