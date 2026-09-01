from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT.parent
SCRIPT = PROJECT / "scripts/run_fixed_publication_dry_run.py"
SPEC = importlib.util.spec_from_file_location("run_fixed_publication_dry_run", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FixedPublicationDryRunTest(unittest.TestCase):
    @staticmethod
    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def fixture(self, root: Path, version: str = "1.2") -> Path:
        pre = root / "pre.md"
        zh = root / "zh.txt"
        en = root / "en.txt"
        pre.write_text("pre", encoding="utf-8")
        zh.write_text("zh", encoding="utf-8")
        en.write_text("en", encoding="utf-8")
        package = {
            "interface": "website-publication-package",
            "version": version,
            "content_type": "sermon",
            "prepublish": {"path": str(pre), "sha256": self.sha(pre)},
            "official_chinese": {"path": str(zh), "sha256": self.sha(zh)},
            "english_source": {"path": str(en), "sha256": self.sha(en)},
            "fidelity_status": "pass_by_max_audit_policy" if version == "1.2" else "independently_verified",
            "metadata": {
                "slug": "fixed-surface-sample",
                "publish_date": "2026-09-01",
                "batch_id": "fixed-surface-test",
                "content_type": "sermon",
                "website_source": "data/raw/教会讲道/fixed-surface-sample",
            },
            "notification_policy": "suppress",
            "archive_status": "archived",
        }
        contract = root / "contract.json"
        contract.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        return contract

    def workflow(self, root: Path, returncode: int = 0) -> tuple[Path, Path]:
        marker = root / "workflow-args.json"
        workflow = root / "workflow.py"
        workflow.write_text(
            "import json,sys\nfrom pathlib import Path\n"
            f"Path({str(marker)!r}).write_text(json.dumps(sys.argv[1:], ensure_ascii=False), encoding='utf-8')\n"
            f"raise SystemExit({returncode})\n",
            encoding="utf-8",
        )
        return workflow, marker

    def invoke(self, root: Path, contract: Path, workflow: Path, operation_id: str):
        return MODULE.execute_fixed_dry_run(
            contract=contract,
            content_root=root,
            operation_id=operation_id,
            output_root=root / "fixed-output",
            workflow_script=workflow,
        )

    def test_valid_v12_produces_v11_dry_run_result_and_exact_mapping(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT / "tmp") as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            workflow, marker = self.workflow(root)
            code, receipt = self.invoke(root, contract, workflow, "success-1")
            self.assertEqual(code, 0, receipt)
            self.assertEqual(receipt["status"], "dry_run_passed")
            self.assertEqual(receipt["side_effects"], [])
            args = json.loads(marker.read_text(encoding="utf-8"))
            self.assertIn("--dry-run", args)

            result_path = WORKSPACE / receipt["result_path"]
            evidence_path = WORKSPACE / receipt["evidence_path"]
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result["interface"], "website-publication-result")
            self.assertEqual(result["version"], "1.1")
            self.assertEqual(result["status"], "dry_run_passed")
            self.assertEqual(result["build"]["status"], "not_run")
            self.assertEqual(result["push_status"], "not_run")
            self.assertEqual(result["deployment_status"], "not_run")
            self.assertEqual(result["notification_status"], "not_run")
            self.assertEqual(result["evidence"]["source_contract"], receipt["source_contract"])
            self.assertEqual(result["evidence"]["acceptance_evidence_id"], "success-1")
            self.assertEqual(result["evidence"]["acceptance_evidence_path"], receipt["evidence_path"])
            self.assertEqual(result["evidence"]["acceptance_evidence_sha256"], self.sha(evidence_path))
            self.assertEqual(result["evidence"]["final_status_authority"], "个人网页项目 fixed dry-run evidence")

    def test_invalid_contract_fails_closed_before_workflow_and_writes_no_result(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT / "tmp") as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            package = json.loads(contract.read_text(encoding="utf-8"))
            package["prepublish"]["sha256"] = "0" * 64
            contract.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            workflow, marker = self.workflow(root)
            code, receipt = self.invoke(root, contract, workflow, "invalid-1")
            self.assertEqual(code, 3)
            self.assertFalse(marker.exists())
            self.assertIsNone(receipt["result_path"])
            self.assertEqual(receipt["side_effects"], [])

    def test_invalid_publish_date_schema_fails_closed_before_workflow_and_result(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT / "tmp") as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            package = json.loads(contract.read_text(encoding="utf-8"))
            package["metadata"]["publish_date"] = "NOT-A-DATE"
            contract.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
            workflow, marker = self.workflow(root)
            code, receipt = self.invoke(root, contract, workflow, "invalid-date-1")
            self.assertEqual(code, 3)
            self.assertFalse(marker.exists())
            self.assertIsNone(receipt["result_path"])
            self.assertEqual(receipt["side_effects"], [])
            result_path = root / "fixed-output" / "invalid-date-1" / "publication-result.json"
            self.assertFalse(result_path.exists())

    def test_workflow_failure_fails_closed_and_writes_no_result(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT / "tmp") as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            workflow, marker = self.workflow(root, returncode=7)
            code, receipt = self.invoke(root, contract, workflow, "workflow-fail-1")
            self.assertEqual(code, 3)
            self.assertTrue(marker.exists())
            args = json.loads(marker.read_text(encoding="utf-8"))
            self.assertIn("--dry-run", args)
            self.assertIsNone(receipt["result_path"])
            self.assertEqual(receipt["side_effects"], [])

    def test_fixed_surface_rejects_v11_without_breaking_existing_consumer_compatibility(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT / "tmp") as tmp:
            root = Path(tmp)
            contract = self.fixture(root, version="1.1")
            workflow, marker = self.workflow(root)
            code, receipt = self.invoke(root, contract, workflow, "v11-rejected-1")
            self.assertEqual(code, 2)
            self.assertEqual(receipt["error_stage"], "contract_identity")
            self.assertFalse(marker.exists())

    def test_operation_id_is_single_use(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT / "tmp") as tmp:
            root = Path(tmp)
            contract = self.fixture(root)
            workflow, _ = self.workflow(root)
            code, _ = self.invoke(root, contract, workflow, "single-use-1")
            self.assertEqual(code, 0)
            code, receipt = self.invoke(root, contract, workflow, "single-use-1")
            self.assertEqual(code, 2)
            self.assertEqual(receipt["error_stage"], "operation_id_reuse")


if __name__ == "__main__":
    unittest.main()
