from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ConsumePublicationPackageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[2]
        self.workspace = self.project.parent
        self.script = self.project / "scripts/consume_publication_package.py"
        self.validator = self.project / "scripts/validate_publication_package.py"
        self.schema = self.workspace / "workspace-control/schemas/website-publication-package-v1.1.schema.json"

    @staticmethod
    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def fixture(self, root: Path) -> Path:
        pre = root / "pre.md"
        zh = root / "zh.txt"
        en = root / "en.txt"
        for path, text in ((pre, "pre"), (zh, "zh"), (en, "en")):
            path.write_text(text, encoding="utf-8")
        package = {
            "interface": "website-publication-package",
            "version": "1.1",
            "content_type": "sermon",
            "prepublish": {"path": str(pre), "sha256": self.sha(pre)},
            "official_chinese": {"path": str(zh), "sha256": self.sha(zh)},
            "english_source": {"path": str(en), "sha256": self.sha(en)},
            "fidelity_status": "independently_verified",
            "metadata": {
                "slug": "sample",
                "publish_date": "2026-07-20",
                "batch_id": "batch",
                "content_type": "sermon",
                "website_source": "data/raw/教会讲道/sample",
            },
            "notification_policy": "suppress",
            "archive_status": "archived",
        }
        contract = root / "contract.json"
        contract.write_text(json.dumps(package), encoding="utf-8")
        return contract

    def invoke(self, contract: Path, root: Path, mode: str, workflow: Path | None = None, allow_write: bool = False):
        command = [
            sys.executable, str(self.script), "--contract", str(contract),
            "--schema", str(self.schema), "--content-root", str(root),
            "--validator-script", str(self.validator), "--mode", mode,
        ]
        if workflow:
            command.extend(["--workflow-script", str(workflow)])
        if allow_write:
            command.append("--allow-write")
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_plan_validates_without_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            result = self.invoke(contract, root, "plan")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["validation_passed"])
            self.assertIsNone(payload["command"])

    def test_invalid_contract_blocks_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            package = json.loads(contract.read_text())
            package["prepublish"]["sha256"] = "0" * 64
            contract.write_text(json.dumps(package), encoding="utf-8")
            marker = root / "called"
            workflow = root / "workflow.py"
            workflow.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('called')\n", encoding="utf-8")
            result = self.invoke(contract, root, "dry-run", workflow)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(marker.exists())

    def test_dry_run_calls_workflow_with_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            output = root / "args.json"
            workflow = root / "workflow.py"
            workflow.write_text(
                "import json,sys\nfrom pathlib import Path\n"
                f"Path({str(output)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n",
                encoding="utf-8",
            )
            result = self.invoke(contract, root, "dry-run", workflow)
            self.assertEqual(result.returncode, 0, result.stderr)
            args = json.loads(output.read_text())
            self.assertIn("--dry-run", args)
            self.assertIn("data/raw/教会讲道/sample", args)

    def test_publish_requires_explicit_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            result = self.invoke(contract, root, "publish")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires --allow-write", result.stderr)

    def test_share_contract_passes_metadata_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            package = json.loads(contract.read_text())
            package["content_type"] = "share"
            package["metadata"] = {
                "slug": "prepublish-slug",
                "website_slug": "2026-07-23-obey-christ-commands",
                "topic_slug": "obey-christ-commands",
                "publish_date": "2026-07-23",
                "batch_id": "batch",
                "content_type": "share",
                "website_source": "20260723_我们真能遵行基督的命令吗_Ronnie_中文.txt",
                "title": "我们真能遵行基督的命令吗？",
                "scripture": "马太福音 5:17-20",
                "description": "本文说明信徒不是靠自己守全律法，而是在基督里蒙恩并学习真实顺服。",
                "tags": ["顺服", "律法", "恩典"],
            }
            contract.write_text(json.dumps(package), encoding="utf-8")
            output = root / "args.json"
            workflow = root / "workflow.py"
            workflow.write_text(
                "import json,sys\nfrom pathlib import Path\n"
                f"Path({str(output)!r}).write_text(json.dumps(sys.argv[1:], ensure_ascii=False), encoding='utf-8')\n",
                encoding="utf-8",
            )
            result = self.invoke(contract, root, "dry-run", workflow)
            self.assertEqual(result.returncode, 0, result.stderr)
            args = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("--source-file", args)
            self.assertIn("--title", args)
            self.assertIn("我们真能遵行基督的命令吗？", args)
            self.assertIn("--scripture", args)
            self.assertIn("马太福音 5:17-20", args)
            self.assertIn("--slug", args)
            self.assertIn("2026-07-23-obey-christ-commands", args)
            self.assertIn("--tags", args)
            self.assertIn("顺服,律法,恩典", args)


if __name__ == "__main__":
    unittest.main()
