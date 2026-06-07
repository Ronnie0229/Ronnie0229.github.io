from __future__ import annotations

import re
import shutil
import textwrap
import csv
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "教会讲道"
ORGANIZED_DIR = ROOT / "整理后的讲道文章"
POSTS_DIR = ROOT / "src" / "content" / "posts"
REPORT_DIR = ROOT / "内容整理报告"

SPEAKER_TAGS = {
    "Patrick": "Patrick",
    "Grayson": "Grayson",
    "Ryan": "Ryan",
    "Akira": "Akira",
    "Sundy": "Sundy",
    "Kota": "Kota",
    "Kaz": "Kaz",
}

CATEGORY_RULES = [
    ("圣诞节", ("圣诞", "降生", "所应许的礼物", "礼物的宣告", "最伟大的礼物")),
    ("复活节", ("复活节", "复活", "十字架", "伟大的交换")),
    ("VBS", ("VBS",)),
    ("分享见证", ("见证",)),
]

BOOKS = (
    "创世记", "出埃及记", "利未记", "民数记", "申命记", "约书亚记", "士师记", "路得记",
    "撒母耳记上", "撒母耳记下", "列王纪上", "列王纪下", "历代志上", "历代志下", "以斯拉记",
    "尼希米记", "以斯帖记", "约伯记", "诗篇", "箴言", "传道书", "雅歌", "以赛亚书",
    "耶利米书", "耶利米哀歌", "以西结书", "但以理书", "何西阿书", "约珥书", "阿摩司书",
    "俄巴底亚书", "约拿书", "约拿", "弥迦书", "那鸿书", "哈巴谷书", "西番雅书", "哈该书",
    "撒迦利亚书", "玛拉基书", "马太福音", "马可福音", "路加福音", "约翰福音", "使徒行传",
    "罗马书", "哥林多前书", "哥林多后书", "加拉太书", "以弗所书", "腓立比书", "歌罗西书",
    "帖撒罗尼迦前书", "帖撒罗尼迦后书", "提摩太前书", "提摩太后书", "提多书", "腓利门书",
    "希伯来书", "雅各书", "彼得前书", "彼得后书", "约翰一书", "约翰二书", "约翰三书",
    "犹大书", "启示录",
)

CHINESE_NUMBERS = {
    "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
    "六": "6", "七": "7", "八": "8", "九": "9", "十": "10",
}

TEXT_REPLACEMENTS = {
    "创世纪": "创世记",
    "约伯纪": "约伯记",
    "钉S字J": "钉十字架",
    "人囗": "人口",
    "无庸置疑": "毋庸置疑",
    "想像": "想象",
    "彷佛": "仿佛",
    "于于神": "于神",
    "神。 神。": "神。",
    "整整一整夜": "整整一夜",
}


def clean_title(value: str) -> str:
    value = value.replace("：", ":").replace("；", ";").replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s*([:;,\-])\s*", r"\1", value)
    value = re.sub(r"(\d+:\d+-\d+):(\d+-\d+)", r"\1;\2", value)
    return value.strip(" _-:;，。")


def title_parts(title: str) -> tuple[str, str]:
    normalized = clean_title(title)
    normalized = re.sub(r"^(?:中文|福音\d+)", "", normalized).strip()
    books = "|".join(sorted((re.escape(book) for book in BOOKS), key=len, reverse=True))
    match = re.search(
        rf"(?P<book>{books})\s*(?:第(?:(?P<cn>[一二三四五六七八九十]+)|(?P<chapter_named>\d+))章|(?P<chapter>\d+)(?P<range>-\d+)?章?)"
        rf"(?:\s*[:;,]\s*(?P<verses>\d+(?:-\d+:\d+|-\d+)?(?:[;,]\d+(?:-\d+)?)?))?",
        normalized,
    )
    if not match:
        return "", normalized

    book = "约拿书" if match.group("book") == "约拿" else match.group("book")
    chapter = (
        match.group("chapter")
        or match.group("chapter_named")
        or CHINESE_NUMBERS.get(match.group("cn"), match.group("cn") or "")
    )
    chapter_range = match.group("range") or ""
    verses = match.group("verses") or ""
    scripture = f"{book} {chapter}{chapter_range}"
    if verses:
        scripture += f":{verses.replace(',', ';')}"
    summary = (normalized[:match.start()] + normalized[match.end():]).strip(" _-:;，。")
    summary = re.sub(r"^(?:系列:)?", "", summary).strip(" _-:;，。")
    return scripture, summary


