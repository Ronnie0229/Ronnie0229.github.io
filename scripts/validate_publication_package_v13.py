#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from publication_contract_invariants import validate_package_presentation_bindings
except ModuleNotFoundError:
    from scripts.publication_contract_invariants import validate_package_presentation_bindings


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _object(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


SCHEMA_KEYWORDS = {
    "$ref", "$defs", "type", "const", "enum", "minLength", "pattern", "format",
    "minimum", "required", "properties", "additionalProperties", "items",
    "minItems", "uniqueItems", "allOf", "if", "then",
}
SCHEMA_ANNOTATIONS = {"$schema", "$id", "title", "description", "default"}


def schema_definition_errors(schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    for key, value in schema.items():
        if key in SCHEMA_ANNOTATIONS:
            continue
        if key not in SCHEMA_KEYWORDS:
            errors.append(f"{path}: unsupported JSON Schema keyword {key}")
            continue
        if key == "properties" and isinstance(value, dict):
            for name, child in value.items():
                if isinstance(child, dict):
                    errors.extend(schema_definition_errors(child, f"{path}.properties.{name}"))
        elif key == "$defs" and isinstance(value, dict):
            for name, child in value.items():
                if isinstance(child, dict):
                    errors.extend(schema_definition_errors(child, f"{path}.$defs.{name}"))
        elif key == "items" and isinstance(value, dict):
            errors.extend(schema_definition_errors(value, f"{path}.items"))
        elif key in {"if", "then"} and isinstance(value, dict):
            errors.extend(schema_definition_errors(value, f"{path}.{key}"))
        elif key == "allOf" and isinstance(value, list):
            for index, child in enumerate(value):
                if isinstance(child, dict):
                    errors.extend(schema_definition_errors(child, f"{path}.allOf[{index}]"))
        elif key == "format" and value != "date-time":
            errors.append(f"{path}: unsupported JSON Schema format {value}")
        elif key == "additionalProperties" and isinstance(value, dict):
            errors.append(f"{path}: schema-valued additionalProperties is not supported")
    return errors


def _type_ok(value: Any, expected: str) -> bool:
    return {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }.get(expected, lambda _v: True)(value)


def validate_schema_node(value: Any, schema: dict[str, Any], root_schema: dict[str, Any], path: str, errors: list[str]) -> None:
    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/$defs/"):
        target = root_schema.get("$defs", {}).get(ref.rsplit("/", 1)[-1])
        if not isinstance(target, dict):
            errors.append(f"{path}: unresolved schema ref {ref}")
        else:
            validate_schema_node(value, target, root_schema, path, errors)

    expected = schema.get("type")
    if isinstance(expected, str) and not _type_ok(value, expected):
        errors.append(f"{path or '$'}: expected {expected}")
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path or '$'}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path or '$'}: value {value!r} is not in enum")

    if isinstance(value, str):
        if isinstance(schema.get("minLength"), int) and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: string does not match required pattern")
        if schema.get("format") == "date-time":
            try:
                dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time format")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(schema.get("minimum"), (int, float)) and value < schema["minimum"]:
            errors.append(f"{path}: below minimum")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path or '$'}: missing required field {key}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, child in value.items():
                if key in properties and isinstance(properties[key], dict):
                    validate_schema_node(child, properties[key], root_schema, f"{path}.{key}" if path else key, errors)
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path or '$'}: unknown field {key}")

    if isinstance(value, list):
        if isinstance(schema.get("minItems"), int) and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems")
        if schema.get("uniqueItems") is True:
            try:
                if len({json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value}) != len(value):
                    errors.append(f"{path}: items must be unique")
            except TypeError:
                errors.append(f"{path}: items are not JSON values")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_node(item, item_schema, root_schema, f"{path}[{index}]", errors)

    for condition in schema.get("allOf", []):
        if not isinstance(condition, dict):
            continue
        if_schema = condition.get("if")
        then_schema = condition.get("then")
        if isinstance(if_schema, dict) and isinstance(then_schema, dict):
            condition_errors: list[str] = []
            validate_schema_node(value, if_schema, root_schema, path, condition_errors)
            if not condition_errors:
                validate_schema_node(value, then_schema, root_schema, path, errors)


