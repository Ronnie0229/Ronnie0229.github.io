#!/usr/bin/env python3
"""Bounded frozen Render View -> existing S4 durable workflow activation.

This only runs with an exact activated policy selector allowing unattended TTS.
No NAS/R2/Git/Cloudflare/media publication is performed here.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import read_aloud_s4_runner as s4
import read_aloud_workflow as wf
from read_aloud_new_post_reconcile import read_selector, SelectorError
from read_aloud_exact_one_pilot_grant import require_pilot_stage, claim_pilot_stage, PilotGrantError


class IntakeExecutionError(RuntimeError):
    pass


def execute_one(project_root: Path, runtime_root: Path, *, pilot_grant_path: Path | None = None) -> dict[str, Any] | None:
    selector = read_selector(runtime_root) if pilot_grant_path is None else None
    if pilot_grant_path is not None:
        try:
            pilot = require_pilot_stage(pilot_grant_path, project_root, 'TTS_ONCE')
        except PilotGrantError as exc:
            raise IntakeExecutionError(str(exc)) from exc
        selector = {'allow_unattended_tts': True, 'authorization_ref': pilot['authorization_ref']}
    if selector is None or selector.get("allow_unattended_tts") is not True:
        return None
    if not isinstance(selector.get("authorization_ref"), str):
        raise IntakeExecutionError("AUTOMATION_AUTH_MISSING")
    directory = runtime_root / "new-post-intake"
    if not directory.exists():
        return None
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IntakeExecutionError("INTAKE_CORRUPT") from exc
        if record.get("status") != "WAIT_RENDER_AND_EXPLICIT_TTS_AUTHORIZATION":
            continue
        if record.get("authorization_ref") != selector["authorization_ref"]:
            raise IntakeExecutionError("INTAKE_AUTH_MISMATCH")
        post = record.get("post")
        if not isinstance(post, dict):
            raise IntakeExecutionError("POST_IDENTITY_INVALID")
        file_path = post.get("post_path")
        sha = post.get("post_sha256")
        source = post.get("source_commit")
        article_id = post.get("article_id")
        if not all(isinstance(v, str) and v for v in (file_path, sha, source, article_id)):
            raise IntakeExecutionError("POST_IDENTITY_INVALID")
        if pilot_grant_path is not None:
            try:
                require_pilot_stage(pilot_grant_path, project_root, 'TTS_ONCE',
                                    article_id=article_id, post_path=file_path, source_sha256=sha)
            except PilotGrantError as exc:
                raise IntakeExecutionError(str(exc)) from exc
        # Exact Git blob is the frozen publication source, not mutable working tree.
        blob = subprocess.run(["git", "-C", str(project_root), "show", f"{source}:{file_path}"],
                              capture_output=True, check=False)
        if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != sha:
            raise IntakeExecutionError("FROZEN_POST_NOT_AVAILABLE_OR_SHA_MISMATCH")
        rendered = subprocess.run(["node", str(project_root / "scripts/read_aloud_render_view.mjs"), "-"],
                                  input=blob.stdout, capture_output=True, check=False)
        if rendered.returncode:
            raise IntakeExecutionError("RENDER_VIEW_FAILED")
        try:
            payload = json.loads(rendered.stdout)
        except (ValueError, UnicodeDecodeError) as exc:
            raise IntakeExecutionError("RENDER_RESULT_INVALID") from exc
        if payload.get("article_id") != article_id or payload.get("post_sha256") != sha:
            raise IntakeExecutionError("RENDER_POST_IDENTITY_MISMATCH")
        render_text = payload.get("text")
        if not isinstance(render_text, str) or hashlib.sha256(render_text.encode("utf-8")).hexdigest() != payload.get("render_sha256"):
            raise IntakeExecutionError("RENDER_TEXT_SHA_MISMATCH")
        if pilot_grant_path is not None:
            claim_pilot_stage(runtime_root, 'TTS_ONCE', pilot)
        # Stable immutable path; S4 provider consumes it via safe project-local file open.
        rel_path = Path("artifacts") / "read-aloud" / "auto" / record["intake_id"] / "tts-readaloud.txt"
        full_path = project_root / rel_path
        if full_path.exists():
            if full_path.is_symlink() or full_path.read_bytes() != render_text.encode():
                raise IntakeExecutionError("RENDER_EXISTING_CONFLICT")
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(full_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(render_text.encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
        wf_obj = wf.start_workflow(
            runtime_root,
            authorization_ref=selector["authorization_ref"],
            generation_epoch="auto-new-post-" + source,
            operation_id="post-" + record["intake_id"],
            article_id=article_id,
            render_sha256=payload["render_sha256"],
            render_ref=rel_path.as_posix(),
            review_policy="AUTO_TECHNICAL_QC",
        )
        record["status"] = "S4_WORKFLOW_REGISTERED"
        record["workflow_id"] = wf_obj["workflow_id"]
        record["render_sha256"] = payload["render_sha256"]
        record["render_ref"] = rel_path.as_posix()
        s4.atomic_write_json(path, record)
        return record
    return None
