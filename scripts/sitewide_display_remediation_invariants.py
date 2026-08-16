#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "src/content/posts"
REPORT_DIR = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation"
BASELINE = REPORT_DIR / "frontmatter-baseline-v1.json"


def split_markdown(text: str) -> tuple[str, str]:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        _, frontmatter, body = core.split("---", 2)
        return bom + "---" + frontmatter + "---", body
    raise ValueError("missing frontmatter")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def capture() -> int:
    rows = []
    for path in sorted(POSTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter, _ = split_markdown(text)
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "frontmatter_sha256": digest(frontmatter),
        })
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps({"schema_version":"sitewide-frontmatter-baseline-v1","items":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"captured":len(rows),"baseline":str(BASELINE)},ensure_ascii=False))
    return 0


def verify() -> int:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    failures=[]
    for row in data["items"]:
        path=ROOT/row["path"]
        if not path.exists():
            failures.append({"path":row["path"],"reason":"missing"})
            continue
        frontmatter,_=split_markdown(path.read_text(encoding="utf-8"))
        actual=digest(frontmatter)
        if actual != row["frontmatter_sha256"]:
            failures.append({"path":row["path"],"reason":"frontmatter_changed","expected":row["frontmatter_sha256"],"actual":actual})
    print(json.dumps({"verified":len(data["items"]),"failures":failures},ensure_ascii=False))
    return 1 if failures else 0


def main() -> int:
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["capture","verify"])
    args=p.parse_args()
    return capture() if args.mode=="capture" else verify()


if __name__ == "__main__":
    raise SystemExit(main())
