from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.tests.test_validate_publication_package_v13 import PublicationPackageV13ConsumerValidationTests


WORKFLOW_SCRIPT = Path(__file__).resolve().parents[1] / "content_workflow.py"
WORKFLOW_SPEC = importlib.util.spec_from_file_location("legacy_share_content_workflow", WORKFLOW_SCRIPT)
content_workflow = importlib.util.module_from_spec(WORKFLOW_SPEC)
WORKFLOW_SPEC.loader.exec_module(content_workflow)

SCRIPT = Path(__file__).resolve().parents[1] / "import_shares.py"
SPEC = importlib.util.spec_from_file_location("v13_import_shares", SCRIPT)
import_shares = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(import_shares)


class SharePresentationImportTests(unittest.TestCase):
    def _run_import(self, root: Path, argv: list[str], raw: Path, organized: Path, posts: Path, reports: Path):
        with (
            patch.object(import_shares, "SOURCE_DIR", raw),
            patch.object(import_shares, "ORGANIZED_DIR", organized),
            patch.object(import_shares, "POSTS_DIR", posts),
            patch.object(import_shares, "REPORT_DIR", reports),
            patch("sys.argv", argv),
        ):
            import_shares.main()

    def test_direct_presentation_import_without_package_fails_closed_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            artifact = root / "presentation.md"
            artifact.write_text("## Heading\n\nA complete body.\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_REQUIRED"):
                self._run_import(root, ["import_shares.py", "--source-file", source.name,
                    "--presentation-file", str(artifact)], raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_v13_direct_import_missing_source_fails_before_output_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH"):
                self._run_import(root, ["import_shares.py", "--source-file", "sample.txt",
                    "--presentation-file", package["presentation"]["artifact"],
                    "--publication-package", str(package_path), "--content-root", str(root), "--dry-run"],
                    raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_v13_direct_import_valid_package_dry_run_passes_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            artifact = Path(package["presentation"]["artifact"])
            argv = ["import_shares.py", "--source-file", source.name,
                "--presentation-file", str(artifact), "--publication-package", str(package_path),
                "--content-root", str(root), "--title", "测试文章标题",
                "--description", "这是一段用于验证的完整文章摘要，清楚说明文章的主要内容与重点。",
                "--scripture", "", "--slug", "2026-11-17-sample-article",
                "--tags", "恩典,信心", "--author", "Ronnie", "--publish-date", "2026-11-17",
                "--dry-run"]
            self._run_import(root, argv, raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_legacy_direct_import_without_author_uses_ronnie_default(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (
                root / name for name in ("raw", "organized", "posts", "reports")
            )
            raw.mkdir()
            source = raw / "2026-11-17-legacy.txt"
            source.write_text("A legacy Share article body for dry-run compatibility.\\n", encoding="utf-8")
            self._run_import(
                root,
                ["import_shares.py", "--source-file", source.name, "--dry-run",
                 "--description", "这是一段人工撰写的摘要，用于验证旧版分享导入入口的作者默认值。",
                 "--tags", "恩典,信心"],
                raw, organized, posts, reports,
            )
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_legacy_workflow_without_author_reaches_real_importer_with_ronnie_default(self):
        from types import SimpleNamespace

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (
                root / name for name in ("raw", "organized", "posts", "reports")
            )
            raw.mkdir()
            source = raw / "2026-11-17-legacy.txt"
            source.write_text("A legacy Share article body for dry-run compatibility.\\n", encoding="utf-8")

            def invoke_real_importer(command, **kwargs):
                self.assertIn("--author", command)
                author_index = command.index("--author")
                self.assertEqual(command[author_index + 1], "Ronnie")
                with (
                    patch.object(import_shares, "SOURCE_DIR", raw),
                    patch.object(import_shares, "ORGANIZED_DIR", organized),
                    patch.object(import_shares, "POSTS_DIR", posts),
                    patch.object(import_shares, "REPORT_DIR", reports),
                    patch("sys.argv", command[1:]),
                ):
                    import_shares.main()
                return SimpleNamespace(returncode=0)

            with (
                patch.dict(content_workflow.RAW_DIRS, {"share": raw}),
                patch.object(content_workflow.subprocess, "run", side_effect=invoke_real_importer),
            ):
                content_workflow.publish(
                    "share",
                    source_file=source.name,
                    dry_run=True,
                    description="这是一段人工撰写的摘要，用于验证旧版分享导入入口的作者默认值。",
                    tags="恩典,信心",
                )

            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_legacy_workflow_preserves_explicit_author(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return type("Result", (), {"returncode": 0})()

        with patch.object(content_workflow.subprocess, "run", side_effect=fake_run):
            content_workflow.publish(
                "share",
                source_file="legacy.txt",
                dry_run=True,
                description="人工摘要",
                tags="恩典,信心",
                author="Patrick",
            )

        self.assertEqual(len(calls), 1)
        author_index = calls[0].index("--author")
        self.assertEqual(calls[0][author_index + 1], "Patrick")

    def test_v13_direct_import_rejects_unbound_artifact_before_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            alternate = root / "alternate.md"
            alternate.write_text(Path(package["presentation"]["artifact"]).read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "presentation artifact does not match package binding"):
                self._run_import(root, ["import_shares.py", "--source-file", source.name,
                    "--presentation-file", str(alternate), "--publication-package", str(package_path),
                    "--content-root", str(root), "--dry-run"], raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_v13_direct_import_rejects_package_without_presentation_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, _package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            with self.assertRaisesRegex(SystemExit, "requires --presentation-file"):
                self._run_import(root, ["import_shares.py", "--source-file", source.name,
                    "--publication-package", str(package_path), "--content-root", str(root)],
                    raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_v13_direct_import_requires_allow_write_before_any_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            with self.assertRaisesRegex(SystemExit, "V13_WRITE_AUTHORIZATION_REQUIRED"):
                self._run_import(root, ["import_shares.py", "--source-file", source.name,
                    "--presentation-file", package["presentation"]["artifact"],
                    "--publication-package", str(package_path), "--content-root", str(root)],
                    raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())

    def test_v13_direct_import_write_is_enabled_only_with_bound_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            self._run_import(root, ["import_shares.py", "--source-file", source.name,
                "--presentation-file", package["presentation"]["artifact"],
                "--publication-package", str(package_path), "--content-root", str(root), "--allow-write"],
                raw, organized, posts, reports)
            self.assertTrue(organized.exists())
            self.assertTrue(posts.exists())
            self.assertTrue((posts / "2026-11-17-sample-article.md").is_file())
            self.assertTrue(reports.exists())
            self.assertNotIn("sample.txt", (reports / "待补经文.csv").read_text(encoding="utf-8-sig"))

    def test_v13_share_without_scripture_requires_confirmed_metadata_to_create_post(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            prepublish = Path(package["prepublish"]["path"])
            prepublish.write_text(
                prepublish.read_text(encoding="utf-8").replace(
                    'metadataStatus: "confirmed"', 'metadataStatus: "needs_review"'
                ),
                encoding="utf-8",
            )
            package["prepublish"]["sha256"] = hashlib.sha256(prepublish.read_bytes()).hexdigest()
            package_path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")

            self._run_import(root, ["import_shares.py", "--source-file", source.name,
                "--presentation-file", package["presentation"]["artifact"],
                "--publication-package", str(package_path), "--content-root", str(root), "--allow-write"],
                raw, organized, posts, reports)

            self.assertTrue((organized / "2026-11-17-sample-article.md").is_file())
            self.assertFalse((posts / "2026-11-17-sample-article.md").exists())
            self.assertIn("sample.txt", (reports / "待补经文.csv").read_text(encoding="utf-8-sig"))

    def test_v13_direct_import_rejects_spoofed_metadata_before_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
            raw.mkdir()
            source = raw / "sample.txt"
            source.write_text("Source attribution.", encoding="utf-8")
            package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
            artifact = Path(package["presentation"]["artifact"])
            with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH: title"):
                self._run_import(root, ["import_shares.py", "--source-file", source.name,
                    "--presentation-file", str(artifact), "--publication-package", str(package_path),
                    "--content-root", str(root), "--title", "Spoofed title", "--dry-run"],
                    raw, organized, posts, reports)
            self.assertFalse(organized.exists())
            self.assertFalse(posts.exists())
            self.assertFalse(reports.exists())


    def test_v13_direct_import_rejects_nested_traversal_and_symlink_source_selectors(self):
        for selector_kind in ("nested", "traversal", "dot_alias", "absolute", "different_file", "internal_symlink", "external_symlink"):
            with self.subTest(selector=selector_kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                raw, organized, posts, reports = (root / name for name in ("raw", "organized", "posts", "reports"))
                raw.mkdir()
                source = raw / "sample.txt"
                source.write_text("Source attribution.", encoding="utf-8")
                package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "share")
                if selector_kind == "nested":
                    nested = raw / "sub"
                    nested.mkdir()
                    (nested / "sample.txt").write_text("Nested source.", encoding="utf-8")
                    selector = "sub/sample.txt"
                elif selector_kind == "traversal":
                    selector = "../sample.txt"
                elif selector_kind == "dot_alias":
                    selector = "./sample.txt"
                elif selector_kind == "absolute":
                    selector = str(source)
                elif selector_kind == "different_file":
                    (raw / "different.txt").write_text("Different source.", encoding="utf-8")
                    selector = "different.txt"
                elif selector_kind == "internal_symlink":
                    alias = raw / "alias.txt"
                    alias.symlink_to(source)
                    selector = alias.name
                else:
                    outside = root / "outside.txt"
                    outside.write_text("Outside source.", encoding="utf-8")
                    alias = raw / "alias.txt"
                    alias.symlink_to(outside)
                    selector = alias.name
                with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_IDENTITY_MISMATCH"):
                    self._run_import(root, ["import_shares.py", "--source-file", selector,
                        "--presentation-file", package["presentation"]["artifact"],
                        "--publication-package", str(package_path), "--content-root", str(root), "--dry-run"],
                        raw, organized, posts, reports)
                self.assertFalse(organized.exists())
                self.assertFalse(posts.exists())
                self.assertFalse(reports.exists())


if __name__ == "__main__":
    unittest.main()
