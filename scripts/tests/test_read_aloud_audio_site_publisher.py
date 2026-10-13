from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read_aloud_audio_site_publisher as publisher
import read_aloud_audio_release_verifier as verifier
import read_aloud_s4_runner as s4
import read_aloud_workflow as wf
from read_aloud_new_post_reconcile import SCHEMA as SELECTOR_SCHEMA
from read_aloud_publication_lock import (
    SCHEMA as RECEIPT_SCHEMA, publication_lock, record_pending_under_lock,
    mark_previous_verified_under_lock, last_receipt,
)


class SitePublisherIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "site"
        self.repo.mkdir()
        self.remote = self.root / "origin.git"
        subprocess.run(["git", "init", "--bare", "-q", str(self.remote)], check=True)
        self.git("init", "-q", "-b", "main")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("config", "user.name", "Audio Fixture")
        self.git("config", "user.email", "audio@test.example")
        (self.repo / ".gitignore").write_text("dist/\n")
        self.relative = "src/content/posts/test.md"
        self.post = self.repo / self.relative
        self.post.parent.mkdir(parents=True)
        self.post.write_text('---\narticleId: "post-demo"\ntitle: "Demo"\ndate: 2026-10-11\n---\n\n正文。\n')
        self.sha = hashlib.sha256(self.post.read_bytes()).hexdigest()
        self.git("add", ".")
        self.git("commit", "-qm", "original article")
        self.git("push", "-q", "origin", "main")
        self.original_commit = self.git("rev-parse", "HEAD")
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        (self.runtime / "new-post-automation-selector.json").write_text(json.dumps({
            "schema": SELECTOR_SCHEMA, "enabled": True,
            "last_processed_commit": self.original_commit,
            "authorization_ref": "test-authority",
            "allow_unattended_publication": True,
            "article_audio_publish_nonoverlap": True
        }))
        self.url = "https://audio.ronniecross.com/audio/articles/post-demo/article.mp3"
        page = self.repo / "dist" / "posts" / "test" / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text(f"<article><audio src='{self.url}'></audio></article>")
        self.workflow = wf.start_workflow(
            self.runtime, authorization_ref="test-authority",
            generation_epoch="test-epoch", operation_id="test-operation",
            article_id="post-demo", render_sha256="b" * 64, render_ref="render.txt",
            review_policy="AUTO_TECHNICAL_QC")
        self.workflow["state"] = "AUDIO_READY_PENDING_PUBLICATION_GATE"
        self.workflow["auto_technical_qc"] = {"status": "PASS"}
        self.workflow["artifact"] = {"artifact_sha256": "a" * 64}
        self.workflow["delivery"] = {"sha256": "c" * 64, "bytes": 3}
        self.workflow["nas_archive"] = {"verified": True, "master_path": "/mock.wav"}
        self.workflow["r2_delivery"] = {"verified": True, "url": self.url}
        wf._persist(self.runtime, self.workflow)
        idir = self.runtime / "new-post-intake"
        idir.mkdir()
        self.intake = idir / "record.json"
        self.intake.write_text(json.dumps({
            "status": "MEDIA_READY_PENDING_WEBSITE_RELEASE",
            "authorization_ref": "test-authority", "workflow_id": self.workflow["workflow_id"],
            "audio_url": self.url,
            "post": {"post_path": self.relative, "article_id": "post-demo",
                     "post_sha256": self.sha, "source_commit": self.original_commit},
        }))
        # Explicitly verified preceding release baseline, never assume from HTTP 200.
        with publication_lock(self.runtime):
            record_pending_under_lock(self.runtime, {
                "schema": RECEIPT_SCHEMA, "kind": "ARTICLE",
                "commit": self.original_commit,
                "publication_state": "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY",
            })
            mark_previous_verified_under_lock(self.runtime, self.original_commit)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args],
                                       text=True, stderr=subprocess.STDOUT).strip()

    def _publish(self):
        with patch.object(publisher, "deployed_sha", return_value=self.original_commit), \
             patch.object(publisher, "sha_file", return_value="a" * 64), \
             patch.object(publisher, "verify_r2", return_value=True):
            return publisher.publish_one(self.repo, self.runtime,
                                         allow_test_repo=True, build=False, push=True)

    def test_exact_audio_only_commit_and_async_readback(self):
        result = self._publish()
        self.assertEqual(result["status"], "AUDIO_RELEASE_PENDING_VERIFY")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.git("rev-parse", "refs/remotes/origin/main"))
        self.assertEqual(self.git("show", "--pretty=format:", "--name-only", "HEAD"), self.relative)
        self.assertIn(f'audioUrl: "{self.url}"', self.post.read_text())
        pending = last_receipt(self.runtime)
        self.assertEqual(pending["kind"], "AUDIO_ONLY_UPDATE")
        self.assertEqual(pending["notification_sent_count"], 0)
        self.assertEqual(pending["publication_state"], "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY")
        with patch.object(verifier, "deployed_sha", return_value=result["website_commit"]), \
             patch.object(verifier, "_site_page", return_value=f'<audio src="{self.url}"></audio>'), \
             patch.object(verifier, "_email_zero_verified", return_value=True), \
             patch.object(verifier, "verify_r2", return_value=True):
            done = verifier.verify_one(self.runtime)
        self.assertEqual(done["status"], "COMPLETE")
        self.assertEqual(last_receipt(self.runtime)["publication_state"], "VERIFIED")
        self.assertEqual(wf.workflow_status(self.runtime, self.workflow["workflow_id"])["state"], "COMPLETE")

    def test_crash_after_audio_push_reconstructs_receipt_without_second_commit(self):
        done = self._publish()
        post_commit = done['website_commit']
        # Simulate crash after successful push, before durable receipt/intake update.
        receipt_path = self.runtime / 'website-publication/last_website_release.json'
        previous = last_receipt(self.runtime)
        previous['publication_state'] = 'VERIFIED'
        previous['kind'] = 'ARTICLE'
        previous['commit'] = self.original_commit
        receipt_path.write_text(json.dumps(previous))
        entry = json.loads(self.intake.read_text())
        entry['status'] = 'MEDIA_READY_PENDING_WEBSITE_RELEASE'
        entry.pop('website_commit', None)
        self.intake.write_text(json.dumps(entry))
        with patch.object(publisher, 'sha_file', return_value='a'*64), \
             patch.object(publisher, 'verify_r2', return_value=True):
            with self.assertRaises(publisher.AudioPublicationError) as blocked:
                publisher.publish_one(self.repo, self.runtime, allow_test_repo=True, build=False, push=True)
        self.assertIn('SOURCE_POST_SHA_DRIFT', str(blocked.exception))
        self.assertEqual(self.git('rev-parse', 'HEAD'), post_commit)
        self.assertEqual(last_receipt(self.runtime)['commit'], self.original_commit)

    def test_previous_release_pending_does_not_change_website(self):
        with publication_lock(self.runtime):
            # User's previous release not yet verified: recreate pending receipt state.
            from read_aloud_s4_runner import atomic_write_json
            p = self.runtime / "website-publication" / "last_website_release.json"
            payload = last_receipt(self.runtime)
            payload["publication_state"] = "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY"
            atomic_write_json(p, payload)
        with patch.object(publisher, "deployed_sha", return_value=self.original_commit), \
             patch.object(publisher, "sha_file", return_value="a" * 64), \
             patch.object(publisher, "verify_r2", return_value=True):
            self.assertIsNone(publisher.publish_one(self.repo, self.runtime,
                                                    allow_test_repo=True, build=False, push=True))
        self.assertEqual(self.git("rev-parse", "HEAD"), self.original_commit)
        self.assertNotIn("audioUrl", self.post.read_text())


if __name__ == "__main__":
    unittest.main()
