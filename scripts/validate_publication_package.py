#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def validate_schema_shape(package: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in package:
            errors.append(f"missing required field: {key}")

    properties = schema.get("properties", {})
    for key, definition in properties.items():
        if key not in package:
            continue
        value = package[key]
        if "const" in definition and value != definition["const"]:
            errors.append(f"invalid {key}: expected {definition['const']!r}")
        if "enum" in definition and value not in definition["enum"]:
            errors.append(f"invalid {key}: {value!r}")
        expected_type = definition.get("type")
        if expected_type == "object" and not isinstance(value, dict):
            errors.append(f"invalid {key}: expected object")
        for nested in definition.get("required", []):
            if isinstance(value, dict) and nested not in value:
                errors.append(f"missing required field: {key}.{nested}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only consumer validation for website-publication-package/v1."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--content-root", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    checks: dict[str, bool] = {}
    errors: list[str] = []

    try:
        package = load_json(args.contract)
        schema = load_json(args.schema)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    schema_errors = validate_schema_shape(package, schema)
    checks["schema_shape_valid"] = not schema_errors
    errors.extend(schema_errors)

    checks["interface_and_version_valid"] = (
        package.get("interface") == "website-publication-package"
        and package.get("version") in {"1.0", "1.1"}
    )
    if not checks["interface_and_version_valid"]:
        errors.append("interface/version mismatch")

    metadata = package.get("metadata")
    required_metadata = ("slug", "publish_date", "batch_id", "content_type")
    checks["metadata_minimum_present"] = isinstance(metadata, dict) and all(
        isinstance(metadata.get(key), str) and metadata.get(key).strip()
        for key in required_metadata
    )
    if not checks["metadata_minimum_present"]:
        errors.append("metadata must include non-empty slug, publish_date, batch_id, content_type")

    checks["metadata_content_type_matches"] = (
        isinstance(metadata, dict)
        and metadata.get("content_type") == package.get("content_type")
    )
    if not checks["metadata_content_type_matches"]:
        errors.append("metadata.content_type does not match content_type")

    content_root = args.content_root.resolve(strict=False)
    references = {
        "prepublish": package.get("prepublish", {}),
        "official_chinese": package.get("official_chinese", {}),
        "english_source": package.get("english_source", {}),
    }

    for label, entry in references.items():
        raw = entry.get("path") if isinstance(entry, dict) else None
        path = Path(raw) if isinstance(raw, str) else None
        checks[f"{label}_path_present"] = path is not None
        if path is None:
            errors.append(f"missing path: {label}")
            continue
        resolved = path.resolve(strict=False)
        checks[f"{label}_within_content_root"] = is_within(resolved, content_root)
        if not checks[f"{label}_within_content_root"]:
            errors.append(f"reference outside content root: {label}: {path}")
            continue
        checks[f"{label}_exists"] = resolved.is_file()
        if not checks[f"{label}_exists"]:
            errors.append(f"missing referenced file: {label}: {path}")
            continue
        expected_sha = entry.get("sha256") if isinstance(entry, dict) else None
        if label in {"official_chinese", "english_source"}:
            checks[f"{label}_sha_present"] = isinstance(expected_sha, str)
            checks[f"{label}_sha_current"] = (
                isinstance(expected_sha, str) and sha256(resolved) == expected_sha
            )
            if not checks[f"{label}_sha_current"]:
                errors.append(f"sha mismatch: {label}: {path}")
        elif isinstance(expected_sha, str):
            checks["prepublish_sha_current"] = sha256(resolved) == expected_sha
            if not checks["prepublish_sha_current"]:
                errors.append(f"sha mismatch: prepublish: {path}")
        elif package.get("version") == "1.1":
            checks["prepublish_sha_required"] = False
            errors.append("website-publication-package/v1.1 requires prepublish.sha256")
        else:
            checks["prepublish_sha_not_available"] = True

    fidelity = package.get("fidelity_status")
    checks["fidelity_status_accepted"] = fidelity in {
        "not_required",
        "independently_verified",
        "authorized_exception",
    }
    if not checks["fidelity_status_accepted"]:
        errors.append(f"invalid fidelity_status: {fidelity!r}")

    checks["notification_policy_accepted"] = package.get("notification_policy") in {
        "normal_first_publish",
        "suppress",
        "manual_authorization_required",
    }
    if not checks["notification_policy_accepted"]:
        errors.append("invalid notification_policy")

    checks["archive_status_accepted"] = package.get("archive_status") in {
        "not_applicable",
        "pending",
        "archived",
        "pending_mount",
        "verification_failed",
    }
    if not checks["archive_status_accepted"]:
        errors.append("invalid archive_status")

    passed = all(checks.values()) and not errors
    report = {
        "interface": "website-publication-package-consumer-validation",
        "version": "1.0",
        "contract": str(args.contract),
        "consumer": "个人网页项目",
        "read_only": True,
        "pass": passed,
        "checks": checks,
        "errors": errors,
        "normalized": {
            "slug": metadata.get("slug") if isinstance(metadata, dict) else None,
            "content_type": package.get("content_type"),
            "notification_policy": package.get("notification_policy"),
            "archive_status": package.get("archive_status"),
        },
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
