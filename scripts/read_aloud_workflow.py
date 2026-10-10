#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import read_aloud_s4_runner as s4

SCHEMA = "ronniecross-readaloud-workflow/v0"
DEFAULT_ROOT = s4.PRODUCTION_ROOT
WORKFLOW_DIR = "workflows"

TERMINAL_WORKFLOW_STATES = {
    "TERMINAL_BLOCKED",
    "TERMINAL_FAIL_CLOSED",
    "COMPLETE",
}

AUTO_STATES = {
    "RENDER_READY",
    "TTS_SUBMITTED",
    "TTS_RUNNING",
    "WAIT_PROVIDER",
    "WAV_VERIFIED",
}

HUMAN_OR_OPERATOR_STATES = {
    "RESULT_UNKNOWN_OPERATOR_REQUIRED",
    "WAIT_HUMAN_LISTENING",
    "WAIT_HUMAN_DEVICE_ACCEPTANCE",
}


class WorkflowError(RuntimeError):
    pass


def _workflow_dir(root: Path) -> Path:
    path = root / WORKFLOW_DIR
    path.mkdir(parents=True, exist_ok=True, mode=s4.DIR_MODE)
    os.chmod(path, s4.DIR_MODE)
    return path


def _workflow_path(root: Path, workflow_id: str) -> Path:
    if len(workflow_id) != 64 or any(c not in "0123456789abcdef" for c in workflow_id):
        raise WorkflowError("WORKFLOW_ID_INVALID")
    return _workflow_dir(root) / f"{workflow_id}.json"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowError("WORKFLOW_STATE_CORRUPT") from exc
    if not isinstance(value, dict):
        raise WorkflowError("WORKFLOW_STATE_CORRUPT")
    return value


def _cleanup_gate(workflow: dict[str, Any]) -> dict[str, Any]:
    human = workflow.get("human_listening")
    nas = workflow.get("nas_archive")
    r2 = workflow.get("r2_delivery")
    live = workflow.get("website_live")
    repair = workflow.get("repair_support")
    checks = {
        "human_listening_pass": isinstance(human, dict) and human.get("status") == "PASS",
        "nas_archive_verified": isinstance(nas, dict) and nas.get("verified") is True,
        "r2_delivery_verified": isinstance(r2, dict) and r2.get("verified") is True,
        "website_live_verified": isinstance(live, dict) and live.get("verified") is True,
        "repair_support_complete": isinstance(repair, dict) and repair.get("complete") is True,
        "no_open_repairs": workflow.get("open_repairs") == 0,
    }
    eligible = all(checks.values())
    return {
        "status": "CLEANUP_ELIGIBLE" if eligible else "NOT_ELIGIBLE",
        "eligible": eligible,
        "checks": checks,
        "deletable_scope": [
            "worktree human-review WAV/MP3",
            "runtime artifact-cache media for this workflow",
            "runtime delivery-cache media for this workflow",
        ],
        "preserve_scope": [
            "jobs/claims/workflows JSON",
            "task/evidence + Render View",
            "repair-support metadata",
            "NAS authoritative WAV/manifest",
            "R2 delivery",
        ],
    }


