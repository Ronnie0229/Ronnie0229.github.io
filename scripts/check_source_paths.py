from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [
    ROOT / "data" / "processed" / "整理后的分享文章",
    ROOT / "data" / "processed" / "整理后的讲道文章",
    ROOT / "src" / "content" / "posts",
]
REPORT_DIR = ROOT / "docs" / "内容整理报告"
REPORT_PATH = REPORT_DIR / "source-path-check.csv"
SOURCE_RE = re.compile(r'^source:\s*["\'](?P<source>.*?)["\']\s*$', re.MULTILINE)


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for folder in TARGET_DIRS:
        if folder.exists():
            files.extend(sorted(folder.glob("*.md")))
    return files


def extract_source(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    match = SOURCE_RE.search(text)
    return match.group("source") if match else ""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

    rows: list[tuple[str, str, str, str]] = []
    missing_count = 0
    no_source_count = 0
    checked = 0

    for path in iter_markdown_files():
        checked += 1
        source = extract_source(path)
        rel_article = path.relative_to(ROOT).as_posix()
        if not source:
            no_source_count += 1
            rows.append((rel_article, "", "no_source", ""))
            continue
        source_path = ROOT / source
        if source_path.exists():
            rows.append((rel_article, source, "ok", source_path.relative_to(ROOT).as_posix()))
        else:
            missing_count += 1
            rows.append((rel_article, source, "missing", source_path.relative_to(ROOT).as_posix()))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("article", "source", "status", "resolved_path"))
        writer.writerows(rows)

    print(f"Checked: {checked}")
    print(f"No source: {no_source_count}")
    print(f"Missing: {missing_count}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT).as_posix()}")
    return 1 if missing_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
