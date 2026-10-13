#!/usr/bin/env python3
"""Optional, fail-closed incremental Git intake for the existing five-minute tick.

Never backfills old missing-audio posts. Disabled unless an explicit v1 baseline
selector is placed in the runtime by a separate, authorized activation task.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from read_aloud_new_post_intake import register

SCHEMA = "ronniecross-readaloud-new-post-selector/v1"
SHA = re.compile(r"^[a-f0-9]{40}$")


class SelectorError(RuntimeError):
    pass


def _command(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)
    if p.returncode:
        raise SelectorError("GIT_REMOTE_OBSERVATION_FAILED")
    return p.stdout.strip()


def read_selector(runtime: Path) -> dict[str, Any] | None:
    file = runtime / "new-post-automation-selector.json"
    if not file.is_file():
        return None
    try:
        value = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SelectorError("SELECTOR_CORRUPT") from exc
    if not isinstance(value, dict) or value.get("schema") != SCHEMA or value.get("enabled") is not True:
        raise SelectorError("SELECTOR_INVALID_OR_DISABLED")
    if not isinstance(value.get("last_processed_commit"), str) or not SHA.fullmatch(value["last_processed_commit"]):
        raise SelectorError("SELECTOR_COMMIT_INVALID")
    if not isinstance(value.get("authorization_ref"), str) or not value["authorization_ref"]:
        raise SelectorError("SELECTOR_AUTHORIZATION_MISSING")
    return value


def reconcile(repo: Path, runtime: Path) -> list[dict[str, Any]]:
    selector = read_selector(runtime)
    if selector is None:
        return []
    before = selector["last_processed_commit"]
    # Fetch only; never checkout, reset, merge or rebase the working tree.
    _command(repo, "fetch", "--quiet", "origin", "main")
    after = _command(repo, "rev-parse", "refs/remotes/origin/main")
    if not SHA.fullmatch(after):
        raise SelectorError("REMOTE_SHA_INVALID")
    if after == before:
        return []
    entries = register(repo, runtime, before, after, selector["authorization_ref"])
    selector["last_processed_commit"] = after
    selector["last_reconciled_commit"] = after
    path = runtime / "new-post-automation-selector.json"
    tmp = path.with_suffix(".pending")
    if tmp.exists():
        raise SelectorError("SELECTOR_PREVIOUS_WRITE_INCOMPLETE")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(selector, output, ensure_ascii=False, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    return entries
