from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import import_sermons
from scripts.tests.test_validate_publication_package_v13 import PublicationPackageV13ConsumerValidationTests


class SermonSourceIdentityTests(unittest.TestCase):
    def build_tree(self, root: Path):
        sermon_root = root / "data" / "raw" / "教会讲道"
        real = sermon_root / "real-sermon"
        other = sermon_root / "other-sermon"
        real.mkdir(parents=True)
        other.mkdir()
        alias = sermon_root / "package-bound-alias"
        alias.symlink_to(real, target_is_directory=True)
        return sermon_root, real, other, alias

    def test_expected_canonical_folder_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sermon_root, real, _other, _alias = self.build_tree(root)
            with patch.object(import_sermons, "ROOT", root), patch.object(import_sermons, "SOURCE_DIR", sermon_root):
                self.assertEqual(
                    import_sermons.resolve_folder("real-sermon", str(real.resolve())),
                    real.resolve(),
                )

    def test_in_root_symlink_alias_is_rejected_with_expected_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sermon_root, real, _other, alias = self.build_tree(root)
            with patch.object(import_sermons, "ROOT", root), patch.object(import_sermons, "SOURCE_DIR", sermon_root):
                with self.assertRaisesRegex(SystemExit, "SERMON_SOURCE_IDENTITY_MISMATCH.*symlink"):
                    import_sermons.resolve_folder(alias.name, str(real.resolve()))

    def test_different_in_root_real_folder_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sermon_root, real, other, _alias = self.build_tree(root)
            with patch.object(import_sermons, "ROOT", root), patch.object(import_sermons, "SOURCE_DIR", sermon_root):
                with self.assertRaisesRegex(SystemExit, "SERMON_SOURCE_IDENTITY_MISMATCH"):
                    import_sermons.resolve_folder(other.name, str(real.resolve()))

    def test_importer_entry_rejects_alias_before_presentation_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sermon_root, real, _other, alias = self.build_tree(root)
            presentation = root / "presentation.md"
            presentation.write_text("## Heading\n\nBody.\n", encoding="utf-8")
            args = SimpleNamespace(
                folder=alias.name,
                expected_source_folder=str(real.resolve()),
                presentation_file=str(presentation),
                dry_run=True,
                description=None,
                tags=None,
                update_existing=False,
            )
            with (
                patch.object(import_sermons, "ROOT", root),
                patch.object(import_sermons, "SOURCE_DIR", sermon_root),
                patch.object(import_sermons, "parse_args", return_value=args),
                patch.object(import_sermons.subprocess, "run") as run,
            ):
                with self.assertRaisesRegex(SystemExit, "SERMON_SOURCE_IDENTITY_MISMATCH.*symlink"):
                    import_sermons.main()
                run.assert_not_called()

    def test_package_aware_iteration_skips_alias_and_selects_canonical_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sermon_root = root / "data" / "raw" / "教会讲道"
            canonical = sermon_root / "20261118_测试讲道_Patrick"
            canonical.mkdir(parents=True)
            (canonical / "source.txt").write_text("source", encoding="utf-8")
            (sermon_root / "000-alias").symlink_to(canonical, target_is_directory=True)
            presentation = root / "presentation.md"
            presentation.write_text("## Heading\n\nBody.\n", encoding="utf-8")
            args = SimpleNamespace(
                folder=canonical.name,
                expected_source_folder=str(canonical.resolve()),
                publication_package=None,
                content_root=None,
                allow_write=True,
                presentation_file=str(presentation),
                dry_run=False,
                description=None,
                tags=None,
                update_existing=False,
            )
            selected = []

            def capture_source(folder):
                selected.append(folder.name)
                return folder / "source.txt"

            markdown = '---\ntitle: "测试标题"\n---\n\n正文。\n'
            with (
                patch.object(import_sermons, "ROOT", root),
                patch.object(import_sermons, "SOURCE_DIR", sermon_root),
                patch.object(import_sermons, "ORGANIZED_DIR", root / "processed"),
                patch.object(import_sermons, "POSTS_DIR", root / "posts"),
                patch.object(import_sermons, "REPORT_DIR", root / "reports"),
                patch.object(import_sermons, "parse_args", return_value=args),
                patch.object(import_sermons, "validate_v13_import_identity"),
                patch.object(import_sermons.subprocess, "run", return_value=SimpleNamespace(
                    returncode=0,
                    stdout='{"status":"SERMON_PRESENTATION_STRUCTURE_PASS","completion_ceiling":"publication_structure_ready"}',
                    stderr="",
                )),
                patch.object(import_sermons, "choose_source_file", side_effect=capture_source),
                patch.object(import_sermons, "file_sha256", return_value="a" * 64),
                patch.object(import_sermons, "markdown_for", return_value=("2026-11-18", markdown)),
                patch.object(import_sermons, "folder_meta", return_value=("20261118", "测试讲道", "Patrick")),
                patch.object(import_sermons, "title_parts", return_value=("", "测试讲道")),
                patch.object(import_sermons, "category_for", return_value="教会讲道"),
                patch.object(import_sermons, "target_paths_for", return_value=(
                    "2026-11-18-test-sermon", root / "processed.md", root / "post.md"
                )),
                patch.object(import_sermons, "ensure_safe_targets"),
                patch.object(import_sermons, "read_sermon_registry", return_value={}),
            ):
                import_sermons.main()

            self.assertEqual(selected, [canonical.name])
            self.assertTrue((root / "processed.md").is_file())
            self.assertTrue((root / "post.md").is_file())
            self.assertTrue((root / "reports" / "sermon-import-registry.csv").is_file())

    def build_v13_sermon_identity(self, root: Path):
        package_path, package = PublicationPackageV13ConsumerValidationTests().build_fixture(root, "sermon")
        sermon_root = root / "data" / "raw" / "教会讲道"
        source_folder = sermon_root / "sample-sermon"
        source_folder.mkdir(parents=True)
        (source_folder / "source.txt").write_text("Sermon source.", encoding="utf-8")
        args = SimpleNamespace(
            publication_package=str(package_path),
            content_root=str(root),
            expected_source_folder=str(source_folder.resolve()),
            allow_write=True,
        )
        return args, package, sermon_root, source_folder

    def test_v13_sermon_direct_import_requires_allow_write_before_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args, package, sermon_root, source_folder = self.build_v13_sermon_identity(root)
            args.folder = source_folder.name
            args.presentation_file = package["presentation"]["artifact"]
            args.dry_run = False
            args.description = None
            args.tags = None
            args.update_existing = False
            args.allow_write = False
            with (
                patch.object(import_sermons, "ROOT", root),
                patch.object(import_sermons, "SOURCE_DIR", sermon_root),
                patch.object(import_sermons, "parse_args", return_value=args),
                patch.object(import_sermons.subprocess, "run", return_value=SimpleNamespace(
                    returncode=0, stdout=json.dumps({"pass": True}), stderr=""
                )) as run,
            ):
                with self.assertRaisesRegex(SystemExit, "V13_WRITE_AUTHORIZATION_REQUIRED"):
                    import_sermons.main()
                run.assert_called_once()

    def test_v13_sermon_importer_requires_package_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args, package, sermon_root, source_folder = self.build_v13_sermon_identity(root)
            args.publication_package = None
            with patch.object(import_sermons, "ROOT", root), patch.object(import_sermons, "SOURCE_DIR", sermon_root):
                with self.assertRaisesRegex(SystemExit, "V13_PACKAGE_REQUIRED"):
                    import_sermons.validate_v13_import_identity(
                        args, source_folder, Path(package["presentation"]["artifact"])
                    )

    def test_v13_sermon_importer_revalidates_package_source_and_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args, package, sermon_root, source_folder = self.build_v13_sermon_identity(root)
            validation = SimpleNamespace(returncode=0, stdout=json.dumps({"pass": True}), stderr="")
            artifact = Path(package["presentation"]["artifact"])
            with (
                patch.object(import_sermons, "ROOT", root),
                patch.object(import_sermons, "SOURCE_DIR", sermon_root),
                patch.object(import_sermons.subprocess, "run", return_value=validation) as run,
            ):
                import_sermons.validate_v13_import_identity(args, source_folder, artifact)
            self.assertIn("validate_publication_package_v13.py", " ".join(run.call_args.args[0]))

    def test_v13_sermon_importer_rejects_unbound_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args, package, sermon_root, source_folder = self.build_v13_sermon_identity(root)
            alternate = root / "alternate.md"
            alternate.write_text(Path(package["presentation"]["artifact"]).read_text(encoding="utf-8"), encoding="utf-8")
            validation = SimpleNamespace(returncode=0, stdout=json.dumps({"pass": True}), stderr="")
            with (
                patch.object(import_sermons, "ROOT", root),
                patch.object(import_sermons, "SOURCE_DIR", sermon_root),
                patch.object(import_sermons.subprocess, "run", return_value=validation),
            ):
                with self.assertRaisesRegex(SystemExit, "presentation artifact does not match package binding"):
                    import_sermons.validate_v13_import_identity(args, source_folder, alternate)

    def test_v13_sermon_importer_rejects_wrong_package_bound_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args, package, sermon_root, source_folder = self.build_v13_sermon_identity(root)
            other = sermon_root / "other-sermon"
            other.mkdir()
            validation = SimpleNamespace(returncode=0, stdout=json.dumps({"pass": True}), stderr="")
            with (
                patch.object(import_sermons, "ROOT", root),
                patch.object(import_sermons, "SOURCE_DIR", sermon_root),
                patch.object(import_sermons.subprocess, "run", return_value=validation),
            ):
                with self.assertRaisesRegex(SystemExit, "SERMON_SOURCE_IDENTITY_MISMATCH"):
                    import_sermons.validate_v13_import_identity(args, other, Path(package["presentation"]["artifact"]))


if __name__ == "__main__":
    unittest.main()
