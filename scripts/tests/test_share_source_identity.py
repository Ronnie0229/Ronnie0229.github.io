from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.share_source_identity import (
    resolve_package_bound_share_source,
    resolve_share_source_path,
)


class ShareSourceIdentityTests(unittest.TestCase):
    def test_initial_path_resolution_requires_existing_regular_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sample.txt").write_text("source", encoding="utf-8")
            self.assertEqual(resolve_share_source_path("sample.txt", root), (root / "sample.txt").resolve(strict=True))
            with self.assertRaises((FileNotFoundError, ValueError)):
                resolve_share_source_path("missing.txt", root)
            (root / "directory.txt").mkdir()
            with self.assertRaises((OSError, ValueError)):
                resolve_share_source_path("directory.txt", root)
            (root / "broken.txt").symlink_to(root / "missing-target.txt")
            with self.assertRaises(ValueError):
                resolve_share_source_path("broken.txt", root)

    def test_package_bound_helper_requires_expected_source_argument_and_value(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sample.txt").write_text("source", encoding="utf-8")
            with self.assertRaises(TypeError):
                resolve_package_bound_share_source("sample.txt", root)
            with self.assertRaisesRegex(ValueError, "missing or invalid"):
                resolve_package_bound_share_source("sample.txt", root, expected_source=None)
            with self.assertRaisesRegex(ValueError, "missing or invalid"):
                resolve_package_bound_share_source("sample.txt", root, expected_source="")

    def test_package_bound_helper_accepts_only_exact_existing_canonical_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.txt"
            source.write_text("source", encoding="utf-8")
            self.assertEqual(
                resolve_package_bound_share_source(
                    "sample.txt", root, expected_source="data/raw/分享/sample.txt"
                ),
                source.resolve(strict=True),
            )
            for expected in (
                "../data/raw/分享/sample.txt",
                "data/raw/分享/sub/sample.txt",
                "data/raw/other/sample.txt",
                "data/raw/分享/./sample.txt",
                str(source),
            ):
                with self.subTest(expected=expected), self.assertRaises(ValueError):
                    resolve_package_bound_share_source("sample.txt", root, expected_source=expected)

    def test_package_bound_helper_rejects_selector_aliases_and_missing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.txt"
            source.write_text("source", encoding="utf-8")
            for selector in ("sub/sample.txt", "../sample.txt", "./sample.txt", str(source), "sample\\sample.txt"):
                with self.subTest(selector=selector), self.assertRaises(ValueError):
                    resolve_package_bound_share_source(
                        selector, root, expected_source="data/raw/分享/sample.txt"
                    )
            with self.assertRaises((FileNotFoundError, ValueError)):
                resolve_package_bound_share_source(
                    "missing.txt", root, expected_source="data/raw/分享/missing.txt"
                )


if __name__ == "__main__":
    unittest.main()
