#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
SCHEMA = WORKSPACE_ROOT / "workspace-control/schemas/website-publication-package-v1.2.schema.json"
CONSUMER = PROJECT_ROOT / "scripts/consume_publication_package.py"
RESULT_WRITER = PROJECT_ROOT / "scripts/write_publication_result.py"
OUTPUT_ROOT = PROJECT_ROOT / "logs/website-publication-dry-run"
OPERATION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def workspace_reference(path: Path, workspace_root: Path) -> str:
    return str(path.resolve(strict=False).relative_to(workspace_root.resolve(strict=False)))


def bounded_text(value: str, limit: int = 16000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n...[truncated]"


def execute_fixed_dry_run(
    *,
    contract: Path,
    content_root: Path,
    operation_id: str,
    workspace_root: Path = WORKSPACE_ROOT,
    output_root: Path = OUTPUT_ROOT,
    schema: Path = SCHEMA,
    consumer_script: Path = CONSUMER,
    result_writer_script: Path = RESULT_WRITER,
    workflow_script: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    if not OPERATION_ID_RE.fullmatch(operation_id):
        return 2, {"status": "failed", "error_stage": "operation_id", "error": "invalid operation_id"}

    workspace_root = workspace_root.resolve(strict=True)
    contract = contract.resolve(strict=True)
    content_root = content_root.resolve(strict=True)
    schema = schema.resolve(strict=True)
    consumer_script = consumer_script.resolve(strict=True)
    result_writer_script = result_writer_script.resolve(strict=True)

    if not contract.is_file() or not within(contract, workspace_root):
        return 2, {"status": "failed", "error_stage": "contract_path", "error": "contract must be a file within RonnieCross"}
    if not content_root.is_dir() or not within(content_root, workspace_root):
        return 2, {"status": "failed", "error_stage": "content_root", "error": "content_root must be a directory within RonnieCross"}
    expected_schema = (workspace_root / "workspace-control/schemas/website-publication-package-v1.2.schema.json").resolve(strict=True)
    if schema != expected_schema:
        return 2, {"status": "failed", "error_stage": "schema_binding", "error": "schema binding mismatch"}

    try:
        package = load_json(contract)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return 2, {"status": "failed", "error_stage": "contract_load", "error": str(exc)}

    if package.get("interface") != "website-publication-package" or package.get("version") != "1.2":
        return 2, {"status": "failed", "error_stage": "contract_identity", "error": "fixed surface requires website-publication-package/v1.2"}

    metadata = package.get("metadata")
    slug = metadata.get("slug") if isinstance(metadata, dict) else None
    if not isinstance(slug, str) or not slug.strip() or "/" in slug or "\\" in slug or slug in {".", ".."}:
        return 2, {"status": "failed", "error_stage": "slug", "error": "invalid metadata.slug for fixed result mapping"}

    operation_dir = output_root / operation_id
    try:
        operation_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        return 2, {"status": "failed", "error_stage": "operation_id_reuse", "error": "operation_id already exists"}

    plan_path = operation_dir / "controlled-consumption-plan.json"
    evidence_path = operation_dir / "dry-run-evidence.json"
    result_path = operation_dir / "publication-result.json"
    source_contract_ref = workspace_reference(contract, workspace_root)
    evidence_ref = workspace_reference(evidence_path, workspace_root)
    result_ref = workspace_reference(result_path, workspace_root)

    command = [
        sys.executable, str(consumer_script),
        "--contract", str(contract),
        "--schema", str(schema),
        "--content-root", str(content_root),
        "--mode", "dry-run",
        "--plan-output", str(plan_path),
    ]
    if workflow_script is not None:
        command.extend(["--workflow-script", str(workflow_script.resolve(strict=True))])

    consumer_result = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False)
    plan: dict[str, Any] | None = None
    if plan_path.is_file():
        try:
            plan = load_json(plan_path)
        except (OSError, json.JSONDecodeError, ValueError):
            plan = None

    evidence: dict[str, Any] = {
        "interface": "website-owner-fixed-dry-run-evidence",
        "version": "1.0",
        "operation_id": operation_id,
        "surface": "website-publication-package/v1.2 -> Website Owner dry-run -> website-publication-result/v1.1",
        "source_contract": source_contract_ref,
        "source_contract_sha256": sha256(contract),
        "schema": workspace_reference(schema, workspace_root),
        "schema_sha256": sha256(schema),
        "consumer": workspace_reference(consumer_script, workspace_root),
        "consumer_sha256": sha256(consumer_script),
        "result_writer": workspace_reference(result_writer_script, workspace_root),
        "result_writer_sha256": sha256(result_writer_script),
        "mode": "dry-run",
        "read_only_business_flow": True,
        "production_side_effects": [],
        "consumer_returncode": consumer_result.returncode,
        "consumer_plan": plan,
        "consumer_stdout": bounded_text(consumer_result.stdout),
        "consumer_stderr": bounded_text(consumer_result.stderr),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if consumer_result.returncode != 0 or not isinstance(plan, dict) or plan.get("validation_passed") is not True or plan.get("read_only") is not True:
        evidence["status"] = "failed"
        evidence["error_stage"] = "website_dry_run"
        atomic_write_json(evidence_path, evidence)
        return 3, {
            "status": "failed", "error_stage": "website_dry_run", "operation_id": operation_id,
            "evidence_path": evidence_ref, "evidence_sha256": sha256(evidence_path),
            "result_path": None, "side_effects": [],
        }

    evidence["status"] = "dry_run_passed"
    evidence["error_stage"] = None
    atomic_write_json(evidence_path, evidence)
    evidence_sha = sha256(evidence_path)

    expected_post_path = f"src/content/posts/{slug}.md"
    writer_command = [
        sys.executable, str(result_writer_script),
        "--contract-version", "1.1",
        "--status", "dry_run_passed",
        "--slug", slug,
        "--post-path", expected_post_path,
        "--push-status", "not_run",
        "--deployment-status", "not_run",
        "--notification-status", "not_run",
        "--source-contract", source_contract_ref,
        "--acceptance-evidence-id", operation_id,
        "--acceptance-evidence-path", evidence_ref,
        "--acceptance-evidence-sha256", evidence_sha,
        "--output", str(result_path),
    ]
    writer_result = subprocess.run(writer_command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False)
    if writer_result.returncode != 0 or not result_path.is_file():
        return 4, {
            "status": "failed", "error_stage": "result_write", "operation_id": operation_id,
            "evidence_path": evidence_ref, "evidence_sha256": evidence_sha,
            "result_path": None, "side_effects": [], "writer_stderr": bounded_text(writer_result.stderr),
        }

    try:
        result_payload = load_json(result_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result_path.unlink(missing_ok=True)
        return 5, {
            "status": "failed", "error_stage": "result_verification", "operation_id": operation_id,
            "evidence_path": evidence_ref, "evidence_sha256": evidence_sha,
            "result_path": None, "side_effects": [], "error": str(exc),
        }

    result_evidence = result_payload.get("evidence")
    result_valid = (
        result_payload.get("interface") == "website-publication-result"
        and result_payload.get("version") == "1.1"
        and result_payload.get("status") == "dry_run_passed"
        and result_payload.get("build", {}).get("status") == "not_run"
        and result_payload.get("push_status") == "not_run"
        and result_payload.get("deployment_status") == "not_run"
        and result_payload.get("notification_status") == "not_run"
        and isinstance(result_evidence, dict)
        and result_evidence.get("source_contract") == source_contract_ref
        and result_evidence.get("acceptance_evidence_id") == operation_id
        and result_evidence.get("acceptance_evidence_path") == evidence_ref
        and result_evidence.get("acceptance_evidence_sha256") == evidence_sha
    )
    if not result_valid:
        result_path.unlink(missing_ok=True)
        return 5, {
            "status": "failed", "error_stage": "result_verification", "operation_id": operation_id,
            "evidence_path": evidence_ref, "evidence_sha256": evidence_sha,
            "result_path": None, "side_effects": [], "error": "result mapping verification failed",
        }

    return 0, {
        "surface": "website-publication-package/v1.2 -> Website Owner dry-run -> website-publication-result/v1.1",
        "status": "dry_run_passed",
        "operation_id": operation_id,
        "source_contract": source_contract_ref,
        "source_contract_sha256": sha256(contract),
        "evidence_path": evidence_ref,
        "evidence_sha256": evidence_sha,
        "result_path": result_ref,
        "result_sha256": sha256(result_path),
        "side_effects": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fixed Website Owner dry-run surface for website-publication-package/v1.2.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--content-root", required=True, type=Path)
    parser.add_argument("--operation-id", required=True)
    args = parser.parse_args()

    try:
        returncode, receipt = execute_fixed_dry_run(
            contract=args.contract,
            content_root=args.content_root,
            operation_id=args.operation_id,
        )
    except (OSError, ValueError) as exc:
        returncode = 2
        receipt = {"status": "failed", "error_stage": "preflight", "error": str(exc), "side_effects": []}
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
