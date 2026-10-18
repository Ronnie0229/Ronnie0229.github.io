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


def import_command(package: dict[str, Any], workflow: Path, mode: str, allow_write: bool) -> list[str]:
    version = package.get("version")
    if version not in {"1.1", "1.2"}:
        raise SystemExit("controlled import requires website-publication-package version 1.1 or 1.2")

    metadata = package.get("metadata")
    if not isinstance(metadata, dict):
        raise SystemExit("metadata object is required")

    content_type = package.get("content_type")
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
    elif mode == "publish" and not allow_write:
        raise SystemExit("publish mode requires --allow-write")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate website-publication-package/v1.1 or v1.2 before entering the existing website import flow."
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

    report = run_validator(args.validator_script, args.contract, args.schema, args.content_root)
    package = load_json(args.contract)

    command: list[str] | None = None
    structure_evidence: dict[str, Any] | None = None
    if args.mode != "plan":
        structure_evidence = enforce_sermon_prepublication_structure(package)
        command = import_command(package, args.workflow_script, args.mode, args.allow_write)

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
