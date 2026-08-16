#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT.parent / "讲道整理/reports/sitewide-published-content-display-remediation/bare-numeric-ref-review-v1.json"
DECISIONS = ROOT / "scripts/bare_numeric_ref_decisions_v2.json"
PROCESSED = ROOT / "data/processed"


def split_markdown(text: str) -> tuple[str, str]:
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    core = text[1:] if bom else text
    if core.startswith("---") and core.count("---") >= 2:
        _, frontmatter, body = core.split("---", 2)
        return bom + "---" + frontmatter + "---", body
    raise RuntimeError("markdown file missing canonical frontmatter")


def mirror_for(filename: str) -> Path:
    matches = list(PROCESSED.rglob(filename))
    if len(matches) != 1:
        raise RuntimeError(f"expected one processed mirror for {filename}, got {len(matches)}")
    return matches[0]


def apply_decision(body: str, old_line: str, decision: dict, *, label: str) -> tuple[str, bool]:
    lines = body.splitlines(keepends=True)
    indexes = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == old_line]
    if len(indexes) != 1:
        raise RuntimeError(f"expected exact review line once in {label}, got {len(indexes)}: {old_line[:100]}")
    idx = indexes[0]
    line = lines[idx]
    if decision["action"] == "NO_CHANGE_NON_SCRIPTURE":
        return body, False
    if decision["action"] != "FIX":
        raise RuntimeError(f"unsupported decision action: {decision['action']}")
    current = line
    for old, new in decision.get("replacements", []):
        count = current.count(old)
        if count != 1:
            raise RuntimeError(f"expected reviewed token once in {label}, got {count}: {old}")
        current = current.replace(old, new, 1)
    lines[idx] = current
    return "".join(lines), current != line


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    decisions_payload = json.loads(DECISIONS.read_text(encoding="utf-8"))
    decisions = decisions_payload["decisions"]
    if report["denominator"] != decisions_payload["denominator"] or len(decisions) != report["denominator"]:
        raise RuntimeError("report/decision denominator mismatch")

    grouped: dict[str, list[tuple[dict, dict]]] = {}
    fixed_decisions = 0
    exceptions = 0
    for index, item in enumerate(report["items"], start=1):
        decision = decisions.get(str(index))
        if decision is None:
            raise RuntimeError(f"missing decision {index}")
        grouped.setdefault(item["path"], []).append((item, decision))
        if decision["action"] == "FIX":
            fixed_decisions += 1
        else:
            exceptions += 1

    changed_posts = 0
    changed_processed = 0
    for rel_path, entries in grouped.items():
        post = ROOT / rel_path
        processed = mirror_for(post.name)
        post_prefix, post_body = split_markdown(post.read_text(encoding="utf-8"))
        processed_prefix, processed_body = split_markdown(processed.read_text(encoding="utf-8"))
        post_changed = False
        processed_changed = False
        for item, decision in entries:
            post_body, changed = apply_decision(post_body, item["text"], decision, label=rel_path)
            post_changed = post_changed or changed
            processed_body, changed = apply_decision(
                processed_body,
                item["text"],
                decision,
                label=str(processed.relative_to(ROOT)),
            )
            processed_changed = processed_changed or changed
        if post_body != processed_body:
            raise RuntimeError(f"post/processed mismatch after bare-ref decisions: {post.name}")
        if post_changed:
            changed_posts += 1
            if args.write:
                post.write_text(post_prefix + post_body, encoding="utf-8")
        if processed_changed:
            changed_processed += 1
            if args.write:
                processed.write_text(processed_prefix + processed_body, encoding="utf-8")

    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "decision_denominator": report["denominator"],
        "fixed_decisions": fixed_decisions,
        "non_scripture_exceptions": exceptions,
        "changed_posts": changed_posts,
        "changed_processed": changed_processed,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
