from __future__ import annotations

import importlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "content_workflow.py"
SPEC = importlib.util.spec_from_file_location("content_workflow_v13_share", SCRIPT)
content_workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(content_workflow)
_fixture_module = importlib.import_module("scripts.tests.test_validate_publication_package_v13")


class ContentWorkflowV13ShareGateTests(unittest.TestCase):
    def build_share_fixture(self, root: Path, *, source_kind: str = "file"):
        package_path, package = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
        raw = root / "data" / "raw" / "分享"
        raw.mkdir(parents=True, exist_ok=True)
        source = raw / "sample.txt"
        if source_kind == "file":
            source.write_text("Source attribution.", encoding="utf-8")
        elif source_kind == "directory":
            source.mkdir()
        elif source_kind == "broken_symlink":
            source.symlink_to(root / "missing-target.txt")
        return package_path, package, raw

    def test_v13_share_route_revalidates_package_and_render_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package, raw = self.build_share_fixture(root)
            evidence = {
                "status": "CONTENT_PRESENTATION_STRUCTURE_PASS",
                "completion_ceiling": "publication_structure_ready",
                "rendered_html": {"sha256": "a" * 64},
            }
            package_evidence = {"pass": True}
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                if "validate_publication_package_v13.py" in " ".join(command):
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps(package_evidence), "stderr": ""})()
                if command[0] == "node":
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps(evidence), "stderr": ""})()
                return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

            with patch.dict(content_workflow.RAW_DIRS, {"share": raw}), patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
                content_workflow.publish(
                    "share",
                    source_file="sample.txt",
                    presentation_file=package["presentation"]["artifact"],
                    dry_run=True,
                    title="测试文章标题",
                    scripture="",
                    slug="2026-11-17-sample-article",
                    description="这是一段用于验证的完整文章摘要，清楚说明文章的主要内容与重点。",
                    tags="恩典,信心",
                    author="Ronnie",
                    publish_date="2026-11-17",
                    publication_package=str(package_path),
                    content_root=str(root),
                    allow_write=True,
                )

            self.assertEqual(len(calls), 3)
            self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))
            self.assertIn("share_article", calls[1])
            self.assertIn("--presentation-file", calls[2])
            self.assertIn("--contract", calls[0])
            self.assertIn(str(package_path.resolve()), calls[0])
            self.assertIn("--content-root", calls[0])
            self.assertIn(str(root), calls[0])
            self.assertIn("--author", calls[2])
            self.assertIn("Ronnie", calls[2])
            self.assertIn("--publish-date", calls[2])
            self.assertIn("2026-11-17", calls[2])
            self.assertIn("--dry-run", calls[2])
            self.assertIn("--publication-package", calls[2])
            self.assertIn(str(package_path.resolve()), calls[2])
            self.assertIn("--content-root", calls[2])
            self.assertIn(str(root), calls[2])

    def test_v13_share_workflow_rejects_source_and_metadata_spoofing_before_importer(self):
        mismatches = {
            "source": {"source_file": "different-source.txt"},
            "title": {"title": "Spoofed title"},
            "description": {"description": "Spoofed but sufficiently long description."},
            "scripture": {"scripture": "罗马书1章15节"},
            "tags": {"tags": "恩典,伪造"},
            "author": {"author": "Spoofed Author"},
            "publish_date": {"publish_date": "2026-11-18"},
            "slug": {"slug": "2026-11-17-spoofed"},
        }
        for field, override in mismatches.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                package_path, package, raw = self.build_share_fixture(root)
                calls = []

                def fake_run(command, **kwargs):
                    calls.append(command)
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps({"pass": True}), "stderr": ""})()

                values = {
                    "source_file": "sample.txt",
                    "presentation_file": package["presentation"]["artifact"],
                    "dry_run": True,
                    "title": "测试文章标题",
                    "description": "这是一段用于验证的完整文章摘要，清楚说明文章的主要内容与重点。",
                    "scripture": "",
                    "slug": "2026-11-17-sample-article",
                    "tags": "恩典,信心",
                    "author": "Ronnie",
                    "publish_date": "2026-11-17",
                    "publication_package": str(package_path),
                    "content_root": str(root),
                }
                values.update(override)
                with patch.dict(content_workflow.RAW_DIRS, {"share": raw}), patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
                    with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH"):
                        content_workflow.publish("share", **values)
                self.assertEqual(len(calls), 1, f"{field} mismatch must fail before renderer/importer")
                self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))

    def test_v13_sermon_route_revalidates_package_and_sermon_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "sermon")
            (root / "data" / "raw" / "教会讲道" / "sample-sermon").mkdir(parents=True)
            sermon_evidence = {
                "status": "SERMON_PRESENTATION_STRUCTURE_PASS",
                "completion_ceiling": "publication_structure_ready",
                "rendered_html": {"sha256": "b" * 64},
            }
            package_evidence = {"pass": True}
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                if "validate_publication_package_v13.py" in " ".join(command):
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps(package_evidence), "stderr": ""})()
                if command[0] == "node":
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps(sermon_evidence), "stderr": ""})()
                return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

            with patch.dict(content_workflow.RAW_DIRS, {"sermon": root / "data" / "raw" / "教会讲道"}), patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
                content_workflow.publish(
                    "sermon",
                    folder="sample-sermon",
                    presentation_file=package["presentation"]["artifact"],
                    dry_run=False,
                    publication_package=str(package_path),
                    content_root=str(root),
                    allow_write=True,
                )

            self.assertEqual(len(calls), 3)
            self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))
            self.assertIn("validate_sermon_presentation.mjs", " ".join(calls[1]))
            self.assertIn("--presentation-file", calls[2])
            self.assertIn("--allow-write", calls[2])
            self.assertIn("sample-sermon", calls[2])
            self.assertIn("--expected-source-folder", calls[2])
            self.assertIn(str((root / "data" / "raw" / "教会讲道" / "sample-sermon").resolve()), calls[2])
            self.assertIn("--publication-package", calls[2])
            self.assertIn(str(package_path.resolve()), calls[2])
            self.assertIn("--content-root", calls[2])
            self.assertIn(str(root), calls[2])
            self.assertNotIn("--dry-run", calls[2])

    def test_v13_sermon_workflow_rejects_mismatched_folder_before_renderer_or_importer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "sermon")
            sermon_root = root / "data" / "raw" / "教会讲道"
            (sermon_root / "sample-sermon").mkdir(parents=True)
            (sermon_root / "other-sermon").mkdir()
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                return type("Result", (), {"returncode": 0, "stdout": json.dumps({"pass": True}), "stderr": ""})()

            with patch.dict(content_workflow.RAW_DIRS, {"sermon": root / "data" / "raw" / "教会讲道"}), patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH.*folder"):
                    content_workflow.publish(
                        "sermon", folder="other-sermon", presentation_file=package["presentation"]["artifact"],
                        dry_run=True, publication_package=str(package_path), content_root=str(root),
                    )
            self.assertEqual(len(calls), 1, "mismatched folder must fail before renderer/importer")
            self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))

    def test_v13_sermon_workflow_rejects_package_bound_in_root_symlink_alias_before_renderer_or_importer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "sermon")
            sermon_root = root / "data" / "raw" / "教会讲道"
            (sermon_root / "real-sermon").mkdir(parents=True)
            (sermon_root / "package-bound-alias").symlink_to(sermon_root / "real-sermon", target_is_directory=True)
            prepublish = Path(package["prepublish"]["path"])
            prepublish.write_text(
                prepublish.read_text(encoding="utf-8").replace(
                    "data/raw/教会讲道/sample-sermon", "data/raw/教会讲道/package-bound-alias"
                ),
                encoding="utf-8",
            )
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                return type("Result", (), {"returncode": 0, "stdout": json.dumps({"pass": True}), "stderr": ""})()

            with patch.dict(content_workflow.RAW_DIRS, {"sermon": sermon_root}), patch.object(
                content_workflow.subprocess, "run", side_effect=fake_run
            ):
                with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH.*symlink alias"):
                    content_workflow.publish(
                        "sermon", folder="package-bound-alias",
                        presentation_file=package["presentation"]["artifact"], dry_run=True,
                        publication_package=str(package_path), content_root=str(root),
                    )

            self.assertEqual(len(calls), 1, "in-root symlink alias must fail before renderer/importer")
            self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))

    def test_v13_sermon_workflow_rejects_missing_folder_before_renderer_or_importer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package = _fixture_module.PublicationPackageV13ConsumerValidationTests().build_fixture(root, "sermon")
            (root / "data" / "raw" / "教会讲道" / "sample-sermon").mkdir(parents=True)
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                return type("Result", (), {"returncode": 0, "stdout": json.dumps({"pass": True}), "stderr": ""})()

            with patch.dict(content_workflow.RAW_DIRS, {"sermon": root / "data" / "raw" / "教会讲道"}), patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH.*requires"):
                    content_workflow.publish(
                        "sermon", folder=None, presentation_file=package["presentation"]["artifact"],
                        dry_run=True, publication_package=str(package_path), content_root=str(root),
                    )
            self.assertEqual(len(calls), 1, "missing folder must fail before renderer/importer")

    def test_legacy_sermon_route_remains_unchanged_without_publication_package(self):
        calls = []
        evidence = {
            "status": "SERMON_PRESENTATION_STRUCTURE_PASS",
            "completion_ceiling": "publication_structure_ready",
            "rendered_html": {"sha256": "c" * 64},
        }

        def fake_run(command, **kwargs):
            calls.append(command)
            return type("Result", (), {"returncode": 0, "stdout": json.dumps(evidence), "stderr": ""})()

        with patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
            content_workflow.publish(
                "sermon", folder="legacy-sermon", presentation_file="/tmp/legacy-presentation.md", dry_run=True
            )
        self.assertEqual(len(calls), 2)
        self.assertIn("validate_sermon_presentation.mjs", " ".join(calls[0]))
        self.assertIn("legacy-sermon", calls[1])
        self.assertNotIn("--publication-package", calls[1])

    def test_share_presentation_path_without_package_is_blocked(self):
        with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_REQUIRED"):
            content_workflow.publish(
                "share", source_file="legacy.txt", presentation_file="/tmp/presentation.md", dry_run=True
            )

    def test_v13_workflow_publish_requires_allow_write_at_direct_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, _package, raw = self.build_share_fixture(root)
            calls = []
            with patch.dict(content_workflow.RAW_DIRS, {"share": raw}), patch.object(
                content_workflow.subprocess, "run", side_effect=lambda *args, **kwargs: calls.append(args)
            ):
                with self.assertRaisesRegex(SystemExit, "V13_WRITE_AUTHORIZATION_REQUIRED"):
                    content_workflow.publish(
                        "share", source_file="sample.txt", dry_run=False,
                        publication_package=str(package_path), content_root=str(root),
                    )
            self.assertEqual(calls, [])

    def test_v13_share_publish_dispatches_only_after_package_and_render_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_path, package, raw = self.build_share_fixture(root)
            package_evidence = {"pass": True}
            render_evidence = {
                "status": "CONTENT_PRESENTATION_STRUCTURE_PASS",
                "completion_ceiling": "publication_structure_ready",
                "rendered_html": {"sha256": "a" * 64},
            }
            calls = []

            def fake_run(command, **kwargs):
                calls.append(command)
                if "validate_publication_package_v13.py" in " ".join(command):
                    stdout = json.dumps(package_evidence)
                elif command[0] == "node":
                    stdout = json.dumps(render_evidence)
                else:
                    stdout = ""
                return type("Result", (), {"returncode": 0, "stdout": stdout, "stderr": ""})()

            with patch.dict(content_workflow.RAW_DIRS, {"share": raw}), patch.object(
                content_workflow.subprocess, "run", side_effect=fake_run
            ):
                content_workflow.publish(
                    "share", source_file="sample.txt",
                    presentation_file=package["presentation"]["artifact"], dry_run=False,
                    publication_package=str(package_path), content_root=str(root), allow_write=True,
                )
            importer_command = calls[-1]
            self.assertIn("import_shares.py", " ".join(importer_command))
            self.assertIn("--allow-write", importer_command)
            self.assertIn("--publication-package", importer_command)
            self.assertIn(str(package_path.resolve()), importer_command)
            self.assertNotIn("--dry-run", importer_command)

    def test_legacy_share_route_remains_unchanged_without_presentation_file(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
            content_workflow.publish("share", source_file="legacy.txt", dry_run=True)

        self.assertEqual(len(calls), 1)
        self.assertNotIn("--presentation-file", calls[0])
        self.assertNotIn("--publication-package", calls[0])
        self.assertIn("--source-file", calls[0])
        self.assertIn("legacy.txt", calls[0])


    def test_v13_share_workflow_rejects_nested_traversal_absolute_and_symlink_selectors_before_renderer(self):
        for selector in ("sub/sample.txt", "../sample.txt", "./sample.txt", "/tmp/sample.txt", "alias.txt", "external-alias.txt"):
            with self.subTest(selector=selector), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                package_path, package, raw = self.build_share_fixture(root)
                source = raw / "sample.txt"
                (raw / "alias.txt").symlink_to(source)
                outside = root / "outside.txt"
                outside.write_text("Outside source.", encoding="utf-8")
                (raw / "external-alias.txt").symlink_to(outside)
                calls = []

                def fake_run(command, **kwargs):
                    calls.append(command)
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps({"pass": True}), "stderr": ""})()

                values = {
                    "source_file": selector,
                    "presentation_file": package["presentation"]["artifact"],
                    "dry_run": True,
                    "publication_package": str(package_path),
                    "content_root": str(root),
                }
                with patch.dict(content_workflow.RAW_DIRS, {"share": raw}):
                    with patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
                        with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH"):
                            content_workflow.publish("share", **values)
                self.assertEqual(len(calls), 1, "invalid selector must fail before renderer/importer")
                self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))


    def test_v13_share_workflow_rejects_missing_directory_and_broken_symlink_source_before_renderer(self):
        for source_kind in ("missing", "directory", "broken_symlink"):
            with self.subTest(source_kind=source_kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                package_path, package, raw = self.build_share_fixture(root, source_kind=source_kind)
                calls = []

                def fake_run(command, **kwargs):
                    calls.append(command)
                    return type("Result", (), {"returncode": 0, "stdout": json.dumps({"pass": True}), "stderr": ""})()

                with patch.dict(content_workflow.RAW_DIRS, {"share": raw}), patch.object(
                    content_workflow.subprocess, "run", side_effect=fake_run
                ):
                    with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH"):
                        content_workflow.publish(
                            "share",
                            source_file="sample.txt",
                            presentation_file=package["presentation"]["artifact"],
                            dry_run=True,
                            publication_package=str(package_path),
                            content_root=str(root),
                        )

                self.assertEqual(len(calls), 1, "source must be rejected before renderer/importer")
                self.assertIn("validate_publication_package_v13.py", " ".join(calls[0]))


if __name__ == "__main__":
    unittest.main()
