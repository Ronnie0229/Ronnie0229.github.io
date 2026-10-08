#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

SCHEMA = "ronniecross-readaloud-generation-operation/v1"
VOICE_CONTRACT_ID = "VOICE_AI_LOCAL_HTTP_V1"
PRODUCTION_ROOT = Path("/Volumes/DevSSD/RonnieWork/RonnieCross/runtime/read-aloud")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$", re.ASCII)
STATES = {
    "QUEUED",
    "WAITING_PROVIDER_READY",
    "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN",
    "TERMINAL_PASS",
    "TERMINAL_BLOCKED",
    "TERMINAL_FAIL_CLOSED",
}
TERMINAL_STATES = {"TERMINAL_PASS", "TERMINAL_BLOCKED", "TERMINAL_FAIL_CLOSED"}
DIR_MODE = 0o700
FILE_MODE = 0o600
SUBDIRS = ("jobs", "claims", "tmp", "artifact-cache", "logs")
EXECUTION_LOCK_NAME = "execution-owner.json"
MAX_PROVIDER_ID_LENGTH = 1024
MAX_FAILURE_CODE_LENGTH = 256


class RunnerError(RuntimeError):
    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


class Provider(Protocol):
    def ready(self) -> bool: ...
    def speech(self, text: str, request_id: str) -> dict[str, Any]: ...
    def artifact(self, artifact_ref: str) -> bytes: ...


def canonical_descriptor(descriptor: dict[str, str]) -> bytes:
    required = {
        "schema",
        "authorization_ref",
        "generation_epoch",
        "operation_id",
        "article_id",
        "render_sha256",
        "voice_contract_id",
    }
    if set(descriptor) != required:
        raise RunnerError("DESCRIPTOR_SCHEMA_INVALID")
    if descriptor["schema"] != SCHEMA:
        raise RunnerError("DESCRIPTOR_SCHEMA_INVALID")
    if descriptor["voice_contract_id"] != VOICE_CONTRACT_ID:
        raise RunnerError("VOICE_CONTRACT_ID_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", descriptor["render_sha256"]):
        raise RunnerError("RENDER_SHA256_INVALID")
    for key, value in descriptor.items():
        if not isinstance(value, str) or not value:
            raise RunnerError("DESCRIPTOR_FIELD_INVALID", key)
    return json.dumps(
        descriptor, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def descriptor_sha256(descriptor: dict[str, str]) -> str:
    return hashlib.sha256(canonical_descriptor(descriptor)).hexdigest()


def derive_request_id(descriptor: dict[str, str]) -> str:
    request_id = "rc-readaloud-v1:" + descriptor_sha256(descriptor)
    if REQUEST_ID_RE.fullmatch(request_id) is None:
        raise RunnerError("REQUEST_ID_INVALID")
    return request_id


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("short write")
        view = view[written:]


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=DIR_MODE)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        os.fchmod(fd, FILE_MODE)
        _write_all(fd, _json_bytes(payload))
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(temp, path)
        os.chmod(path, FILE_MODE)
        _fsync_dir(path.parent)
    except Exception:
        if fd >= 0:
            os.close(fd)
        temp.unlink(missing_ok=True)
        raise


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=DIR_MODE)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        os.fchmod(fd, FILE_MODE)
        _write_all(fd, data)
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(temp, path)
        os.chmod(path, FILE_MODE)
        _fsync_dir(path.parent)
    except Exception:
        if fd >= 0:
            os.close(fd)
        temp.unlink(missing_ok=True)
        raise


def ensure_runtime_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True, mode=DIR_MODE)
    os.chmod(root, DIR_MODE)
    for name in SUBDIRS:
        path = root / name
        path.mkdir(exist_ok=True, mode=DIR_MODE)
        os.chmod(path, DIR_MODE)


def execution_lock_path(root: Path) -> Path:
    return root / EXECUTION_LOCK_NAME


