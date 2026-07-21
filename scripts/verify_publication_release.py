#!/usr/bin/env python3
"""Verify that a published page is live and an optional email workflow completed.

This intentionally checks expected page content in addition to HTTP status because
Cloudflare Pages may return the site homepage with HTTP 200 for an unknown route.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request


def fetch_page(url: str, timeout: int) -> tuple[int, str, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "RonnieCross-Publication-Verifier/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, response.geturl(), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, exc.geturl(), body


def read_workflow(run_id: str) -> dict[str, object]:
    command = [
        "gh",
        "run",
        "view",
        run_id,
        "--json",
        "status,conclusion,url,name,createdAt,updatedAt",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "gh run view failed")
    return json.loads(completed.stdout)


def read_workflow_log(run_id: str) -> str:
    completed = subprocess.run(
        ["gh", "run", "view", run_id, "--log"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "gh run view --log failed")
    return completed.stdout


def extract_send_summary(log: str) -> dict[str, int | list[str]] | None:
    fields = ("postCount", "recipientCount", "successCount", "failedCount")
    summary: dict[str, int | list[str]] = {}
    for line in log.splitlines():
        stripped = line.rsplit("\t", 1)[-1].strip().rstrip(",")
        for field in fields:
            marker = f'"{field}":'
            if marker in stripped:
                value = stripped.split(marker, 1)[1].strip()
                try:
                    summary[field] = int(value)
                except ValueError:
                    pass
        if '"skippedSlugs":' in stripped:
            value = stripped.split(":", 1)[1].strip()
            try:
                summary["skippedSlugs"] = json.loads(value)
            except json.JSONDecodeError:
                pass
    return summary if summary else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--expect", action="append", default=[])
    parser.add_argument("--run-id")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    failures: list[str] = []
    status, final_url, body = fetch_page(args.url, args.timeout)
    page_checks = {expected: expected in body for expected in args.expect}

    if status != 200:
        failures.append(f"unexpected HTTP status: {status}")
    missing = [value for value, present in page_checks.items() if not present]
    if missing:
        failures.append("missing expected page content: " + ", ".join(missing))

    result: dict[str, object] = {
        "url": args.url,
        "final_url": final_url,
        "http_status": status,
        "page_checks": page_checks,
        "page_verified": status == 200 and not missing,
    }

    if args.run_id:
        try:
            workflow = read_workflow(args.run_id)
            log = read_workflow_log(args.run_id)
            send_summary = extract_send_summary(log)
            result["workflow"] = workflow
            result["send_summary"] = send_summary
            workflow_ok = (
                workflow.get("status") == "completed"
                and workflow.get("conclusion") == "success"
            )
            if not workflow_ok:
                failures.append(
                    "workflow not successful: "
                    f"status={workflow.get('status')} conclusion={workflow.get('conclusion')}"
                )
            if send_summary is not None:
                failed_count = int(send_summary.get("failedCount", 0))
                recipient_count = int(send_summary.get("recipientCount", 0))
                success_count = int(send_summary.get("successCount", 0))
                if failed_count != 0 or success_count != recipient_count:
                    failures.append(
                        "email send incomplete: "
                        f"recipients={recipient_count} success={success_count} failed={failed_count}"
                    )
        except (RuntimeError, json.JSONDecodeError) as exc:
            failures.append(f"workflow verification failed: {exc}")

    result["ok"] = not failures
    result["failures"] = failures
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
