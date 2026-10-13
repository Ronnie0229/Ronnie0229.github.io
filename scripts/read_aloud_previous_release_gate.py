#!/usr/bin/env python3
"""Fail-closed, read-only previous website-release gate for article and audio publishers.

Never waits for deployments, writes website content, sends email or changes Git.
Caller must hold the Website publication serialization lock while checking and committing.
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import urllib.request
from typing import Any

SHA = re.compile(r"^[a-f0-9]{40}$")
KINDS = {"ARTICLE", "AUDIO_ONLY_UPDATE", "SITE_MAINTENANCE"}


class PreflightError(RuntimeError):
    pass


def validate_previous_release(receipt: dict[str, Any], deployment: dict[str, Any],
                              *, page_status: int, page_contains_identity: bool,
                              media_ready: bool = False) -> dict[str, Any]:
    """Validate strictly typed previous release evidence, not just HTTP 200."""
    if not isinstance(receipt, dict) or not isinstance(deployment, dict):
        raise PreflightError("RELEASE_EVIDENCE_INVALID")
    kind = receipt.get("kind")
    commit = receipt.get("commit")
    if kind not in KINDS or not isinstance(commit, str) or not SHA.fullmatch(commit):
        raise PreflightError("RELEASE_IDENTITY_INVALID")
    if deployment.get("commit") != commit:
        raise PreflightError("PREVIOUS_DEPLOYMENT_NOT_EXACT")
    if page_status != 200 or page_contains_identity is not True:
        raise PreflightError("PREVIOUS_LIVE_CONTENT_UNVERIFIED")
    if kind == "ARTICLE":
        if receipt.get("rss_verified") is not True or receipt.get("sitemap_verified") is not True:
            raise PreflightError("PREVIOUS_ARTICLE_FEEDS_UNVERIFIED")
        if receipt.get("notification_terminal") != "PASS":
            raise PreflightError("PREVIOUS_ARTICLE_NOTIFICATION_UNVERIFIED")
    elif kind == "SITE_MAINTENANCE":
        if receipt.get("notification_policy") != "NO_EMAIL" or type(receipt.get("notification_sent_count")) is not int or receipt.get("notification_sent_count") != 0:
            raise PreflightError("MAINTENANCE_EMAIL_POLICY_INVALID")
    else:
        if receipt.get("notification_policy") != "NO_EMAIL":
            raise PreflightError("AUDIO_RELEASE_EMAIL_POLICY_INVALID")
        if type(receipt.get("notification_sent_count")) is not int or receipt.get("notification_sent_count") != 0:
            raise PreflightError("AUDIO_RELEASE_EMAIL_COUNT_INVALID")
        if media_ready is not True:
            raise PreflightError("PREVIOUS_AUDIO_R2_UNVERIFIED")
    return {"status": "PREVIOUS_RELEASE_PASS", "kind": kind, "commit": commit}


def retrieve_deployment(url: str, timeout: float = 10.0) -> dict[str, Any]:
    if url != "https://ronniecross.com/deployment.json":
        raise PreflightError("DEPLOYMENT_URL_NOT_ALLOWLISTED")
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            if response.status != 200:
                raise PreflightError("DEPLOYMENT_HTTP_INVALID")
            data = json.load(response)
    except (OSError, ValueError) as exc:
        raise PreflightError("DEPLOYMENT_READ_FAILED") from exc
    if not isinstance(data, dict) or not isinstance(data.get("commit"), str):
        raise PreflightError("DEPLOYMENT_CONTENT_INVALID")
    return data


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--receipt", required=True)
    p.add_argument("--page-status", type=int, required=True)
    p.add_argument("--page-contains-identity", action="store_true")
    p.add_argument("--media-ready", action="store_true")
    args = p.parse_args()
    from pathlib import Path
    try:
        receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
        deployment = retrieve_deployment("https://ronniecross.com/deployment.json")
        result = validate_previous_release(receipt, deployment, page_status=args.page_status,
                                           page_contains_identity=args.page_contains_identity,
                                           media_ready=args.media_ready)
    except (OSError, json.JSONDecodeError, PreflightError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
