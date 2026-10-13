import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read_aloud_new_post_delivery as delivery
import read_aloud_workflow as wf
from read_aloud_new_post_reconcile import SCHEMA


class NewPostMediaDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", self.repo.as_posix()], check=True)
        self.post = "src/content/posts/test.md"
        (self.repo / "src/content/posts").mkdir(parents=True)
        raw = b'---\narticleId: "post-demo"\ndate: 2026-10-11\ntitle: "Demo"\n---\nBody.\n'
        (self.repo / self.post).write_bytes(raw)
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.email=test@example.org",
                        "-c", "user.name=Tester", "commit", "-qm", "post"], check=True)
        self.commit = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        (self.runtime / "new-post-automation-selector.json").write_text(json.dumps({
            "schema": SCHEMA, "enabled": True, "last_processed_commit": self.commit,
            "authorization_ref": "auto-published", "allow_media_delivery": True,
        }))
        self.wav = self.runtime / "artifact-cache/demo.bin"
        self.wav.parent.mkdir()
        self.wav.write_bytes(b"demo")
        self.mp3 = self.runtime / "delivery-cache/demo.mp3"
        self.mp3.parent.mkdir()
        self.mp3.write_bytes(b"mp3")
        sha = hashlib.sha256(b"render text").hexdigest()
        self.workflow = wf.start_workflow(
            self.runtime, authorization_ref="auto-published", generation_epoch="epoch",
            operation_id="operation", article_id="post-demo", render_sha256=sha,
            render_ref="render.txt", review_policy="AUTO_TECHNICAL_QC",
        )
        self.workflow["state"] = "AUDIO_READY_PENDING_PUBLICATION_GATE"
        self.workflow["auto_technical_qc"] = {"status": "PASS"}
        self.workflow["artifact"] = {"cache_name": "demo.bin", "artifact_sha256": hashlib.sha256(b"demo").hexdigest()}
        self.workflow["delivery"] = {"absolute_path": str(self.mp3), "sha256": hashlib.sha256(b"mp3").hexdigest(), "bytes": 3}
        wf._persist(self.runtime, self.workflow)
        self.intake_dir = self.runtime / "new-post-intake"
        self.intake_dir.mkdir()
        self.intake = self.intake_dir / "entry.json"
        self.intake.write_text(json.dumps({
            "status": "S4_WORKFLOW_REGISTERED", "authorization_ref": "auto-published",
            "workflow_id": self.workflow["workflow_id"],
            "post": {"post_path": self.post, "source_commit": self.commit,
                     "article_id": "post-demo", "post_sha256": hashlib.sha256(raw).hexdigest()},
        }))

    def tearDown(self):
        self.temp.cleanup()

    def test_success_reconciles_nas_r2_and_no_repeat(self):
        fake_nas = {"verified": True, "master_path": "/fake/master.wav"}
        fake_r2 = {"verified": True, "url": "https://audio.ronniecross.com/audio/articles/post-demo/article.mp3"}
        with patch.object(delivery, "archive_wav", return_value=fake_nas) as nas, patch.object(delivery, "upload_r2", return_value=fake_r2) as r2:
            result = delivery.deliver_one(self.repo, self.runtime)
            self.assertEqual(result["status"], "MEDIA_READY_PENDING_WEBSITE_RELEASE")
            self.assertEqual(delivery.deliver_one(self.repo, self.runtime), None)
            nas.assert_called_once()
            r2.assert_called_once()
        state = wf.workflow_status(self.runtime, self.workflow["workflow_id"])
        self.assertEqual(state["r2_delivery"]["url"], fake_r2["url"])

    def test_not_authorized_to_deliver_is_noop(self):
        config = self.runtime / "new-post-automation-selector.json"
        payload = json.loads(config.read_text())
        payload["allow_media_delivery"] = False
        config.write_text(json.dumps(payload))
        with patch.object(delivery, "archive_wav") as nas:
            self.assertIsNone(delivery.deliver_one(self.repo, self.runtime))
            nas.assert_not_called()

    def test_frozen_source_drift_fail_closed(self):
        item = json.loads(self.intake.read_text())
        item["post"]["post_sha256"] = "0" * 64
        self.intake.write_text(json.dumps(item))
        with self.assertRaises(delivery.ReadyDeliveryError):
            delivery.deliver_one(self.repo, self.runtime)


if __name__ == "__main__":
    unittest.main()