def _persist(root: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    workflow["automatic_action_available"] = workflow.get("state") in AUTO_STATES
    workflow["operator_or_human_required"] = workflow.get("state") in HUMAN_OR_OPERATOR_STATES
    workflow["implementation_pending"] = False
    workflow["cleanup"] = _cleanup_gate(workflow)
    s4.atomic_write_json(_workflow_path(root, workflow["workflow_id"]), workflow)
    return workflow


def _descriptor(
    *,
    authorization_ref: str,
    generation_epoch: str,
    operation_id: str,
    article_id: str,
    render_sha256: str,
) -> dict[str, str]:
    return {
        "schema": s4.SCHEMA,
        "authorization_ref": authorization_ref,
        "generation_epoch": generation_epoch,
        "operation_id": operation_id,
        "article_id": article_id,
        "render_sha256": render_sha256,
        "voice_contract_id": s4.VOICE_CONTRACT_ID,
    }


def start_workflow(
    root: Path,
    *,
    authorization_ref: str,
    generation_epoch: str,
    operation_id: str,
    article_id: str,
    render_sha256: str,
    render_ref: str,
) -> dict[str, Any]:
    descriptor = _descriptor(
        authorization_ref=authorization_ref,
        generation_epoch=generation_epoch,
        operation_id=operation_id,
        article_id=article_id,
        render_sha256=render_sha256,
    )
    workflow_id = s4.descriptor_sha256(descriptor)
    path = _workflow_path(root, workflow_id)
    expected_identity = {
        "descriptor": descriptor,
        "render_ref": render_ref,
        "workflow_id": workflow_id,
    }
    if path.exists():
        existing = _load_json(path)
        for key, value in expected_identity.items():
            if existing.get(key) != value:
                raise WorkflowError("WORKFLOW_IDENTITY_CONFLICT")
        return existing

    workflow: dict[str, Any] = {
        "schema": SCHEMA,
        "workflow_id": workflow_id,
        "descriptor": descriptor,
        "render_ref": render_ref,
        "state": "RENDER_READY",
        "s4_job_id": None,
        "request_id": None,
        "worker_pid": None,
        "artifact": None,
        "last_error": None,
        "next_action": "ACTIVATE_TTS",
    }
    return _persist(root, workflow)


def workflow_status(root: Path, workflow_id: str) -> dict[str, Any]:
    path = _workflow_path(root, workflow_id)
    if not path.exists():
        raise WorkflowError("WORKFLOW_NOT_FOUND")
    return _load_json(path)


def _pid_alive(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _execution_owner(root: Path) -> dict[str, Any] | None:
    path = s4.execution_lock_path(root)
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise WorkflowError("EXECUTION_OWNER_CORRUPT")
    if not isinstance(value, dict):
        raise WorkflowError("EXECUTION_OWNER_CORRUPT")
    return value


def _default_spawn_worker() -> int:
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).with_name("read_aloud_s4_runner.py")), "worker-once"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    return int(proc.pid)


def _verify_terminal_artifact(root: Path, job: dict[str, Any]) -> dict[str, Any]:
    artifact = job.get("artifact")
    if not isinstance(artifact, dict) or artifact.get("verified") is not True:
        raise WorkflowError("TERMINAL_PASS_ARTIFACT_INVALID")
    cache_name = artifact.get("cache_name")
    expected_sha = artifact.get("artifact_sha256")
    if not isinstance(cache_name, str) or not cache_name:
        raise WorkflowError("TERMINAL_PASS_ARTIFACT_INVALID")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise WorkflowError("TERMINAL_PASS_ARTIFACT_INVALID")
    path = root / "artifact-cache" / cache_name
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise WorkflowError("TERMINAL_PASS_ARTIFACT_MISSING") from exc
    actual_sha = hashlib.sha256(data).hexdigest()
    if actual_sha != expected_sha:
        raise WorkflowError("TERMINAL_PASS_ARTIFACT_SHA_MISMATCH")
    return {
        "cache_name": cache_name,
        "artifact_ref": artifact.get("artifact_ref"),
        "artifact_sha256": expected_sha,
        "bytes": len(data),
        "verified": True,
    }




