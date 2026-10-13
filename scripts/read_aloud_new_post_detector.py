#!/usr/bin/env python3
"""Read-only, bounded detection of newly added posts from an explicit pushed Git interval.

This is a discovery/identity component, NOT permission to generate audio or publish.
The caller must bind a verified publication transaction and successful origin push.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

POST_PREFIX = "src/content/posts/"
HEX_SHA = re.compile(r"^[0-9a-f]{40}$")
ID_PATTERN = re.compile(r'^articleId:\s*["\']?(post-[a-zA-Z0-9-]+)["\']?\s*$', re.M)
AUDIO_URL = re.compile(r"^audioUrl:\s*.+$", re.M)


class DetectionError(RuntimeError):
    pass


def git(repo: Path, *args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if p.returncode:
        raise DetectionError("GIT_COMMAND_FAILED:" + (p.stderr.decode("utf-8", "replace")[:250]))
    return p.stdout


def detect_new_posts(repo: Path, before: str, after: str, remote_ref: str = "refs/remotes/origin/main") -> list[dict[str, str]]:
    """Only exact new files in a pushed interval; no missing-audio backfill."""
    if not HEX_SHA.fullmatch(before) or not HEX_SHA.fullmatch(after) or before == after:
        raise DetectionError("INVALID_COMMIT_RANGE")
    verified_after = git(repo, "rev-parse", "--verify", after + "^{commit}").decode().strip()
    verified_remote = git(repo, "rev-parse", "--verify", remote_ref + "^{commit}").decode().strip()
    if verified_after != after or not verified_remote:
        raise DetectionError("REVISION_IDENTITY_INVALID")
    git(repo, "merge-base", "--is-ancestor", before, after)
    git(repo, "merge-base", "--is-ancestor", after, verified_remote)
    paths = git(repo, "diff", "--name-only", "--diff-filter=A", "-z", before, after).decode().split("\0")
    entries: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for path in paths:
        if not path or not path.startswith(POST_PREFIX) or not path.endswith(".md"):
            continue
        # Git pathspecs and exact files, never arbitrary paths.
        if ".." in Path(path).parts or Path(path).is_absolute():
            raise DetectionError("INVALID_POST_PATH")
        raw = git(repo, "show", after + ":" + path)
        try:
            body = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise DetectionError("POST_UTF8_INVALID") from exc
        if not body.startswith("---\n") or "\n---\n" not in body[4:]:
            raise DetectionError("POST_FRONTMATTER_MISSING")
        frontmatter = body[4:].split("\n---\n", 1)[0]
        ids = ID_PATTERN.findall(frontmatter)
        if len(ids) != 1 or ids[0] in seen_ids:
            raise DetectionError("ARTICLE_ID_INVALID_OR_DUPLICATE")
        seen_ids.add(ids[0])
        # Already-bound media must not be regenerated.
        if AUDIO_URL.search(frontmatter):
            continue
        entries.append({
            "article_id": ids[0],
            "post_path": path,
            "source_commit": after,
            "post_sha256": hashlib.sha256(raw).hexdigest(),
            "trigger_kind": "NEW_POST_ADDED_IN_PUSH_INTERVAL",
        })
    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--remote-ref", default="refs/remotes/origin/main")
    args = parser.parse_args()
    try:
        entries = detect_new_posts(args.repo.resolve(), args.before, args.after, args.remote_ref)
    except DetectionError as exc:
        print(json.dumps({"status": "BLOCKED", "code": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"status": "READ_ONLY_NEW_POST_DETECTION", "entries": entries}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
