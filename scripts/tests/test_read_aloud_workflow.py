#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import read_aloud_s4_runner as s4
import read_aloud_workflow as wf


class DurableWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "runtime"
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir(parents=True)
        self.render = self.project / "render.txt"
        self.render.write_text("测试文本\n", encoding="utf-8")
        self.render_sha = hashlib.sha256(self.render.read_bytes()).hexdigest()
        self.kw = dict(
            authorization_ref="auth-a1",
            generation_epoch="epoch-a1",
            operation_id="op-a1",
            article_id="post-test",
            render_sha256=self.render_sha,
            render_ref="render.txt",
        )
        self.old_project_root = s4.PROJECT_ROOT
        s4.PROJECT_ROOT = self.project

    def tearDown(self) -> None:
        s4.PROJECT_ROOT = self.old_project_root
        self.tmp.cleanup()

    def start(self):
        return wf.start_workflow(self.root, **self.kw)

    def test_start_is_idempotent_and_machine_readable(self):
        a = self.start()
        b = self.start()
        self.assertEqual(a["workflow_id"], b["workflow_id"])
        self.assertEqual(b["state"], "RENDER_READY")
        self.assertTrue(b["automatic_action_available"])
        self.assertFalse(b["operator_or_human_required"])

    def test_start_identity_conflict_fails_closed(self):
        a = self.start()
        path = self.root / "workflows" / f"{a['workflow_id']}.json"
        data = json.loads(path.read_text())
        data["render_ref"] = "other.txt"
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(wf.WorkflowError):
            self.start()

    def test_tick_submits_and_detaches_worker_without_waiting(self):
        started = self.start()
        result = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 4242)
        self.assertEqual(result["state"], "TTS_RUNNING")
        self.assertEqual(result["worker_pid"], 4242)
        self.assertIsNotNone(result["s4_job_id"])
        job = s4.status(self.root, result["s4_job_id"])
        self.assertEqual(job["status"], "QUEUED")

    def test_tick_detects_terminal_pass_and_verifies_cached_wav(self):
        started = self.start()
        current = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 4242)
        job_path = self.root / "jobs" / f"{current['s4_job_id']}.json"
        job = json.loads(job_path.read_text())
        wav = b"RIFF-test-audio"
        sha = hashlib.sha256(wav).hexdigest()
        cache_name = f"{current['s4_job_id']}.bin"
        cache = self.root / "artifact-cache" / cache_name
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(wav)
        job["status"] = "TERMINAL_PASS"
        job["artifact"] = {
            "artifact_ref": "voice-ai-artifact:test",
            "artifact_sha256": sha,
            "cache_name": cache_name,
            "verified": True,
        }
        job_path.write_text(json.dumps(job), encoding="utf-8")
        result = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 9999)
        self.assertEqual(result["state"], "WAV_VERIFIED")
        self.assertEqual(result["artifact"]["artifact_sha256"], sha)
        self.assertEqual(result["artifact"]["bytes"], len(wav))
        self.assertEqual(result["next_action"], "TECHNICAL_QC")
        self.assertTrue(result["automatic_action_available"])
        self.assertFalse(result["implementation_pending"])

    def test_wav_verified_tick_runs_qc_encodes_mp3_and_stops_for_human(self):
        started = self.start()
        current = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 4242)
        job_path = self.root / "jobs" / f"{current['s4_job_id']}.json"
        job = json.loads(job_path.read_text())

        wav = self.root / "artifact-cache" / f"{current['s4_job_id']}.bin"
        wav.parent.mkdir(parents=True, exist_ok=True)
        import subprocess
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
                "-ac", "1", "-ar", "24000", "-c:a", "pcm_f32le",
                "-f", "wav", str(wav),
            ],
            check=True,
        )
        sha = hashlib.sha256(wav.read_bytes()).hexdigest()
        job["status"] = "TERMINAL_PASS"
        job["artifact"] = {
            "artifact_ref": "voice-ai-artifact:test",
            "artifact_sha256": sha,
            "cache_name": wav.name,
            "verified": True,
        }
        job_path.write_text(json.dumps(job), encoding="utf-8")

        verified = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 9999)
        self.assertEqual(verified["state"], "WAV_VERIFIED")

        result = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 9999)
        self.assertEqual(result["state"], "WAIT_HUMAN_LISTENING")
        self.assertTrue(result["operator_or_human_required"])
        self.assertFalse(result["automatic_action_available"])
        self.assertEqual(result["technical_qc"]["wav_full_decode"], "PASS")
        self.assertEqual(result["technical_qc"]["mp3_full_decode"], "PASS")
        mp3 = Path(result["delivery"]["absolute_path"])
        self.assertTrue(mp3.is_file())
        self.assertEqual(hashlib.sha256(mp3.read_bytes()).hexdigest(), result["delivery"]["sha256"])

    def test_cleanup_gate_requires_all_closure_checks_and_repair_support(self):
        started = self.start()
        self.assertEqual(started["cleanup"]["status"], "NOT_ELIGIBLE")

        current = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 4242)
        job_path = self.root / "jobs" / f"{current['s4_job_id']}.json"
        job = json.loads(job_path.read_text())
        wav_bytes = b"RIFF-repair-support"
        wav_sha = hashlib.sha256(wav_bytes).hexdigest()
        cache = self.root / "artifact-cache" / f"{current['s4_job_id']}.bin"
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(wav_bytes)
        job["status"] = "TERMINAL_PASS"
        job["artifact"] = {
            "artifact_ref": "voice-ai-artifact:test",
            "artifact_sha256": wav_sha,
            "cache_name": cache.name,
            "verified": True,
        }
        job_path.write_text(json.dumps(job), encoding="utf-8")
        ready = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 9999)

        support = {
            "schema": "ronniecross-readaloud-repair-support/v1",
            "article_id": "post-test",
            "workflow_id": started["workflow_id"],
            "request_id": ready["request_id"],
            "generation_epoch": "epoch-a1",
            "render_sha256": self.render_sha,
            "final_wav_sha256": wav_sha,
            "sample_rate_hz": 24000,
            "total_frames": 24000,
            "exact_text_to_chunk_alignment": False,
            "chunks": [{
                "chunk_index": 0,
                "start_frame": 0,
                "end_frame_exclusive": 24000,
                "frames": 24000,
            }],
        }
        support_path = self.project / "repair-support.json"
        support_path.write_text(json.dumps(support), encoding="utf-8")
        attached = wf.attach_repair_support(self.root, started["workflow_id"], support_path)
        self.assertTrue(attached["repair_support"]["complete"])
        self.assertEqual(attached["cleanup"]["status"], "NOT_ELIGIBLE")

        attached["human_listening"] = {"status": "PASS"}
        attached["nas_archive"] = {"verified": True}
        attached["r2_delivery"] = {"verified": True}
        attached["website_live"] = {"verified": True}
        attached["open_repairs"] = 0
        eligible = wf._persist(self.root, attached)
        self.assertEqual(eligible["cleanup"]["status"], "CLEANUP_ELIGIBLE")
        self.assertTrue(eligible["cleanup"]["eligible"])

    def test_unknown_without_live_owner_stops_for_operator(self):
        started = self.start()
        current = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 4242)
        job_path = self.root / "jobs" / f"{current['s4_job_id']}.json"
        job = json.loads(job_path.read_text())
        job["status"] = "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN"
        job_path.write_text(json.dumps(job), encoding="utf-8")
        result = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 9999)
        self.assertEqual(result["state"], "RESULT_UNKNOWN_OPERATOR_REQUIRED")
        self.assertTrue(result["operator_or_human_required"])
        self.assertFalse(result["automatic_action_available"])

    def test_terminal_artifact_sha_mismatch_fails_closed(self):
        started = self.start()
        current = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 4242)
        job_path = self.root / "jobs" / f"{current['s4_job_id']}.json"
        job = json.loads(job_path.read_text())
        cache_name = f"{current['s4_job_id']}.bin"
        cache = self.root / "artifact-cache" / cache_name
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(b"wrong")
        job["status"] = "TERMINAL_PASS"
        job["artifact"] = {
            "artifact_ref": "voice-ai-artifact:test",
            "artifact_sha256": "0" * 64,
            "cache_name": cache_name,
            "verified": True,
        }
        job_path.write_text(json.dumps(job), encoding="utf-8")
        result = wf.tick_workflow(self.root, started["workflow_id"], spawn_worker=lambda: 9999)
        self.assertEqual(result["state"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(result["last_error"], "TERMINAL_PASS_ARTIFACT_SHA_MISMATCH")


if __name__ == "__main__":
    unittest.main()