def scripture_from_body(body: str) -> str:
    sample = re.sub(r"\s+", " ", body[:4000])
    scripture, _summary = title_parts(sample)
    return scripture


def category_for(title: str) -> str:
    for category, keywords in CATEGORY_RULES:
        if any(keyword.lower() in title.lower() for keyword in keywords):
            return category
    return "圣经学习"


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
    for old, new in TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)
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

    title = clean_title(title or name)
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
    date, raw_title, speaker = folder_meta(folder)
    scripture, summary = title_parts(raw_title)
    category = category_for(raw_title)
    if source_file.suffix.lower() == ".docx":
        body = read_docx(source_file)
    else:
        body = decode_text(source_file)
    body = normalize_body(body)
    scripture = scripture or scripture_from_body(body)
    if category == "分享见证":
        title = f"{scripture}｜{summary or raw_title}" if scripture else (summary or raw_title)
    elif scripture:
        title = f"{scripture}｜{summary or '经文讲解'}"
    else:
        title = summary or raw_title

    description_source = re.sub(r"\s+", " ", body).strip()
    description = description_source[:80] or title
    tags = ["讲道", category]
    if speaker:
        tags.append(speaker)

    frontmatter = textwrap.dedent(
        f"""\
        ---
        title: "{yaml_escape(title)}"
        description: "{yaml_escape(description)}"
        date: {date}
        tags: [{", ".join(f'"{yaml_escape(tag)}"' for tag in tags)}]
        category: "{yaml_escape(category)}"
        scripture: "{yaml_escape(scripture)}"
        author: "{yaml_escape(speaker)}"
        reviewed: false
        source: "{yaml_escape(folder.name)} / {yaml_escape(source_file.name)}"
        ---
        """
    )
    return date, frontmatter + "\n" + body + "\n"


def main() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit(f"找不到源目录: {SOURCE_DIR}")

    ORGANIZED_DIR.mkdir(exist_ok=True)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)

    for old_file in ORGANIZED_DIR.glob("*.md"):
        old_file.unlink()

    for old_file in POSTS_DIR.glob("*.md"):
        old_file.unlink()

    imported = 0
    skipped: list[str] = []
    rows = []
    for folder in sorted(p for p in SOURCE_DIR.iterdir() if p.is_dir()):
        source_file = choose_source_file(folder)
        if source_file is None:
            skipped.append(folder.name)
            continue

        markdown = markdown_for(folder, source_file)[1]
        title_match = re.search(r'^title: "(.+)"$', markdown, flags=re.MULTILINE)
        publish_title = title_match.group(1) if title_match else folder.name
        date, _raw_title, _speaker = folder_meta(folder)
        slug = f"{date}-{slugify(publish_title)}"
        organized_path = ORGANIZED_DIR / f"{slug}.md"
        post_path = POSTS_DIR / f"{slug}.md"
        organized_path.write_text(markdown, encoding="utf-8")
        shutil.copyfile(organized_path, post_path)
        date, raw_title, speaker = folder_meta(folder)
        scripture, summary = title_parts(raw_title)
        if not scripture:
            scripture_match = re.search(r'^scripture: "(.+)"$', markdown, flags=re.MULTILINE)
            scripture = scripture_match.group(1) if scripture_match else ""
        category = category_for(raw_title)
        rows.append((folder.name, date, scripture, category, speaker, publish_title, source_file.name))
        imported += 1

    with (REPORT_DIR / "讲道文章目录.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("源目录", "日期", "经文", "分类", "讲员", "发布标题", "正文来源"))
        writer.writerows(rows)

    print(f"Imported: {imported}")
    print(f"Skipped: {len(skipped)}")
    for name in skipped:
        print("Skipped: " + name.encode("unicode_escape").decode("ascii"))


if __name__ == "__main__":
    main()
