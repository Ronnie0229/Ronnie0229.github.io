#!/usr/bin/env python3
"""Exact-one Patrick production pilot grant verifier. Never activates future-post selector.

This is an authorization preflight, not a TTS submission or site publisher.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re

PATRICK_ID = "post-072eda6a5bfbe1f9"
PATRICK_POST = "src/content/posts/2026-10-11-腓立比书-1-20-30｜活着就是基督.md"
SCHEMA = "ronniecross-exact-one-audio-pilot-grant/v1"
ALLOWED = ("TTS_ONCE", "NAS_WAV_APPEND_ONLY", "R2_MP3_EXACT_OBJECT", "AUDIO_URL_ONLY_RELEASE")


class PilotGrantError(RuntimeError):
    pass


def require_pilot_stage(grant_path: Path, project_root: Path, operation: str, *,
                        article_id: str = PATRICK_ID, post_path: str = PATRICK_POST,
                        source_sha256: str | None = None) -> dict:
    """Fail-closed pilot gate to call immediately before each side-effect stage."""
    if operation not in ALLOWED:
        raise PilotGrantError("PILOT_OPERATION_INVALID")
    if not grant_path.is_file() or grant_path.is_symlink():
        raise PilotGrantError("PILOT_GRANT_NOT_REGULAR_FILE")
    try:
        grant = json.loads(grant_path.read_text(encoding="utf-8"))
        raw = (project_root / post_path).read_bytes()
    except (OSError, ValueError) as exc:
        raise PilotGrantError("PILOT_GRANT_OR_SOURCE_UNAVAILABLE") from exc
    verified = validate_exact_one(grant, raw, article_id=article_id, post_path=post_path)
    if source_sha256 is not None and verified["source_sha256"] != source_sha256:
        raise PilotGrantError("PILOT_INTAKE_SHA_MISMATCH")
    return {"authorization_ref": grant["authorization_ref"], **verified}


def claim_pilot_stage(runtime_root: Path, operation: str, verified: dict) -> Path:
    """Durable one-attempt-only marker. UNKNOWN requires manual intervention; no replay."""
    if operation not in ALLOWED or verified.get("article_id") != PATRICK_ID:
        raise PilotGrantError("PILOT_STAGE_CLAIM_INVALID")
    digest = verified.get("source_sha256")
    ref = verified.get("authorization_ref")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest) or not isinstance(ref, str) or not ref:
        raise PilotGrantError("PILOT_CLAIM_IDENTITY_INVALID")
    folder = runtime_root / "exact-one-pilot" / PATRICK_ID
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = folder / (operation.lower() + ".claimed.json")
    record = {"schema": SCHEMA, "status": "CLAIMED_UNKNOWN_UNTIL_OPERATOR_VERIFIES",
              "article_id": PATRICK_ID, "source_sha256": digest,
              "authorization_ref": ref, "operation": operation}
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise PilotGrantError("PILOT_STAGE_ALREADY_CLAIMED_NO_REPLAY") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(record, stream, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return path


def validate_exact_one(grant: dict, post_bytes: bytes, *, article_id: str = PATRICK_ID,
                       post_path: str = PATRICK_POST) -> dict:
    if not isinstance(grant, dict) or grant.get("schema") != SCHEMA:
        raise PilotGrantError("GRANT_SCHEMA_INVALID")
    if article_id != PATRICK_ID or post_path != PATRICK_POST:
        raise PilotGrantError("PILOT_SCOPE_MISMATCH")
    if grant.get("article_id") != PATRICK_ID or grant.get("post_path") != PATRICK_POST:
        raise PilotGrantError("GRANT_ARTICLE_IDENTITY_MISMATCH")
    if grant.get("operation_classes") != list(ALLOWED):
        raise PilotGrantError("GRANT_OPERATIONS_NOT_EXACT")
    if grant.get("future_posts_enabled") is not False or grant.get("historical_backfill") is not False:
        raise PilotGrantError("GRANT_MUST_FORBID_ONGOING_AUTOMATION")
    if any(key in grant for key in ("allow_unattended_tts", "allow_unattended_publication", "last_processed_commit")):
        raise PilotGrantError("ONGOING_SELECTOR_FIELDS_FORBIDDEN")
    ref = grant.get("authorization_ref")
    if not isinstance(ref, str) or not ref.strip() or len(ref) > 256:
        raise PilotGrantError("PILOT_AUTH_INVALID")
    actual_sha = hashlib.sha256(post_bytes).hexdigest()
    if grant.get("source_sha256") != actual_sha or not re.fullmatch("[a-f0-9]{64}", actual_sha):
        raise PilotGrantError("PILOT_SOURCE_SHA_DRIFT")
    try:
        body = post_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PilotGrantError("PILOT_POST_ENCODING_INVALID") from exc
    if not body.startswith("---\n") or "\n---\n" not in body[4:]:
        raise PilotGrantError("PILOT_FRONTMATTER_INVALID")
    fm = body[4:].split("\n---\n", 1)[0]
    if not re.search(r'^articleId:\s*["\']?' + re.escape(PATRICK_ID) + r'["\']?\s*$', fm, re.M):
        raise PilotGrantError("PILOT_ARTICLE_ID_INVALID")
    if re.search(r"^audioUrl\s*:", fm, re.M):
        raise PilotGrantError("PILOT_ALREADY_AUDIO_BOUND")
    return {"status": "EXACT_ONE_PILOT_PREFLIGHT_PASS", "article_id": PATRICK_ID,
            "source_sha256": actual_sha, "ongoing_automation_enabled": False}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--grant", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    args = p.parse_args()
    try:
        result = validate_exact_one(json.loads(args.grant.read_text(encoding="utf-8")),
                                    (args.repo / PATRICK_POST).read_bytes())
    except (OSError, ValueError, PilotGrantError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
