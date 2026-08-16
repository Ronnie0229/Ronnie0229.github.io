#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripture_reference_normalizer import normalize_scripture_references

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "src/content/posts"
PROCESSED = ROOT / "data/processed"


def split_markdown(text: str) -> tuple[str, str]:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        _, frontmatter, body = core.split("---", 2)
        return bom + "---" + frontmatter + "---", body
    raise RuntimeError("markdown file missing canonical frontmatter")


def processed_match(filename: str) -> Path | None:
    matches = list(PROCESSED.rglob(filename))
    if len(matches) > 1:
        raise RuntimeError(f"multiple processed mirrors for {filename}")
    return matches[0] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    posts_changed = 0
    processed_changed = 0
    missing_processed = []

    for post in sorted(POSTS.glob("*.md")):
        post_prefix, post_body = split_markdown(post.read_text(encoding="utf-8"))
        post_new = normalize_scripture_references(post_body)
        processed = processed_match(post.name)
        if processed is None:
            missing_processed.append(post.name)
        else:
            processed_prefix, processed_body = split_markdown(processed.read_text(encoding="utf-8"))
            processed_new = normalize_scripture_references(processed_body)
            if post_new != processed_new:
                raise RuntimeError(f"post/processed body mismatch after safe normalization: {post.name}")
            if processed_new != processed_body:
                processed_changed += 1
                if args.write:
                    processed.write_text(processed_prefix + processed_new, encoding="utf-8")

        if post_new != post_body:
            posts_changed += 1
            if args.write:
                post.write_text(post_prefix + post_new, encoding="utf-8")

    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "posts_changed": posts_changed,
        "processed_changed": processed_changed,
        "missing_processed_count": len(missing_processed),
        "missing_processed": missing_processed,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
