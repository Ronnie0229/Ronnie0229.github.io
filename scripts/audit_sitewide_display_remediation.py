#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from scripture_reference_normalizer import (
    find_compact_chinese_references,
    normalize_scripture_references,
)

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "src/content/posts"
PROCESSED = ROOT / "data/processed"
REPORT = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation/inventory-v4-post-reviewed-fixes.json"

COLLAPSED = re.compile(r"^[ \t]*\d+[.)][ \t]+.+[ \t]+\d+[.)][ \t]+", re.M)
DOXOLOGY = re.compile(r"\bDoxology\b", re.I)
BENEDICTION = re.compile(r"\bBenediction\b", re.I)
WAKACHIAI = re.compile(r"\bWakachiai\b", re.I)
DRAFT = re.compile(r"(?m)^draft:\s*true\s*$", re.I)


def split_markdown(text: str) -> tuple[str, str, str]:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        _, frontmatter, body = core.split("---", 2)
        return bom + "---" + frontmatter + "---", frontmatter, body
    return "", "", text


def processed_matches(name: str) -> list[str]:
    return [str(path.relative_to(ROOT)) for path in PROCESSED.rglob(name)]


def main() -> int:
    items: list[dict] = []
    published = 0
    for path in sorted(POSTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        _prefix, frontmatter, body = split_markdown(text)
        if DRAFT.search(frontmatter):
            continue
        published += 1
        normalized = normalize_scripture_references(body)
        remaining_compact = find_compact_chinese_references(normalized)
        collapsed = bool(COLLAPSED.search(body))
        doxology = bool(DOXOLOGY.search(body))
        benediction = bool(BENEDICTION.search(body))
        wakachiai = bool(WAKACHIAI.search(body))
        scripture_change = normalized != body
        reasons: list[str] = []
        if remaining_compact:
            reasons.append("unsupported_or_ambiguous_compact_scripture")
        if collapsed:
            reasons.append("collapsed_numbered_list_candidate")
        if doxology:
            reasons.append("doxology_term_requires_context_review")
        if benediction:
            reasons.append("benediction_term_requires_context_review")
        if wakachiai:
            reasons.append("wakachiai_term_requires_context_review")

        if reasons:
            classification = "REVIEW_REQUIRED"
        elif scripture_change:
            classification = "AUTO_SAFE"
        else:
            classification = "NO_CHANGE"

        items.append(
            {
                "path": str(path.relative_to(ROOT)),
                "classification": classification,
                "scripture_display_change": scripture_change,
                "remaining_compact_after_safe_normalization": remaining_compact,
                "collapsed_numbered_list_candidate": collapsed,
                "doxology_term": doxology,
                "benediction_term": benediction,
                "wakachiai_term": wakachiai,
                "processed_matches": processed_matches(path.name),
                "reasons": reasons,
            }
        )

    counts = {key: 0 for key in ("AUTO_SAFE", "REVIEW_REQUIRED", "NO_CHANGE", "BLOCKED")}
    for item in items:
        counts[item["classification"]] += 1
    result = {
        "schema_version": "sitewide-display-remediation-inventory-v1",
        "published_denominator": published,
        "scope": "website-visible-content-only",
        "forbidden": [
            "GEO",
            "SEO",
            "frontmatter_machine_metadata",
            "slug_url",
            "archived_sermon_sources",
            "fidelity_audit_objects",
        ],
        "counts": counts,
        "items": items,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "published_denominator": published, "counts": counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
