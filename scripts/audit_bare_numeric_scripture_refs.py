#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "src/content/posts"
REPORT = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation/bare-numeric-ref-review-v1.json"
TOKEN_RE = re.compile(r"\d{1,3}\s*[:：]\s*\d{1,3}(?:\s*[-–—]\s*\d{1,3})?")


def body_only(text: str) -> str:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        return core.split("---", 2)[2]
    return text


def main() -> int:
    items = []
    for path in sorted(POSTS.glob("*.md")):
        body = body_only(path.read_text(encoding="utf-8"))
        for line_no, line in enumerate(body.splitlines(), start=1):
            tokens = [m.group(0) for m in TOKEN_RE.finditer(line)]
            if not tokens:
                continue
            # Already normalized scripture references use 章/节 and therefore do not match.
            # Keep all remaining numeric-colon tokens for explicit review; do not guess here.
            items.append({
                "path": str(path.relative_to(ROOT)),
                "body_line": line_no,
                "tokens": tokens,
                "text": line,
            })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "schema_version": "bare-numeric-scripture-ref-review-v1",
        "denominator": len(items),
        "items": items,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "denominator": len(items)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
