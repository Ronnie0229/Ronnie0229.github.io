from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class WritePublicationResultTest(unittest.TestCase):
    def test_writes_dry_run_result_without_false_build_success(self) -> None:
        project = Path(__file__).resolve().parents[2]
        script = project / "scripts/write_publication_result.py"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "result.json"
            result = subprocess.run([
                sys.executable, str(script), "--contract-version", "1.0", "--status", "dry_run_passed",
                "--slug", "sample", "--post-path", "src/content/posts/sample.md",
                "--deployment-status", "not_run", "--notification-status", "suppressed",
                "--output", str(output),
            ], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["interface"], "website-publication-result")
            self.assertEqual(payload["status"], "dry_run_passed")
            self.assertFalse(payload["build"]["passed"])
            self.assertEqual(payload["deployment_status"], "not_run")

    def test_writes_v11_with_atomic_evidence_and_enums(self) -> None:
        project = Path(__file__).resolve().parents[2]
        script = project / "scripts/write_publication_result.py"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "result.json"
            result = subprocess.run([
                sys.executable, str(script), "--contract-version", "1.1",
                "--status", "dry_run_passed", "--slug", "sample",
                "--post-path", "src/content/posts/sample.md",
                "--processed-path", "data/processed/sample.md",
                "--push-status", "not_run", "--deployment-status", "not_run",
                "--notification-status", "suppressed", "--source-contract", "contract.json",
                "--output", str(output),
            ], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["version"], "1.1")
            self.assertEqual(payload["build"]["status"], "not_run")
            self.assertTrue(payload["evidence"]["atomic_write"])
            self.assertEqual(payload["evidence"]["source_contract"], "contract.json")
            self.assertFalse(any(path.suffix == ".tmp" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
