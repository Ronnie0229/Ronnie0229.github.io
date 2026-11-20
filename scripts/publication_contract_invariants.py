from __future__ import annotations


def validate_package_presentation_bindings(package: dict, manifest: dict) -> list[str]:
    """Validate cross-document identity rules not expressible as JSON Schema equality."""
    errors: list[str] = []
    official = package.get("official_chinese", {})
    presentation = package.get("presentation", {})
    candidate = manifest.get("candidate", {})
    artifact = manifest.get("artifact", {})
    manifest_identity = manifest.get("record_identity", {})
    package_identity = presentation.get("record_identity", {})

    official_path = official.get("path")
    official_sha = official.get("sha256")
    if candidate.get("path") != official_path:
        errors.append("manifest candidate path does not match package official_chinese path")
    if candidate.get("sha256") != official_sha:
        errors.append("manifest candidate SHA-256 does not match package official_chinese SHA-256")
    if presentation.get("candidate_sha256") != official_sha:
        errors.append("package presentation candidate SHA-256 does not match official_chinese SHA-256")

    if artifact.get("path") != presentation.get("artifact"):
        errors.append("manifest artifact path does not match package presentation artifact")
    if artifact.get("sha256") != presentation.get("artifact_sha256"):
        errors.append("manifest artifact SHA-256 does not match package presentation artifact_sha256")

    if manifest.get("content_type") != package.get("content_type"):
        errors.append("manifest content_type does not match package content_type")
    if presentation.get("content_type") != package.get("content_type"):
        errors.append("package presentation content_type does not match package content_type")
    if manifest.get("profile") != presentation.get("profile"):
        errors.append("manifest profile does not match package presentation profile")

    record_ids = manifest_identity.get("record_ids", [])
    record_count = manifest_identity.get("record_count")
    if not isinstance(record_ids, list):
        errors.append("manifest record_ids must be an array")
        record_ids = []
    if record_count != len(record_ids):
        errors.append("manifest record_count does not equal record_ids length")
    if len(record_ids) != len(set(record_ids)):
        errors.append("manifest record_ids must be unique")

    for field in ("record_count", "record_order_sha256", "pair_set_sha256"):
        if manifest_identity.get(field) != package_identity.get(field):
            errors.append(f"manifest record_identity {field} does not match package presentation record_identity")

    return errors
