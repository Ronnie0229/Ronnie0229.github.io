#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from scripture_reference_normalizer import normalize_scripture_references

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation/inventory-v2-post-p2.json"


def split_markdown(text: str) -> tuple[str, str]:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        _, frontmatter, body = core.split("---", 2)
        return bom + "---" + frontmatter + "---", body
    raise SystemExit("markdown file missing canonical frontmatter")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = 0
    processed_changed = 0
    for item in manifest["items"]:
        if item["classification"] != "AUTO_SAFE":
            continue
        post_path = ROOT / item["path"]
        original = post_path.read_text(encoding="utf-8")
        frontmatter, body = split_markdown(original)
        normalized = normalize_scripture_references(body)
        if normalized == body:
            continue
        post_path.write_text(frontmatter + normalized, encoding="utf-8")
        changed += 1
        for rel in item["processed_matches"]:
            processed_path = ROOT / rel
            processed_original = processed_path.read_text(encoding="utf-8")
            processed_frontmatter, processed_body = split_markdown(processed_original)
            processed_normalized = normalize_scripture_references(processed_body)
            if processed_normalized != processed_body:
                processed_path.write_text(processed_frontmatter + processed_normalized, encoding="utf-8")
                processed_changed += 1
    print(json.dumps({"auto_safe_posts_changed": changed, "processed_copies_changed": processed_changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
