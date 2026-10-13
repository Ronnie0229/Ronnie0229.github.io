#!/usr/bin/env python3
"""One bounded auto-QC audio media delivery continuation, not a Website publisher."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import read_aloud_workflow as wf
import read_aloud_s4_runner as s4
from read_aloud_new_post_reconcile import read_selector
from read_aloud_exact_one_pilot_grant import require_pilot_stage, claim_pilot_stage, PilotGrantError
from read_aloud_media_delivery import archive_wav, upload_r2, DeliveryError


class ReadyDeliveryError(RuntimeError):
    pass


def _frontmatter(blob: bytes, article_id: str) -> tuple[str, str]:
    try:
        body = blob.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ReadyDeliveryError("POST_ENCODING_INVALID") from exc
    if not body.startswith("---\n") or "\n---\n" not in body[4:]:
        raise ReadyDeliveryError("POST_FRONTMATTER_INVALID")
    fm = body[4:].split("\n---\n", 1)[0]
    got_id = re.search(r'^articleId:\s*["\']?(post-[\w-]+)["\']?\s*$', fm, re.M)
    date = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})\s*$", fm, re.M)
    title = re.search(r'^title:\s*"([^"\n]+)"\s*$', fm, re.M)
    if not got_id or got_id.group(1) != article_id or not date or not title:
        raise ReadyDeliveryError("POST_IDENTITY_OR_METADATA_INVALID")
    return date.group(1), title.group(1)


def deliver_one(project_root: Path, runtime_root: Path, *, pilot_grant_path: Path | None = None) -> dict[str, Any] | None:
    selector = read_selector(runtime_root) if pilot_grant_path is None else None
    if pilot_grant_path is not None:
        try:
            pilot = require_pilot_stage(pilot_grant_path, project_root, 'NAS_WAV_APPEND_ONLY')
        except PilotGrantError as exc:
            raise ReadyDeliveryError(str(exc)) from exc
        selector = {'allow_media_delivery': True, 'authorization_ref': pilot['authorization_ref']}
    if selector is None or selector.get("allow_media_delivery") is not True:
        return None
    intake_dir = runtime_root / "new-post-intake"
    if not intake_dir.exists():
        return None
    for path in sorted(intake_dir.glob("*.json")):
        try:
            intake = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReadyDeliveryError("INTAKE_INVALID") from exc
        if intake.get("status") != "S4_WORKFLOW_REGISTERED":
            continue
        if intake.get("authorization_ref") != selector.get("authorization_ref"):
            raise ReadyDeliveryError("AUTHORIZATION_MISMATCH")
        workflow_id = intake.get("workflow_id")
        if not isinstance(workflow_id, str) or len(workflow_id) != 64:
            raise ReadyDeliveryError("WORKFLOW_ID_INVALID")
        workflow = wf.workflow_status(runtime_root, workflow_id)
        if workflow.get("state") != "AUDIO_READY_PENDING_PUBLICATION_GATE":
            continue
        if workflow.get("review_policy") != "AUTO_TECHNICAL_QC" or workflow.get("auto_technical_qc", {}).get("status") != "PASS":
            raise ReadyDeliveryError("AUTO_QC_UNVERIFIED")
        identity = intake.get("post")
        if not isinstance(identity, dict):
            raise ReadyDeliveryError("POST_IDENTITY_INVALID")
        source = identity.get("source_commit")
        post_path = identity.get("post_path")
        article_id = identity.get("article_id")
        expected_sha = identity.get("post_sha256")
        if not all(isinstance(v, str) and v for v in (source, post_path, article_id, expected_sha)):
            raise ReadyDeliveryError("POST_IDENTITY_INVALID")
        source_blob = subprocess.run(["git", "-C", str(project_root), "show", f"{source}:{post_path}"], capture_output=True, check=False)
        if source_blob.returncode or hashlib.sha256(source_blob.stdout).hexdigest() != expected_sha:
            raise ReadyDeliveryError("POST_VERSION_DRIFT")
        if pilot_grant_path is not None:
            try:
                for operation in ('NAS_WAV_APPEND_ONLY', 'R2_MP3_EXACT_OBJECT'):
                    require_pilot_stage(pilot_grant_path, project_root, operation,
                                        article_id=article_id, post_path=post_path, source_sha256=expected_sha)
            except PilotGrantError as exc:
                raise ReadyDeliveryError(str(exc)) from exc
        date, title = _frontmatter(source_blob.stdout, article_id)
        art = workflow.get("artifact")
        mp3 = workflow.get("delivery")
        if not isinstance(art, dict) or not isinstance(mp3, dict):
            raise ReadyDeliveryError("AUDIO_ARTIFACT_MISSING")
        wav_path = runtime_root / "artifact-cache" / art.get("cache_name", "")
        mp3_path = Path(mp3.get("absolute_path", ""))
        if not wav_path.is_file() or not mp3_path.is_file():
            raise ReadyDeliveryError("MEDIA_FILE_MISSING")
        # Each step reconciles exact bytes on retry; never upload mismatched or overwrite archive.
        if pilot_grant_path is not None:
            claim_pilot_stage(runtime_root, 'NAS_WAV_APPEND_ONLY', pilot)
        nas = archive_wav(wav_path, art["artifact_sha256"], article_id=article_id,
                          date=date, title=title, workflow_id=workflow_id,
                          render_sha=workflow["descriptor"]["render_sha256"],
                          provenance={
                              "generation": {"request_id": workflow.get("request_id"), "epoch": workflow["descriptor"].get("generation_epoch"), "post_sha256": expected_sha},
                              "delivery": {"mp3_sha256": mp3["sha256"], "mp3_bytes": mp3["bytes"], "url": f"https://audio.ronniecross.com/audio/articles/{article_id}/article.mp3"},
                              "acceptance": {"mode": "AUTO_TECHNICAL_QC", "status": "PASS", "human_listening_pass": False},
                          })
        workflow["nas_archive"] = nas
        wf._persist(runtime_root, workflow)
        if pilot_grant_path is not None:
            claim_pilot_stage(runtime_root, 'R2_MP3_EXACT_OBJECT', pilot)
        r2 = upload_r2(mp3_path, mp3["sha256"], article_id=article_id, upload_allowed=True)
        workflow["r2_delivery"] = r2
        wf._persist(runtime_root, workflow)
        intake["status"] = "MEDIA_READY_PENDING_WEBSITE_RELEASE"
        intake["audio_url"] = r2["url"]
        intake["wav_master_path"] = nas["master_path"]
        s4.atomic_write_json(path, intake)
        return intake
    return None
