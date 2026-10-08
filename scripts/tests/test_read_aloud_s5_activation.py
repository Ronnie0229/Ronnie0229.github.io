from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
TASK_DIR = PROJECT / "docs/tasks/article-read-aloud-p1b-pre-s5-activation-preparation-20261008"
MODULE_PATH = PROJECT / "scripts/read_aloud_s4_runner.py"
SPEC = importlib.util.spec_from_file_location("read_aloud_s4_runner_s5", MODULE_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class PilotProvider:
    def __init__(self, *, ready: bool = True) -> None:
        self.ready_value = ready
        self.ready_calls = 0
        self.speech_calls = 0
        self.artifact_calls = 0
        self.request_ids: list[str] = []
        self.artifact_bytes = b"pilot-fake-audio"

    def ready(self) -> bool:
        self.ready_calls += 1
        return self.ready_value

    def speech(self, text: str, request_id: str) -> dict:
        self.speech_calls += 1
        self.request_ids.append(request_id)
        return {
            "status": "PASS",
            "request_id": request_id,
            "run_id": "s5-pilot-run",
            "artifact_ref": "voice-ai-artifact:s5-pilot-run",
            "artifact_sha256": hashlib.sha256(self.artifact_bytes).hexdigest(),
            "receipt_ref": "s5-pilot-receipt",
        }

    def artifact(self, artifact_ref: str) -> bytes:
        self.artifact_calls += 1
        return self.artifact_bytes


class S5MinimalActivationTest(unittest.TestCase):
    def setUp(self) -> None:
        TASK_DIR.mkdir(parents=True, exist_ok=True)
        self._runtime = tempfile.TemporaryDirectory(prefix=".s5-runtime-", dir=TASK_DIR)
        self.runtime = Path(self._runtime.name)
        self._fixture = tempfile.TemporaryDirectory(prefix=".s5-fixture-", dir=TASK_DIR)
        self.fixture = Path(self._fixture.name)
        self.render = self.fixture / "render.txt"
        self.render.write_text("S5 isolated pilot text\n", encoding="utf-8")
        self.render_ref = self.render.relative_to(PROJECT).as_posix()

    def tearDown(self) -> None:
        self._fixture.cleanup()
        self._runtime.cleanup()

    def descriptor(self, suffix: str) -> dict[str, str]:
        return {
            "schema": runner.SCHEMA,
            "authorization_ref": f"s5-auth-{suffix}",
            "generation_epoch": f"s5-epoch-{suffix}",
            "operation_id": f"s5-operation-{suffix}",
            "article_id": f"s5-article-{suffix}",
            "render_sha256": hashlib.sha256(self.render.read_bytes()).hexdigest(),
            "voice_contract_id": runner.VOICE_CONTRACT_ID,
        }

    def test_idle_one_shot_exits_without_provider_contact(self) -> None:
        provider = PilotProvider()
        result = runner.worker_once(self.runtime, provider, project_root=PROJECT)
        self.assertIsNone(result)
        self.assertEqual(provider.ready_calls, 0)
        self.assertEqual(provider.speech_calls, 0)
        self.assertEqual(provider.artifact_calls, 0)

    def test_queued_job_uses_existing_s4_path_once_then_terminal_is_idle(self) -> None:
        job = runner.submit(self.runtime, self.descriptor("queued"), self.render_ref)
        original_request_id = job["request_id"]
        provider = PilotProvider()
        first = runner.worker_once(self.runtime, provider, project_root=PROJECT)
        self.assertIsNotNone(first)
        self.assertEqual(first["status"], "TERMINAL_PASS")
        self.assertEqual(provider.speech_calls, 1)
        self.assertEqual(provider.request_ids, [original_request_id])
        second = runner.worker_once(self.runtime, provider, project_root=PROJECT)
        self.assertIsNone(second)
        self.assertEqual(provider.speech_calls, 1)

    def test_provider_not_ready_never_posts(self) -> None:
        job = runner.submit(self.runtime, self.descriptor("not-ready"), self.render_ref)
        provider = PilotProvider(ready=False)
        result = runner.worker_once(self.runtime, provider, project_root=PROJECT)
        self.assertEqual(result["status"], "WAITING_PROVIDER_READY")
        self.assertEqual(result["request_id"], job["request_id"])
        self.assertEqual(provider.speech_calls, 0)
        self.assertEqual(provider.artifact_calls, 0)

    def test_unknown_reentry_preserves_same_request_id(self) -> None:
        job = runner.submit(self.runtime, self.descriptor("unknown"), self.render_ref)
        path = self.runtime / "jobs" / f"{job['descriptor_sha256']}.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["status"] = "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN"
        path.write_text(
            json.dumps(state, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        provider = PilotProvider()
        result = runner.worker_once(self.runtime, provider, project_root=PROJECT)
        self.assertEqual(result["status"], "TERMINAL_PASS")
        self.assertEqual(provider.request_ids, [job["request_id"]])
        self.assertEqual(result["request_id"], job["request_id"])

    def test_activation_uses_external_project_runtime_root(self) -> None:
        self.assertEqual(
            runner.PRODUCTION_ROOT,
            Path("/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud"),
        )
        self.assertFalse(runner.PRODUCTION_ROOT.is_relative_to(PROJECT))


if __name__ == "__main__":
    unittest.main()
