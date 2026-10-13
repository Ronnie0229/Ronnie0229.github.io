#!/usr/bin/env python3
"""Narrow patch planner for an already-published post audioUrl.

Defaults to verification only. Mutation only for explicitly requested and validated
single post in a dedicated publication transaction; does not invoke git or notify.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


class BindingError(RuntimeError):
    pass


def plan_audio_binding(raw: bytes, article_id: str, source_sha256: str, audio_url: str) -> bytes:
    if hashlib.sha256(raw).hexdigest() != source_sha256:
        raise BindingError("SOURCE_POST_SHA_DRIFT")
    if not re.fullmatch(r"post-[A-Za-z0-9-]+", article_id):
        raise BindingError("ARTICLE_ID_INVALID")
    expected = f"https://audio.ronniecross.com/audio/articles/{article_id}/article.mp3"
    if audio_url != expected:
        raise BindingError("R2_AUDIO_URL_NOT_ALLOWED")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise BindingError("POST_ENCODING_INVALID") from exc
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise BindingError("POST_FRONTMATTER_INVALID")
    end = text.index("\n---\n", 4)
    fm = text[4:end]
    if len(re.findall(r"^articleId:\s*", fm, re.M)) != 1:
        raise BindingError("ARTICLE_ID_MISSING_OR_DUPLICATE")
    if not re.search(r'^articleId:\s*["\']?' + re.escape(article_id) + r'["\']?\s*$', fm, re.M):
        raise BindingError("ARTICLE_ID_MISMATCH")
    if re.search(r"^audioUrl\s*:", fm, re.M):
        raise BindingError("AUDIO_URL_ALREADY_EXISTS")
    if not text.encode("utf-8") == raw:
        raise BindingError("POST_BOM_NOT_SUPPORTED")
    return (text[:end] + f'\naudioUrl: "{audio_url}"' + text[end:]).encode("utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--post", type=Path, required=True)
    p.add_argument("--article-id", required=True)
    p.add_argument("--source-sha256", required=True)
    p.add_argument("--audio-url", required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    try:
        if not args.post.is_file() or args.post.is_symlink():
            raise BindingError("POST_MISSING_OR_SYMLINK")
        original = args.post.read_bytes()
        updated = plan_audio_binding(original, args.article_id, args.source_sha256, args.audio_url)
        if args.apply:
            # Real publication tool must hold serialized publication lock and freshly verify the preceding release.
            raise BindingError("DIRECT_UNSERIALIZED_APPLY_FORBIDDEN")
        print(f"BINDING_PLAN_PASS old_sha={hashlib.sha256(original).hexdigest()} new_sha={hashlib.sha256(updated).hexdigest()}")
        return 0
    except (BindingError, OSError) as exc:
        print("BLOCKED", str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
