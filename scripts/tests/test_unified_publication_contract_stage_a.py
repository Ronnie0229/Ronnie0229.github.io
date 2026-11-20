from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from scripts.publication_contract_invariants import validate_package_presentation_bindings

ROOT = Path(__file__).resolve().parents[2]
SHA = re.compile(r"^[a-f0-9]{64}$")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _matches_type(value, expected):
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }.get(expected, True)


def schema_errors(value, schema, root_schema=None, at="$"):
    root_schema = root_schema or schema
    errors = []
    if "$ref" in schema:
        target = root_schema
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return schema_errors(value, target, root_schema, at)
    expected = schema.get("type")
    if expected and not _matches_type(value, expected):
        return [f"{at}: expected {expected}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{at}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{at}: enum mismatch")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{at}: minLength")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{at}: pattern")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{at}: minItems")
        if schema.get("uniqueItems") and len(value) != len(set(value)):
            errors.append(f"{at}: uniqueItems")
        if "items" in schema:
            for i, item in enumerate(value):
                errors.extend(schema_errors(item, schema["items"], root_schema, f"{at}[{i}]"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{at}: missing {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                errors.append(f"{at}: unexpected {sorted(extras)}")
        for key, child in properties.items():
            if key in value:
                errors.extend(schema_errors(value[key], child, root_schema, f"{at}.{key}"))
    for child in schema.get("allOf", []):
        errors.extend(schema_errors(value, child, root_schema, at))
    condition = schema.get("if")
    if condition is not None and not schema_errors(value, condition, root_schema, at):
        if "then" in schema:
            errors.extend(schema_errors(value, schema["then"], root_schema, at))
    return errors



class UnifiedPublicationContractStageATest(unittest.TestCase):
    def setUp(self):
        self.presentation_schema = load(ROOT / "contracts/content-presentation-v1.schema.json")
        self.package_schema = load(ROOT / "contracts/website-publication-package-v1.3.schema.json")
        self.fixtures = ROOT / "contracts/fixtures"

    def test_schema_mirrors_are_byte_identical(self):
        owner_root = ROOT.parent / "讲道整理-unified-publication-stage-a-20261116"
        self.assertEqual((ROOT / "contracts/content-presentation-v1.schema.json").read_bytes(),
                         (owner_root / "docs/contracts/content-presentation-v1.schema.json").read_bytes())
        self.assertEqual((ROOT / "contracts/website-publication-package-v1.3.schema.json").read_bytes(),
                         (owner_root / "docs/contracts/website-publication-package-v1.3.schema.json").read_bytes())

    def test_positive_and_negative_v13_fixtures_validate_against_schema(self):
        for name in ("content-presentation-share.valid.json", "content-presentation-sermon.valid.json",
                     "website-publication-package-share.v1.3.valid.json",
                     "website-publication-package-sermon.v1.3.valid.json"):
            schema = self.presentation_schema if name.startswith("content-presentation") else self.package_schema
            self.assertEqual(schema_errors(load(self.fixtures / name), schema), [], name)
        for name in ("website-publication-package-share.v1.3.invalid-archive.json",
                     "website-publication-package-sermon.v1.3.invalid-archive.json",
                     "website-publication-package-share.v1.3.invalid-profile.json",
                     "website-publication-package-sermon.v1.3.missing-presentation.json",
                     "website-publication-package-share.v1.3.missing-category.json",
                     "website-publication-package-sermon.v1.3.missing-category.json"):
            self.assertTrue(schema_errors(load(self.fixtures / name), self.package_schema), name)

    def test_share_profile_does_not_require_sermon_structure(self):
        share = load(self.fixtures / "content-presentation-share.valid.json")
        self.assertEqual(share["profile"], "share_article")
        self.assertNotIn("sermon_outline", share)
        self.assertNotIn("full_sermon_mode", share)

    def test_cross_document_identity_validator_accepts_valid_share_pair(self):
        manifest = load(self.fixtures / "content-presentation-share.valid.json")
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        self.assertEqual(validate_package_presentation_bindings(package, manifest), [])

    def test_cross_document_identity_validator_rejects_record_count_mismatch(self):
        manifest = load(self.fixtures / "content-presentation-share.valid.json")
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        manifest["record_identity"]["record_count"] = 4
        errors = validate_package_presentation_bindings(package, manifest)
        self.assertTrue(any("record_count does not equal" in error for error in errors), errors)

    def test_cross_document_identity_validator_rejects_candidate_sha_mismatch(self):
        manifest = load(self.fixtures / "content-presentation-share.valid.json")
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        package["presentation"]["candidate_sha256"] = "b" * 64
        errors = validate_package_presentation_bindings(package, manifest)
        self.assertTrue(any("package presentation candidate SHA-256" in error for error in errors), errors)
        manifest["candidate"]["sha256"] = "b" * 64
        errors = validate_package_presentation_bindings(package, manifest)
        self.assertTrue(any("manifest candidate SHA-256" in error for error in errors), errors)

    def test_cross_document_identity_validator_rejects_duplicate_record_ids(self):
        manifest = load(self.fixtures / "content-presentation-share.valid.json")
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        manifest["record_identity"]["record_ids"][2] = manifest["record_identity"]["record_ids"][1]
        errors = validate_package_presentation_bindings(package, manifest)
        self.assertTrue(any("record_ids must be unique" in error for error in errors), errors)

    def test_cross_document_identity_validator_rejects_artifact_and_record_identity_mismatch(self):
        manifest = load(self.fixtures / "content-presentation-share.valid.json")
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        manifest["artifact"]["sha256"] = "e" * 64
        package["presentation"]["record_identity"]["record_order_sha256"] = "e" * 64
        errors = validate_package_presentation_bindings(package, manifest)
        self.assertTrue(any("artifact SHA-256" in error for error in errors), errors)
        self.assertTrue(any("record_order_sha256" in error for error in errors), errors)

    def test_package_rejects_unknown_nested_metadata_and_record_identity_fields(self):
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        package["metadata"]["unfrozen_extension"] = "unexpected"
        self.assertTrue(schema_errors(package, self.package_schema))
        package = load(self.fixtures / "website-publication-package-share.v1.3.valid.json")
        package["presentation"]["record_identity"]["unfrozen_extension"] = "unexpected"
        self.assertTrue(schema_errors(package, self.package_schema))

    def test_schema_has_explicit_fidelity_and_translation_terminal(self):
        self.assertIn("translation_status", self.package_schema["required"])
        self.assertIn("fidelity_status", self.package_schema["required"])

if __name__ == "__main__":
    unittest.main()