def resolve_ref(raw: Any, root: Path, label: str, errors: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        errors.append(f"{label}: missing path")
        return None
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        errors.append(f"{label}: referenced file does not exist: {candidate}")
        return None
    try:
        resolved.relative_to(root.resolve(strict=True))
    except (ValueError, OSError):
        errors.append(f"{label}: path escapes content root: {resolved}")
        return None
    if not resolved.is_file():
        errors.append(f"{label}: path is not a regular file: {resolved}")
        return None
    return resolved


def check_sha(path: Path | None, expected: Any, label: str, errors: list[str]) -> None:
    if path is None:
        return
    if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
        errors.append(f"{label}: missing or malformed SHA-256")
    elif sha256(path) != expected:
        errors.append(f"{label}: SHA-256 mismatch")


def validate_v13(package_path: Path, schema_path: Path, content_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}
    try:
        package = read_json(package_path)
        schema = read_json(schema_path)
    except ValueError as exc:
        return {"interface": "website-publication-package-consumer-validation", "version": "1.0", "read_only": True, "pass": False, "checks": {}, "errors": [str(exc)]}

    errors.extend(schema_definition_errors(schema))
    validate_schema_node(package, schema, schema, "", errors)
    checks["schema_valid"] = not errors
    if errors:
        return {
            "interface": "website-publication-package-consumer-validation",
            "version": "1.0",
            "contract_version": "1.3",
            "contract": str(package_path),
            "consumer": "个人网页项目",
            "read_only": True,
            "pass": False,
            "checks": checks,
            "errors": errors,
        }
    root = content_root.resolve(strict=True)
    file_paths: dict[str, Path | None] = {}
    for label in ("prepublish", "official_chinese", "english_source"):
        entry = package.get(label)
        path = resolve_ref(entry.get("path") if isinstance(entry, dict) else None, root, label, errors)
        file_paths[label] = path
        check_sha(path, entry.get("sha256") if isinstance(entry, dict) else None, label, errors)
    presentation = package.get("presentation", {})
    manifest_path = resolve_ref(presentation.get("manifest"), root, "presentation.manifest", errors)
    artifact_path = resolve_ref(presentation.get("artifact"), root, "presentation.artifact", errors)
    check_sha(manifest_path, presentation.get("manifest_sha256"), "presentation.manifest", errors)
    check_sha(artifact_path, presentation.get("artifact_sha256"), "presentation.artifact", errors)

    manifest: dict[str, Any] | None = None
    report: dict[str, Any] | None = None
    paired: dict[str, Any] | None = None
    report_path: Path | None = None
    paired_path: Path | None = None
    if manifest_path:
        try:
            manifest = read_json(manifest_path)
        except ValueError as exc:
            errors.append(str(exc))
    if manifest is not None:
        presentation_schema_path = schema_path.with_name("content-presentation-v1.schema.json")
        try:
            presentation_schema = read_json(presentation_schema_path)
            errors.extend(schema_definition_errors(presentation_schema, "$presentation"))
            validate_schema_node(manifest, presentation_schema, presentation_schema, "manifest", errors)
        except ValueError as exc:
            errors.append(str(exc))
        validator = _object(manifest.get("validator"))
        if validator.get("name") != "content-presentation-validator" or validator.get("version") != "1.0.0":
            errors.append("manifest validator identity/version mismatch")
        report_path = resolve_ref(validator.get("report_path"), root, "validator.report", errors)
        check_sha(report_path, validator.get("report_sha256"), "validator.report", errors)
        if report_path:
            try:
                report = read_json(report_path)
            except ValueError as exc:
                errors.append(str(exc))
        paired_ref = _object(report.get("paired_package")) if isinstance(report, dict) else {}
        paired_path = resolve_ref(paired_ref.get("path"), root, "paired_package", errors)
        check_sha(paired_path, paired_ref.get("sha256"), "paired_package", errors)
        if paired_path:
            try:
                paired = read_json(paired_path)
            except ValueError as exc:
                errors.append(str(exc))

    identity_paths = [file_paths.get("official_chinese"), artifact_path, manifest_path, report_path, paired_path]
    existing_identity_paths = [path for path in identity_paths if path is not None]
    checks["five_identity_paths_distinct"] = len(existing_identity_paths) == 5 and len(set(existing_identity_paths)) == 5
    if not checks["five_identity_paths_distinct"]:
        errors.append("candidate, artifact, manifest, validator report and paired package must be five distinct files")

    if manifest is not None and report is not None and paired is not None:
        try:
            errors.extend(validate_package_presentation_bindings(package, manifest))
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            errors.append(f"cross-document presentation binding validation failed closed: {exc}")
        identity = _object(manifest.get("record_identity"))
        manifest_candidate = _object(manifest.get("candidate"))
        manifest_artifact = _object(manifest.get("artifact"))
        report_candidate = _object(report.get("candidate"))
        report_artifact = _object(report.get("artifact"))
        report_paired = _object(report.get("paired_package"))
        paired_candidate = _object(paired.get("candidate"))
        official_candidate = _object(package.get("official_chinese"))
        records = paired.get("records")
        ids = identity.get("record_ids")
        if not isinstance(records, list) or not isinstance(ids, list):
            errors.append("paired package records and manifest record_ids are required")
        else:
            expected_ids = [f"r-{record.get('record_id'):03d}" for record in records if isinstance(record, dict) and isinstance(record.get("record_id"), int)]
            if len(expected_ids) != len(records) or ids != expected_ids:
                errors.append("manifest record_ids do not match paired package record order")
            if identity.get("record_count") != len(records) or paired.get("record_count") != len(records):
                errors.append("record count does not match paired package records")
            if identity.get("record_order_sha256") != canonical_digest(ids):
                errors.append("record_order_sha256 mismatch")
        if report.get("status") != "PASS" or report.get("presentation_status") != "mechanically_verified":
            errors.append("validator report is not a PASS mechanically_verified report")
        if report.get("content_type") != package.get("content_type") or report.get("profile") != presentation.get("profile"):
            errors.append("validator report content_type/profile mismatch")
        if report_candidate.get("path") != manifest_candidate.get("path"):
            errors.append("validator report candidate path mismatch")
        if report_candidate.get("sha256") != official_candidate.get("sha256"):
            errors.append("validator report candidate SHA mismatch")
        if report_artifact.get("path") != manifest_artifact.get("path"):
            errors.append("validator report artifact path mismatch")
        if report_artifact.get("sha256") != presentation.get("artifact_sha256"):
            errors.append("validator report artifact SHA mismatch")
        if report.get("record_identity") != identity:
            errors.append("validator report record_identity mismatch")
        if report.get("allowed_transformations_used") != manifest.get("allowed_transformations"):
            errors.append("validator report allowed transformations mismatch")
        if report.get("restored_record_count") != paired.get("record_count"):
            errors.append("validator report restored record count mismatch")
        if report_paired.get("sha256") != (sha256(paired_path) if paired_path else None):
            errors.append("validator report paired package SHA mismatch")
        if report_paired.get("pair_set_sha256") != paired.get("pair_set_sha256"):
            errors.append("validator report paired package pair_set mismatch")
        if report_paired.get("audit_id") != paired.get("audit_id"):
            errors.append("validator report paired package audit_id mismatch")
        if paired.get("pair_set_sha256") != identity.get("pair_set_sha256"):
            errors.append("paired package pair_set_sha256 does not match manifest identity")
        if paired_candidate.get("path") != manifest_candidate.get("path"):
            errors.append("paired package candidate path does not match manifest candidate")
        if paired_candidate.get("sha256") != official_candidate.get("sha256"):
            errors.append("paired package candidate SHA does not match official Chinese SHA")

    # The prepublish body must be exactly the bound presentation artifact; frontmatter is metadata only.
    prepublish_path = file_paths.get("prepublish")
    if prepublish_path and artifact_path:
        text = prepublish_path.read_text(encoding="utf-8-sig")
        if not text.startswith("---\n") and not text.startswith("---\r\n"):
            errors.append("prepublish Markdown must contain frontmatter")
        else:
            lines = text.splitlines(keepends=True)
            closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
            if closing is None:
                errors.append("prepublish frontmatter is not closed")
            else:
                body_lines = lines[closing + 1:]
                if body_lines and not body_lines[0].strip():
                    body_lines = body_lines[1:]
                body = "".join(body_lines)
                artifact_text = artifact_path.read_text(encoding="utf-8-sig")
                if body != artifact_text:
                    errors.append("prepublish body is not text-identical to the bound presentation artifact")

    # Website verifies TTS display normalization; it never rewrites frozen candidate bytes.
    if artifact_path:
        try:
            try:
                from scripture_reference_normalizer import find_compact_chinese_references, normalize_scripture_references
            except ModuleNotFoundError:
                from scripts.scripture_reference_normalizer import find_compact_chinese_references, normalize_scripture_references
            artifact_text = artifact_path.read_text(encoding="utf-8-sig")
            compact = find_compact_chinese_references(artifact_text)
            normalized = normalize_scripture_references(artifact_text)
            english_compact = re.findall(
                r"(?i)\b(?:Genesis|Gen|Exodus|Exod?|Ex|Leviticus|Lev|Numbers|Num|Deuteronomy|Deut|Deu|Joshua|Josh|Judges|Judg|Jdg|Ruth|1\s*Samuel|2\s*Samuel|1\s*Sam|2\s*Sam|1\s*Kings|2\s*Kings|1\s*Kin|2\s*Kin|1\s*Chronicles|2\s*Chronicles|1\s*Chron|2\s*Chron|1\s*Chr|2\s*Chr|Ezra|Nehemiah|Neh|Esther|Esth|Job|Psalms?|Ps|Proverbs|Prov|Ecclesiastes|Eccl|Song\s+of\s+(?:Solomon|Songs)|Canticles|Isaiah|Isa|Jeremiah|Jer|Lamentations|Lam|Ezekiel|Ezek|Daniel|Dan|Hosea|Hos|Joel|Amos|Obadiah|Obad|Jonah|Micah|Mic|Nahum|Nah|Habakkuk|Hab|Zephaniah|Zeph|Haggai|Hag|Zechariah|Zech|Malachi|Mal|Matthew|Matt|Mt|Mark|Mk|Luke|Lk|John|Jn|Acts|Romans|Rom|1\s*Corinthians|2\s*Corinthians|1\s*Cor|2\s*Cor|Galatians|Gal|Ephesians|Eph|Philippians|Phil|Colossians|Col|1\s*Thessalonians|2\s*Thessalonians|1\s*Thess|2\s*Thess|1\s*Timothy|2\s*Timothy|1\s*Tim|2\s*Tim|Titus|Tit|Philemon|Phlm|Hebrews|Heb|James|Jas|1\s*Peter|2\s*Peter|1\s*Pet|2\s*Pet|1\s*John|2\s*John|3\s*John|Jude|Revelation|Rev)\.?\s+\d{1,3}\s*:\s*\d{1,3}",
                artifact_text,
            )
            if compact or normalized != artifact_text or english_compact:
                errors.append(f"presentation contains compact/non-normalized scripture references: Chinese={compact[:8]}, English={english_compact[:8]}")
        except Exception as exc:
            errors.append(f"scripture display normalizer unavailable or failed: {exc}")

    content_type = package.get("content_type")
    fidelity = package.get("fidelity_status")
    translation = package.get("translation_status")
    checks["translation_fidelity_pair_valid"] = (
        (translation == "translated" and fidelity in {"independently_verified", "pass_by_max_audit_policy", "authorized_exception"})
        or (translation == "not_translated" and fidelity == "not_required")
    )
    if not checks["translation_fidelity_pair_valid"]:
        errors.append("translation_status and fidelity_status combination is invalid")

    checks["archive_semantics_valid"] = (
        (content_type == "share" and package.get("archive_status") == "not_applicable")
        or (content_type == "sermon" and package.get("archive_status") in {"pending", "archived", "pending_mount", "verification_failed"})
    )
    if not checks["archive_semantics_valid"]:
        errors.append("archive_status does not match content_type semantics")

    passed = not errors
    return {
        "interface": "website-publication-package-consumer-validation",
        "version": "1.0",
        "contract_version": "1.3",
        "contract": str(package_path),
        "consumer": "个人网页项目",
        "read_only": True,
        "pass": passed,
        "checks": checks,
        "errors": errors,
        "normalized": {
            "slug": package.get("metadata", {}).get("slug"),
            "content_type": content_type,
            "profile": presentation.get("profile"),
            "notification_policy": package.get("notification_policy"),
            "archive_status": package.get("archive_status"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Website validation for website-publication-package/v1.3.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--content-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = validate_v13(args.contract, args.schema, args.content_root)
    except (OSError, ValueError) as exc:
        report = {"interface": "website-publication-package-consumer-validation", "version": "1.0", "read_only": True, "pass": False, "checks": {}, "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("pass") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