def _acquire_execution_lock(root: Path, job_id: str, request_id: str) -> str:
    ensure_runtime_root(root)
    path = execution_lock_path(root)
    token = secrets.token_hex(16)
    payload = {
        "schema": "ronniecross-readaloud-s4-execution-owner/v1",
        "token": token,
        "pid": os.getpid(),
        "job_id": job_id,
        "request_id": request_id,
    }
    data = _json_bytes(payload)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    except FileExistsError as exc:
        raise RunnerError("EXECUTION_BUSY_OR_STALE_LOCK") from exc
    try:
        os.fchmod(fd, FILE_MODE)
        _write_all(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(root)
    return token


def _release_execution_lock(root: Path, token: str) -> None:
    path = execution_lock_path(root)
    try:
        current = _load_json(path, "EXECUTION_LOCK_CORRUPT")
    except RunnerError:
        # Never delete an ambiguous lock. Manual/operator recovery is required.
        raise
    if current.get("token") != token:
        raise RunnerError("EXECUTION_LOCK_OWNERSHIP_MISMATCH")
    path.unlink()
    _fsync_dir(root)


def claim_key(authorization_ref: str, generation_epoch: str) -> str:
    payload = json.dumps(
        [authorization_ref, generation_epoch],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def claim_path(root: Path, descriptor: dict[str, str]) -> Path:
    return root / "claims" / f"{claim_key(descriptor['authorization_ref'], descriptor['generation_epoch'])}.json"


def job_path(root: Path, descriptor: dict[str, str]) -> Path:
    return root / "jobs" / f"{descriptor_sha256(descriptor)}.json"


def _load_json(path: Path, failure_code: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise RunnerError(failure_code) from exc
    if not isinstance(value, dict):
        raise RunnerError(failure_code)
    return value


def _claim_payload(descriptor: dict[str, str], request_id: str) -> dict[str, str]:
    return {
        "authorization_ref": descriptor["authorization_ref"],
        "generation_epoch": descriptor["generation_epoch"],
        "descriptor_sha256": descriptor_sha256(descriptor),
        "request_id": request_id,
        "operation_id": descriptor["operation_id"],
        "article_id": descriptor["article_id"],
        "render_sha256": descriptor["render_sha256"],
        "voice_contract_id": descriptor["voice_contract_id"],
    }


def _claim_matches(claim: dict[str, Any], expected: dict[str, str]) -> bool:
    return claim == expected


def _load_existing_claim_after_exclusive_race(path: Path) -> dict[str, Any]:
    # A successful O_EXCL create makes the pathname visible before the creator
    # finishes writing and fsyncing. Exact duplicate callers may wait briefly for
    # that same claim to reach durable JSON completion, but never delete, replace,
    # expire, or take over an incomplete claim. Persistent incompleteness remains
    # operator-required fail-closed, preserving the frozen crash invariant.
    for attempt in range(100):
        try:
            return _load_json(path, "AUTHORIZATION_CLAIM_CORRUPT")
        except RunnerError:
            if attempt == 99:
                raise
            time.sleep(0.01)
    raise RunnerError("AUTHORIZATION_CLAIM_CORRUPT")


def _exclusive_create_claim(path: Path, payload: dict[str, str]) -> bool:
    data = _json_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(path, flags, FILE_MODE)
    except FileExistsError:
        return False
    try:
        os.fchmod(fd, FILE_MODE)
        _write_all(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(path.parent)
    return True


def _validate_supplied_request_id(descriptor: dict[str, str], supplied: str | None) -> str:
    derived = derive_request_id(descriptor)
    if supplied is not None and supplied != derived:
        raise RunnerError("REQUEST_ID_DESCRIPTOR_MISMATCH")
    return derived


def submit(
    root: Path,
    descriptor: dict[str, str],
    render_ref: str,
    *,
    supplied_request_id: str | None = None,
) -> dict[str, Any]:
    request_id = _validate_supplied_request_id(descriptor, supplied_request_id)
    ensure_runtime_root(root)
    expected_claim = _claim_payload(descriptor, request_id)
    cpath = claim_path(root, descriptor)

    created = _exclusive_create_claim(cpath, expected_claim)
    if not created:
        existing = _load_existing_claim_after_exclusive_race(cpath)
        if not _claim_matches(existing, expected_claim):
            raise RunnerError("AUTHORIZATION_IDENTITY_CONFLICT")

    jpath = job_path(root, descriptor)
    if jpath.exists():
        job = _load_json(jpath, "JOB_STATE_CORRUPT")
        if (
            job.get("descriptor") != descriptor
            or job.get("request_id") != request_id
            or job.get("render_ref") != render_ref
        ):
            raise RunnerError("JOB_IDENTITY_CONFLICT")
        return job

    job = {
        "schema": "ronniecross-readaloud-s4-job/v1",
        "descriptor": descriptor,
        "descriptor_sha256": descriptor_sha256(descriptor),
        "request_id": request_id,
        "render_ref": render_ref,
        "status": "QUEUED",
        "provider_result": None,
        "artifact": None,
        "last_error": None,
    }
    atomic_write_json(jpath, job)
    return job


def _safe_render_bytes(project_root: Path, render_ref: str) -> bytes:
    rel = PurePosixPath(render_ref)
    if rel.is_absolute() or not rel.parts or any(part in ("", ".", "..") for part in rel.parts):
        raise RunnerError("RENDER_PATH_INVALID")

    flags_dir = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    flags_file = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    opened: list[int] = []
    try:
        current = os.open(project_root, flags_dir)
        opened.append(current)
        for part in rel.parts[:-1]:
            current = os.open(part, flags_dir, dir_fd=current)
            opened.append(current)
        leaf_fd = os.open(rel.parts[-1], flags_file, dir_fd=current)
        opened.append(leaf_fd)
        st = os.fstat(leaf_fd)
        if not stat.S_ISREG(st.st_mode):
            raise RunnerError("RENDER_NOT_REGULAR_FILE")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(leaf_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    except RunnerError:
        raise
    except FileNotFoundError as exc:
        raise RunnerError("RENDER_MISSING") from exc
    except PermissionError as exc:
        raise RunnerError("RENDER_UNREADABLE") from exc
    except OSError as exc:
        raise RunnerError("RENDER_PATH_AMBIGUOUS") from exc
    finally:
        for fd in reversed(opened):
            try:
                os.close(fd)
            except OSError:
                pass


def validated_render_text(
    project_root: Path,
    render_ref: str,
    expected_sha256: str,
) -> tuple[bytes, str]:
    raw = _safe_render_bytes(project_root, render_ref)
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise RunnerError("RENDER_SHA256_MISMATCH")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RunnerError("RENDER_UTF8_DECODE_FAILED") from exc
    return raw, text


def _job_by_id(root: Path, job_id: str) -> tuple[Path, dict[str, Any]]:
    if re.fullmatch(r"[0-9a-f]{64}", job_id) is None:
        raise RunnerError("JOB_ID_INVALID")
    path = root / "jobs" / f"{job_id}.json"
    if not path.exists():
        raise RunnerError("JOB_NOT_FOUND")
    return path, _load_json(path, "JOB_STATE_CORRUPT")


def status(root: Path, job_id: str) -> dict[str, Any]:
    _, job = _job_by_id(root, job_id)
    return {
        "job_id": job["descriptor_sha256"],
        "request_id": job["request_id"],
        "status": job["status"],
        "last_error": job.get("last_error"),
    }


def result(root: Path, job_id: str) -> dict[str, Any]:
    _, job = _job_by_id(root, job_id)
    if job["status"] not in TERMINAL_STATES:
        raise RunnerError("JOB_NOT_TERMINAL")
    return {
        "job_id": job["descriptor_sha256"],
        "request_id": job["request_id"],
        "status": job["status"],
        "provider_result": job.get("provider_result"),
        "artifact": job.get("artifact"),
    }


def _verify_claim_for_job(root: Path, job: dict[str, Any]) -> None:
    descriptor = job["descriptor"]
    expected = _claim_payload(descriptor, job["request_id"])
    path = claim_path(root, descriptor)
    if not path.exists():
        raise RunnerError("AUTHORIZATION_CLAIM_MISSING")
    existing = _load_json(path, "AUTHORIZATION_CLAIM_CORRUPT")
    if not _claim_matches(existing, expected):
        raise RunnerError("AUTHORIZATION_IDENTITY_CONFLICT")


def _persist_job(path: Path, job: dict[str, Any]) -> dict[str, Any]:
    if job.get("status") not in STATES:
        raise RunnerError("JOB_STATUS_INVALID")
    atomic_write_json(path, job)
    return job


def _bounded_nonempty_string(value: Any, *, max_length: int) -> bool:
    return isinstance(value, str) and 0 < len(value) <= max_length


def _provider_result_evidence(
    job: dict[str, Any],
    provider_result: dict[str, Any],
) -> dict[str, Any]:
    # Provider values are untrusted. Durable diagnostic evidence must be both
    # individually bounded and semantically attributable to the current job and
    # raw terminal status. Invalid values are omitted, never truncated, repaired,
    # normalized, or reused as terminal truth.
    status = provider_result.get("status")
    if not isinstance(status, str):
        return {}
    if status not in {"PASS", "BLOCKED", "FAIL_CLOSED"}:
        return {}

    evidence: dict[str, Any] = {"status": status}

    request_id = provider_result.get("request_id")
    request_matches_job = (
        isinstance(request_id, str)
        and REQUEST_ID_RE.fullmatch(request_id) is not None
        and request_id == job["request_id"]
    )
    if not request_matches_job:
        return evidence

    evidence["request_id"] = request_id

    if status == "PASS":
        for key in ("run_id", "artifact_ref", "receipt_ref"):
            value = provider_result.get(key)
            if _bounded_nonempty_string(value, max_length=MAX_PROVIDER_ID_LENGTH):
                evidence[key] = value

        artifact_sha256 = provider_result.get("artifact_sha256")
        if (
            isinstance(artifact_sha256, str)
            and re.fullmatch(r"[0-9a-f]{64}", artifact_sha256) is not None
        ):
            evidence["artifact_sha256"] = artifact_sha256

        # PASS explicitly forbids non-empty failure_code. Never persist it,
        # even when it is otherwise bounded and syntactically valid.
        return evidence

    failure_code = provider_result.get("failure_code")
    if _bounded_nonempty_string(
        failure_code, max_length=MAX_FAILURE_CODE_LENGTH
    ):
        evidence["failure_code"] = failure_code

    # BLOCKED / FAIL_CLOSED do not persist PASS-only success identity fields.
    return evidence


def _validate_provider_terminal_result(job: dict[str, Any], provider_result: dict[str, Any]) -> None:
    provider_status = provider_result.get("status")
    if not isinstance(provider_status, str):
        raise RunnerError("PROVIDER_RESULT_STATUS_INVALID")
    if provider_status not in {"PASS", "BLOCKED", "FAIL_CLOSED"}:
        raise RunnerError("PROVIDER_RESULT_STATUS_INVALID")

    request_id = provider_result.get("request_id")
    if (
        not isinstance(request_id, str)
        or REQUEST_ID_RE.fullmatch(request_id) is None
        or request_id != job["request_id"]
    ):
        raise RunnerError("PROVIDER_RESULT_REQUEST_ID_MISMATCH")

    if provider_status == "PASS":
        for key in ("run_id", "artifact_ref", "receipt_ref"):
            if not _bounded_nonempty_string(
                provider_result.get(key), max_length=MAX_PROVIDER_ID_LENGTH
            ):
                raise RunnerError(f"PROVIDER_PASS_{key.upper()}_INVALID")
        artifact_sha256 = provider_result.get("artifact_sha256")
        if (
            not isinstance(artifact_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", artifact_sha256) is None
        ):
            raise RunnerError("PROVIDER_ARTIFACT_SHA_INVALID")
        if provider_result.get("failure_code") not in (None, ""):
            raise RunnerError("PROVIDER_PASS_FAILURE_CODE_INVALID")
        return

    failure_code = provider_result.get("failure_code")
    if not _bounded_nonempty_string(
        failure_code, max_length=MAX_FAILURE_CODE_LENGTH
    ):
        raise RunnerError("PROVIDER_FAILURE_CODE_INVALID")


def _finalize_artifact(
    root: Path,
    job: dict[str, Any],
    provider: Provider,
    provider_result: dict[str, Any],
) -> dict[str, Any]:
    artifact_ref = provider_result.get("artifact_ref")
    artifact_sha256 = provider_result.get("artifact_sha256")
    if not isinstance(artifact_ref, str) or not artifact_ref:
        raise RunnerError("PROVIDER_ARTIFACT_REF_INVALID")
    if not isinstance(artifact_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", artifact_sha256) is None:
        raise RunnerError("PROVIDER_ARTIFACT_SHA_INVALID")
    data = provider.artifact(artifact_ref)
    actual = hashlib.sha256(data).hexdigest()
    if actual != artifact_sha256:
        raise RunnerError("ARTIFACT_SHA256_MISMATCH")
    final_path = root / "artifact-cache" / f"{job['descriptor_sha256']}.bin"
    atomic_write_bytes(final_path, data)
    return {
        "artifact_ref": artifact_ref,
        "artifact_sha256": artifact_sha256,
        "cache_name": final_path.name,
        "verified": True,
    }


def _apply_provider_result(
    root: Path,
    path: Path,
    job: dict[str, Any],
    provider: Provider,
    provider_result: dict[str, Any],
) -> dict[str, Any]:
    evidence = _provider_result_evidence(job, provider_result)
    try:
        _validate_provider_terminal_result(job, provider_result)
    except RunnerError as exc:
        job["status"] = "TERMINAL_FAIL_CLOSED"
        job["last_error"] = exc.code
        job["provider_result"] = evidence
        job["artifact"] = None
        return _persist_job(path, job)

    provider_status = provider_result["status"]
    if provider_status == "PASS":
        try:
            artifact = _finalize_artifact(root, job, provider, provider_result)
        except RunnerError as exc:
            job["status"] = "TERMINAL_FAIL_CLOSED"
            job["last_error"] = exc.code
            job["provider_result"] = evidence
            job["artifact"] = None
            return _persist_job(path, job)
        job["status"] = "TERMINAL_PASS"
        job["provider_result"] = evidence
        job["artifact"] = artifact
        job["last_error"] = None
    elif provider_status == "BLOCKED":
        job["status"] = "TERMINAL_BLOCKED"
        job["provider_result"] = evidence
        job["last_error"] = provider_result["failure_code"]
    else:
        job["status"] = "TERMINAL_FAIL_CLOSED"
        job["provider_result"] = evidence
        job["last_error"] = provider_result["failure_code"]
    return _persist_job(path, job)


def execute_job(
    root: Path,
    job_id: str,
    provider: Provider,
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    # Fast terminal read remains side-effect free. Every non-terminal path must
    # acquire the single Website execution owner before re-reading state.
    _, observed = _job_by_id(root, job_id)
    if observed["status"] in TERMINAL_STATES:
        return observed

    token = _acquire_execution_lock(root, job_id, observed["request_id"])
    safe_release = False
    provider_entered = False
    try:
        path, job = _job_by_id(root, job_id)
        if job["status"] in TERMINAL_STATES:
            safe_release = True
            return job

        try:
            _verify_claim_for_job(root, job)
        except RunnerError:
            safe_release = True
            raise

        try:
            is_ready = provider.ready()
        except Exception:
            job["status"] = "WAITING_PROVIDER_READY"
            job["last_error"] = "PROVIDER_READY_UNAVAILABLE"
            persisted = _persist_job(path, job)
            safe_release = True
            return persisted
        if not is_ready:
            job["status"] = "WAITING_PROVIDER_READY"
            job["last_error"] = "PROVIDER_NOT_READY"
            persisted = _persist_job(path, job)
            safe_release = True
            return persisted

        try:
            _raw, text = validated_render_text(
                project_root,
                job["render_ref"],
                job["descriptor"]["render_sha256"],
            )
            expected_request_id = derive_request_id(job["descriptor"])
            if expected_request_id != job["request_id"]:
                raise RunnerError("REQUEST_ID_DESCRIPTOR_MISMATCH")
        except RunnerError as exc:
            job["status"] = "TERMINAL_FAIL_CLOSED"
            job["last_error"] = exc.code
            persisted = _persist_job(path, job)
            safe_release = True
            return persisted

        job["status"] = "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN"
        job["last_error"] = None
        _persist_job(path, job)

        provider_entered = True
        try:
            provider_result = provider.speech(text, job["request_id"])
        except Exception:
            job["status"] = "CALL_IN_PROGRESS_OR_RESULT_UNKNOWN"
            job["last_error"] = "PROVIDER_CALL_RESULT_UNKNOWN"
            persisted = _persist_job(path, job)
            safe_release = True
            return persisted

        if not isinstance(provider_result, dict):
            job["status"] = "TERMINAL_FAIL_CLOSED"
            job["last_error"] = "PROVIDER_RESULT_INVALID"
            job["provider_result"] = None
            persisted = _persist_job(path, job)
            safe_release = True
            return persisted

        persisted = _apply_provider_result(root, path, job, provider, provider_result)
        safe_release = True
        return persisted
    finally:
        # Clean release happens only after a state transition has been durably
        # persisted or before provider entry. If an unexpected exception occurs
        # after provider entry, leave the lock in place for operator resolution.
        if safe_release:
            _release_execution_lock(root, token)
        elif not provider_entered:
            _release_execution_lock(root, token)


def worker_once(
    root: Path,
    provider: Provider,
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any] | None:
    ensure_runtime_root(root)
    candidates: list[str] = []
    for path in sorted((root / "jobs").glob("*.json")):
        try:
            job = _load_json(path, "JOB_STATE_CORRUPT")
        except RunnerError:
            continue
        if job.get("status") not in TERMINAL_STATES:
            candidates.append(path.stem)
    if not candidates:
        return None
    return execute_job(root, candidates[0], provider, project_root=project_root)


def reconcile(
    root: Path,
    job_id: str,
    provider: Provider,
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    path, job = _job_by_id(root, job_id)
    if job["status"] in TERMINAL_STATES:
        return job
    _verify_claim_for_job(root, job)
    return execute_job(root, job_id, provider, project_root=project_root)


class HttpVoiceProvider:
    def __init__(self, base_url: str = "http://127.0.0.1:8765", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def ready(self) -> bool:
        request = urllib.request.Request(self.base_url + "/ready", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status == 200 and payload.get("status") == "READY"
        except (urllib.error.URLError, TimeoutError, ValueError):
            return False

    def speech(self, text: str, request_id: str) -> dict[str, Any]:
        body = json.dumps(
            {"text": text, "request_id": request_id},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + "/v1/speech",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=None) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                return json.loads(exc.read().decode("utf-8"))
            finally:
                exc.close()

    def artifact(self, artifact_ref: str) -> bytes:
        encoded = urllib.parse.quote(artifact_ref, safe="")
        request = urllib.request.Request(
            self.base_url + "/v1/artifacts/" + encoded,
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return response.read()


def _descriptor_from_args(args: argparse.Namespace) -> dict[str, str]:
    return {
        "schema": SCHEMA,
        "authorization_ref": args.authorization_ref,
        "generation_epoch": args.generation_epoch,
        "operation_id": args.operation_id,
        "article_id": args.article_id,
        "render_sha256": args.render_sha256,
        "voice_contract_id": VOICE_CONTRACT_ID,
    }


def _runtime_root(args: argparse.Namespace) -> Path:
    if args.test_root:
        return Path(args.test_root).resolve()
    return PRODUCTION_ROOT


def _add_identity_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--authorization-ref", required=True)
    parser.add_argument("--generation-epoch", required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--article-id", required=True)
    parser.add_argument("--render-sha256", required=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Website S4 durable read-aloud runner")
    parser.add_argument(
        "--test-root",
        help="Explicit verification-only runtime root. Omit in production to use the frozen production root.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit")
    _add_identity_args(p_submit)
    p_submit.add_argument("--render-ref", required=True)
    p_submit.add_argument("--request-id")

    for name in ("status", "result", "reconcile"):
        p = sub.add_parser(name)
        p.add_argument("--job-id", required=True)

    sub.add_parser("worker-once")

    args = parser.parse_args()
    root = _runtime_root(args)

    try:
        if args.command == "submit":
            descriptor = _descriptor_from_args(args)
            value = submit(
                root,
                descriptor,
                args.render_ref,
                supplied_request_id=args.request_id,
            )
        elif args.command == "status":
            value = status(root, args.job_id)
        elif args.command == "result":
            value = result(root, args.job_id)
        elif args.command == "reconcile":
            value = reconcile(root, args.job_id, HttpVoiceProvider())
        elif args.command == "worker-once":
            value = worker_once(root, HttpVoiceProvider())
        else:
            raise RunnerError("COMMAND_INVALID")
    except RunnerError as exc:
        print(json.dumps({"status": "BLOCKED", "failure_code": exc.code}, separators=(",", ":")))
        return 2

    print(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
