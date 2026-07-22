#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a website publication result without performing deployment.")
    parser.add_argument("--contract-version", choices=["1.0", "1.1"], default="1.1")
    parser.add_argument("--status", choices=["dry_run_passed", "built", "committed", "pushed", "deployed", "failed"], required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--post-path", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--build-status", choices=["not_run", "passed", "failed"], default="not_run")
    parser.add_argument("--build-passed", action="store_true", help="兼容旧版调用；等同于 --build-status passed。")
    parser.add_argument("--build-command")
    parser.add_argument("--build-completed-at")
    parser.add_argument("--build-error")
    parser.add_argument("--article-id")
    parser.add_argument("--published-at")
    parser.add_argument("--processed-path")
    parser.add_argument("--commit-hash")
    parser.add_argument("--push-status", choices=["not_run", "committed", "pushed", "failed"], default="not_run")
    parser.add_argument("--deployment-status", choices=["not_run", "pending", "deployed", "failed"], default="not_run")
    parser.add_argument("--notification-status", choices=["not_run", "suppressed", "sent", "partial_failed", "failed"], default="not_run")
    parser.add_argument("--source-contract")
    parser.add_argument("--acceptance-evidence-id")
    parser.add_argument("--acceptance-evidence-path")
    parser.add_argument("--acceptance-evidence-sha256")
    parser.add_argument("--error-stage")
    args = parser.parse_args()

    if args.build_passed:
        args.build_status = "passed"
    build_passed = args.build_status == "passed"
    if args.contract_version == "1.0":
        payload = {
            "interface": "website-publication-result",
            "version": "1.0",
            "status": args.status,
            "slug": args.slug,
            "article_id": args.article_id,
            "published_at": args.published_at,
            "post_path": args.post_path,
            "processed_path": args.processed_path,
            "build": {"passed": build_passed},
            "commit_hash": args.commit_hash,
            "push_status": None if args.push_status == "not_run" else args.push_status,
            "deployment_status": args.deployment_status,
            "notification_status": args.notification_status,
        }
    else:
        payload = {
            "interface": "website-publication-result",
            "version": "1.1",
            "status": args.status,
            "slug": args.slug,
            "article_id": args.article_id,
            "published_at": args.published_at,
            "post_path": args.post_path,
            "processed_path": args.processed_path,
            "build": {
                "status": args.build_status,
                "passed": build_passed,
                "command": args.build_command,
                "completed_at": args.build_completed_at,
                "error": args.build_error,
            },
            "commit_hash": args.commit_hash,
            "push_status": args.push_status,
            "deployment_status": args.deployment_status,
            "notification_status": args.notification_status,
            "evidence": {
                "producer": "个人网页项目/scripts/write_publication_result.py",
                "written_at": datetime.now(timezone.utc).isoformat(),
                "atomic_write": True,
                "source_contract": args.source_contract,
                "acceptance_evidence_id": args.acceptance_evidence_id,
                "acceptance_evidence_path": args.acceptance_evidence_path,
                "acceptance_evidence_sha256": args.acceptance_evidence_sha256,
                "final_status_authority": "workspace-control publication-acceptance-evidence/v1 bundle",
                "error_stage": args.error_stage,
            },
        }

    atomic_write_json(Path(args.output), payload)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
