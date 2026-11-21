from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_publication_package_v13 import canonical_digest, schema_definition_errors, validate_v13


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SCHEMA = ROOT / "contracts/website-publication-package-v1.3.schema.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PublicationPackageV13ConsumerValidationTests(unittest.TestCase):
    def build_fixture(self, root: Path, content_type: str = "share", body: str | None = None) -> tuple[Path, dict]:
        body = body if body is not None else "## Article heading\n\nA complete article paragraph with sufficient content.\n\n- First item\n- Second item\n\n> A quotation.\n"
        candidate = root / "official-chinese.txt"
        candidate.write_text("第一条正文。\n第二条正文。\n", encoding="utf-8")
        english = root / "english-source.txt"
        english.write_text("Source record one.\nSource record two.\n", encoding="utf-8")
        artifact = root / "presentation.md"
        artifact.write_text(body, encoding="utf-8")
        prepublish = root / "prepublish.md"
        person_key = "author" if content_type == "share" else "author"
        category = "灵命成长" if content_type == "share" else "教会讲道"
        source = "data/raw/分享/sample.txt" if content_type == "share" else "data/raw/教会讲道/sample-sermon"
        frontmatter = (
            "---\n"
            'articleId: ""\n'
            'title: "测试文章标题"\n'
            'description: "这是一段用于验证的完整文章摘要，清楚说明文章的主要内容与重点。"\n'
            "date: 2026-11-17\n"
            'tags: ["恩典", "信心"]\n'
            f'category: "{category}"\n'
            'scripture: ""\n'
            f'author: "{ "Ronnie" if content_type == "share" else "Patrick" }"\n'
            'metadataStatus: "confirmed"\n'
            "reviewed: false\n"
            f'source: "{source}"\n'
            f'contentType: "{content_type}"\n'
            "---\n\n"
        )
        prepublish.write_text(frontmatter + body, encoding="utf-8")

        ids = ["r-001", "r-002"]
        identity = {
            "record_count": 2,
            "record_ids": ids,
            "record_order_sha256": canonical_digest(ids),
            "pair_set_sha256": "a" * 64,
        }
        paired = {
            "audit_id": "audit-2026-11-17",
            "pair_set_sha256": "a" * 64,
            "record_count": 2,
            "candidate": {"path": str(candidate), "sha256": digest(candidate)},
            "records": [{"record_id": 1}, {"record_id": 2}],
        }
        paired_path = root / "paired-package.json"
        paired_path.write_text(json.dumps(paired, ensure_ascii=False), encoding="utf-8")

        report = {
            "status": "PASS",
            "presentation_status": "mechanically_verified",
            "content_type": content_type,
            "profile": "share_article" if content_type == "share" else "sermon",
            "candidate": {"path": str(candidate), "sha256": digest(candidate)},
            "artifact": {"path": str(artifact), "sha256": digest(artifact)},
            "record_identity": identity,
            "allowed_transformations_used": ["blank_line_boundaries"],
            "restored_record_count": 2,
            "paired_package": {
                "path": str(paired_path),
                "sha256": digest(paired_path),
                "pair_set_sha256": "a" * 64,
                "audit_id": "audit-2026-11-17",
            },
        }
        report_path = root / "validator-report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

        manifest = {
            "interface": "content-presentation",
            "version": "1.0",
            "content_type": content_type,
            "profile": "share_article" if content_type == "share" else "sermon",
            "candidate": {"path": str(candidate), "sha256": digest(candidate)},
            "artifact": {"path": str(artifact), "sha256": digest(artifact)},
            "record_identity": identity,
            "presentation_status": "mechanically_verified",
            "text_identity_status": "exact_record_order_preserved",
            "allowed_transformations": ["blank_line_boundaries"],
            "validator": {
                "name": "content-presentation-validator",
                "version": "1.0.0",
                "executed_at": "2026-11-17T12:00:00+09:00",
                "report_path": str(report_path),
                "report_sha256": digest(report_path),
            },
        }
        manifest_path = root / "presentation-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

        metadata = {
            "slug": "2026-11-17-sample-article",
            "publish_date": "2026-11-17",
            "batch_id": "batch-2026-11-17",
            "content_type": content_type,
            "category": category,
            "author": "Ronnie",
        }
        if content_type == "sermon":
            metadata.pop("author")
            metadata["speaker"] = "Patrick"

        package = {
            "interface": "website-publication-package",
            "version": "1.3",
            "content_type": content_type,
            "prepublish": {"path": str(prepublish), "sha256": digest(prepublish)},
            "official_chinese": {"path": str(candidate), "sha256": digest(candidate)},
            "english_source": {"path": str(english), "sha256": digest(english)},
            "fidelity_status": "independently_verified",
            "translation_status": "translated",
            "metadata": metadata,
            "notification_policy": "suppress",
            "archive_status": "not_applicable" if content_type == "share" else "archived",
            "presentation": {
                "manifest": str(manifest_path),
                "artifact": str(artifact),
                "manifest_sha256": digest(manifest_path),
                "content_type": content_type,
                "profile": "share_article" if content_type == "share" else "sermon",
                "presentation_status": "mechanically_verified",
                "text_identity_status": "exact_record_order_preserved",
                "candidate_sha256": digest(candidate),
                "artifact_sha256": digest(artifact),
                "record_identity": {
                    "record_count": 2,
                    "record_order_sha256": identity["record_order_sha256"],
                    "pair_set_sha256": identity["pair_set_sha256"],
                },
            },
        }
        package_path = root / "package.json"
        package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        return package_path, package

    def validate(self, package_path: Path, root: Path) -> dict:
        return validate_v13(package_path, PACKAGE_SCHEMA, root)

    def test_current_owner_schemas_use_only_supported_consumer_keywords(self):
        package_schema = json.loads(PACKAGE_SCHEMA.read_text(encoding="utf-8"))
        presentation_schema = json.loads((ROOT / "contracts/content-presentation-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema_definition_errors(package_schema), [])
        self.assertEqual(schema_definition_errors(presentation_schema), [])
        unsupported = dict(package_schema)
        unsupported["unevaluatedProperties"] = False
        self.assertTrue(any("unsupported JSON Schema keyword" in item for item in schema_definition_errors(unsupported)))

    def test_valid_share_v13_package_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, _ = self.build_fixture(root, "share")
            report = self.validate(package_path, root)
            self.assertTrue(report["pass"], report["errors"])
            self.assertTrue(report["checks"]["schema_valid"])
            self.assertTrue(report["checks"]["five_identity_paths_distinct"])
            self.assertTrue(report["checks"]["translation_fidelity_pair_valid"])
            self.assertTrue(report["checks"]["archive_semantics_valid"])

    def test_valid_sermon_v13_package_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, _ = self.build_fixture(root, "sermon")
            report = self.validate(package_path, root)
            self.assertTrue(report["pass"], report["errors"])

    def test_rejects_unknown_top_level_and_file_ref_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            package["unapproved"] = True
            package["official_chinese"]["extra"] = "no"
            package["metadata"]["unexpected"] = "no"
            package["presentation"]["unexpected"] = "no"
            package_path.write_text(json.dumps(package), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("unknown field" in item for item in report["errors"]))

    def test_rejects_share_archive_and_category_semantics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root, "share")
            package["archive_status"] = "archived"
            package["metadata"]["category"] = "教会讲道"
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("archive_status" in item or "category" in item for item in report["errors"]))

    def test_rejects_translation_fidelity_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            package["translation_status"] = "not_translated"
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertFalse(report["checks"]["schema_valid"])

    def test_rejects_candidate_sha_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            package["official_chinese"]["sha256"] = "0" * 64
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("official_chinese: SHA-256 mismatch" in item for item in report["errors"]))

    def test_rejects_compact_chinese_scripture_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root, body="正文引用（罗马书 1:15）。\n")
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("scripture references" in item for item in report["errors"]))

    def test_rejects_english_scripture_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root, body="Read John 3:16 carefully.\n")
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("scripture references" in item for item in report["errors"]))

    def test_accepts_tts_friendly_chinese_scripture_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root, body="保罗在（罗马书1章15节）这样说。\n")
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertTrue(report["pass"], report["errors"])

    def test_rejects_noncontinuous_scripture_reference_list(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root, body="请阅读（罗马书8:28,31）。\n")
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("scripture references" in item for item in report["errors"]))

    def test_rejects_profile_mismatch_and_missing_identity_field(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root, "share")
            package["presentation"]["profile"] = "sermon"
            del package["presentation"]["record_identity"]["record_count"]
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("profile" in item or "record_count" in item for item in report["errors"]))

    def test_rejects_out_of_root_file_reference(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            external = Path(outside) / "external.txt"
            external.write_text("outside", encoding="utf-8")
            package["english_source"]["path"] = str(external)
            package["english_source"]["sha256"] = digest(external)
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("escapes content root" in item for item in report["errors"]))

    def test_rejects_validator_report_sha_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            manifest = json.loads(Path(package["presentation"]["manifest"]).read_text(encoding="utf-8"))
            report_path = Path(manifest["validator"]["report_path"])
            report_path.write_text(report_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("validator.report: SHA-256 mismatch" in item for item in report["errors"]))

    def test_rejects_identity_path_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            candidate = Path(package["official_chinese"]["path"])
            package["presentation"]["artifact"] = str(candidate)
            package["presentation"]["artifact_sha256"] = digest(candidate)
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertFalse(report["checks"]["five_identity_paths_distinct"])

    def test_rejects_pair_set_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            paired_path = root / "paired-package.json"
            paired = json.loads(paired_path.read_text(encoding="utf-8"))
            paired["pair_set_sha256"] = "b" * 64
            paired_path.write_text(json.dumps(paired, ensure_ascii=False), encoding="utf-8")
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("pair_set" in item for item in report["errors"]))

    def test_rejects_prepublication_body_artifact_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = self.build_fixture(root)
            prepublish = Path(package["prepublish"]["path"])
            prepublish.write_text(prepublish.read_text(encoding="utf-8") + "unbound text\n", encoding="utf-8")
            package["prepublish"]["sha256"] = digest(prepublish)
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            report = self.validate(package_path, root)
            self.assertFalse(report["pass"])
            self.assertTrue(any("text-identical" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
