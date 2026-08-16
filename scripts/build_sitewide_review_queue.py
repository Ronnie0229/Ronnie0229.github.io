#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation/inventory-v3-post-auto-safe.json"
REPORT = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation/review-queue-v1.json"

COLLAPSED = re.compile(r"^[ \t]*\d+[.)][ \t]+.+[ \t]+\d+[.)][ \t]+")
TERMS = re.compile(r"\b(?:Doxology|Benediction|Wakachiai)\b", re.I)


def contexts_for(path: Path, item: dict) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    contexts: list[dict] = []
    remaining = item.get("remaining_compact_after_safe_normalization") or []
    for index, line in enumerate(lines, start=1):
        matched_reasons: list[str] = []
        refs = [ref for ref in remaining if ref in line]
        if refs:
            matched_reasons.append("unsupported_or_ambiguous_compact_scripture")
        if item.get("collapsed_numbered_list_candidate") and COLLAPSED.search(line):
            matched_reasons.append("collapsed_numbered_list_candidate")
        if TERMS.search(line):
            matched_reasons.append("fixed_term_requires_context_review")
        if matched_reasons:
            contexts.append({
                "line": index,
                "text": line,
                "matched_reasons": matched_reasons,
                "refs": refs,
            })
    return contexts


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    queue = []
    for item in manifest["items"]:
        if item["classification"] != "REVIEW_REQUIRED":
            continue
        path = ROOT / item["path"]
        queue.append({
            "path": item["path"],
            "reasons": item["reasons"],
            "processed_matches": item["processed_matches"],
            "contexts": contexts_for(path, item),
        })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "schema_version": "sitewide-display-remediation-review-queue-v1",
        "denominator": len(queue),
        "items": queue,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "denominator": len(queue)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
