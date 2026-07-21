#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VALIDATOR = ROOT / "scripts" / "validate_publication_package.py"
DEFAULT_WORKFLOW = ROOT / "scripts" / "content_workflow.py"


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


def import_command(package: dict[str, Any], workflow: Path, mode: str, allow_write: bool) -> list[str]:
    version = package.get("version")
    if version != "1.1":
        raise SystemExit("controlled import requires website-publication-package version 1.1")

    metadata = package.get("metadata")
    if not isinstance(metadata, dict):
        raise SystemExit("metadata object is required")

    content_type = package.get("content_type")
    website_source = metadata.get("website_source")
    if not isinstance(website_source, str) or not website_source.strip():
        raise SystemExit("metadata.website_source is required for dry-run or publish mode")

    command = [sys.executable, str(workflow), "publish", str(content_type)]
    if content_type == "sermon":
        command.extend(["--folder", website_source])
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

    if mode == "dry-run":
        command.append("--dry-run")
    elif mode == "publish" and not allow_write:
        raise SystemExit("publish mode requires --allow-write")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate website-publication-package/v1.1 before entering the existing website import flow."
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
    if args.mode != "plan":
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