def _run_checked(command: list[str], failure_code: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise WorkflowError(failure_code) from exc


def _probe_audio(path: Path) -> dict[str, Any]:
    proc = _run_checked(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bit_rate",
            "-show_entries",
            "format=duration,size,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        "FFPROBE_FAILED",
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise WorkflowError("FFPROBE_JSON_INVALID") from exc
    streams = payload.get("streams")
    fmt = payload.get("format")
    if not isinstance(streams, list) or len(streams) != 1 or not isinstance(streams[0], dict):
        raise WorkflowError("AUDIO_STREAM_LAYOUT_INVALID")
    if not isinstance(fmt, dict):
        raise WorkflowError("AUDIO_FORMAT_INVALID")
    return {"stream": streams[0], "format": fmt}


def _float_value(value: Any, code: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowError(code) from exc


def _int_value(value: Any, code: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowError(code) from exc


def _technical_qc_and_encode(root: Path, workflow: dict[str, Any]) -> dict[str, Any]:
    artifact = workflow.get("artifact")
    if not isinstance(artifact, dict):
        raise WorkflowError("WAV_ARTIFACT_MISSING")
    cache_name = artifact.get("cache_name")
    if not isinstance(cache_name, str) or not cache_name:
        raise WorkflowError("WAV_ARTIFACT_MISSING")
    wav = root / "artifact-cache" / cache_name
    if not wav.is_file():
        raise WorkflowError("WAV_ARTIFACT_MISSING")

    wav_probe = _probe_audio(wav)
    wav_stream = wav_probe["stream"]
    wav_format = wav_probe["format"]
    if wav_stream.get("codec_name") != "pcm_f32le":
        raise WorkflowError("WAV_CODEC_INVALID")
    if _int_value(wav_stream.get("sample_rate"), "WAV_SAMPLE_RATE_INVALID") != 24000:
        raise WorkflowError("WAV_SAMPLE_RATE_INVALID")
    if _int_value(wav_stream.get("channels"), "WAV_CHANNELS_INVALID") != 1:
        raise WorkflowError("WAV_CHANNELS_INVALID")
    wav_duration = _float_value(wav_format.get("duration"), "WAV_DURATION_INVALID")
    if wav_duration <= 0:
        raise WorkflowError("WAV_DURATION_INVALID")

    _run_checked(
        ["ffmpeg", "-v", "error", "-i", str(wav), "-f", "null", "-"],
        "WAV_FULL_DECODE_FAILED",
    )

    delivery_dir = root / "delivery-cache" / workflow["workflow_id"]
    delivery_dir.mkdir(parents=True, exist_ok=True, mode=s4.DIR_MODE)
    os.chmod(delivery_dir, s4.DIR_MODE)
    final_mp3 = delivery_dir / "article-64k.mp3"
    temp_mp3 = delivery_dir / ".article-64k.mp3.tmp"

    _run_checked(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(wav),
            "-ac",
            "1",
            "-ar",
            "24000",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "64k",
            "-f",
            "mp3",
            str(temp_mp3),
        ],
        "MP3_ENCODE_FAILED",
    )
    os.replace(temp_mp3, final_mp3)
    os.chmod(final_mp3, s4.FILE_MODE)
    s4._fsync_dir(delivery_dir)

    _run_checked(
        ["ffmpeg", "-v", "error", "-i", str(final_mp3), "-f", "null", "-"],
        "MP3_FULL_DECODE_FAILED",
    )
    mp3_probe = _probe_audio(final_mp3)
    mp3_stream = mp3_probe["stream"]
    mp3_format = mp3_probe["format"]
    if mp3_stream.get("codec_name") != "mp3":
        raise WorkflowError("MP3_CODEC_INVALID")
    if _int_value(mp3_stream.get("sample_rate"), "MP3_SAMPLE_RATE_INVALID") != 24000:
        raise WorkflowError("MP3_SAMPLE_RATE_INVALID")
    if _int_value(mp3_stream.get("channels"), "MP3_CHANNELS_INVALID") != 1:
        raise WorkflowError("MP3_CHANNELS_INVALID")
    mp3_duration = _float_value(mp3_format.get("duration"), "MP3_DURATION_INVALID")
    if mp3_duration <= 0 or abs(mp3_duration - wav_duration) > 1.0:
        raise WorkflowError("MP3_DURATION_INVALID")

    mp3_bytes = final_mp3.read_bytes()
    mp3_sha = hashlib.sha256(mp3_bytes).hexdigest()
    workflow["technical_qc"] = {
        "wav_codec": "pcm_f32le",
        "wav_sample_rate_hz": 24000,
        "wav_channels": 1,
        "wav_duration_sec": round(wav_duration, 3),
        "wav_full_decode": "PASS",
        "mp3_codec": "mp3",
        "mp3_sample_rate_hz": 24000,
        "mp3_channels": 1,
        "mp3_duration_sec": round(mp3_duration, 3),
        "mp3_full_decode": "PASS",
        "delivery_bitrate_kbps": 64,
    }
    workflow["delivery"] = {
        "relative_path": str(final_mp3.relative_to(root)),
        "absolute_path": str(final_mp3),
        "sha256": mp3_sha,
        "bytes": len(mp3_bytes),
        "codec": "mp3",
        "bitrate_kbps": 64,
        "sample_rate_hz": 24000,
        "channels": 1,
        "duration_sec": round(mp3_duration, 3),
    }
    workflow["state"] = "WAIT_HUMAN_LISTENING"
    workflow["last_error"] = None
    workflow["next_action"] = "HUMAN_LISTENING"
    return _persist(root, workflow)


def _consume_s4_state(
    root: Path,
    workflow: dict[str, Any],
    *,
    spawn_worker: Callable[[], int],
) -> dict[str, Any]:
    job_id = workflow.get("s4_job_id")
    if not isinstance(job_id, str):
        raise WorkflowError("S4_JOB_ID_MISSING")
    _, job = s4._job_by_id(root, job_id)
    status = job.get("status")

    if status == "TERMINAL_PASS":
        try:
            verified = _verify_terminal_artifact(root, job)
        except WorkflowError as exc:
            workflow["state"] = "TERMINAL_FAIL_CLOSED"
            workflow["last_error"] = str(exc)
            workflow["next_action"] = "STOP"
            return _persist(root, workflow)
        workflow["artifact"] = verified
        workflow["state"] = "WAV_VERIFIED"
        workflow["last_error"] = None
        workflow["worker_pid"] = None
        workflow["next_action"] = "TECHNICAL_QC"
        return _persist(root, workflow)

    if status == "TERMINAL_BLOCKED":
        workflow["state"] = "TERMINAL_BLOCKED"
        workflow["last_error"] = job.get("last_error")
        workflow["next_action"] = "STOP"
        workflow["worker_pid"] = None
        return _persist(root, workflow)

    if status == "TERMINAL_FAIL_CLOSED":
        workflow["state"] = "TERMINAL_FAIL_CLOSED"
        workflow["last_error"] = job.get("last_error")
        workflow["next_action"] = "STOP"
        workflow["worker_pid"] = None
        return _persist(root, workflow)

    owner = _execution_owner(root)
    if status == "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN":
        if owner is not None and owner.get("job_id") == job_id and _pid_alive(owner.get("pid")):
            workflow["state"] = "TTS_RUNNING"
            workflow["worker_pid"] = owner.get("pid")
            workflow["last_error"] = None
            workflow["next_action"] = "WAIT_TTS"
            return _persist(root, workflow)
        workflow["state"] = "RESULT_UNKNOWN_OPERATOR_REQUIRED"
        workflow["worker_pid"] = None
        workflow["last_error"] = "S4_RESULT_UNKNOWN_WITHOUT_LIVE_OWNER"
        workflow["next_action"] = "SAFE_SAME_ID_RECONCILE_REVIEW"
        return _persist(root, workflow)

    if owner is not None:
        if owner.get("job_id") == job_id and _pid_alive(owner.get("pid")):
            workflow["state"] = "TTS_RUNNING"
            workflow["worker_pid"] = owner.get("pid")
            workflow["last_error"] = None
            workflow["next_action"] = "WAIT_TTS"
            return _persist(root, workflow)
        workflow["state"] = "RESULT_UNKNOWN_OPERATOR_REQUIRED"
        workflow["worker_pid"] = None
        workflow["last_error"] = "STALE_OR_FOREIGN_EXECUTION_OWNER"
        workflow["next_action"] = "OPERATOR_REVIEW"
        return _persist(root, workflow)

    if status in {"QUEUED", "WAITING_PROVIDER_READY"}:
        pid = spawn_worker()
        workflow["state"] = "TTS_RUNNING" if status == "QUEUED" else "WAIT_PROVIDER"
        workflow["worker_pid"] = pid
        workflow["last_error"] = None
        workflow["next_action"] = "WAIT_TTS" if status == "QUEUED" else "RECHECK_PROVIDER"
        return _persist(root, workflow)

    workflow["state"] = "TERMINAL_FAIL_CLOSED"
    workflow["last_error"] = "S4_STATUS_UNRECOGNIZED"
    workflow["next_action"] = "STOP"
    return _persist(root, workflow)


def tick_workflow(
    root: Path,
    workflow_id: str,
    *,
    spawn_worker: Callable[[], int] = _default_spawn_worker,
) -> dict[str, Any]:
    workflow = workflow_status(root, workflow_id)
    state = workflow.get("state")
    if state in TERMINAL_WORKFLOW_STATES or state in HUMAN_OR_OPERATOR_STATES:
        return workflow

    if state == "RENDER_READY":
        descriptor = workflow["descriptor"]
        job = s4.submit(
            root,
            descriptor,
            workflow["render_ref"],
            supplied_request_id=s4.derive_request_id(descriptor),
        )
        workflow["s4_job_id"] = job["descriptor_sha256"]
        workflow["request_id"] = job["request_id"]
        workflow["state"] = "TTS_SUBMITTED"
        workflow["last_error"] = None
        workflow["next_action"] = "START_OR_OBSERVE_TTS"
        _persist(root, workflow)
        return _consume_s4_state(root, workflow, spawn_worker=spawn_worker)

    if state in {"TTS_SUBMITTED", "TTS_RUNNING", "WAIT_PROVIDER"}:
        return _consume_s4_state(root, workflow, spawn_worker=spawn_worker)

    if state == "WAV_VERIFIED":
        try:
            return _technical_qc_and_encode(root, workflow)
        except WorkflowError as exc:
            workflow["state"] = "TERMINAL_FAIL_CLOSED"
            workflow["last_error"] = str(exc)
            workflow["next_action"] = "STOP"
            return _persist(root, workflow)

    workflow["state"] = "TERMINAL_FAIL_CLOSED"
    workflow["last_error"] = "WORKFLOW_STATE_UNRECOGNIZED"
    workflow["next_action"] = "STOP"
    return _persist(root, workflow)




def attach_repair_support(root: Path, workflow_id: str, support_path: Path) -> dict[str, Any]:
    workflow = workflow_status(root, workflow_id)
    try:
        raw = support_path.read_bytes()
        support = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkflowError("REPAIR_SUPPORT_INVALID") from exc
    if not isinstance(support, dict) or support.get("schema") != "ronniecross-readaloud-repair-support/v1":
        raise WorkflowError("REPAIR_SUPPORT_INVALID")
    descriptor = workflow.get("descriptor")
    artifact = workflow.get("artifact")
    if not isinstance(descriptor, dict) or not isinstance(artifact, dict):
        raise WorkflowError("REPAIR_SUPPORT_WORKFLOW_NOT_READY")
    expected = {
        "article_id": descriptor.get("article_id"),
        "workflow_id": workflow_id,
        "request_id": workflow.get("request_id"),
        "generation_epoch": descriptor.get("generation_epoch"),
        "render_sha256": descriptor.get("render_sha256"),
        "final_wav_sha256": artifact.get("artifact_sha256"),
    }
    for key, value in expected.items():
        if support.get(key) != value:
            raise WorkflowError(f"REPAIR_SUPPORT_{key.upper()}_MISMATCH")
    if support.get("sample_rate_hz") != 24000:
        raise WorkflowError("REPAIR_SUPPORT_SAMPLE_RATE_INVALID")
    chunks = support.get("chunks")
    total_frames = support.get("total_frames")
    if not isinstance(chunks, list) or not chunks or not isinstance(total_frames, int) or total_frames <= 0:
        raise WorkflowError("REPAIR_SUPPORT_CHUNK_MAP_INVALID")
    cursor = 0
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            raise WorkflowError("REPAIR_SUPPORT_CHUNK_MAP_INVALID")
        if chunk.get("chunk_index") != index or chunk.get("start_frame") != cursor:
            raise WorkflowError("REPAIR_SUPPORT_CHUNK_MAP_INVALID")
        frames = chunk.get("frames")
        end = chunk.get("end_frame_exclusive")
        if not isinstance(frames, int) or frames <= 0 or end != cursor + frames:
            raise WorkflowError("REPAIR_SUPPORT_CHUNK_MAP_INVALID")
        cursor = end
    if cursor != total_frames:
        raise WorkflowError("REPAIR_SUPPORT_CHUNK_MAP_INVALID")
    workflow["repair_support"] = {
        "complete": True,
        "schema": support["schema"],
        "path": str(support_path.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "chunk_count": len(chunks),
        "total_frames": total_frames,
        "sample_rate_hz": 24000,
        "exact_text_to_chunk_alignment": support.get("exact_text_to_chunk_alignment") is True,
    }
    return _persist(root, workflow)


def tick_all(
    root: Path,
    *,
    spawn_worker: Callable[[], int] = _default_spawn_worker,
) -> list[dict[str, Any]]:
    directory = _workflow_dir(root)
    results: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        workflow = _load_json(path)
        if workflow.get("state") in TERMINAL_WORKFLOW_STATES:
            continue
        results.append(tick_workflow(root, workflow["workflow_id"], spawn_worker=spawn_worker))
    return results


def _root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.runtime_root).resolve() if args.runtime_root else DEFAULT_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Durable RonnieCross read-aloud workflow controller")
    parser.add_argument("--runtime-root", help="Override runtime root for tests/controlled use")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--authorization-ref", required=True)
    p_start.add_argument("--generation-epoch", required=True)
    p_start.add_argument("--operation-id", required=True)
    p_start.add_argument("--article-id", required=True)
    p_start.add_argument("--render-sha256", required=True)
    p_start.add_argument("--render-ref", required=True)

    for name in ("status", "tick"):
        p = sub.add_parser(name)
        p.add_argument("--workflow-id", required=True)

    p_repair = sub.add_parser("attach-repair-support")
    p_repair.add_argument("--workflow-id", required=True)
    p_repair.add_argument("--path", required=True)

    sub.add_parser("tick-all")

    args = parser.parse_args()
    root = _root_from_args(args)
    try:
        if args.command == "start":
            value: Any = start_workflow(
                root,
                authorization_ref=args.authorization_ref,
                generation_epoch=args.generation_epoch,
                operation_id=args.operation_id,
                article_id=args.article_id,
                render_sha256=args.render_sha256,
                render_ref=args.render_ref,
            )
        elif args.command == "status":
            value = workflow_status(root, args.workflow_id)
        elif args.command == "tick":
            value = tick_workflow(root, args.workflow_id)
        elif args.command == "attach-repair-support":
            value = attach_repair_support(root, args.workflow_id, Path(args.path))
        elif args.command == "tick-all":
            value = tick_all(root)
        else:
            raise WorkflowError("COMMAND_INVALID")
    except (WorkflowError, s4.RunnerError) as exc:
        print(json.dumps({"status": "BLOCKED", "failure_code": str(exc)}, separators=(",", ":")))
        return 2

    print(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
