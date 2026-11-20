from __future__ import annotations

import argparse
import hashlib
import json
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
CONTRACT_CONSUMER = ROOT / "scripts" / "consume_publication_package.py"


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


def list_files(path: Path, *, skip_ds_store: bool = False) -> list[Path]:
    if not path.is_dir():
        raise SystemExit(f"找不到目录: {path}")
    return sorted(
        item for item in path.iterdir()
        if item.is_file() and (not skip_ds_store or item.name != ".DS_Store")
    )


def inspect(kind: str, inbox_value: str | None) -> None:
    inbox = configured_path(inbox_value, INBOX_ENV[kind])
    files = list_files(inbox, skip_ds_store=(kind == "share"))
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
    files = list_files(inbox, skip_ds_store=True)
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


def publish(
    kind: str,
    folder: str | None = None,
    source_file: str | None = None,
    dry_run: bool = False,
    description: str | None = None,
    tags: str | None = None,
    update_existing: bool = False,
    title: str | None = None,
    scripture: str | None = None,
    slug: str | None = None,
    slug_topic: str | None = None,
    presentation_file: str | None = None,
    author: str | None = None,
    publish_date: str | None = None,
    publication_package: str | None = None,
    content_root: str | None = None,
    allow_write: bool = False,
) -> None:
    expected_sermon_source: Path | None = None
    if publication_package:
        if not dry_run and not allow_write:
            raise SystemExit("V13_WRITE_AUTHORIZATION_REQUIRED: v1.3 publish requires --allow-write")
        if not content_root:
            raise SystemExit("V13_PACKAGE_REQUIRED: --content-root is required with --publication-package")
        package_path = Path(publication_package).resolve(strict=True)
        package = json.loads(package_path.read_text(encoding="utf-8-sig"))
        if package.get("version") != "1.3" or package.get("content_type") != kind:
            raise SystemExit("V13_PACKAGE_REQUIRED: package version/content_type mismatch")
        package_artifact = package.get("presentation", {}).get("artifact")
        if not isinstance(package_artifact, str) or not presentation_file:
            raise SystemExit("V13_PACKAGE_REQUIRED: presentation artifact does not match package binding")
        package_artifact_path = Path(package_artifact).expanduser()
        if not package_artifact_path.is_absolute():
            package_artifact_path = Path(content_root).expanduser() / package_artifact_path
        if Path(presentation_file).resolve(strict=True) != package_artifact_path.resolve(strict=True):
            raise SystemExit("V13_PACKAGE_REQUIRED: presentation artifact does not match package binding")
        validation = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_publication_package_v13.py"),
             "--contract", str(package_path),
             "--schema", str(ROOT / "contracts/website-publication-package-v1.3.schema.json"),
             "--content-root", content_root],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        try:
            validation_evidence = json.loads(validation.stdout)
        except json.JSONDecodeError:
            raise SystemExit("V13_PACKAGE_REQUIRED: package validator returned invalid evidence")
        if validation.returncode != 0 or validation_evidence.get("pass") is not True:
            print(json.dumps(validation_evidence, ensure_ascii=False, indent=2))
            raise SystemExit("V13_PACKAGE_REQUIRED: package validation FAIL")
        if kind == "share":
            try:
                from consume_publication_package import parse_prepublication_frontmatter
            except ModuleNotFoundError:
                from scripts.consume_publication_package import parse_prepublication_frontmatter
            prepublish_ref = package.get("prepublish", {}).get("path")
            prepublish_path = Path(prepublish_ref).expanduser()
            if not prepublish_path.is_absolute():
                prepublish_path = Path(content_root).expanduser() / prepublish_path
            frontmatter = parse_prepublication_frontmatter(prepublish_path.resolve(strict=True))
            metadata = package.get("metadata", {})
            expected_source = frontmatter.get("source")
            if not isinstance(expected_source, str) or not expected_source:
                raise SystemExit("V13_PACKAGE_IDENTITY_MISMATCH: package-bound source path is missing or invalid")
            try:
                from share_source_identity import resolve_package_bound_share_source
            except ModuleNotFoundError:
                from scripts.share_source_identity import resolve_package_bound_share_source
            try:
                resolve_package_bound_share_source(
                    source_file or "", RAW_DIRS["share"], expected_source=expected_source
                )
            except (ValueError, OSError) as exc:
                raise SystemExit(f"V13_PACKAGE_IDENTITY_MISMATCH: {exc}") from exc
            if (frontmatter.get("author") != metadata.get("author")
                or frontmatter.get("date") != metadata.get("publish_date")
                or frontmatter.get("category") != metadata.get("category")
                or frontmatter.get("contentType") != kind):
                raise SystemExit("V13_PACKAGE_IDENTITY_MISMATCH: prepublish author/date/category/contentType do not match package metadata")
            expected = {
                "title": frontmatter.get("title"),
                "description": frontmatter.get("description"),
                "scripture": frontmatter.get("scripture", ""),
                "tags": frontmatter.get("tags"),
                "author": metadata.get("author"),
                "publish_date": metadata.get("publish_date"),
                "slug": metadata.get("slug"),
            }
            actual = {"title": title, "description": description, "scripture": scripture,
                      "tags": [item.strip() for item in tags.split(",")] if tags is not None else None, "author": author,
                      "publish_date": publish_date, "slug": slug}
            for field, value in actual.items():
                if value is not None and value != expected[field]:
                    raise SystemExit(f"V13_PACKAGE_IDENTITY_MISMATCH: {field} does not match package-bound prepublish metadata")
            if slug_topic:
                raise SystemExit("V13_PACKAGE_IDENTITY_MISMATCH: v1.3 Share requires the package-bound full slug")
            source_file = Path(expected_source).name
            title = expected["title"]
            description = expected["description"]
            scripture = expected["scripture"]
            tags = ",".join(expected["tags"])
            author = expected["author"]
            publish_date = expected["publish_date"]
            slug = expected["slug"]
        elif kind == "sermon":
            try:
                from consume_publication_package import parse_prepublication_frontmatter, v13_source_selector
            except ModuleNotFoundError:
                from scripts.consume_publication_package import parse_prepublication_frontmatter, v13_source_selector
            prepublish_ref = package.get("prepublish", {}).get("path")
            if not isinstance(prepublish_ref, str) or not prepublish_ref:
                raise SystemExit("V13_PACKAGE_IDENTITY_MISMATCH: package-bound prepublish path is missing or invalid")
            prepublish_path = Path(prepublish_ref).expanduser()
            if not prepublish_path.is_absolute():
                prepublish_path = Path(content_root).expanduser() / prepublish_path
            try:
                frontmatter = parse_prepublication_frontmatter(prepublish_path.resolve(strict=True))
                expected_folder = v13_source_selector(
                    package, frontmatter, raw_sermon_root=RAW_DIRS["sermon"]
                )
                expected_sermon_source = (RAW_DIRS["sermon"] / expected_folder).resolve(strict=True)
                canonical_sermon_root = RAW_DIRS["sermon"].resolve(strict=True)
                if (expected_sermon_source.parent != canonical_sermon_root
                        or expected_sermon_source.name != expected_folder
                        or not expected_sermon_source.is_dir()):
                    raise SystemExit("package-bound Sermon source does not resolve to its exact canonical intake directory")
            except (OSError, ValueError, SystemExit) as exc:
                raise SystemExit(f"V13_PACKAGE_IDENTITY_MISMATCH: unable to resolve package-bound Sermon source: {exc}") from exc
            if not folder:
                raise SystemExit("V13_PACKAGE_IDENTITY_MISMATCH: package-aware Sermon publish requires the package-bound --folder")
            if folder != expected_folder:
                raise SystemExit(
                    "V13_PACKAGE_IDENTITY_MISMATCH: --folder does not match package-bound Sermon source folder"
                )
    command = [sys.executable, str(IMPORTERS[kind])]
    if publication_package and not dry_run and allow_write:
        command.append("--allow-write")
    if kind == "sermon":
        if not folder:
            raise SystemExit("Sermon publish requires --folder to avoid importing all sermon folders.")
        if not presentation_file:
            raise SystemExit("PRESENTATION_ARTIFACT_REQUIRED: sermon publish requires --presentation-file")
        # Protect the direct workflow entrypoint as well as package consumption.
        gate = subprocess.run(
            ["node", str(ROOT / "scripts/validate_sermon_presentation.mjs"),
             "--source", str(Path(presentation_file).resolve()),
             "--candidate-id", Path(folder).name],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        try:
            evidence = json.loads(gate.stdout)
        except json.JSONDecodeError:
            raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: invalid rendered gate evidence")
        if (gate.returncode != 0
            or evidence.get("status") != "SERMON_PRESENTATION_STRUCTURE_PASS"
            or evidence.get("completion_ceiling") != "publication_structure_ready"
            or not evidence.get("rendered_html", {}).get("sha256")):
            print(json.dumps(evidence, ensure_ascii=False, indent=2))
            raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: direct workflow gate FAIL")
        command.extend(["--folder", folder, "--presentation-file", presentation_file])
        if expected_sermon_source is not None:
            command.extend(["--expected-source-folder", str(expected_sermon_source)])
            command.extend(["--publication-package", str(package_path), "--content-root", str(content_root)])
    elif kind == "share":
        if not source_file:
            raise SystemExit("Share publish requires --source-file to avoid importing all share files.")
        command.extend(["--source-file", source_file])
        if presentation_file:
            if not publication_package:
                raise SystemExit("V13_PACKAGE_REQUIRED: Share presentation import requires a v1.3 publication package.")
            gate = subprocess.run(
                ["node", str(ROOT / "scripts/validate_content_presentation.mjs"),
                 "--profile", "share_article", "--source", str(Path(presentation_file).resolve()),
                 "--candidate-id", Path(source_file).name],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            try:
                evidence = json.loads(gate.stdout)
            except json.JSONDecodeError:
                raise SystemExit("SHARE_PREPUBLICATION_STRUCTURE_BLOCKED: invalid rendered gate evidence")
            if (gate.returncode != 0
                or evidence.get("status") != "CONTENT_PRESENTATION_STRUCTURE_PASS"
                or evidence.get("completion_ceiling") != "publication_structure_ready"
                or not evidence.get("rendered_html", {}).get("sha256")):
                print(json.dumps(evidence, ensure_ascii=False, indent=2))
                raise SystemExit("SHARE_PREPUBLICATION_STRUCTURE_BLOCKED: direct workflow gate FAIL")
            command.extend([
                "--presentation-file", presentation_file,
                "--publication-package", str(package_path),
                "--content-root", content_root,
            ])
            if author:
                command.extend(["--author", author])
            if publish_date:
                command.extend(["--publish-date", publish_date])
        else:
            # Legacy Share keeps its historical Ronnie default. Do not apply
            # this fallback to v1.3: its author is package-bound above.
            command.extend(["--author", author or "Ronnie"])
    if dry_run:
        command.append("--dry-run")
    if description:
        command.extend(["--description", description])
    if tags:
        command.extend(["--tags", tags])
    if kind == "share":
        if title:
            command.extend(["--title", title])
        if scripture:
            command.extend(["--scripture", scripture])
        if slug:
            command.extend(["--slug", slug])
        if slug_topic:
            command.extend(["--slug-topic", slug_topic])
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

    publish_parser = subparsers.add_parser("publish", help="现行版本绑定的兼容发布入口；v1.3 统一合同使用 publish-contract")
    publish_parser.add_argument("kind", choices=("sermon", "share"))
    publish_parser.add_argument("--folder", help="讲道发布时必须指定的单个 data/raw/教会讲道 子目录。")
    publish_parser.add_argument("--presentation-file", help="Package-bound body-only presentation artifact; mandatory for sermon and v1.3 Share consumption.")
    publish_parser.add_argument("--author", help="Share author from the accepted publication package; defaults to Ronnie for legacy Share path.")
    publish_parser.add_argument("--publish-date", help="Frozen publication date in YYYY-MM-DD format for v1.3 Share consumption.")
    publish_parser.add_argument("--publication-package", help="v1.3 package binding this presentation artifact; required for v1.3 consumer mode.")
    publish_parser.add_argument("--content-root", help="Root that contains all package-bound files; required with --publication-package.")
    publish_parser.add_argument("--source-file", help="分享发布时必须指定的单个 data/raw/分享 源文件。")
    publish_parser.add_argument("--dry-run", action="store_true", help="只预览导入结果，不写入文件。")
    publish_parser.add_argument("--allow-write", action="store_true", help="Explicitly authorize package-bound v1.3 writes.")
    publish_parser.add_argument("--description", help="人工概括型摘要；不得使用正文截取或模板句。")
    publish_parser.add_argument("--tags", help="分享或讲道的人工精准标签，使用逗号分隔；将与确定性规则结果合并并统一校验。")
    publish_parser.add_argument("--title", help="分享文章人工发布标题。")
    publish_parser.add_argument("--scripture", help="分享文章人工经文。")
    publish_parser.add_argument("--slug", help="分享文章完整 slug。")
    publish_parser.add_argument("--slug-topic", help="分享文章英文主题 slug；最终 slug 为 <date>-<slug-topic>。")
    publish_parser.add_argument("--update-existing", action="store_true", help="只更新同一个已登记 source folder 对应的既有文章。")

    contract_parser = subparsers.add_parser("publish-contract", help="统一 v1.3 Share/Sermon package consumer。")
    contract_parser.add_argument("--contract", required=True)
    contract_parser.add_argument("--schema", required=True)
    contract_parser.add_argument("--content-root", required=True)
    contract_parser.add_argument("--mode", choices=("plan", "dry-run", "publish"), default="plan", help="publish mode requires --allow-write.")
    contract_parser.add_argument("--allow-write", action="store_true", help="Explicitly allow the validated package-bound import to write Website content.")
    contract_parser.add_argument("--plan-output")
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
        publish(
            args.kind,
            args.folder,
            args.source_file,
            args.dry_run,
            args.description,
            args.tags,
            args.update_existing,
            args.title,
            args.scripture,
            args.slug,
            args.slug_topic,
            args.presentation_file,
            args.author,
            args.publish_date,
            args.publication_package,
            args.content_root,
            args.allow_write,
        )
    elif args.command == "publish-contract":
        command = [
            sys.executable,
            str(CONTRACT_CONSUMER),
            "--contract", args.contract,
            "--schema", args.schema,
            "--content-root", args.content_root,
            "--mode", args.mode,
        ]
        if args.allow_write:
            command.append("--allow-write")
        if args.plan_output:
            command.extend(["--plan-output", args.plan_output])
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
