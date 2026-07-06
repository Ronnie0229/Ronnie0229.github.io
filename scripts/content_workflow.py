from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RAW_DIRS = {
    "sermon": ROOT / "data" / "raw" / "教会讲道",
    "share": ROOT / "data" / "raw" / "分享",
}
INBOX_ENV = {
    "sermon": "RONNIE_SERMON_INBOX",
    "share": "RONNIE_SHARE_INBOX",
}
IMPORTERS = {
    "sermon": ROOT / "scripts" / "import_sermons.py",
    "share": ROOT / "scripts" / "import_shares.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def configured_path(explicit: str | None, env_name: str) -> Path:
    value = explicit or os.environ.get(env_name)
    if not value:
        raise SystemExit(f"请通过参数或环境变量 {env_name} 指定目录。")
    return Path(value).expanduser()


def list_files(path: Path) -> list[Path]:
    if not path.is_dir():
        raise SystemExit(f"找不到目录: {path}")
    return sorted(item for item in path.iterdir() if item.is_file())


def inspect(kind: str, inbox_value: str | None) -> None:
    inbox = configured_path(inbox_value, INBOX_ENV[kind])
    files = list_files(inbox)
    print(f"Type: {kind}")
    print(f"Inbox: {inbox}")
    print(f"Files: {len(files)}")
    for path in files:
        print(f"{path.name}\t{path.stat().st_size}\t{sha256(path)}")


def verified_move(source: Path, destination: Path) -> None:
    if destination.exists():
        raise SystemExit(f"目标已存在，停止以避免覆盖: {destination}")
    source_hash = sha256(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if sha256(destination) != source_hash:
        destination.unlink(missing_ok=True)
        raise SystemExit(f"SHA-256 校验失败: {source.name}")
    source.unlink()


def extract_pdf(source: Path, destination: Path) -> None:
    reader = PdfReader(str(source))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").replace("\x00", "").strip()
        if text:
            pages.append(f"[Page {page_number}]\n{text}")
    destination.write_text("\n\n".join(pages) + "\n", encoding="utf-8")


def ingest_share(inbox: Path) -> None:
    files = list_files(inbox)
    if not files:
        raise SystemExit("分享收件目录没有文件。")
    RAW_DIRS["share"].mkdir(parents=True, exist_ok=True)
    for source in files:
        destination = RAW_DIRS["share"] / source.name
        verified_move(source, destination)
        print(f"Moved: {destination}")


def ingest_sermon(inbox: Path, date: str, title: str, speaker: str) -> None:
    if len(date) != 8 or not date.isdigit():
        raise SystemExit("--date 必须使用 YYYYMMDD 格式。")
    folder = RAW_DIRS["sermon"] / f"{date}{title}_{speaker}"
    if folder.exists():
        raise SystemExit(f"讲道目录已存在，停止以避免覆盖: {folder}")
    files = list_files(inbox)
    pdfs = [path for path in files if path.suffix.lower() == ".pdf"]
    if not pdfs:
        raise SystemExit("讲道收件目录没有 PDF 文件。")
    folder.mkdir(parents=True)
    for source in pdfs:
        destination = folder / source.name
        verified_move(source, destination)
        extracted = folder / f"{source.stem}.extracted.txt"
        extract_pdf(destination, extracted)
        print(f"Moved: {destination}")
        print(f"Extracted: {extracted}")
    print("下一步：校订并翻译 extracted.txt，保存为中文 TXT；不要直接发布机器提取稿。")


def allowed_sermon_archive_file(path: Path) -> bool:
    """Return True only for files allowed in the protected sermon archive.

    The archive is a long-term preservation area. Keep only the three
    non-regenerable source categories: original files, official source-language
    text, and final Chinese text. Do not archive metadata.json, generated posts,
    processed copies, audit reports, extracted text, logs, or other helper files.
    """
    if not path.is_file():
        return False
    name_lower = path.name.lower()
    if name_lower.endswith(".extracted.txt"):
        return False
    if path.name == "metadata.json":
        return False
    if name_lower.endswith((".log", ".csv", ".md", ".json")):
        return False
    if ".english-source" in name_lower:
        return True
    if "中文" in path.name and path.suffix.lower() == ".txt":
        return True
    return path.suffix.lower() in {".pdf", ".docx", ".txt", ".md"} and "中文" not in path.name


def archive_sermon(folder_value: str, archive_value: str | None) -> None:
    folder = Path(folder_value).expanduser()
    archive_root = configured_path(archive_value, "RONNIE_SERMON_ARCHIVE")
    if not folder.is_dir():
        raise SystemExit(f"找不到讲道目录: {folder}")
    destination = archive_root / folder.name
    if destination.exists():
        raise SystemExit(f"归档目录已存在，停止以避免覆盖: {destination}")
    source_files = sorted(path for path in folder.rglob("*") if allowed_sermon_archive_file(path))
    if not source_files:
        raise SystemExit("没有找到可归档的讲道源文件。")
    for source in source_files:
        target = destination / source.relative_to(folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    destination_files = sorted(path for path in destination.rglob("*") if path.is_file())
    if len(source_files) != len(destination_files):
        raise SystemExit("归档文件数量不一致。")
    source_bytes = sum(path.stat().st_size for path in source_files)
    destination_bytes = sum(path.stat().st_size for path in destination_files)
    for source in source_files:
        relative = source.relative_to(folder)
        if sha256(source) != sha256(destination / relative):
            raise SystemExit(f"归档 SHA-256 校验失败: {relative}")
    if source_bytes != destination_bytes:
        raise SystemExit("归档字节数不一致。")
    print(f"Archived: {destination}")
    print(f"Files: {len(source_files)}")
    print(f"Bytes: {source_bytes}")


def publish(kind: str, folder: str | None = None, source_file: str | None = None, dry_run: bool = False, description: str | None = None, update_existing: bool = False) -> None:
    command = [sys.executable, str(IMPORTERS[kind])]
    if kind == "sermon":
        if not folder:
            raise SystemExit("Sermon publish requires --folder to avoid importing all sermon folders.")
        command.extend(["--folder", folder])
    elif kind == "share":
        if not source_file:
            raise SystemExit("Share publish requires --source-file to avoid importing all share files.")
        command.extend(["--source-file", source_file])
    if dry_run:
        command.append("--dry-run")
    if description:
        command.extend(["--description", description])
    if update_existing:
        command.append("--update-existing")
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="分享和讲道资料统一处理入口")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="只读检查收件目录")
    inspect_parser.add_argument("kind", choices=("sermon", "share"))
    inspect_parser.add_argument("--inbox")

    ingest_parser = subparsers.add_parser("ingest", help="校验后移入 data/raw")
    ingest_parser.add_argument("kind", choices=("sermon", "share"))
    ingest_parser.add_argument("--inbox")
    ingest_parser.add_argument("--date")
    ingest_parser.add_argument("--title")
    ingest_parser.add_argument("--speaker")

    archive_parser = subparsers.add_parser("archive-sermon", help="校验后复制讲道目录到受保护归档区")
    archive_parser.add_argument("--folder", required=True)
    archive_parser.add_argument("--archive")

    publish_parser = subparsers.add_parser("publish", help="生成文章和整理报告")
    publish_parser.add_argument("kind", choices=("sermon", "share"))
    publish_parser.add_argument("--folder", help="讲道发布时必须指定的单个 data/raw/教会讲道 子目录。")
    publish_parser.add_argument("--source-file", help="分享发布时必须指定的单个 data/raw/分享 源文件。")
    publish_parser.add_argument("--dry-run", action="store_true", help="只预览导入结果，不写入文件。")
    publish_parser.add_argument("--description", help="讲道发布用的人工概括型摘要；不得使用正文截取或模板句。")
    publish_parser.add_argument("--update-existing", action="store_true", help="只更新同一个已登记 source folder 对应的既有文章。")
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    args = parse_args()
    if args.command == "inspect":
        inspect(args.kind, args.inbox)
    elif args.command == "ingest":
        inbox = configured_path(args.inbox, INBOX_ENV[args.kind])
        if args.kind == "share":
            ingest_share(inbox)
        else:
            missing = [
                name
                for name in ("date", "title", "speaker")
                if not getattr(args, name)
            ]
            if missing:
                raise SystemExit("讲道入库缺少参数: " + ", ".join(missing))
            ingest_sermon(inbox, args.date, args.title, args.speaker)
    elif args.command == "archive-sermon":
        archive_sermon(args.folder, args.archive)
    elif args.command == "publish":
        publish(args.kind, args.folder, args.source_file, args.dry_run, args.description, args.update_existing)


if __name__ == "__main__":
    main()
