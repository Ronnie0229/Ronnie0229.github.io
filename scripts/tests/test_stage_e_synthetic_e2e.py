from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SERMON_ROOT = Path("/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理-unified-publication-stage-a-20261116")
SERMON_SCRIPTS = SERMON_ROOT / "scripts"
sys.path.insert(0, str(SERMON_SCRIPTS))
from translation_fidelity_orchestration_lib import build_paired_audit_package_from_nonempty_lines

from scripts import consume_publication_package as consumer


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore_candidate_record(line: str) -> str:
    value = line
    heading = re.match(r"^#{2,3} (.*)$", value)
    if heading:
        return heading.group(1)
    quote = re.match(r"^> (.*)$", value)
    if quote:
        value = quote.group(1)
    else:
        item = re.match(r"^(?:[-+*]|\\d+[.)]) (.*)$", value)
        if item:
            value = item.group(1)
    for marker in ("**", "__", "*", "_"):
        if value.startswith(marker) and value.endswith(marker) and len(value) > 2 * len(marker):
            value = value[len(marker):-len(marker)]
            break
    return value


class StageESyntheticProducerConsumerE2ETests(unittest.TestCase):
    def build_and_consume(self, root: Path, content_type: str, artifact_body: str) -> dict:
        records = [restore_candidate_record(line) for line in artifact_body.splitlines() if line.strip()]
        self.assertGreater(len(records), 3)
        candidate = root / "official-chinese.txt"
        candidate.write_text("\n".join(records) + "\n", encoding="utf-8")
        english = root / "english-source.txt"
        english.write_text("\n".join(f"Synthetic source record {i}." for i in range(1, len(records) + 1)) + "\n", encoding="utf-8")
        artifact = root / "presentation.md"
        artifact.write_text(artifact_body.rstrip("\n") + "\n", encoding="utf-8")

        paired = build_paired_audit_package_from_nonempty_lines(
            audit_id=f"stage-e-{content_type}",
            source_path=english,
            candidate_path=candidate,
            provenance={"synthetic_stage_e": True, "content_type": content_type},
        )
        paired_path = root / "paired-package.json"
        paired_path.write_text(json.dumps(paired, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        manifest = root / "content-presentation-manifest.json"
        validator_report = root / "content-presentation-report.json"
        validator = subprocess.run([
            sys.executable, str(SERMON_SCRIPTS / "validate_content_presentation_artifact.py"),
            "--content-type", content_type,
            "--candidate", str(candidate),
            "--artifact", str(artifact),
            "--paired-package", str(paired_path),
            "--output-manifest", str(manifest),
            "--report", str(validator_report),
        ], capture_output=True, text=True, check=False)
        self.assertEqual(validator.returncode, 0, validator.stderr or validator.stdout)
        presentation_report = json.loads(validator_report.read_text(encoding="utf-8"))
        self.assertEqual(presentation_report["status"], "PASS")

        category = "灵命成长" if content_type == "share" else "教会讲道"
        person_key = "author" if content_type == "share" else "speaker"
        person = "Ronnie" if content_type == "share" else "Patrick"
        slug = f"stage-e-{content_type}"
        source_rel = (
            "data/raw/分享/synthetic-share.txt"
            if content_type == "share"
            else "data/raw/教会讲道/synthetic-sermon/synthetic-sermon_中文.txt"
        )
        prepublish = root / "prepublish.md"
        frontmatter = (
            "---\n"
            f'title: "Stage E Synthetic {content_type.title()}"\n'
            'description: "Synthetic end-to-end acceptance fixture; not a real publication."\n'
            "date: 2026-11-19\n"
            'tags: ["合成验收", "测试"]\n'
            f'category: "{category}"\n'
            'scripture: "罗马书1章15节"\n'
            f'author: "{person}"\n'
            f'source: "{source_rel}"\n'
            f'contentType: "{content_type}"\n'
            "---\n\n"
        )
        prepublish.write_text(frontmatter + artifact.read_text(encoding="utf-8"), encoding="utf-8")

        if content_type == "share":
            raw = root / "data/raw/分享"
            raw.mkdir(parents=True)
            (raw / "synthetic-share.txt").write_text("Synthetic Share raw attribution only.", encoding="utf-8")
        else:
            raw = root / "data/raw/教会讲道/synthetic-sermon"
            raw.mkdir(parents=True)
            (raw / "synthetic-sermon_中文.txt").write_text("Synthetic Sermon raw attribution only.", encoding="utf-8")

        metadata = {
            "slug": slug,
            "publish_date": "2026-11-19",
            "batch_id": f"stage-e-{content_type}",
            "content_type": content_type,
            "category": category,
            person_key: person,
        }
        metadata_path = root / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        package_path = root / "website-publication-package-v1.3.json"
        builder = subprocess.run([
            sys.executable, str(SERMON_SCRIPTS / "build_website_publication_package.py"),
            "--contract-version", "1.3",
            "--content-type", content_type,
            "--prepublish", str(prepublish),
            "--official-chinese", str(candidate),
            "--english-source", str(english),
            "--metadata-json", str(metadata_path),
            "--output", str(package_path),
            "--fidelity-status", "independently_verified",
            "--notification-policy", "suppress",
            "--content-presentation-manifest", str(manifest),
        ], capture_output=True, text=True, check=False)
        self.assertEqual(builder.returncode, 0, builder.stderr or builder.stdout)
        package = json.loads(package_path.read_text(encoding="utf-8"))
        self.assertEqual(package["version"], "1.3")
        self.assertEqual(package["archive_status"], "not_applicable" if content_type == "share" else "pending")

        fake_workflow = root / "workflow_stub.py"
        fake_workflow.write_text("print('synthetic dry-run dispatch only')\n", encoding="utf-8")
        argv = [
            "consume_publication_package.py",
            "--contract", str(package_path),
            "--schema", str(ROOT / "contracts/website-publication-package-v1.3.schema.json"),
            "--content-root", str(root),
            "--mode", "dry-run",
            "--workflow-script", str(fake_workflow),
        ]
        output = io.StringIO()
        with (
            patch.object(consumer, "ROOT", root),
            patch("sys.argv", argv),
            contextlib.redirect_stdout(output),
        ):
            try:
                exit_code = consumer.main()
            except SystemExit as exc:
                self.fail(f"Website consumer exited {exc.code}: {output.getvalue()}")
        self.assertEqual(exit_code, 0, output.getvalue())
        plan = json.loads(output.getvalue())
        self.assertTrue(plan["validation_passed"])
        self.assertTrue(plan["read_only"])
        self.assertEqual(plan["contract_version"], "1.3")
        self.assertEqual(plan["archive_status"], package["archive_status"])
        self.assertIn("--dry-run", plan["command"])
        self.assertEqual(plan["workflow_returncode"], 0)
        self.assertIsNotNone(plan["prepublication_structure_gate"])
        self.assertEqual(plan["prepublication_structure_gate"]["source"]["sha256"], sha(artifact))
        self.assertEqual(Path(plan["prepublication_structure_gate"]["source"]["path"]), artifact.resolve())
        self.assertRegex(plan["prepublication_structure_gate"]["rendered_html"]["sha256"], r"^[a-f0-9]{64}$")
        return plan

    def test_synthetic_share_producer_to_website_dry_run(self):
        body = (
            "## Article heading\n\n"
            "A complete synthetic article paragraph with sufficient context.\n\n"
            "- First article item\n"
            "- Second article item\n\n"
            "> A synthetic quotation.\n"
        )
        with tempfile.TemporaryDirectory(prefix="stage-e-share-") as tmp:
            plan = self.build_and_consume(Path(tmp), "share", body)
        self.assertEqual(plan["archive_status"], "not_applicable")
        self.assertEqual(plan["prepublication_structure_gate"]["status"], "CONTENT_PRESENTATION_STRUCTURE_PASS")

    def test_synthetic_sermon_producer_to_website_dry_run(self):
        fixture = ROOT / "scripts/tests/fixtures/sermon_presentation/pass.md"
        body = fixture.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="stage-e-sermon-") as tmp:
            plan = self.build_and_consume(Path(tmp), "sermon", body)
        self.assertEqual(plan["archive_status"], "pending")
        self.assertEqual(plan["prepublication_structure_gate"]["status"], "SERMON_PRESENTATION_STRUCTURE_PASS")


if __name__ == "__main__":
    unittest.main()
