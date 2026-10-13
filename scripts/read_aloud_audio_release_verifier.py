#!/usr/bin/env python3
"""One-shot fresh production verification for a pending AUDIO_ONLY_UPDATE release."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import read_aloud_workflow as wf
import read_aloud_s4_runner as s4
from read_aloud_audio_site_publisher import deployed_sha
from read_aloud_media_delivery import verify_r2, DeliveryError
from read_aloud_publication_lock import publication_lock, last_receipt, mark_previous_verified_under_lock


class AudioVerificationError(RuntimeError):
    pass


def _site_page(url: str) -> str:
    if not url.startswith("https://ronniecross.com/posts/") or not url.endswith("/"):
        raise AudioVerificationError("CANONICAL_URL_NOT_ALLOWED")
    result = subprocess.run(["curl", "-fsSL", "--max-time", "20", url],
                            capture_output=True, check=False)
    if result.returncode:
        raise AudioVerificationError("CANONICAL_LIVE_PAGE_UNAVAILABLE")
    return result.stdout.decode("utf-8", errors="replace")


def _email_zero_verified(commit: str) -> bool:
    run = subprocess.run(["gh", "run", "list", "--workflow", "email-published-posts.yml",
                          "--commit", commit, "--limit", "15",
                          "--json", "databaseId,status,conclusion,headSha"],
                         capture_output=True, text=True, check=False)
    if run.returncode:
        raise AudioVerificationError("GITHUB_MAIL_RUN_QUERY_FAILED")
    try:
        matches = [item for item in json.loads(run.stdout) if item.get("headSha") == commit]
    except (ValueError, TypeError) as exc:
        raise AudioVerificationError("GITHUB_MAIL_RUN_JSON_INVALID") from exc
    if not matches:
        return False
    for item in matches:
        if item.get("status") != "completed":
            return False
        if item.get("conclusion") != "success":
            raise AudioVerificationError("AUDIO_ONLY_EMAIL_WORKFLOW_FAILED")
        logs = subprocess.run(["gh", "run", "view", str(item["databaseId"]), "--log"],
                              capture_output=True, text=True, check=False)
        if logs.returncode:
            raise AudioVerificationError("GITHUB_MAIL_LOG_UNAVAILABLE")
        if "No changed published posts were found in this push." not in logs.stdout:
            raise AudioVerificationError("AUDIO_ONLY_EMAIL_ZERO_NOT_PROVEN")
    return True


def verify_one(runtime_root: Path) -> dict[str, Any] | None:
    intake_dir = runtime_root / "new-post-intake"
    if not intake_dir.exists():
        return None
    for path in sorted(intake_dir.glob("*.json")):
        try:
            intake = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AudioVerificationError("INTAKE_INVALID") from exc
        if intake.get("status") != "AUDIO_RELEASE_PENDING_VERIFY":
            continue
        commit = intake.get("website_commit")
        if not isinstance(commit, str) or len(commit) != 40:
            raise AudioVerificationError("AUDIO_RELEASE_COMMIT_INVALID")
        with publication_lock(runtime_root):
            receipt = last_receipt(runtime_root)
            if not receipt or receipt.get("kind") != "AUDIO_ONLY_UPDATE" or receipt.get("commit") != commit:
                raise AudioVerificationError("PENDING_RELEASE_RECEIPT_MISMATCH")
            if deployed_sha() != commit:
                return None  # Cloudflare deploy remains async, do not wait.
            url = receipt.get("canonical_url")
            audio_url = intake.get("audio_url")
            if not isinstance(audio_url, str) or not isinstance(url, str):
                raise AudioVerificationError("AUDIO_LIVE_IDENTITY_MISSING")
            html = _site_page(url)
            if audio_url not in html or "<audio" not in html:
                raise AudioVerificationError("LIVE_AUDIO_BINDING_MISSING")
            if not _email_zero_verified(commit):
                return None  # GitHub Actions still pending.
            workflow_id = intake.get("workflow_id")
            if not isinstance(workflow_id, str):
                raise AudioVerificationError("WORKFLOW_ID_INVALID")
            state = wf.workflow_status(runtime_root, workflow_id)
            mp3 = state.get("delivery")
            if not isinstance(mp3, dict):
                raise AudioVerificationError("MP3_PROOF_MISSING")
            try:
                if not verify_r2(audio_url, mp3["sha256"], mp3["bytes"]):
                    raise AudioVerificationError("LIVE_MP3_UNVERIFIED")
            except (KeyError, DeliveryError) as exc:
                raise AudioVerificationError("LIVE_MP3_READBACK_FAILED") from exc
            if receipt["publication_state"] == "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY":
                mark_previous_verified_under_lock(runtime_root, commit)
            elif receipt["publication_state"] != "VERIFIED":
                raise AudioVerificationError("RELEASE_STATE_INVALID")
            state["website_live"] = {"verified": True, "production_commit": commit, "canonical_url": url}
            state["open_repairs"] = 0
            state["state"] = "COMPLETE"
            state["next_action"] = "NONE"
            wf._persist(runtime_root, state)
            intake["status"] = "COMPLETE"
            s4.atomic_write_json(path, intake)
            return intake
    return None
