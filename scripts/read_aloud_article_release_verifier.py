#!/usr/bin/env python3
"""Fresh asynchronous verification of previous normal ARTICLE / SITE_MAINTENANCE release."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

from read_aloud_audio_site_publisher import deployed_sha
from read_aloud_publication_lock import publication_lock, last_receipt, mark_previous_verified_under_lock


class ArticleReleaseVerificationError(RuntimeError):
    pass


def _curl(url: str) -> str:
    if not url.startswith("https://ronniecross.com/"):
        raise ArticleReleaseVerificationError("URL_NOT_ALLOWED")
    reply = subprocess.run(["curl", "-fsSL", "--max-time", "20", url], capture_output=True, check=False)
    if reply.returncode:
        raise ArticleReleaseVerificationError("LIVE_RESOURCE_UNAVAILABLE")
    return reply.stdout.decode("utf-8", errors="replace")


def _mail_runs(commit: str) -> list[dict]:
    reply = subprocess.run(["gh", "run", "list", "--workflow", "email-published-posts.yml",
                            "--commit", commit, "--limit", "15",
                            "--json", "databaseId,status,conclusion,headSha"],
                           capture_output=True, text=True, check=False)
    if reply.returncode:
        raise ArticleReleaseVerificationError("GITHUB_MAIL_QUERY_FAILED")
    try:
        runs = json.loads(reply.stdout)
        return [item for item in runs if item.get("headSha") == commit]
    except (ValueError, TypeError) as exc:
        raise ArticleReleaseVerificationError("MAIL_RUN_JSON_INVALID") from exc


def _mail_log(run_id: int) -> str:
    reply = subprocess.run(["gh", "run", "view", str(run_id), "--log"],
                           capture_output=True, text=True, check=False)
    if reply.returncode:
        raise ArticleReleaseVerificationError("GITHUB_MAIL_LOG_UNAVAILABLE")
    return reply.stdout


def _article_email_terminal(commit: str) -> bool:
    runs = _mail_runs(commit)
    if not runs:
        return False
    from verify_publication_release import extract_send_summary
    found_post = False
    for run in runs:
        if run.get("status") != "completed":
            return False
        if run.get("conclusion") != "success":
            raise ArticleReleaseVerificationError("ARTICLE_EMAIL_RUN_FAILED")
        summary = extract_send_summary(_mail_log(run["databaseId"]))
        if not summary or not isinstance(summary.get("postCount"), int):
            raise ArticleReleaseVerificationError("ARTICLE_EMAIL_SUMMARY_MISSING")
        if summary.get("failedCount") != 0:
            raise ArticleReleaseVerificationError("ARTICLE_EMAIL_FAILED_COUNT_NONZERO")
        if summary.get("postCount", 0) >= 1:
            found_post = True
    return found_post


def _maintenance_email_zero(commit: str) -> bool:
    runs = _mail_runs(commit)
    for run in runs:
        if run.get("status") != "completed":
            return False
        if run.get("conclusion") != "success":
            raise ArticleReleaseVerificationError("MAINTENANCE_EMAIL_WORKFLOW_FAILED")
        if "No changed published posts were found in this push." not in _mail_log(run["databaseId"]):
            raise ArticleReleaseVerificationError("MAINTENANCE_EMAIL_ZERO_NOT_PROVEN")
    return True  # No path-triggered workflow also means no subscriber email from this workflow.


def verify_previous_article(runtime: Path) -> dict | None:
    with publication_lock(runtime):
        receipt = last_receipt(runtime)
        if not receipt or receipt.get("publication_state") != "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY":
            return None
        kind = receipt.get("kind")
        if kind not in {"ARTICLE", "SITE_MAINTENANCE"}:
            return None
        sha = receipt.get("commit")
        if not isinstance(sha, str) or not re.fullmatch("[a-f0-9]{40}", sha):
            raise ArticleReleaseVerificationError("PREVIOUS_RELEASE_SHA_INVALID")
        if deployed_sha() != sha:
            return None
        url = receipt.get("canonical_url")
        marker = receipt.get("expected_identity")
        if not isinstance(url, str) or not isinstance(marker, str) or not marker:
            raise ArticleReleaseVerificationError("LIVE_ARTICLE_IDENTITY_MISSING")
        page = _curl(url)
        if marker not in page:
            raise ArticleReleaseVerificationError("LIVE_ARTICLE_IDENTITY_MISMATCH")
        if kind == "ARTICLE":
            rss = _curl("https://ronniecross.com/rss.xml")
            sitemap = _curl("https://ronniecross.com/sitemap.xml")
            # Presence of exact URL (possibly XML escaping URL ampersands) is required.
            if url not in rss or url not in sitemap:
                raise ArticleReleaseVerificationError("ARTICLE_FEEDS_MISSING_CANONICAL_URL")
            if not _article_email_terminal(sha):
                return None
        else:
            if not _maintenance_email_zero(sha):
                return None
        if kind == "ARTICLE":
            receipt["rss_verified"] = True
            receipt["sitemap_verified"] = True
            receipt["notification_terminal"] = "PASS"
        from read_aloud_s4_runner import atomic_write_json
        atomic_write_json(runtime / "website-publication" / "last_website_release.json", receipt)
        mark_previous_verified_under_lock(runtime, sha)
        return {"status": "VERIFIED", "commit": sha, "kind": kind}
