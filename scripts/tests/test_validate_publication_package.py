from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ValidatePublicationPackageTest(unittest.TestCase):
    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[2]
        self.workspace = self.project.parent
        self.script = self.project / "scripts/validate_publication_package.py"
        self.schema = self.workspace / "workspace-control/schemas/website-publication-package-v1.schema.json"

    def _fixture(self, root: Path) -> tuple[Path, dict]:
        prepublish = root / "prepublish.md"
        chinese = root / "official.zh.txt"
        english = root / "source.en.txt"
        prepublish.write_text("# sample\n", encoding="utf-8")
        chinese.write_text("中文\n", encoding="utf-8")
        english.write_text("English\n", encoding="utf-8")
        package = {
            "interface": "website-publication-package",
            "version": "1.0",
            "content_type": "sermon",
            "prepublish": {"path": str(prepublish)},
            "official_chinese": {"path": str(chinese), "sha256": self._sha(chinese)},
            "english_source": {"path": str(english), "sha256": self._sha(english)},
            "fidelity_status": "independently_verified",
            "metadata": {
                "slug": "sample",
                "publish_date": "2026-07-19",
                "batch_id": "batch-1",
                "content_type": "sermon",
            },
            "notification_policy": "suppress",
            "archive_status": "archived",
        }
        contract = root / "contract.json"
        contract.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        return contract, package

    def _run(self, contract: Path, content_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.script),
                "--contract",
                str(contract),
                "--schema",
                str(self.schema),
                "--content-root",
                str(content_root),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_accepts_valid_package_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract, _ = self._fixture(root)
            before = sorted((p.name, p.read_bytes()) for p in root.iterdir())
            result = self._run(contract, root)
            after = sorted((p.name, p.read_bytes()) for p in root.iterdir())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, after)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["pass"])
            self.assertTrue(payload["read_only"])

    def test_rejects_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract, package = self._fixture(root)
            package["prepublish"]["path"] = str(root / "missing.md")
            contract.write_text(json.dumps(package), encoding="utf-8")
            result = self._run(contract, root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing referenced file", result.stdout)

    def test_rejects_sha_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract, package = self._fixture(root)
            Path(package["official_chinese"]["path"]).write_text("changed\n", encoding="utf-8")
            result = self._run(contract, root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("sha mismatch", result.stdout)

    def test_rejects_invalid_enum_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract, package = self._fixture(root)
            package["notification_policy"] = "send_everything"
            del package["metadata"]["slug"]
            contract.write_text(json.dumps(package), encoding="utf-8")
            result = self._run(contract, root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("metadata must include", result.stdout)
            self.assertIn("invalid notification_policy", result.stdout)

    def test_rejects_reference_outside_content_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            contract, package = self._fixture(root)
            outside = Path(outside_tmp) / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            package["prepublish"]["path"] = str(outside)
            contract.write_text(json.dumps(package), encoding="utf-8")
            result = self._run(contract, root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("reference outside content root", result.stdout)

    def test_v11_requires_and_validates_prepublish_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract, package = self._fixture(root)
            package["version"] = "1.1"
            package["prepublish"]["sha256"] = self._sha(Path(package["prepublish"]["path"]))
            contract.write_text(json.dumps(package), encoding="utf-8")
            schema = self.schema
            self.schema = self.workspace / "workspace-control/schemas/website-publication-package-v1.1.schema.json"
            try:
                result = self._run(contract, root)
                self.assertEqual(result.returncode, 0, result.stdout)
                Path(package["prepublish"]["path"]).write_text("changed\n", encoding="utf-8")
                result = self._run(contract, root)
                self.assertEqual(result.returncode, 1)
                self.assertIn("sha mismatch: prepublish", result.stdout)
            finally:
                self.schema = schema


if __name__ == "__main__":
    unittest.main()
