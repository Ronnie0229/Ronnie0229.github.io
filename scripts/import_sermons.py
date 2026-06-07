from __future__ import annotations

import re
import shutil
import textwrap
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "教会讲道"
ORGANIZED_DIR = ROOT / "整理后的讲道文章"
POSTS_DIR = ROOT / "src" / "content" / "posts"

SPEAKER_TAGS = {
    "Patrick": "Patrick",
    "Grayson": "Grayson",
    "Ryan": "Ryan",
    "Akira": "Akira",
    "Sundy": "Sundy",
    "Kota": "Kota",
    "Kaz": "Kaz",
}


def decode_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "big5", "shift_jis"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def read_docx(path: Path) -> str:
    doc = Document(path)
    lines: list[str] = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            lines.append(text)
    return "\n\n".join(lines)


def normalize_body(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    lines = [line.strip() for line in text.splitlines()]
    blocks: list[str] = []
    current: list[str] = []

    for line in lines:
        if not line:
            if current:
                blocks.append(" ".join(current).strip())
                current = []
            continue
        if re.match(r"^#{1,6}\s+", line) or re.match(r"^[-*]\s+", line):
            if current:
                blocks.append(" ".join(current).strip())
                current = []
            blocks.append(line)
        else:
            current.append(line)

    if current:
        blocks.append(" ".join(current).strip())

    return "\n\n".join(blocks).strip()


def yaml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[\s_：:;；,，.。()（）\[\]【】/\\]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "sermon"


def folder_meta(folder: Path) -> tuple[str, str, str]:
    name = folder.name
    match = re.match(r"^(\d{8})(.*)$", name)
    if not match:
        raise ValueError(f"目录名没有日期开头: {name}")

    raw_date, rest = match.groups()
    date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    speaker = ""
    title = rest.strip(" _-")

    if "_" in title:
        before, after = title.rsplit("_", 1)
        if after.strip():
            title = before.strip()
            speaker = after.strip()

    for key, value in SPEAKER_TAGS.items():
        if key.lower() in name.lower():
            speaker = value
            break

    title = title or name
    return date, title, speaker


def choose_source_file(folder: Path) -> Path | None:
    txt_files = sorted(folder.glob("*.txt"), key=lambda p: p.name)
    docx_files = sorted(folder.glob("*.docx"), key=lambda p: p.name)

    preferred_txt = [
        p for p in txt_files
        if any(token in p.name for token in ("中文", "中", "文本"))
        and not any(token in p.name.lower() for token in ("英文", "英", "日文", "jp"))
    ]
    if preferred_txt:
        return preferred_txt[0]

    neutral_txt = [
        p for p in txt_files
        if not any(token in p.name.lower() for token in ("英文", "英", "日文", "jp"))
    ]
    if neutral_txt:
        return neutral_txt[0]

    preferred_docx = [
        p for p in docx_files
        if any(token in p.name for token in ("中文", "中"))
        and not any(token in p.name.lower() for token in ("英文", "英", "jp"))
    ]
    if preferred_docx:
        return preferred_docx[0]

    neutral_docx = [
        p for p in docx_files
        if not any(token in p.name.lower() for token in ("英文", "英", "jp"))
    ]
    if neutral_docx:
        return neutral_docx[0]

    return None


def markdown_for(folder: Path, source_file: Path) -> tuple[str, str]:
    date, title, speaker = folder_meta(folder)
    if source_file.suffix.lower() == ".docx":
        body = read_docx(source_file)
    else:
        body = decode_text(source_file)
    body = normalize_body(body)

    description_source = re.sub(r"\s+", " ", body).strip()
    description = description_source[:80] or title
    tags = ["讲道"]
    if speaker:
        tags.append(speaker)

    frontmatter = textwrap.dedent(
        f"""\
        ---
        title: "{yaml_escape(title)}"
        description: "{yaml_escape(description)}"
        date: {date}
        tags: [{", ".join(f'"{yaml_escape(tag)}"' for tag in tags)}]
        ---
        """
    )
    source_note = f"\n\n> 来源：`{yaml_escape(folder.name)}` / `{yaml_escape(source_file.name)}`\n\n"
    return date, frontmatter + source_note + body + "\n"


def main() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit(f"找不到源目录: {SOURCE_DIR}")

    ORGANIZED_DIR.mkdir(exist_ok=True)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    for old_file in ORGANIZED_DIR.glob("*.md"):
        old_file.unlink()

    for old_file in POSTS_DIR.glob("*.md"):
        old_file.unlink()

    imported = 0
    skipped: list[str] = []
    for folder in sorted(p for p in SOURCE_DIR.iterdir() if p.is_dir()):
        source_file = choose_source_file(folder)
        if source_file is None:
            skipped.append(folder.name)
            continue

        date, title, _speaker = folder_meta(folder)
        slug = f"{date}-{slugify(title)}"
        markdown = markdown_for(folder, source_file)[1]
        organized_path = ORGANIZED_DIR / f"{slug}.md"
        post_path = POSTS_DIR / f"{slug}.md"
        organized_path.write_text(markdown, encoding="utf-8")
        shutil.copyfile(organized_path, post_path)
        imported += 1

    print(f"Imported: {imported}")
    print(f"Skipped: {len(skipped)}")
    for name in skipped:
        print("Skipped: " + name.encode("unicode_escape").decode("ascii"))


if __name__ == "__main__":
    main()
