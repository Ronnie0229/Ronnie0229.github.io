from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

PROJECT = Path(__file__).resolve().parents[2]
TASK_DIR = PROJECT / "docs/tasks/article-read-aloud-p1b-pre-s4-durable-runner-implementation-20261007"
MODULE_PATH = PROJECT / "scripts/read_aloud_s4_runner.py"
SPEC = importlib.util.spec_from_file_location("read_aloud_s4_runner", MODULE_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

PILOT_DESCRIPTOR = {
    "schema": runner.SCHEMA,
    "authorization_ref": "article-read-aloud-pilot-generation-authorization-20261007-a1",
    "generation_epoch": "pilot-20261007-a1",
    "operation_id": "article-read-aloud-pilot-post-32d30724d859c99c",
    "article_id": "post-32d30724d859c99c",
    "render_sha256": "5d7cf8826482b64bd0600d7dd2637d5a4ca3f52c3b53ef04c7b68873c160925a",
    "voice_contract_id": runner.VOICE_CONTRACT_ID,
}
PILOT_DESCRIPTOR_SHA = "49e16f2f1972ea4b4ad3f39534b367ec664584d623cc0d3d985e54e24e397005"
PILOT_REQUEST_ID = "rc-readaloud-v1:" + PILOT_DESCRIPTOR_SHA


class FakeProvider:
    def __init__(
        self,
        *,
        ready: bool = True,
        result: dict | None = None,
        artifact: bytes = b"fake-audio-bytes",
        speech_error: bool = False,
    ) -> None:
        self.ready_value = ready
        self.result_value = result
        self.artifact_bytes = artifact
        self.speech_error = speech_error
        self.ready_calls = 0
        self.speech_calls = 0
        self.artifact_calls = 0
        self.texts: list[str] = []
        self.request_ids: list[str] = []

    def ready(self) -> bool:
        self.ready_calls += 1
        return self.ready_value

    def speech(self, text: str, request_id: str) -> dict:
        self.speech_calls += 1
        self.texts.append(text)
        self.request_ids.append(request_id)
        if self.speech_error:
            raise ConnectionError("simulated lost response")
        if self.result_value is not None:
            return dict(self.result_value)
        sha = hashlib.sha256(self.artifact_bytes).hexdigest()
        return {
            "status": "PASS",
            "request_id": request_id,
            "run_id": "fake-run-1",
            "artifact_ref": "voice-ai-artifact:fake-run-1",
            "artifact_sha256": sha,
            "receipt_ref": "fake-receipt-1",
        }

    def artifact(self, artifact_ref: str) -> bytes:
        self.artifact_calls += 1
        return self.artifact_bytes


class BlockingProvider(FakeProvider):
    def __init__(self) -> None:
        super().__init__()
        self.entered = threading.Event()
        self.release = threading.Event()

    def speech(self, text: str, request_id: str) -> dict:
        self.speech_calls += 1
        self.texts.append(text)
        self.request_ids.append(request_id)
        self.entered.set()
        if not self.release.wait(timeout=5):
            raise TimeoutError("test provider release timeout")
        sha = hashlib.sha256(self.artifact_bytes).hexdigest()
        return {
            "status": "PASS",
            "request_id": request_id,
            "run_id": "blocking-run-1",
            "artifact_ref": "voice-ai-artifact:blocking-run-1",
            "artifact_sha256": sha,
            "receipt_ref": "blocking-receipt-1",
        }


class RunnerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TASK_DIR.mkdir(parents=True, exist_ok=True)
        self._runtime = tempfile.TemporaryDirectory(prefix=".test-runtime-", dir=TASK_DIR)
        self.runtime = Path(self._runtime.name)
        self._fixtures = tempfile.TemporaryDirectory(prefix=".test-fixtures-", dir=TASK_DIR)
        self.fixture_dir = Path(self._fixtures.name)
        self.render = self.fixture_dir / "render.txt"
        self.render.write_text("精确渲染文本\n第二行\n", encoding="utf-8")
        self.render_ref = self.render.relative_to(PROJECT).as_posix()

    def tearDown(self) -> None:
        self._fixtures.cleanup()
        self._runtime.cleanup()

    def descriptor(self, **changes: str) -> dict[str, str]:
        d = {
            "schema": runner.SCHEMA,
            "authorization_ref": "test-auth-a1",
            "generation_epoch": "test-epoch-a1",
            "operation_id": "test-operation-a1",
            "article_id": "test-article-a1",
            "render_sha256": hashlib.sha256(self.render.read_bytes()).hexdigest(),
            "voice_contract_id": runner.VOICE_CONTRACT_ID,
        }
        d.update(changes)
        return d

    def submit_default(self, descriptor: dict[str, str] | None = None) -> dict:
        return runner.submit(self.runtime, descriptor or self.descriptor(), self.render_ref)

    def valid_pass_result(self, job: dict, **changes: object) -> dict:
        artifact = b"fake-audio-bytes"
        value = {
            "status": "PASS",
            "request_id": job["request_id"],
            "run_id": "run-valid-1",
            "artifact_ref": "voice-ai-artifact:run-valid-1",
            "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
            "receipt_ref": "receipt-valid-1",
        }
        value.update(changes)
        return value

    def durable_job_text(self, job: dict) -> str:
        path = self.runtime / "jobs" / f"{job['descriptor_sha256']}.json"
        return path.read_text(encoding="utf-8")

    def test_pilot_canonical_descriptor_sha_and_request_id_exact(self) -> None:
        self.assertEqual(runner.descriptor_sha256(PILOT_DESCRIPTOR), PILOT_DESCRIPTOR_SHA)
        self.assertEqual(runner.derive_request_id(PILOT_DESCRIPTOR), PILOT_REQUEST_ID)
        self.assertRegex(PILOT_REQUEST_ID, runner.REQUEST_ID_RE)
        self.assertEqual(len(PILOT_REQUEST_ID), 80)

    def test_first_and_duplicate_submit_use_one_claim_and_same_job(self) -> None:
        first = self.submit_default()
        second = self.submit_default()
        self.assertEqual(first["descriptor_sha256"], second["descriptor_sha256"])
        self.assertEqual(first["request_id"], second["request_id"])
        self.assertEqual(len(list((self.runtime / "claims").glob("*.json"))), 1)
        self.assertEqual(len(list((self.runtime / "jobs").glob("*.json"))), 1)

    def test_supplied_wrong_request_id_fails_before_claim(self) -> None:
        with self.assertRaisesRegex(runner.RunnerError, "REQUEST_ID_DESCRIPTOR_MISMATCH"):
            runner.submit(
                self.runtime,
                self.descriptor(),
                self.render_ref,
                supplied_request_id="wrong-id",
            )
        self.assertFalse((self.runtime / "claims").exists())

    def test_concurrent_duplicate_submit_has_one_claim_identity(self) -> None:
        descriptor = self.descriptor()
        barrier = threading.Barrier(8)
        results: list[tuple[str, str]] = []
        errors: list[Exception] = []
        lock = threading.Lock()

        def call() -> None:
            try:
                barrier.wait()
                job = runner.submit(self.runtime, descriptor, self.render_ref)
                with lock:
                    results.append((job["descriptor_sha256"], job["request_id"]))
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=call) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertFalse(errors, errors)
        self.assertEqual(len(results), 8)
        self.assertEqual(len(set(results)), 1)
        self.assertEqual(len(list((self.runtime / "claims").glob("*.json"))), 1)

    def test_same_authorization_changed_identity_fails_closed(self) -> None:
        self.submit_default()
        for field, value in (
            ("article_id", "different-article"),
            ("operation_id", "different-operation"),
            ("render_sha256", "a" * 64),
            ("voice_contract_id", "OTHER"),
        ):
            changed = self.descriptor(**{field: value})
            with self.subTest(field=field):
                with self.assertRaises(runner.RunnerError) as caught:
                    runner.submit(self.runtime, changed, self.render_ref)
                self.assertIn(
                    caught.exception.code,
                    {"AUTHORIZATION_IDENTITY_CONFLICT", "VOICE_CONTRACT_ID_INVALID"},
                )

    def test_incomplete_claim_fails_closed_and_is_not_released(self) -> None:
        descriptor = self.descriptor()
        runner.ensure_runtime_root(self.runtime)
        cpath = runner.claim_path(self.runtime, descriptor)
        cpath.write_bytes(b"{")
        os.chmod(cpath, 0o600)
        with self.assertRaisesRegex(runner.RunnerError, "AUTHORIZATION_CLAIM_CORRUPT"):
            runner.submit(self.runtime, descriptor, self.render_ref)
        self.assertTrue(cpath.exists())
        self.assertEqual(cpath.read_bytes(), b"{")

    def test_claim_survives_simulated_restart(self) -> None:
        first = self.submit_default()
        cpath = runner.claim_path(self.runtime, first["descriptor"])
        before = cpath.read_bytes()
        second = runner.submit(self.runtime, first["descriptor"], self.render_ref)
        self.assertEqual(before, cpath.read_bytes())
        self.assertEqual(first["request_id"], second["request_id"])

    def test_render_exact_bytes_pass_and_provider_gets_exact_text(self) -> None:
        job = self.submit_default()
        provider = FakeProvider()
        final = runner.execute_job(
            self.runtime,
            job["descriptor_sha256"],
            provider,
            project_root=PROJECT,
        )
        self.assertEqual(final["status"], "TERMINAL_PASS")
        self.assertEqual(provider.speech_calls, 1)
        self.assertEqual(provider.texts, [self.render.read_text(encoding="utf-8")])
        self.assertEqual(provider.request_ids, [job["request_id"]])

    def test_render_sha_mismatch_never_calls_provider_speech(self) -> None:
        job = self.submit_default()
        self.render.write_text("drifted", encoding="utf-8")
        provider = FakeProvider()
        final = runner.execute_job(self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "RENDER_SHA256_MISMATCH")
        self.assertEqual(provider.speech_calls, 0)

    def test_render_negative_paths_never_call_provider_speech(self) -> None:
        cases: list[tuple[str, callable]] = []

        def missing() -> tuple[dict, str]:
            descriptor = self.descriptor(operation_id="missing")
            job = runner.submit(self.runtime, descriptor, self.render_ref)
            self.render.unlink()
            return job, self.render_ref

        cases.append(("missing", missing))

        for name, maker in cases:
            with self.subTest(case=name):
                provider = FakeProvider()
                job, _ = maker()
                final = runner.execute_job(self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT)
                self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
                self.assertEqual(provider.speech_calls, 0)
                self.render.write_text("精确渲染文本\n第二行\n", encoding="utf-8")

    def test_path_escape_absolute_symlink_decode_failure_and_unreadable_never_post(self) -> None:
        scenarios: list[tuple[str, str, dict[str, str], Path | None]] = []

        descriptor = self.descriptor(operation_id="escape")
        scenarios.append(("escape", "../outside.txt", descriptor, None))

        descriptor = self.descriptor(operation_id="absolute")
        scenarios.append(("absolute", str(self.render), descriptor, None))

        symlink = self.fixture_dir / "symlink.txt"
        symlink.symlink_to(self.render)
        descriptor = self.descriptor(operation_id="symlink")
        scenarios.append(("symlink", symlink.relative_to(PROJECT).as_posix(), descriptor, None))

        bad_utf8 = self.fixture_dir / "bad-utf8.txt"
        bad_utf8.write_bytes(b"\xff\xfe")
        descriptor = self.descriptor(
            operation_id="decode",
            render_sha256=hashlib.sha256(bad_utf8.read_bytes()).hexdigest(),
        )
        scenarios.append(("decode", bad_utf8.relative_to(PROJECT).as_posix(), descriptor, None))

        unreadable = self.fixture_dir / "unreadable.txt"
        unreadable.write_text("secret", encoding="utf-8")
        os.chmod(unreadable, 0)
        descriptor = self.descriptor(
            operation_id="unreadable",
            render_sha256=hashlib.sha256(unreadable.read_bytes() if os.access(unreadable, os.R_OK) else b"secret").hexdigest(),
        )
        scenarios.append(("unreadable", unreadable.relative_to(PROJECT).as_posix(), descriptor, unreadable))

        try:
            for name, render_ref, desc, _ in scenarios:
                with self.subTest(case=name):
                    isolated = Path(tempfile.mkdtemp(prefix=f".case-{name}-", dir=TASK_DIR))
                    try:
                        job = runner.submit(isolated, desc, render_ref)
                        provider = FakeProvider()
                        final = runner.execute_job(isolated, job["descriptor_sha256"], provider, project_root=PROJECT)
                        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
                        self.assertEqual(provider.speech_calls, 0)
                    finally:
                        import shutil
                        shutil.rmtree(isolated, ignore_errors=True)
        finally:
            os.chmod(unreadable, 0o600)

    def test_verified_render_is_read_once_and_sent_without_normalization(self) -> None:
        job = self.submit_default()
        provider = FakeProvider()
        original = runner._safe_render_bytes
        calls = {"count": 0}

        def counted(project_root: Path, render_ref: str) -> bytes:
            calls["count"] += 1
            return original(project_root, render_ref)

        with mock.patch.object(runner, "_safe_render_bytes", side_effect=counted):
            final = runner.execute_job(self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT)
        self.assertEqual(final["status"], "TERMINAL_PASS")
        self.assertEqual(calls["count"], 1)
        self.assertEqual(provider.texts[0].encode("utf-8"), self.render.read_bytes())

    def test_provider_not_ready_preserves_identity_and_never_posts(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(ready=False)
        state = runner.execute_job(self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT)
        self.assertEqual(state["status"], "WAITING_PROVIDER_READY")
        self.assertEqual(state["request_id"], job["request_id"])
        self.assertEqual(provider.speech_calls, 0)

    def test_connection_failure_unknown_then_same_id_reconcile_pass(self) -> None:
        job = self.submit_default()
        failing = FakeProvider(speech_error=True)
        unknown = runner.execute_job(self.runtime, job["descriptor_sha256"], failing, project_root=PROJECT)
        self.assertEqual(unknown["status"], "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN")
        self.assertEqual(failing.request_ids, [job["request_id"]])

        replay = FakeProvider()
        final = runner.reconcile(self.runtime, job["descriptor_sha256"], replay, project_root=PROJECT)
        self.assertEqual(final["status"], "TERMINAL_PASS")
        self.assertEqual(replay.request_ids, [job["request_id"]])
        self.assertEqual(final["provider_result"]["request_id"], job["request_id"])

    def test_terminal_reconcile_does_not_call_provider_again(self) -> None:
        job = self.submit_default()
        first = FakeProvider()
        final = runner.execute_job(self.runtime, job["descriptor_sha256"], first, project_root=PROJECT)
        self.assertEqual(final["status"], "TERMINAL_PASS")
        second = FakeProvider()
        replay = runner.reconcile(self.runtime, job["descriptor_sha256"], second, project_root=PROJECT)
        self.assertEqual(replay["provider_result"]["run_id"], "fake-run-1")
        self.assertEqual(second.ready_calls, 0)
        self.assertEqual(second.speech_calls, 0)
        self.assertEqual(second.artifact_calls, 0)

    def test_two_concurrent_execute_job_calls_allow_at_most_one_provider_speech(self) -> None:
        job = self.submit_default()
        provider = BlockingProvider()
        outcomes: list[object] = []

        def first() -> None:
            try:
                outcomes.append(
                    runner.execute_job(
                        self.runtime,
                        job["descriptor_sha256"],
                        provider,
                        project_root=PROJECT,
                    )
                )
            except Exception as exc:
                outcomes.append(exc)

        thread = threading.Thread(target=first)
        thread.start()
        self.assertTrue(provider.entered.wait(timeout=2))

        with self.assertRaises(runner.RunnerError) as caught:
            runner.execute_job(
                self.runtime,
                job["descriptor_sha256"],
                provider,
                project_root=PROJECT,
            )
        self.assertEqual(caught.exception.code, "EXECUTION_BUSY_OR_STALE_LOCK")
        self.assertEqual(provider.speech_calls, 1)

        provider.release.set()
        thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(provider.speech_calls, 1)
        terminal = runner.status(self.runtime, job["descriptor_sha256"])
        self.assertEqual(terminal["status"], "TERMINAL_PASS")
        self.assertFalse(runner.execution_lock_path(self.runtime).exists())

    def test_global_execution_lock_blocks_different_job_provider_post(self) -> None:
        first = self.submit_default()
        second_descriptor = self.descriptor(
            authorization_ref="test-auth-b1",
            generation_epoch="test-epoch-b1",
            operation_id="test-operation-b1",
            article_id="test-article-b1",
        )
        second = self.submit_default(second_descriptor)
        provider = BlockingProvider()
        outcomes: list[object] = []

        thread = threading.Thread(
            target=lambda: outcomes.append(
                runner.execute_job(
                    self.runtime,
                    first["descriptor_sha256"],
                    provider,
                    project_root=PROJECT,
                )
            )
        )
        thread.start()
        self.assertTrue(provider.entered.wait(timeout=2))

        with self.assertRaises(runner.RunnerError) as caught:
            runner.execute_job(
                self.runtime,
                second["descriptor_sha256"],
                provider,
                project_root=PROJECT,
            )
        self.assertEqual(caught.exception.code, "EXECUTION_BUSY_OR_STALE_LOCK")
        self.assertEqual(provider.speech_calls, 1)
        provider.release.set()
        thread.join(timeout=3)
        self.assertEqual(provider.speech_calls, 1)

    def test_worker_once_vs_reconcile_cannot_double_post(self) -> None:
        job = self.submit_default()
        provider = BlockingProvider()
        worker_outcome: list[object] = []

        thread = threading.Thread(
            target=lambda: worker_outcome.append(
                runner.worker_once(self.runtime, provider, project_root=PROJECT)
            )
        )
        thread.start()
        self.assertTrue(provider.entered.wait(timeout=2))

        with self.assertRaises(runner.RunnerError) as caught:
            runner.reconcile(
                self.runtime,
                job["descriptor_sha256"],
                provider,
                project_root=PROJECT,
            )
        self.assertEqual(caught.exception.code, "EXECUTION_BUSY_OR_STALE_LOCK")
        self.assertEqual(provider.speech_calls, 1)

        provider.release.set()
        thread.join(timeout=3)
        self.assertEqual(provider.speech_calls, 1)
        self.assertEqual(
            runner.status(self.runtime, job["descriptor_sha256"])["status"],
            "TERMINAL_PASS",
        )

    def test_stale_execution_lock_is_never_automatically_taken_over(self) -> None:
        job = self.submit_default()
        path = runner.execution_lock_path(self.runtime)
        runner.atomic_write_json(
            path,
            {
                "schema": "ronniecross-readaloud-s4-execution-owner/v1",
                "token": "marker-a",
                "pid": 999999,
                "job_id": job["descriptor_sha256"],
                "request_id": job["request_id"],
            },
        )
        provider = FakeProvider()
        with self.assertRaises(runner.RunnerError) as caught:
            runner.execute_job(
                self.runtime,
                job["descriptor_sha256"],
                provider,
                project_root=PROJECT,
            )
        self.assertEqual(caught.exception.code, "EXECUTION_BUSY_OR_STALE_LOCK")
        self.assertEqual(provider.speech_calls, 0)
        self.assertTrue(path.exists())

    def test_unknown_state_plus_stale_lock_remains_conservative(self) -> None:
        job = self.submit_default()
        jpath = self.runtime / "jobs" / f"{job['descriptor_sha256']}.json"
        job["status"] = "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN"
        job["last_error"] = "SIMULATED_PROCESS_DEATH_AFTER_POST"
        runner.atomic_write_json(jpath, job)
        runner.atomic_write_json(
            runner.execution_lock_path(self.runtime),
            {
                "schema": "ronniecross-readaloud-s4-execution-owner/v1",
                "token": "marker-b",
                "pid": 999999,
                "job_id": job["descriptor_sha256"],
                "request_id": job["request_id"],
            },
        )

        provider = FakeProvider()
        with self.assertRaises(runner.RunnerError) as caught:
            runner.reconcile(
                self.runtime,
                job["descriptor_sha256"],
                provider,
                project_root=PROJECT,
            )
        self.assertEqual(caught.exception.code, "EXECUTION_BUSY_OR_STALE_LOCK")
        self.assertEqual(provider.speech_calls, 0)
        persisted = runner.status(self.runtime, job["descriptor_sha256"])
        self.assertEqual(persisted["status"], "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN")

    def test_provider_pass_wrong_request_id_fails_closed_before_artifact(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(result=self.valid_pass_result(job, request_id="WRONG-ID"))
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertIsNone(final["artifact"])

    def test_provider_pass_missing_request_id_fails_closed_before_artifact(self) -> None:
        job = self.submit_default()
        result = self.valid_pass_result(job)
        result.pop("request_id")
        provider = FakeProvider(result=result)
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)

    def test_provider_pass_missing_success_identity_fields_fail_closed(self) -> None:
        for field in ("run_id", "artifact_ref", "artifact_sha256", "receipt_ref"):
            with self.subTest(field=field):
                isolated = Path(tempfile.mkdtemp(prefix=f".identity-{field}-", dir=TASK_DIR))
                try:
                    descriptor = self.descriptor(
                        authorization_ref=f"auth-{field}",
                        generation_epoch=f"epoch-{field}",
                        operation_id=f"operation-{field}",
                        article_id=f"article-{field}",
                    )
                    job = runner.submit(isolated, descriptor, self.render_ref)
                    result = self.valid_pass_result(job)
                    result.pop(field)
                    provider = FakeProvider(result=result)
                    final = runner.execute_job(
                        isolated,
                        job["descriptor_sha256"],
                        provider,
                        project_root=PROJECT,
                    )
                    self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
                    self.assertEqual(provider.artifact_calls, 0)
                finally:
                    import shutil
                    shutil.rmtree(isolated, ignore_errors=True)

    def test_provider_pass_invalid_artifact_sha_fails_closed_before_artifact(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            result=self.valid_pass_result(job, artifact_sha256="not-a-sha")
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_ARTIFACT_SHA_INVALID")
        self.assertEqual(provider.artifact_calls, 0)

    def test_provider_pass_failure_code_must_be_empty(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            result=self.valid_pass_result(job, failure_code="SHOULD_NOT_EXIST")
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_PASS_FAILURE_CODE_INVALID")
        self.assertEqual(provider.artifact_calls, 0)

    def test_provider_blocked_wrong_request_id_is_identity_fail_closed(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            result={
                "status": "BLOCKED",
                "request_id": "WRONG-ID",
                "failure_code": "HTTP_DUPLICATE_IN_FLIGHT",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)

    def test_provider_fail_closed_wrong_request_id_is_identity_fail_closed(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            result={
                "status": "FAIL_CLOSED",
                "request_id": "WRONG-ID",
                "failure_code": "PROVIDER_FAIL_CLOSED",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)

    def test_matching_provider_pass_still_succeeds_after_identity_validation(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(result=self.valid_pass_result(job))
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        self.assertEqual(final["status"], "TERMINAL_PASS")
        self.assertEqual(provider.artifact_calls, 1)
        self.assertEqual(final["provider_result"]["request_id"], job["request_id"])
        self.assertTrue(final["artifact"]["verified"])

    def test_provider_evidence_does_not_persist_untrusted_text_field(self) -> None:
        job = self.submit_default()
        provider_result = self.valid_pass_result(job, request_id="WRONG-ID")
        provider_result["text"] = "NONPERSISTED_TEST_PAYLOAD"
        provider = FakeProvider(result=provider_result)
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        persisted = json.dumps(final["provider_result"], ensure_ascii=False)
        self.assertNotIn("NONPERSISTED_TEST_PAYLOAD", persisted)

    def test_oversized_run_id_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "OVERSIZED_RUN_ID_BODY_MARKER"
        provider = FakeProvider(
            result=self.valid_pass_result(
                job, run_id=("R" * (runner.MAX_PROVIDER_ID_LENGTH + 10)) + marker
            )
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_PASS_RUN_ID_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn('"run_id"', durable)

    def test_oversized_artifact_ref_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "OVERSIZED_ARTIFACT_REF_BODY_MARKER"
        provider = FakeProvider(
            result=self.valid_pass_result(
                job,
                artifact_ref=("A" * (runner.MAX_PROVIDER_ID_LENGTH + 10)) + marker,
            )
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_PASS_ARTIFACT_REF_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn('"artifact_ref"', durable)

    def test_oversized_receipt_ref_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "OVERSIZED_RECEIPT_REF_BODY_MARKER"
        provider = FakeProvider(
            result=self.valid_pass_result(
                job,
                receipt_ref=("Q" * (runner.MAX_PROVIDER_ID_LENGTH + 10)) + marker,
            )
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_PASS_RECEIPT_REF_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn('"receipt_ref"', durable)

    def test_oversized_blocked_failure_code_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "OVERSIZED_BLOCKED_FAILURE_BODY_MARKER"
        provider = FakeProvider(
            result={
                "status": "BLOCKED",
                "request_id": job["request_id"],
                "failure_code": ("F" * (runner.MAX_FAILURE_CODE_LENGTH + 10)) + marker,
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_FAILURE_CODE_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn('"failure_code"', durable)

    def test_oversized_fail_closed_failure_code_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "OVERSIZED_FAIL_CLOSED_BODY_MARKER"
        provider = FakeProvider(
            result={
                "status": "FAIL_CLOSED",
                "request_id": job["request_id"],
                "failure_code": ("F" * (runner.MAX_FAILURE_CODE_LENGTH + 10)) + marker,
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_FAILURE_CODE_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn('"failure_code"', durable)

    def test_oversized_request_id_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "OVERSIZED_REQUEST_ID_BODY_MARKER"
        provider = FakeProvider(
            result=self.valid_pass_result(
                job,
                request_id=("X" * 140) + marker,
            )
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertEqual(final["provider_result"].get("request_id"), None)

    def test_malformed_request_id_marker_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "MALFORMED_REQUEST_ID_BODY_MARKER"
        provider_result = self.valid_pass_result(job)
        provider_result["request_id"] = {"nested": marker}
        provider = FakeProvider(result=provider_result)
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertEqual(final["provider_result"].get("request_id"), None)

    def test_malformed_allowlisted_values_are_omitted_not_stringified(self) -> None:
        job = self.submit_default()
        marker = "MALFORMED_ALLOWLIST_BODY_MARKER"
        provider = FakeProvider(
            result={
                "status": "PASS",
                "request_id": job["request_id"],
                "run_id": {"nested": marker},
                "artifact_ref": ["bad", marker],
                "artifact_sha256": {"bad": marker},
                "receipt_ref": 12345,
                "failure_code": {"bad": marker},
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn('"run_id"', durable)
        self.assertNotIn('"artifact_ref"', durable)
        self.assertNotIn('"artifact_sha256"', durable)
        self.assertNotIn('"receipt_ref"', durable)
        self.assertNotIn('"failure_code"', durable)

    def test_unknown_large_provider_key_body_never_reaches_durable_json(self) -> None:
        job = self.submit_default()
        marker = "UNKNOWN_PROVIDER_BODY_MARKER"
        provider_result = self.valid_pass_result(job, request_id="WRONG-ID")
        provider_result["unexpected_body"] = ("U" * 5000) + marker
        provider = FakeProvider(result=provider_result)
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn("unexpected_body", durable)

    def test_valid_pass_persists_expected_bounded_identity_evidence(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(result=self.valid_pass_result(job))
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_PASS")
        self.assertEqual(provider.artifact_calls, 1)
        for value in (
            job["request_id"],
            "run-valid-1",
            "voice-ai-artifact:run-valid-1",
            "receipt-valid-1",
        ):
            self.assertIn(value, durable)

    def test_valid_blocked_persists_only_bounded_safe_evidence(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            result={
                "status": "BLOCKED",
                "request_id": job["request_id"],
                "failure_code": "HTTP_DUPLICATE_IN_FLIGHT",
                "unexpected_body": "SHOULD_NOT_PERSIST",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_BLOCKED")
        self.assertIn("HTTP_DUPLICATE_IN_FLIGHT", durable)
        self.assertIn(job["request_id"], durable)
        self.assertNotIn("SHOULD_NOT_PERSIST", durable)

    def test_valid_fail_closed_persists_only_bounded_safe_evidence(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            result={
                "status": "FAIL_CLOSED",
                "request_id": job["request_id"],
                "failure_code": "PROVIDER_FAIL_CLOSED",
                "unexpected_body": "SHOULD_NOT_PERSIST",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertIn("PROVIDER_FAIL_CLOSED", durable)
        self.assertIn(job["request_id"], durable)
        self.assertNotIn("SHOULD_NOT_PERSIST", durable)

    def test_semantic_wrong_but_valid_request_id_marker_absent_from_durable_json(self) -> None:
        job = self.submit_default()
        marker = "WRONG_VALID_REQUEST_MARKER"
        wrong_request_id = f"wrong-valid-{marker}"
        self.assertIsNotNone(runner.REQUEST_ID_RE.fullmatch(wrong_request_id))
        provider = FakeProvider(
            result=self.valid_pass_result(job, request_id=wrong_request_id)
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn(wrong_request_id, durable)
        self.assertNotIn("request_id", final["provider_result"])
        self.assertEqual(final["provider_result"], {"status": "PASS"})

    def test_semantic_pass_nonempty_failure_code_marker_absent_from_durable_json(self) -> None:
        job = self.submit_default()
        marker = "PASS_FAILURE_CODE_MARKER"
        provider = FakeProvider(
            result=self.valid_pass_result(job, failure_code=marker)
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_PASS_FAILURE_CODE_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn("failure_code", final["provider_result"])
        self.assertEqual(final["provider_result"]["request_id"], job["request_id"])
        self.assertEqual(final["provider_result"]["run_id"], "run-valid-1")

    def test_blocked_omits_syntactically_valid_pass_only_identity_markers(self) -> None:
        job = self.submit_default()
        markers = {
            "run_id": "BLOCKED_RUN_MARKER",
            "artifact_ref": "BLOCKED_ARTIFACT_REF_MARKER",
            "artifact_sha256": hashlib.sha256(b"BLOCKED_ARTIFACT_SHA_MARKER").hexdigest(),
            "receipt_ref": "BLOCKED_RECEIPT_MARKER",
        }
        provider = FakeProvider(
            result={
                "status": "BLOCKED",
                "request_id": job["request_id"],
                "failure_code": "HTTP_DUPLICATE_IN_FLIGHT",
                **markers,
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_BLOCKED")
        self.assertEqual(
            final["provider_result"],
            {
                "status": "BLOCKED",
                "request_id": job["request_id"],
                "failure_code": "HTTP_DUPLICATE_IN_FLIGHT",
            },
        )
        self.assertNotIn("BLOCKED_RUN_MARKER", durable)
        self.assertNotIn("BLOCKED_ARTIFACT_REF_MARKER", durable)
        self.assertNotIn("BLOCKED_RECEIPT_MARKER", durable)
        self.assertNotIn(markers["artifact_sha256"], durable)

    def test_fail_closed_omits_syntactically_valid_pass_only_identity_markers(self) -> None:
        job = self.submit_default()
        artifact_sha_marker = hashlib.sha256(b"FAIL_CLOSED_ARTIFACT_SHA_MARKER").hexdigest()
        provider = FakeProvider(
            result={
                "status": "FAIL_CLOSED",
                "request_id": job["request_id"],
                "failure_code": "PROVIDER_FAIL_CLOSED",
                "run_id": "FAIL_CLOSED_RUN_MARKER",
                "artifact_ref": "FAIL_CLOSED_ARTIFACT_REF_MARKER",
                "artifact_sha256": artifact_sha_marker,
                "receipt_ref": "FAIL_CLOSED_RECEIPT_MARKER",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(
            final["provider_result"],
            {
                "status": "FAIL_CLOSED",
                "request_id": job["request_id"],
                "failure_code": "PROVIDER_FAIL_CLOSED",
            },
        )
        for marker_value in (
            "FAIL_CLOSED_RUN_MARKER",
            "FAIL_CLOSED_ARTIFACT_REF_MARKER",
            "FAIL_CLOSED_RECEIPT_MARKER",
            artifact_sha_marker,
        ):
            self.assertNotIn(marker_value, durable)

    def test_blocked_wrong_but_valid_request_id_omits_failure_and_identity_evidence(self) -> None:
        job = self.submit_default()
        marker = "BLOCKED_WRONG_REQUEST_MARKER"
        wrong_request_id = f"blocked-wrong-{marker}"
        self.assertIsNotNone(runner.REQUEST_ID_RE.fullmatch(wrong_request_id))
        provider = FakeProvider(
            result={
                "status": "BLOCKED",
                "request_id": wrong_request_id,
                "failure_code": "BLOCKED_FAILURE_MARKER",
                "run_id": "BLOCKED_RUN_SHOULD_NOT_PERSIST",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertEqual(final["provider_result"], {"status": "BLOCKED"})
        for value in (
            marker,
            wrong_request_id,
            "BLOCKED_FAILURE_MARKER",
            "BLOCKED_RUN_SHOULD_NOT_PERSIST",
        ):
            self.assertNotIn(value, durable)

    def test_fail_closed_wrong_but_valid_request_id_omits_failure_and_identity_evidence(self) -> None:
        job = self.submit_default()
        marker = "FAIL_CLOSED_WRONG_REQUEST_MARKER"
        wrong_request_id = f"fail-closed-wrong-{marker}"
        self.assertIsNotNone(runner.REQUEST_ID_RE.fullmatch(wrong_request_id))
        provider = FakeProvider(
            result={
                "status": "FAIL_CLOSED",
                "request_id": wrong_request_id,
                "failure_code": "FAIL_CLOSED_FAILURE_MARKER",
                "receipt_ref": "FAIL_CLOSED_RECEIPT_SHOULD_NOT_PERSIST",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_REQUEST_ID_MISMATCH")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertEqual(final["provider_result"], {"status": "FAIL_CLOSED"})
        for value in (
            marker,
            wrong_request_id,
            "FAIL_CLOSED_FAILURE_MARKER",
            "FAIL_CLOSED_RECEIPT_SHOULD_NOT_PERSIST",
        ):
            self.assertNotIn(value, durable)

    def test_malformed_status_type_safety_matrix_durable_fail_closed_and_no_retry(self) -> None:
        cases = (
            ("dict", {"nested": "DICT_STATUS_MARK"}, "DICT_STATUS_MARK"),
            ("list", ["LIST_STATUS_MARK"], "LIST_STATUS_MARK"),
            (
                "nested",
                {"outer": ["NESTED_STATUS_MARK", {"deep": "NESTED_STATUS_BODY"}]},
                "NESTED_STATUS_MARK",
            ),
            ("numeric", 12345, None),
            ("bool", True, None),
            ("null", None, None),
            ("tuple", ("TUPLE_STATUS_MARK", {"deep": "TUPLE_STATUS_BODY"}), "TUPLE_STATUS_MARK"),
            ("unknown_string", "UNKNOWN_STATUS_MARK", "UNKNOWN_STATUS_MARK"),
        )

        for name, malformed_status, marker_value in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory(
                    prefix=f".malformed-status-{name}-", dir=TASK_DIR
                ) as isolated_name:
                    isolated = Path(isolated_name)
                    descriptor = self.descriptor(
                        authorization_ref=f"malformed-status-auth-{name}",
                        generation_epoch=f"malformed-status-epoch-{name}",
                        operation_id=f"malformed-status-operation-{name}",
                        article_id=f"malformed-status-article-{name}",
                    )
                    job = runner.submit(isolated, descriptor, self.render_ref)
                    provider = FakeProvider(
                        result={
                            "status": malformed_status,
                            "request_id": job["request_id"],
                            "run_id": f"RUN_MARK_{name}",
                            "artifact_ref": f"ARTIFACT_MARK_{name}",
                            "artifact_sha256": hashlib.sha256(
                                f"SHA_MARK_{name}".encode("utf-8")
                            ).hexdigest(),
                            "receipt_ref": f"RECEIPT_MARK_{name}",
                            "failure_code": f"FAILURE_MARK_{name}",
                        }
                    )

                    final = runner.execute_job(
                        isolated,
                        job["descriptor_sha256"],
                        provider,
                        project_root=PROJECT,
                    )
                    durable_path = (
                        isolated / "jobs" / f"{job['descriptor_sha256']}.json"
                    )
                    durable = durable_path.read_text(encoding="utf-8")

                    self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
                    self.assertEqual(
                        final["last_error"], "PROVIDER_RESULT_STATUS_INVALID"
                    )
                    self.assertEqual(final["provider_result"], {})
                    self.assertIsNone(final["artifact"])
                    self.assertEqual(provider.artifact_calls, 0)
                    self.assertFalse(runner.execution_lock_path(isolated).exists())

                    for provider_marker in (
                        marker_value,
                        f"RUN_MARK_{name}",
                        f"ARTIFACT_MARK_{name}",
                        f"RECEIPT_MARK_{name}",
                        f"FAILURE_MARK_{name}",
                    ):
                        if provider_marker is not None:
                            self.assertNotIn(provider_marker, durable)
                    self.assertNotIn("SHA_MARK_", durable)
                    self.assertNotIn("NESTED_STATUS_BODY", durable)
                    self.assertNotIn("TUPLE_STATUS_BODY", durable)

                    status_value = runner.status(
                        isolated, job["descriptor_sha256"]
                    )
                    result_value = runner.result(
                        isolated, job["descriptor_sha256"]
                    )
                    self.assertEqual(status_value["status"], "TERMINAL_FAIL_CLOSED")
                    self.assertEqual(
                        status_value["last_error"], "PROVIDER_RESULT_STATUS_INVALID"
                    )
                    self.assertEqual(result_value["status"], "TERMINAL_FAIL_CLOSED")
                    self.assertEqual(result_value["provider_result"], {})
                    self.assertIsNone(result_value["artifact"])

                    reconcile_provider = FakeProvider()
                    reconciled = runner.reconcile(
                        isolated,
                        job["descriptor_sha256"],
                        reconcile_provider,
                        project_root=PROJECT,
                    )
                    self.assertEqual(
                        reconciled["status"], "TERMINAL_FAIL_CLOSED"
                    )
                    self.assertEqual(reconcile_provider.ready_calls, 0)
                    self.assertEqual(reconcile_provider.speech_calls, 0)
                    self.assertEqual(reconcile_provider.artifact_calls, 0)

    def test_unknown_status_omits_all_provider_controlled_terminal_evidence(self) -> None:
        job = self.submit_default()
        marker = "UNKNOWN_STATUS_SEMANTIC_MARKER"
        provider = FakeProvider(
            result={
                "status": "UNKNOWN_TERMINAL",
                "request_id": job["request_id"],
                "failure_code": f"FAIL_{marker}",
                "run_id": f"RUN_{marker}",
                "artifact_ref": f"ARTIFACT_{marker}",
                "artifact_sha256": hashlib.sha256(marker.encode("utf-8")).hexdigest(),
                "receipt_ref": f"RECEIPT_{marker}",
            }
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_RESULT_STATUS_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertEqual(final["provider_result"], {})
        self.assertNotIn(marker, durable)
        self.assertNotIn("UNKNOWN_TERMINAL", durable)

    def test_pass_invalid_success_field_marker_absent_but_other_safe_fields_persist(self) -> None:
        job = self.submit_default()
        marker = "PASS_INVALID_RUN_MARKER"
        invalid_run_id = ("R" * (runner.MAX_PROVIDER_ID_LENGTH + 1)) + marker
        provider = FakeProvider(
            result=self.valid_pass_result(job, run_id=invalid_run_id)
        )
        final = runner.execute_job(
            self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT
        )
        durable = self.durable_job_text(job)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "PROVIDER_PASS_RUN_ID_INVALID")
        self.assertEqual(provider.artifact_calls, 0)
        self.assertNotIn(marker, durable)
        self.assertNotIn("run_id", final["provider_result"])
        self.assertEqual(final["provider_result"]["request_id"], job["request_id"])
        self.assertEqual(
            final["provider_result"]["artifact_ref"],
            "voice-ai-artifact:run-valid-1",
        )
        self.assertIn("receipt-valid-1", durable)

    def test_artifact_sha_mismatch_fails_closed_without_final_verified_cache(self) -> None:
        job = self.submit_default()
        provider = FakeProvider(
            artifact=b"wrong",
            result={
                "status": "PASS",
                "request_id": job["request_id"],
                "run_id": "fake-run-2",
                "artifact_ref": "voice-ai-artifact:fake-run-2",
                "artifact_sha256": hashlib.sha256(b"expected").hexdigest(),
                "receipt_ref": "receipt-2",
            },
        )
        final = runner.execute_job(self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT)
        self.assertEqual(final["status"], "TERMINAL_FAIL_CLOSED")
        self.assertEqual(final["last_error"], "ARTIFACT_SHA256_MISMATCH")
        self.assertFalse((self.runtime / "artifact-cache" / f"{job['descriptor_sha256']}.bin").exists())

    def test_status_and_result_are_read_only(self) -> None:
        job = self.submit_default()
        status_value = runner.status(self.runtime, job["descriptor_sha256"])
        self.assertEqual(status_value["status"], "QUEUED")
        with self.assertRaisesRegex(runner.RunnerError, "JOB_NOT_TERMINAL"):
            runner.result(self.runtime, job["descriptor_sha256"])
        provider = FakeProvider()
        runner.execute_job(self.runtime, job["descriptor_sha256"], provider, project_root=PROJECT)
        speech_count = provider.speech_calls
        result_value = runner.result(self.runtime, job["descriptor_sha256"])
        status_value = runner.status(self.runtime, job["descriptor_sha256"])
        self.assertEqual(result_value["status"], "TERMINAL_PASS")
        self.assertEqual(status_value["status"], "TERMINAL_PASS")
        self.assertEqual(provider.speech_calls, speech_count)

    def test_permissions_and_no_full_text_persistence(self) -> None:
        job = self.submit_default()
        text = self.render.read_text(encoding="utf-8")
        self.assertEqual(stat.S_IMODE(self.runtime.stat().st_mode), 0o700)
        for name in runner.SUBDIRS:
            self.assertEqual(stat.S_IMODE((self.runtime / name).stat().st_mode), 0o700)
        for path in list((self.runtime / "claims").glob("*.json")) + list((self.runtime / "jobs").glob("*.json")):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertNotIn(text, path.read_text(encoding="utf-8"))
        self.assertNotIn("text", json.dumps(job, ensure_ascii=False))

    def test_production_root_is_external_to_git_worktree(self) -> None:
        self.assertEqual(
            runner.PRODUCTION_ROOT,
            Path("/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud"),
        )
        self.assertFalse(runner.PRODUCTION_ROOT.is_relative_to(PROJECT))


if __name__ == "__main__":
    unittest.main()
