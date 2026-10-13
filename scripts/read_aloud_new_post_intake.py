#!/usr/bin/env python3
"""Narrow, durable registration of approved new-post release events.

No TTS, NAS, R2, Git mutation or website deployment occurs here.
A release controller may consume only records whose source release has been authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from read_aloud_new_post_detector import DetectionError, detect_new_posts

SCHEMA = "ronniecross-new-post-audio-intake/v1"


class IntakeError(RuntimeError):
    pass


def register(repo: Path, runtime: Path, before: str, after: str, authorization_ref: str) -> list[dict[str, Any]]:
    if not authorization_ref or len(authorization_ref) > 256 or not authorization_ref.strip():
        raise IntakeError("AUTHORIZATION_REF_INVALID")
    # Fail closed when the caller has not explicitly identified an authorized push event.
    entries = detect_new_posts(repo, before, after)
    destination = runtime / "new-post-intake"
    result = []
    for entry in entries:
        identity = hashlib.sha256((entry["source_commit"] + "\n" + entry["article_id"]).encode()).hexdigest()
        record = {
            "schema": SCHEMA,
            "intake_id": identity,
            "source_before": before,
            "source_after": after,
            "authorization_ref": authorization_ref,
            "post": entry,
            "status": "WAIT_RENDER_AND_EXPLICIT_TTS_AUTHORIZATION",
            "no_automatic_side_effects": True,
        }
        path = destination / f"{identity}.json"
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise IntakeError("INTAKE_RECORD_CORRUPT") from exc
            if existing != record:
                raise IntakeError("INTAKE_IDENTITY_CONFLICT")
            result.append(existing)
            continue
        destination.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(destination, 0o700)
        # No accidental clobber on concurrent executions; atomic exclusive create.
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise IntakeError("INTAKE_CONCURRENT_CREATE_RETRY_REQUIRED")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        result.append(record)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--authorization-ref", required=True)
    args = parser.parse_args()
    try:
        result = register(args.repo.resolve(), args.runtime_root.resolve(), args.before, args.after, args.authorization_ref)
    except (IntakeError, DetectionError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 2
    print(json.dumps({"status": "INTAKE_REGISTERED", "records": result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
