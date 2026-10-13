#!/usr/bin/env python3
"""Operator-invoked Patrick-only pilot; never enables future-post selector.

One stage per invocation. The normal S4 tick is a separate existing durable action;
a human checks terminal state before advancing. No automatic retries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from read_aloud_exact_one_pilot_grant import PATRICK_ID, PATRICK_POST, ALLOWED, require_pilot_stage, PilotGrantError
from read_aloud_new_post_executor import execute_one
from read_aloud_new_post_delivery import deliver_one
from read_aloud_audio_site_publisher import publish_one

class PilotDriverError(RuntimeError):
    pass

def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], check=False, capture_output=True, text=True)
    if p.returncode:
        raise PilotDriverError("PILOT_GIT_READBACK_FAILED")
    return p.stdout.strip()

def preflight(repo: Path, runtime: Path, grant_path: Path) -> dict:
    identity = require_pilot_stage(grant_path, repo, "TTS_ONCE")
    if (runtime / "new-post-automation-selector.json").exists():
        raise PilotDriverError("FUTURE_AUTOMATION_SELECTOR_MUST_BE_ABSENT")
    if _git(repo, "status", "--porcelain"):
        raise PilotDriverError("PILOT_CANONICAL_GIT_DIRTY")
    local = _git(repo, "rev-parse", "HEAD")
    remote = _git(repo, "rev-parse", "refs/remotes/origin/main")
    if local != remote:
        raise PilotDriverError("PILOT_GIT_REMOTE_DRIFT")
    committed = subprocess.run(["git","-C",str(repo),"show",f"{local}:{PATRICK_POST}"],
                               capture_output=True, check=False)
    if committed.returncode or hashlib.sha256(committed.stdout).hexdigest() != identity["source_sha256"]:
        raise PilotDriverError("PILOT_FROZEN_GIT_BLOB_MISMATCH")
    return {"article_id": PATRICK_ID, "source_commit": local, "post_path": PATRICK_POST,
            "post_sha256": identity["source_sha256"], "authorization_ref": identity["authorization_ref"]}

def stage(repo: Path, runtime: Path, grant_path: Path, operation: str) -> dict:
    if operation not in ("preflight", "register", "tts", "s4", "media", "publish"):
        raise PilotDriverError("PILOT_STAGE_INVALID")
    frozen = preflight(repo, runtime, grant_path)
    if operation == "preflight":
        return {"status":"PILOT_PREFLIGHT_LOCAL_PASS", **frozen}
    if operation == "register":
        from read_aloud_new_post_intake import SCHEMA
        identity = hashlib.sha256((frozen["source_commit"] + "\n" + PATRICK_ID).encode()).hexdigest()
        path = runtime / "new-post-intake" / f"{identity}.json"
        if path.exists():
            raise PilotDriverError("PILOT_INTAKE_ALREADY_EXISTS_NO_REARM")
        record = {"schema": SCHEMA, "intake_id": identity,
                  "source_before": frozen["source_commit"], "source_after": frozen["source_commit"],
                  "authorization_ref": frozen["authorization_ref"],
                  "post": {k: frozen[k] for k in ("article_id","post_path","post_sha256","source_commit")},
                  "status": "WAIT_RENDER_AND_EXPLICIT_TTS_AUTHORIZATION",
                  "no_automatic_side_effects": True}
        path.parent.mkdir(parents=True, exist_ok=True)
        # Existing runtime intake is exclusive to this one Article ID; refuse unintended entries.
        if any(path.parent.glob("*.json")):
            raise PilotDriverError("PILOT_INTAKE_OTHER_RECORD_PRESENT")
        # No TTS or network action: registration only.
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise PilotDriverError("PILOT_INTAKE_ALREADY_EXISTS_NO_REARM") from exc
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(record, output, ensure_ascii=False, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        return {"status":"PILOT_REGISTERED", "intake_id":identity}
    if operation == "s4":
        from read_aloud_workflow import workflow_status, tick_workflow
        identity = hashlib.sha256((frozen["source_commit"] + "\n" + PATRICK_ID).encode()).hexdigest()
        intake_path = runtime / "new-post-intake" / f"{identity}.json"
        if not intake_path.is_file():
            raise PilotDriverError("PILOT_INTAKE_MISSING")
        intake = json.loads(intake_path.read_text(encoding="utf-8"))
        if (intake.get("authorization_ref") != frozen["authorization_ref"]
            or intake.get("post", {}).get("post_sha256") != frozen["post_sha256"]
            or intake.get("status") != "S4_WORKFLOW_REGISTERED"):
            raise PilotDriverError("PILOT_INTAKE_NOT_READY_FOR_S4")
        workflow_id = intake.get("workflow_id")
        if not isinstance(workflow_id, str) or len(workflow_id) != 64:
            raise PilotDriverError("PILOT_S4_IDENTITY_INVALID")
        current = workflow_status(runtime, workflow_id)
        if (current.get("descriptor", {}).get("article_id") != PATRICK_ID
            or current.get("descriptor", {}).get("authorization_ref") != frozen["authorization_ref"]):
            raise PilotDriverError("PILOT_S4_DESCRIPTOR_NOT_AUTHORIZED")
        if current.get("state") in ("AUDIO_READY_PENDING_PUBLICATION_GATE",
                                    "TERMINAL_BLOCKED", "TERMINAL_FAIL_CLOSED",
                                    "RESULT_UNKNOWN_OPERATOR_REQUIRED"):
            return {"status":"PILOT_S4_OBSERVATION_ONLY", "workflow_id":workflow_id,
                    "state":current.get("state")}
        updated = tick_workflow(runtime, workflow_id)
        return {"status":"PILOT_S4_ADVANCED", "workflow_id":workflow_id,
                "state":updated.get("state")}
    if operation == "tts":
        result = execute_one(repo, runtime, pilot_grant_path=grant_path)
    elif operation == "media":
        result = deliver_one(repo, runtime, pilot_grant_path=grant_path)
    else:
        result = publish_one(repo, runtime, pilot_grant_path=grant_path)
    if result is None:
        raise PilotDriverError("PILOT_STAGE_NOT_READY_OR_ALREADY_CONSUMED")
    return {"status":"PILOT_STAGE_INVOKED", "operation":operation,
            "article_id": result["post"]["article_id"]}

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--runtime", required=True, type=Path)
    p.add_argument("--grant", required=True, type=Path)
    p.add_argument("--stage", choices=["preflight","register","tts","s4","media","publish"], required=True)
    a=p.parse_args()
    try:
        print(json.dumps(stage(a.repo.resolve(),a.runtime.resolve(),a.grant.resolve(),a.stage),
                         ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED", "reason":str(exc)},ensure_ascii=False))
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
