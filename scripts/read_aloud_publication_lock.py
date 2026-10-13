#!/usr/bin/env python3
"""Serialized website publication gate receipt store (local primitive).

All write transactions must take the same flock before checking last receipt.
This does not itself grant production authorization or perform Git/Cloudflare writes.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
from typing import Iterator

from read_aloud_previous_release_gate import PreflightError

SCHEMA = "ronniecross-website-serialized-release/v1"
RECEIPT_NAME = "last_website_release.json"


@contextmanager
def publication_lock(runtime_root: Path) -> Iterator[None]:
    directory = runtime_root / "website-publication"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(directory, 0o700)
    lock_path = directory / "release.lock"
    fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def last_receipt(runtime_root: Path) -> dict | None:
    path = runtime_root / "website-publication" / RECEIPT_NAME
    if not path.exists():
        return None
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightError("PREVIOUS_RELEASE_RECEIPT_CORRUPT") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        raise PreflightError("PREVIOUS_RELEASE_RECEIPT_INVALID")
    return receipt


def record_pending_under_lock(runtime_root: Path, receipt: dict) -> None:
    """Call ONLY while holding publication_lock after authoritative push receipt."""
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        raise PreflightError("RELEASE_RECEIPT_INVALID")
    if receipt.get("kind") not in {"ARTICLE", "AUDIO_ONLY_UPDATE", "SITE_MAINTENANCE"}:
        raise PreflightError("RELEASE_KIND_INVALID")
    if receipt.get("publication_state") != "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY":
        raise PreflightError("RELEASE_STATE_INVALID")
    from read_aloud_previous_release_gate import SHA
    if not isinstance(receipt.get("commit"), str) or not SHA.fullmatch(receipt["commit"]):
        raise PreflightError("RELEASE_SHA_INVALID")
    if receipt["kind"] in {"AUDIO_ONLY_UPDATE", "SITE_MAINTENANCE"}:
        if receipt.get("notification_policy") != "NO_EMAIL" or type(receipt.get("notification_sent_count")) is not int or receipt["notification_sent_count"] != 0:
            raise PreflightError("AUDIO_RELEASE_EMAIL_POLICY_INVALID")
    destination = runtime_root / "website-publication" / RECEIPT_NAME
    previous = last_receipt(runtime_root)
    if previous is not None and previous.get("publication_state") == "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY":
        raise PreflightError("PREVIOUS_RELEASE_STILL_PENDING")
    tmp = destination.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()


def mark_previous_verified_under_lock(runtime_root: Path, expected_commit: str) -> None:
    receipt = last_receipt(runtime_root)
    if receipt is None or receipt.get("commit") != expected_commit:
        raise PreflightError("PREVIOUS_RELEASE_IDENTITY_CHANGED")
    if receipt.get("publication_state") != "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY":
        raise PreflightError("PREVIOUS_RELEASE_NOT_PENDING")
    new_receipt = dict(receipt, publication_state="VERIFIED")
    destination = runtime_root / "website-publication" / RECEIPT_NAME
    temp = destination.with_suffix(".verify.tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(new_receipt, stream, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, destination)
