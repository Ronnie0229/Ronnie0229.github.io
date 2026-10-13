#!/usr/bin/env python3
"""Strict audio-only Website publisher. Disabled unless explicit runtime selector authorizes.

Single post audioUrl only; never invokes email workflow or sends notification.
The serialized release receipt must already be VERIFIED for current origin/main.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any
from urllib.parse import quote

import read_aloud_s4_runner as s4
from read_aloud_audio_binding import BindingError, plan_audio_binding
from read_aloud_media_delivery import sha_file, verify_r2, DeliveryError
import read_aloud_workflow as wf
from read_aloud_new_post_reconcile import read_selector
from read_aloud_exact_one_pilot_grant import require_pilot_stage, claim_pilot_stage, PilotGrantError
from read_aloud_publication_lock import (
    SCHEMA as RELEASE_SCHEMA, last_receipt, publication_lock, record_pending_under_lock
)
from read_aloud_previous_release_gate import PreflightError

CANONICAL = Path("/Volumes/DevSSD/RonnieWork/RonnieCross/个人网页项目")


class AudioPublicationError(RuntimeError):
    pass


def run_git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if p.returncode:
        raise AudioPublicationError("GIT_COMMAND_FAILED:" + " ".join(args[:2]))
    return p.stdout.strip()


def deployed_sha() -> str:
    p = subprocess.run(["curl", "-fsS", "--max-time", "15",
                        "https://ronniecross.com/deployment.json"],
                       capture_output=True, check=False)
    if p.returncode:
        raise AudioPublicationError("PRODUCTION_DEPLOYMENT_UNAVAILABLE")
    try:
        result = json.loads(p.stdout)
    except (ValueError, UnicodeDecodeError) as exc:
        raise AudioPublicationError("PRODUCTION_DEPLOYMENT_INVALID") from exc
    value = result.get("commit") if isinstance(result, dict) else None
    if not isinstance(value, str) or len(value) != 40:
        raise AudioPublicationError("PRODUCTION_DEPLOYMENT_IDENTITY_INVALID")
    return value


def rendered_audio_page(project_root: Path, audio_url: str) -> str:
    matches = []
    for page in (project_root / "dist" / "posts").glob("*/index.html"):
        if audio_url in page.read_text(encoding="utf-8", errors="replace"):
            matches.append(page)
    if len(matches) != 1:
        raise AudioPublicationError("AUDIO_PLAYER_RENDER_IDENTITY_NOT_UNIQUE")
    slug = matches[0].parent.name
    return "https://ronniecross.com/posts/" + quote(slug, safe="") + "/"


def recover_audio_commit_under_lock(project_root: Path, runtime_root: Path, previous: dict, entry: dict, entry_path: Path, remote: str, local: str) -> dict | None:
    """Reconcile only an exact audio-only one-commit descendant after a crash."""
    post = entry["post"]
    relative = post["post_path"]
    if run_git(project_root, "rev-parse", "HEAD^") != previous.get("commit"):
        raise AudioPublicationError("RECOVERY_PARENT_CONFLICT")
    changed = run_git(project_root, "diff-tree", "--no-commit-id", "--name-only", "-r", local).splitlines()
    if changed != [relative]:
        raise AudioPublicationError("RECOVERY_WRITESET_CONFLICT")
    original = subprocess.run(["git", "-C", str(project_root), "show", f"{previous['commit']}:{relative}"],
                              capture_output=True, check=False)
    if original.returncode:
        raise AudioPublicationError("RECOVERY_ORIGINAL_POST_MISSING")
    try:
        target = plan_audio_binding(original.stdout, post["article_id"], post["post_sha256"], entry["audio_url"])
    except BindingError as exc:
        raise AudioPublicationError("RECOVERY_AUDIO_IDENTITY_CONFLICT") from exc
    if (project_root / relative).read_bytes() != target:
        raise AudioPublicationError("RECOVERY_AUDIO_BYTES_MISMATCH")
    if run_git(project_root, "status", "--porcelain"):
        raise AudioPublicationError("RECOVERY_GIT_DIRTY")
    if remote == previous["commit"]:
        try:
            run_git(project_root, "push", "origin", "main")
        except AudioPublicationError as exc:
            raise AudioPublicationError("RECOVERY_PUSH_AMBIGUOUS") from exc
        run_git(project_root, "fetch", "--quiet", "origin", "main")
        if run_git(project_root, "rev-parse", "refs/remotes/origin/main") != local:
            raise AudioPublicationError("RECOVERY_PUSH_READBACK_MISSING")
    elif remote != local:
        raise AudioPublicationError("RECOVERY_REMOTE_CONFLICT")
    page = entry.get("target_canonical_url") or rendered_audio_page(project_root, entry["audio_url"])
    pending = {
        "schema": RELEASE_SCHEMA, "kind": "AUDIO_ONLY_UPDATE",
        "commit": local, "previous_commit": previous["commit"],
        "publication_state": "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY",
        "notification_policy": "NO_EMAIL", "notification_sent_count": 0,
        "article_id": post["article_id"], "post_path": relative,
        "audio_url": entry["audio_url"], "canonical_url": page,
    }
    record_pending_under_lock(runtime_root, pending)
    entry["status"] = "AUDIO_RELEASE_PENDING_VERIFY"
    entry["website_commit"] = local
    s4.atomic_write_json(entry_path, entry)
    return entry


def publish_one(project_root: Path, runtime_root: Path, *, allow_test_repo: bool = False,
                build: bool = True, push: bool = True,
                pilot_grant_path: Path | None = None) -> dict[str, Any] | None:
    selector = read_selector(runtime_root) if pilot_grant_path is None else None
    if pilot_grant_path is not None:
        try:
            pilot = require_pilot_stage(pilot_grant_path, project_root, 'AUDIO_URL_ONLY_RELEASE')
        except PilotGrantError as exc:
            raise AudioPublicationError(str(exc)) from exc
        selector = {'allow_unattended_publication': True, 'authorization_ref': pilot['authorization_ref'],
                    'article_audio_publish_nonoverlap': True}
    if selector is None or selector.get("allow_unattended_publication") is not True:
        return None
    if not allow_test_repo and project_root.resolve() != CANONICAL:
        raise AudioPublicationError("WRONG_PRODUCTION_REPOSITORY")
    intake_dir = runtime_root / "new-post-intake"
    if not intake_dir.exists():
        return None
    for entry_path in sorted(intake_dir.glob("*.json")):
        try:
            entry = json.loads(entry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AudioPublicationError("INTAKE_CORRUPT") from exc
        if entry.get("status") != "MEDIA_READY_PENDING_WEBSITE_RELEASE":
            continue
        if entry.get("authorization_ref") != selector.get("authorization_ref"):
            raise AudioPublicationError("AUDIO_AUTHORIZATION_MISMATCH")
        post = entry.get("post")
        if not isinstance(post, dict) or not isinstance(post.get("post_path"), str):
            raise AudioPublicationError("POST_IDENTITY_INVALID")
        post_path = post["post_path"]
        if pilot_grant_path is not None:
            try:
                require_pilot_stage(pilot_grant_path, project_root, 'AUDIO_URL_ONLY_RELEASE',
                                    article_id=post.get('article_id'), post_path=post_path,
                                    source_sha256=post.get('post_sha256'))
            except PilotGrantError as exc:
                raise AudioPublicationError(str(exc)) from exc
        if not post_path.startswith("src/content/posts/") or ".." in Path(post_path).parts or not post_path.endswith(".md"):
            raise AudioPublicationError("POST_PATH_INVALID")
        audio_url = entry.get("audio_url")
        if not isinstance(audio_url, str):
            raise AudioPublicationError("AUDIO_URL_MISSING")
        workflow_id = entry.get("workflow_id")
        if not isinstance(workflow_id, str):
            raise AudioPublicationError("WORKFLOW_ID_MISSING")
        state = wf.workflow_status(runtime_root, workflow_id)
        nas = state.get("nas_archive")
        r2 = state.get("r2_delivery")
        if not isinstance(nas, dict) or not isinstance(r2, dict):
            raise AudioPublicationError("MEDIA_DELIVERY_PROOF_MISSING")
        if nas.get("verified") is not True or r2.get("verified") is not True or r2.get("url") != audio_url:
            raise AudioPublicationError("MEDIA_DELIVERY_UNVERIFIED")
        try:
            if sha_file(Path(nas["master_path"])) != state["artifact"]["artifact_sha256"]:
                raise AudioPublicationError("NAS_ARCHIVE_READBACK_MISMATCH")
            mp3 = state.get("delivery") or {}
            if not verify_r2(audio_url, mp3["sha256"], mp3["bytes"]):
                raise AudioPublicationError("R2_READBACK_MISMATCH")
        except (KeyError, OSError, DeliveryError) as exc:
            raise AudioPublicationError("MEDIA_READBACK_UNAVAILABLE") from exc
        with publication_lock(runtime_root):
            prev = last_receipt(runtime_root)
            # Business operations remain staggered, not globally locked.
            # The previous website release of ANY kind must have a verified receipt.
            operator_separated = selector.get("article_audio_publish_nonoverlap") is True
            if not operator_separated:
                raise AudioPublicationError("NONOVERLAP_POLICY_NOT_ENABLED")
            run_git(project_root, "fetch", "--quiet", "origin", "main")
            remote = run_git(project_root, "rev-parse", "refs/remotes/origin/main")
            local = run_git(project_root, "rev-parse", "HEAD")
            if isinstance(prev, dict) and prev.get("publication_state") == "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY":
                if (prev.get("kind") == "AUDIO_ONLY_UPDATE" and prev.get("article_id") == post["article_id"]
                    and prev.get("audio_url") == audio_url and prev.get("commit") == remote == local):
                    entry["status"] = "AUDIO_RELEASE_PENDING_VERIFY"
                    entry["website_commit"] = local
                    s4.atomic_write_json(entry_path, entry)
                    return entry
                return None  # Previous article/audio/site release must be verified first.
            if not isinstance(prev, dict) or prev.get('publication_state') != 'VERIFIED':
                raise AudioPublicationError('PREVIOUS_RELEASE_RECEIPT_UNVERIFIED')
            if prev.get('commit') != remote:
                raise AudioPublicationError('PREVIOUS_RELEASE_RECEIPT_STALE')
            if local != remote:
                raise AudioPublicationError("MAIN_REMOTE_DRIFT_STOP_MANUAL_REVIEW")
            # Current Git state and verified last-release receipt are required; this
            # publication records PENDING after push, without waiting for deployment.
            if run_git(project_root, "status", "--porcelain"):
                raise AudioPublicationError("CANONICAL_GIT_DIRTY")
            full_path = project_root / post_path
            if not full_path.is_file() or full_path.is_symlink():
                raise AudioPublicationError("POST_NOT_REGULAR_FILE")
            raw = full_path.read_bytes()
            try:
                updated = plan_audio_binding(raw, post["article_id"], post["post_sha256"], audio_url)
            except BindingError as exc:
                raise AudioPublicationError(str(exc)) from exc
            # Produce exactly one scoped Website mutation. No other files staged.
            if pilot_grant_path is not None:
                claim_pilot_stage(runtime_root, 'AUDIO_URL_ONLY_RELEASE', pilot)
            s4.atomic_write_bytes(full_path, updated)
            try:
                if build:
                    check = subprocess.run(["npm", "run", "build"], cwd=project_root,
                                           capture_output=True, text=True, check=False, timeout=240)
                    if check.returncode:
                        raise AudioPublicationError("AUDIO_ONLY_WEBSITE_BUILD_FAILED")
                page_url = rendered_audio_page(project_root, audio_url)
                entry["target_canonical_url"] = page_url
                entry["site_transaction_parent"] = remote
                s4.atomic_write_json(entry_path, entry)  # durable intent before Git commit/push
                run_git(project_root, "add", "--", post_path)
                staged = run_git(project_root, "diff", "--cached", "--name-only").splitlines()
                if staged != [post_path]:
                    raise AudioPublicationError("AUDIO_STAGING_OUTSIDE_ALLOWED_SCOPE")
                run_git(project_root, "commit", "-m", f"feat: add read-aloud for {post['article_id']}")
                commit = run_git(project_root, "rev-parse", "HEAD")
            except Exception:
                # Restore only if we still own the expected exact file; never reset unrelated work.
                if full_path.read_bytes() == updated:
                    s4.atomic_write_bytes(full_path, raw)
                raise
            # A failed push is an explicit ambiguous external-state boundary. Never reset/rebase/replay.
            if push:
                try:
                    run_git(project_root, "push", "origin", "main")
                except AudioPublicationError as exc:
                    raise AudioPublicationError("AUDIO_PUSH_AMBIGUOUS_MANUAL_RECONCILIATION") from exc
            else:
                raise AudioPublicationError("AUDIO_TEST_COMMITTED_NOT_PUSHED")
            pending = {
                "schema": RELEASE_SCHEMA, "kind": "AUDIO_ONLY_UPDATE",
                "commit": commit, "publication_state": "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY",
                "notification_policy": "NO_EMAIL", "notification_sent_count": 0,
                "article_id": post["article_id"], "post_path": post_path, "audio_url": audio_url,
                "previous_commit": remote, "canonical_url": page_url,
            }
            try:
                record_pending_under_lock(runtime_root, pending)
            except (PreflightError, OSError) as exc:
                raise AudioPublicationError("AUDIO_PUSHED_PENDING_RECEIPT_RECONCILIATION") from exc
            entry["status"] = "AUDIO_RELEASE_PENDING_VERIFY"
            entry["website_commit"] = commit
            s4.atomic_write_json(entry_path, entry)
            return entry
    return None
