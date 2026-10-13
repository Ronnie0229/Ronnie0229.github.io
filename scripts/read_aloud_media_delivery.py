#!/usr/bin/env python3
"""Append-only WAV archive and recoverable R2 MP3 upload primitives.

Never edits Git or triggers article email. Exact sha before and after every copy.
Production archive root is fixed by Website authority, no unsafe fallback to share.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

NAS_ROOT = Path("/Volumes/home/RonnieArchive/ReadAloud/articles")
AUDIO_ORIGIN = "https://audio.ronniecross.com"
R2_BUCKET = "ronniecross-audio"


class DeliveryError(RuntimeError):
    pass


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_title(title: str) -> str:
    value = re.sub(r'[/\\:\x00-\x1f]+', "-", title).strip().strip(".")
    if not value or len(value) > 70 or value in {".", ".."}:
        raise DeliveryError("TITLE_UNSAFE")
    return value


def archive_wav(wav: Path, expected_sha: str, *, article_id: str, date: str, title: str,
                workflow_id: str, render_sha: str, nas_root: Path = NAS_ROOT,
                require_mount: bool = True, provenance: dict | None = None) -> dict:
    if not re.fullmatch(r"post-[A-Za-z0-9-]+", article_id):
        raise DeliveryError("ARTICLE_ID_INVALID")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise DeliveryError("DATE_INVALID")
    if not re.fullmatch(r"[a-f0-9]{64}", expected_sha):
        raise DeliveryError("WAV_SHA_INVALID")
    if not wav.is_file() or wav.is_symlink() or sha_file(wav) != expected_sha:
        raise DeliveryError("WAV_SOURCE_INVALID")
    if require_mount and not os.path.ismount("/Volumes/home"):
        raise DeliveryError("PRODUCTION_NAS_MOUNT_REQUIRED")
    if not nas_root.is_dir():
        raise DeliveryError("NAS_ROOT_UNAVAILABLE")
    t = safe_title(title)
    base = nas_root / f"{date}_{t}_{article_id}"
    master = base / "master" / f"{date}_{t}_master.wav"
    manifest = base / "metadata" / "audio-manifest.json"
    if master.exists():
        if master.is_symlink() or sha_file(master) != expected_sha:
            raise DeliveryError("ARCHIVE_EXISTING_WAV_CONFLICT")
    else:
        master.parent.mkdir(parents=True, exist_ok=True)
        temp = master.with_suffix(".pending")
        if temp.exists():
            raise DeliveryError("ARCHIVE_PREVIOUS_INCOMPLETE")
        with wav.open("rb") as src, temp.open("xb") as dst:
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if sha_file(temp) != expected_sha:
            raise DeliveryError("ARCHIVE_COPY_SHA_MISMATCH")
        os.replace(temp, master)
    payload = {
        "schema": "ronniecross-readaloud-audio-manifest/v1",
        "article_id": article_id, "workflow_id": workflow_id, "render_sha256": render_sha,
        "wav_master_sha256": expected_sha, "wav_master_bytes": master.stat().st_size,
        "master_path": str(master),
        "generation": (provenance or {}).get("generation", {}),
        "delivery": (provenance or {}).get("delivery", {}),
        "acceptance": (provenance or {}).get("acceptance", {"mode": "AUTO_TECHNICAL_QC", "human_listening_pass": False}),
        "storage_roles": {"NAS": "WAV_MASTER_AND_MANIFEST", "R2": "MP3_DELIVERY", "Git": "WEBSITE_POINTER_ONLY"},
    }
    if manifest.exists():
        try:
            existing = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DeliveryError("ARCHIVE_MANIFEST_CORRUPT") from exc
        if existing != payload:
            raise DeliveryError("ARCHIVE_MANIFEST_CONFLICT")
    else:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        with manifest.open("x", encoding="utf-8") as target:
            json.dump(payload, target, ensure_ascii=False, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
    return {"verified": sha_file(master) == expected_sha, "master_path": str(master),
            "master_sha256": expected_sha, "manifest_path": str(manifest)}


def _curl(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["curl", "--silent", "--show-error", "--max-time", "120", *args],
                          capture_output=True, check=False)


def verify_r2(url: str, expected_sha: str, expected_bytes: int) -> bool:
    status = _curl(["--location", "--output", "/dev/null", "--write-out", "%{http_code}", url])
    if status.returncode:
        raise DeliveryError("R2_HEAD_FAILED")
    if status.stdout.strip() == b"404":
        return False
    if status.stdout.strip() != b"200":
        raise DeliveryError("R2_HEAD_NOT_DECISIVE")
    full = _curl(["--fail", "--location", url])
    if full.returncode or len(full.stdout) != expected_bytes:
        return False
    if hashlib.sha256(full.stdout).hexdigest() != expected_sha:
        raise DeliveryError("R2_EXISTING_HASH_MISMATCH")
    partial = _curl(["--header", "Range: bytes=0-1023", "--output", "/dev/null",
                     "--write-out", "%{http_code}", url])
    if partial.returncode or partial.stdout.strip() != b"206":
        raise DeliveryError("R2_RANGE_NOT_SUPPORTED")
    return True


def upload_r2(mp3: Path, expected_sha: str, *, article_id: str, upload_allowed: bool = False) -> dict:
    if not re.fullmatch(r"post-[A-Za-z0-9-]+", article_id):
        raise DeliveryError("ARTICLE_ID_INVALID")
    if not mp3.is_file() or mp3.is_symlink() or sha_file(mp3) != expected_sha:
        raise DeliveryError("MP3_SOURCE_SHA_MISMATCH")
    key = f"audio/articles/{article_id}/article.mp3"
    url = f"{AUDIO_ORIGIN}/{key}"
    if verify_r2(url, expected_sha, mp3.stat().st_size):
        return {"verified": True, "url": url, "sha256": expected_sha, "existed": True}
    if not upload_allowed:
        raise DeliveryError("R2_UPLOAD_AUTHORITY_NOT_ENABLED")
    result = subprocess.run(["npx", "--no-install", "wrangler", "r2", "object", "put",
                             f"{R2_BUCKET}/{key}", "--remote", "--file", str(mp3),
                             "--content-type", "audio/mpeg", "--force"],
                            capture_output=True, text=True, check=False)
    if result.returncode:
        raise DeliveryError("R2_UPLOAD_COMMAND_FAILED")
    if not verify_r2(url, expected_sha, mp3.stat().st_size):
        raise DeliveryError("R2_UPLOADED_NOT_VERIFIED")
    return {"verified": True, "url": url, "sha256": expected_sha, "existed": False}
