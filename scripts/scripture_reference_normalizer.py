from __future__ import annotations

import json
import re
from pathlib import Path


ALIASES_PATH = Path(__file__).with_name("project_bible_book_aliases.json")


def _load_aliases() -> tuple[dict[str, str], list[dict[str, str]]]:
    payload = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    books = payload.get("books")
    if not isinstance(books, list) or len(books) != 66:
        raise RuntimeError("Project Bible book alias inventory must contain exactly 66 books")

    alias_to_name: dict[str, str] = {}
    for record in books:
        if not isinstance(record, dict):
            raise RuntimeError("Invalid Project Bible book alias record")
        name = str(record.get("book_name", "")).strip()
        abbr = str(record.get("book_abbr", "")).strip()
        if not name or not abbr:
            raise RuntimeError("Project Bible book alias record missing book_name/book_abbr")
        for alias in (name, abbr):
            previous = alias_to_name.get(alias)
            if previous is not None and previous != name:
                raise RuntimeError(f"Ambiguous Project Bible book alias: {alias}")
            alias_to_name[alias] = name
    return alias_to_name, books


ALIAS_TO_NAME, BOOK_RECORDS = _load_aliases()
BOOK_ALIASES = sorted(ALIAS_TO_NAME, key=len, reverse=True)
BOOK_PATTERN = "(?:" + "|".join(re.escape(alias) for alias in BOOK_ALIASES) + ")"

COMPACT_REFERENCE_RE = re.compile(
    rf"(?P<book>{BOOK_PATTERN})\s*"
    r"(?P<chapter>\d{1,3})\s*[:：]\s*(?P<verse>\d{1,3})"
    r"(?:\s*[-–—至到]\s*(?:(?P<end_chapter>\d{1,3})\s*[:：]\s*)?(?P<end_verse>\d{1,3}))?"
)

COMPACT_DETECTION_RE = re.compile(
    rf"(?P<book>{BOOK_PATTERN})\s*\d{{1,3}}\s*[:：]\s*\d{{1,3}}"
)


def normalize_scripture_references(text: str) -> str:
    """Normalize unambiguous Chinese scripture refs into TTS-friendly display text.

    Examples:
    - 罗 1:15 -> 罗马书1章15节
    - 罗马书 1:15-18 -> 罗马书1章15节到18节
    - 罗马书 8:38-9:2 -> 罗马书8章38节到9章2节

    The canonical book names/abbreviations are derived from the controlled
    CUVMPS Rv2 Project Bible book inventory. This function does not touch
    already-spoken references such as “罗马书8章38节”.
    """

    def replace(match: re.Match[str]) -> str:
        tail = match.string[match.end():]
        if re.match(r"\s*[,，、]\s*\d", tail):
            return match.group(0)

        book_name = ALIAS_TO_NAME[match.group("book")]
        chapter = int(match.group("chapter"))
        verse = int(match.group("verse"))
        end_chapter_raw = match.group("end_chapter")
        end_verse_raw = match.group("end_verse")

        if end_verse_raw is None:
            return f"{book_name}{chapter}章{verse}节"

        end_verse = int(end_verse_raw)
        if end_chapter_raw is None:
            return f"{book_name}{chapter}章{verse}节到{end_verse}节"

        end_chapter = int(end_chapter_raw)
        return f"{book_name}{chapter}章{verse}节到{end_chapter}章{end_verse}节"

    return COMPACT_REFERENCE_RE.sub(replace, text)


def find_compact_chinese_references(text: str) -> list[str]:
    return [match.group(0) for match in COMPACT_DETECTION_RE.finditer(text)]
