from __future__ import annotations

import contextlib
import importlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import consume_publication_package as consumer

_fixture_module = importlib.import_module("scripts.tests.test_validate_publication_package_v13")


class V13PackageImportCommandTests(unittest.TestCase):
    def build(self, root: Path, content_type: str = "share") -> dict:
        if content_type == "share":
            source_rel = "data/raw/分享/sample.txt"
            category = "灵命成长"
            person_key = "author"
            person = "Ronnie"
            source = root / "data/raw/分享/sample.txt"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("raw source", encoding="utf-8")
        else:
            source_rel = "data/raw/教会讲道/sample-sermon/sample-sermon_中文.txt"
            category = "教会讲道"
            person_key = "speaker"
            person = "Patrick"
            source = root / "data/raw/教会讲道/sample-sermon"
            source.mkdir(parents=True)
            (source / "sample-sermon_中文.txt").write_text("sermon source", encoding="utf-8")
        prepublish = root / "prepublish.md"
        prepublish.write_text(
            "---\n"
            'title: "测试标题"\n'
            'description: "这是一段完整的摘要，说明本文的核心主题和信息。"\n'
            "date: 2026-11-17\n"
            'tags: ["恩典", "信心"]\n'
            f'category: "{category}"\n'
            'scripture: "罗马书1章15节"\n'
            f'author: "{person}"\n'
            f'source: "{source_rel}"\n'
            f'contentType: "{content_type}"\n'
            "---\n\n正文。\n",
            encoding="utf-8",
        )
        if content_type == "sermon":
            prepublish.write_text(
                prepublish.read_text(encoding="utf-8").replace(
                    'contentType: "sermon"\n', 'contentType: "sermon"\nupdateExisting: true\n'
                ),
                encoding="utf-8",
            )
        artifact = root / "presentation.md"
        artifact.write_text("正文。\n", encoding="utf-8")
        metadata = {
            "slug": "2026-11-17-test",
            "publish_date": "2026-11-17",
            "batch_id": "batch-1",
            "content_type": content_type,
            "category": category,
            person_key: person,
        }
        return {
            "version": "1.3",
            "content_type": content_type,
            "metadata": metadata,
            "prepublish": {"path": str(prepublish)},
            "presentation": {"artifact": str(artifact)},
        }

    def command(self, root: Path, package: dict, mode: str, allow_write: bool = False) -> list[str]:
        package_path = root / "package.json"
        package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        return consumer.import_command(
            package, root / "content_workflow.py", mode, allow_write,
            package_path=package_path, content_root=root,
        )

    def test_share_v13_command_uses_bound_artifact_and_package_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.build(root, "share")
            with patch.object(consumer, "ROOT", root):
                command = self.command(root, package, "dry-run")
            self.assertIn("--presentation-file", command)
            self.assertIn(str((root / "presentation.md").resolve()), command)
            self.assertIn("--source-file", command)
            self.assertIn("sample.txt", command)
            self.assertIn("--author", command)
            self.assertIn("Ronnie", command)
            self.assertIn("--publish-date", command)
            self.assertIn("2026-11-17", command)
            self.assertIn("--dry-run", command)

    def test_sermon_v13_command_uses_single_source_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.build(root, "sermon")
            with patch.object(consumer, "ROOT", root):
                command = self.command(root, package, "dry-run")
            self.assertIn("--folder", command)
            self.assertIn("sample-sermon", command)
            self.assertIn("--presentation-file", command)
            self.assertIn("--tags", command)
            self.assertIn("恩典,信心", command)
            self.assertIn("--update-existing", command)

    def test_v13_publish_requires_explicit_allow_write_and_builds_command(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.build(root, "share")
            with patch.object(consumer, "ROOT", root):
                with self.assertRaisesRegex(SystemExit, "requires --allow-write"):
                    self.command(root, package, "publish", False)
                command = self.command(root, package, "publish", True)
            self.assertNotIn("--dry-run", command)
            self.assertIn("--allow-write", command)
            self.assertIn("--presentation-file", command)
            self.assertIn("--publication-package", command)

    def test_prepublication_author_mismatch_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.build(root, "share")
            prepublish = Path(package["prepublish"]["path"])
            prepublish.write_text(prepublish.read_text(encoding="utf-8").replace('author: "Ronnie"', 'author: "Someone Else"'), encoding="utf-8")
            with patch.object(consumer, "ROOT", root):
                with self.assertRaisesRegex(SystemExit, "author/speaker"):
                    self.command(root, package, "dry-run")

    def test_source_path_traversal_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.build(root, "share")
            prepublish = Path(package["prepublish"]["path"])
            prepublish.write_text(prepublish.read_text(encoding="utf-8").replace("data/raw/分享/sample.txt", "data/raw/分享/../outside.txt"), encoding="utf-8")
            with patch.object(consumer, "ROOT", root):
                with self.assertRaisesRegex(SystemExit, "normalized project-relative path"):
                    self.command(root, package, "dry-run")

    def test_missing_prepublication_title_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = self.build(root, "share")
            prepublish = Path(package["prepublish"]["path"])
            prepublish.write_text(prepublish.read_text(encoding="utf-8").replace('title: "测试标题"\n', ""), encoding="utf-8")
            with patch.object(consumer, "ROOT", root):
                with self.assertRaisesRegex(SystemExit, "title is required"):
                    self.command(root, package, "dry-run")

    def test_consumer_main_uses_v13_validator_in_plan_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, _ = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            argv = [
                "consume_publication_package.py",
                "--contract", str(package_path),
                "--schema", str(consumer.V13_PACKAGE_SCHEMA),
                "--content-root", str(root),
                "--mode", "plan",
            ]
            output = io.StringIO()
            with patch("sys.argv", argv), contextlib.redirect_stdout(output):
                exit_code = consumer.main()
            plan = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0, plan)
            self.assertTrue(plan["validation_passed"])
            self.assertEqual(plan["contract_version"], "1.3")
            self.assertIsNone(plan["command"])
            self.assertTrue(plan["validator_report"]["pass"])

    def test_consumer_main_runs_share_v13_dry_run_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, _ = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            raw_source = root / "data/raw/分享/sample.txt"
            raw_source.parent.mkdir(parents=True)
            raw_source.write_text("source attribution only", encoding="utf-8")
            fake_workflow = root / "fake_workflow.py"
            fake_workflow.write_text("pass\n", encoding="utf-8")
            argv = [
                "consume_publication_package.py",
                "--contract", str(package_path),
                "--schema", str(consumer.V13_PACKAGE_SCHEMA),
                "--content-root", str(root),
                "--workflow-script", str(fake_workflow),
                "--mode", "dry-run",
            ]
            output = io.StringIO()
            with (
                patch.object(consumer, "ROOT", root),
                patch("sys.argv", argv),
                contextlib.redirect_stdout(output),
            ):
                exit_code = consumer.main()
            plan = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0, plan)
            self.assertEqual(plan["contract_version"], "1.3")
            self.assertTrue(plan["read_only"])
            self.assertEqual(plan["workflow_returncode"], 0)
            self.assertIn("--publication-package", plan["command"])
            self.assertIn("--content-root", plan["command"])
            self.assertIn("--dry-run", plan["command"])


if __name__ == "__main__":
    unittest.main()
