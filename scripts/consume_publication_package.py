#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VALIDATOR = ROOT / "scripts" / "validate_publication_package.py"
DEFAULT_WORKFLOW = ROOT / "scripts" / "content_workflow.py"
SERMON_STRUCTURE_VALIDATOR = ROOT / "scripts" / "validate_sermon_presentation.mjs"
CONTENT_STRUCTURE_VALIDATOR = ROOT / "scripts" / "validate_content_presentation.mjs"
V13_VALIDATOR = ROOT / "scripts" / "validate_publication_package_v13.py"
V13_PACKAGE_SCHEMA = ROOT / "contracts" / "website-publication-package-v1.3.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def run_validator(validator: Path, contract: Path, schema: Path, content_root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--contract",
            str(contract),
            "--schema",
            str(schema),
            "--content-root",
            str(content_root),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"consumer validation did not return JSON: {result.stderr or result.stdout}") from exc
    if result.returncode != 0 or report.get("pass") is not True:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    return report


def enforce_sermon_prepublication_structure(package: dict[str, Any]) -> dict[str, Any] | None:
    """Fail closed before any sermon dry-run/publish website import side effect."""
    if package.get("content_type") != "sermon":
        return None
    prepublish = package.get("prepublish")
    source = prepublish.get("path") if isinstance(prepublish, dict) else None
    expected_sha = prepublish.get("sha256") if isinstance(prepublish, dict) else None
    if not isinstance(source, str) or not isinstance(expected_sha, str):
        raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: missing bound prepublish identity")
    candidate = Path(source).resolve(strict=True)
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != expected_sha:
        raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: prepublish SHA mismatch")
    batch = package.get("metadata", {}).get("batch_id")
    if not isinstance(batch, str) or not batch:
        raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: missing batch identity")
    result = subprocess.run(
        ["node", str(SERMON_STRUCTURE_VALIDATOR), "--source", str(candidate),
         "--candidate-id", batch],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    try:
        evidence = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: renderer produced no valid evidence")
    if (
        result.returncode != 0
        or evidence.get("status") != "SERMON_PRESENTATION_STRUCTURE_PASS"
        or evidence.get("completion_ceiling") != "publication_structure_ready"
        or evidence.get("source", {}).get("sha256") != expected_sha
        or not isinstance(evidence.get("rendered_html", {}).get("sha256"), str)
    ):
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
        raise SystemExit("SERMON_PREPUBLICATION_STRUCTURE_BLOCKED: source/rendered hard gate FAIL")
    return evidence


def parse_prepublication_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise SystemExit("v1.3 prepublish Markdown must begin with frontmatter")
    lines = text.splitlines()
    closing = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if closing is None:
        raise SystemExit("v1.3 prepublish frontmatter is not closed")
    values: dict[str, Any] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, raw = line.partition(":")
        if not separator:
            raise SystemExit(f"invalid prepublish frontmatter line: {line}")
        raw = raw.strip()
        try:
            value = json.loads(raw) if raw.startswith(('"', "[", "{")) else raw
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid prepublish frontmatter value for {key}: {exc}") from exc
        values[key.strip()] = value
    return values


def v13_source_selector(
    package: dict[str, Any],
    frontmatter: dict[str, Any],
    *,
    raw_sermon_root: Path | None = None,
) -> str:
    content_type = package.get("content_type")
    source = frontmatter.get("source")
    if not isinstance(source, str) or not source.strip():
        raise SystemExit("v1.3 prepublish frontmatter source is required")
    normalized = source.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    parts = normalized.split("/")
    if normalized.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise SystemExit("v1.3 source path must be a normalized project-relative path")
    if content_type == "share":
        if parts[:3] != ["data", "raw", "分享"] or len(parts) != 4:
            raise SystemExit("v1.3 Share source must identify one direct child under data/raw/分享")
        name = parts[3]
        target = ROOT / "data" / "raw" / "分享" / name
        if not target.is_file() or target.suffix.lower() not in {".txt", ".docx"}:
            raise SystemExit(f"v1.3 Share source is unavailable in Website raw intake: {target}")
        return name
    if content_type == "sermon":
        if parts[:3] != ["data", "raw", "教会讲道"] or len(parts) < 4:
            raise SystemExit("v1.3 Sermon source must be within one folder under data/raw/教会讲道")
        folder = parts[3]
        sermon_root = raw_sermon_root or (ROOT / "data" / "raw" / "教会讲道")
        target = sermon_root / folder
        if target.is_symlink():
            raise SystemExit(f"v1.3 Sermon source folder must not be a symlink alias: {target}")
        try:
            canonical_root = sermon_root.resolve(strict=True)
            canonical_target = target.resolve(strict=True)
        except OSError as exc:
            raise SystemExit(f"v1.3 Sermon source folder cannot be resolved: {target}: {exc}") from exc
        if (not canonical_target.is_dir()
                or canonical_target.parent != canonical_root
                or canonical_target.name != folder):
            raise SystemExit(f"v1.3 Sermon source folder is unavailable in Website raw intake: {target}")
        return folder
    raise SystemExit(f"unsupported content_type: {content_type!r}")


def resolve_content_path(raw: str, content_root: Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = content_root / candidate
    return candidate.resolve(strict=True)


def enforce_v13_prepublication_structure(package: dict[str, Any], content_root: Path) -> dict[str, Any]:
    prepublish = package.get("prepublish", {})
    presentation = package.get("presentation", {})
    prepublish_source = prepublish.get("path") if isinstance(prepublish, dict) else None
    prepublish_sha = prepublish.get("sha256") if isinstance(prepublish, dict) else None
    artifact_source = presentation.get("artifact") if isinstance(presentation, dict) else None
    artifact_sha = presentation.get("artifact_sha256") if isinstance(presentation, dict) else None
    profile = presentation.get("profile") if isinstance(presentation, dict) else None
    batch = package.get("metadata", {}).get("batch_id")
    if not isinstance(prepublish_source, str) or not isinstance(prepublish_sha, str):
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: missing bound prepublish identity")
    if not isinstance(artifact_source, str) or not isinstance(artifact_sha, str):
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: missing bound body-only presentation artifact")
    if profile not in {"share_article", "sermon"} or not isinstance(batch, str) or not batch:
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: missing profile/batch identity")
    prepublish_path = resolve_content_path(prepublish_source, content_root)
    if hashlib.sha256(prepublish_path.read_bytes()).hexdigest() != prepublish_sha:
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: prepublish SHA mismatch")
    # Render only the SHA-bound body-only artifact. The prepublish Markdown also
    # contains YAML frontmatter, which is metadata rather than public body structure.
    artifact_path = resolve_content_path(artifact_source, content_root)
    if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact_sha:
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: presentation artifact SHA mismatch")
    result = subprocess.run(
        ["node", str(CONTENT_STRUCTURE_VALIDATOR), "--profile", profile,
         "--source", str(artifact_path), "--candidate-id", batch],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    try:
        evidence = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: renderer produced no valid evidence")
    expected_status = "CONTENT_PRESENTATION_STRUCTURE_PASS" if profile == "share_article" else "SERMON_PRESENTATION_STRUCTURE_PASS"
    if (
        result.returncode != 0
        or evidence.get("status") != expected_status
        or evidence.get("completion_ceiling") != "publication_structure_ready"
        or evidence.get("source", {}).get("sha256") != artifact_sha
        or not isinstance(evidence.get("rendered_html", {}).get("sha256"), str)
    ):
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
        raise SystemExit("V13_PREPUBLICATION_STRUCTURE_BLOCKED: source/rendered hard gate FAIL")
    return evidence


def import_command(
    package: dict[str, Any],
    workflow: Path,
    mode: str,
    allow_write: bool,
    package_path: Path | None = None,
    content_root: Path | None = None,
) -> list[str]:
    if mode == "publish" and not allow_write:
        raise SystemExit("publish mode requires --allow-write")
    version = package.get("version")
    if version not in {"1.1", "1.2", "1.3"}:
        raise SystemExit("controlled import requires website-publication-package version 1.1, 1.2 or 1.3")

    metadata = package.get("metadata")
    if not isinstance(metadata, dict):
        raise SystemExit("metadata object is required")

    content_type = package.get("content_type")
    if version == "1.3":
        prepublish = package.get("prepublish", {})
        if content_root is None:
            raise SystemExit("v1.3 controlled import requires content_root")
        prepublish_raw = prepublish.get("path") if isinstance(prepublish, dict) else None
        prepublish_path = resolve_content_path(prepublish_raw, content_root) if isinstance(prepublish_raw, str) else None
        if prepublish_path is None:
            raise SystemExit("v1.3 package requires a bound prepublish file")
        frontmatter = parse_prepublication_frontmatter(prepublish_path)
        presentation = package.get("presentation", {})
        artifact_raw = presentation.get("artifact") if isinstance(presentation, dict) else None
        if not isinstance(artifact_raw, str) or not artifact_raw.strip():
            raise SystemExit("v1.3 package requires a bound presentation artifact")
        artifact_path = resolve_content_path(artifact_raw, content_root)
        source_name = v13_source_selector(package, frontmatter)
        expected_person = metadata.get("author") if content_type == "share" else metadata.get("speaker")
        if frontmatter.get("author") != expected_person:
            raise SystemExit("v1.3 prepublish author/speaker does not match package identity")
        for required_field in ("title", "description"):
            value = frontmatter.get(required_field)
            if not isinstance(value, str) or not value.strip():
                raise SystemExit(f"v1.3 prepublish {required_field} is required")
        if content_type == "share" and not isinstance(frontmatter.get("scripture", ""), str):
            raise SystemExit("v1.3 Share scripture frontmatter must be a string")
        if frontmatter.get("date") != metadata.get("publish_date"):
            raise SystemExit("v1.3 prepublish date does not match package publish_date")
        if frontmatter.get("category") != metadata.get("category"):
            raise SystemExit("v1.3 prepublish category does not match package category")
        if frontmatter.get("contentType") != content_type:
            raise SystemExit("v1.3 prepublish contentType does not match package content_type")
        if package_path is None or content_root is None:
            raise SystemExit("v1.3 controlled import requires the package path and content root")
        command = [
            sys.executable, str(workflow), "publish", str(content_type),
            "--presentation-file", str(artifact_path),
            "--publication-package", str(package_path.resolve()),
            "--content-root", str(content_root.resolve()),
        ]
        if content_type == "share":
            command.extend([
                "--source-file", source_name,
                "--title", str(frontmatter.get("title", "")),
                "--description", str(frontmatter.get("description", "")),
                "--scripture", str(frontmatter.get("scripture", "")),
                "--slug", str(metadata.get("slug", "")),
                "--author", str(metadata.get("author", "")),
                "--publish-date", str(metadata.get("publish_date", "")),
            ])
            tags = frontmatter.get("tags")
            if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
                raise SystemExit("v1.3 Share prepublish tags must be a string array")
            command.extend(["--tags", ",".join(tags)])
        elif content_type == "sermon":
            command.extend(["--folder", source_name])
        else:
            raise SystemExit(f"unsupported content_type: {content_type!r}")
        if mode == "dry-run":
            command.append("--dry-run")
        elif mode == "publish":
            command.append("--allow-write")
        return command

    website_source = metadata.get("website_source")
    if not isinstance(website_source, str) or not website_source.strip():
        raise SystemExit("metadata.website_source is required for dry-run or publish mode")

    command = [sys.executable, str(workflow), "publish", str(content_type)]
    if content_type == "sermon":
        presentation = package.get("presentation")
        if not isinstance(presentation, dict):
            raise SystemExit("PRESENTATION_ARTIFACT_REQUIRED: sermon dry-run/publish requires presentation binding")
        artifact = presentation.get("artifact")
        artifact_path = artifact.get("path") if isinstance(artifact, dict) else None
        if (
            presentation.get("presentation_status") != "mechanically_verified"
            or presentation.get("text_identity_status") != "exact_record_order_preserved"
            or not isinstance(artifact_path, str)
            or not artifact_path.strip()
        ):
            raise SystemExit("PRESENTATION_ARTIFACT_REQUIRED: invalid sermon presentation binding")
        command.extend(["--folder", website_source, "--presentation-file", artifact_path])
    elif content_type == "share":
        command.extend(["--source-file", website_source])
    else:
        raise SystemExit(f"unsupported content_type: {content_type!r}")

    description = metadata.get("description")
    if isinstance(description, str) and description.strip():
        command.extend(["--description", description])

    tags = metadata.get("tags")
    if isinstance(tags, list) and all(isinstance(item, str) for item in tags):
        command.extend(["--tags", ",".join(tags)])

    if content_type == "share":
        title = metadata.get("chinese_title") or metadata.get("title")
        if isinstance(title, str) and title.strip():
            command.extend(["--title", title])
        scripture = metadata.get("scripture")
        if isinstance(scripture, str) and scripture.strip():
            command.extend(["--scripture", scripture])
        website_slug = metadata.get("website_slug")
        if isinstance(website_slug, str) and website_slug.strip():
            command.extend(["--slug", website_slug])
        else:
            topic_slug = metadata.get("topic_slug")
            if isinstance(topic_slug, str) and topic_slug.strip():
                command.extend(["--slug-topic", topic_slug])

    if mode == "dry-run":
        command.append("--dry-run")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate historical website-publication-package/v1.1/v1.2 or controlled v1.3 before entering the Website import flow."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--content-root", required=True, type=Path)
    parser.add_argument("--mode", choices=["plan", "dry-run", "publish"], default="plan")
    parser.add_argument("--allow-write", action="store_true")
    parser.add_argument("--validator-script", type=Path, default=DEFAULT_VALIDATOR)
    parser.add_argument("--workflow-script", type=Path, default=DEFAULT_WORKFLOW)
    parser.add_argument("--plan-output", type=Path)
    args = parser.parse_args()

    package = load_json(args.contract)
    if package.get("version") == "1.3":
        if args.schema.resolve() != V13_PACKAGE_SCHEMA.resolve():
            raise SystemExit("v1.3 consumer requires the Website mirror website-publication-package-v1.3 schema")
        validator_script = V13_VALIDATOR
    else:
        validator_script = args.validator_script
    report = run_validator(validator_script, args.contract, args.schema, args.content_root)

    command: list[str] | None = None
    structure_evidence: dict[str, Any] | None = None
    if args.mode != "plan":
        if package.get("version") == "1.3":
            structure_evidence = enforce_v13_prepublication_structure(package, args.content_root)
        else:
            structure_evidence = enforce_sermon_prepublication_structure(package)
        command = import_command(
            package, args.workflow_script, args.mode, args.allow_write,
            package_path=args.contract, content_root=args.content_root,
        )

    plan = {
        "interface": "website-publication-package-controlled-consumption",
        "version": "1.0",
        "contract_version": package.get("version"),
        "mode": args.mode,
        "validation_passed": True,
        "read_only": args.mode in {"plan", "dry-run"},
        "command": command,
        "slug": package.get("metadata", {}).get("slug"),
        "notification_policy": package.get("notification_policy"),
        "archive_status": package.get("archive_status"),
        "validator_report": report,
        "prepublication_structure_gate": structure_evidence,
    }

    if args.plan_output:
        args.plan_output.parent.mkdir(parents=True, exist_ok=True)
        args.plan_output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if command is not None:
        result = subprocess.run(command, cwd=ROOT, check=False)
        plan["workflow_returncode"] = result.returncode
        if result.returncode != 0:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return result.returncode

    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
