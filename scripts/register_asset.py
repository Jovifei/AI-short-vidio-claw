#!/usr/bin/env python3
"""Append a content-addressed entry to the local asset ledger JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUS = {
    "DRAFT", "CANDIDATE", "RECOMMENDED", "USER_APPROVED", "PRODUCTION_READY",
    "ACCEPTED", "SUPERSEDED", "REJECTED", "ARCHIVED"
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", default="local/asset_ledger.jsonl")
    p.add_argument("--asset-id", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--project")
    p.add_argument("--shot")
    p.add_argument("--source")
    p.add_argument("--notes", default="")
    args = p.parse_args()

    if args.status not in VALID_STATUS:
        raise SystemExit(f"invalid status: {args.status}")
    if args.status == "USER_APPROVED":
        raise SystemExit(
            "register_asset.py cannot grant USER_APPROVED; use explicit approval workflow first"
        )

    file_path = Path(args.file)
    if not file_path.is_file():
        raise SystemExit(f"file not found: {file_path}")

    entry = {
        "asset_id": args.asset_id,
        "type": args.type,
        "status": args.status,
        "version": args.version,
        "local_path": str(file_path),
        "sha256": sha256_file(file_path),
        "project": args.project,
        "shot": args.shot,
        "source": args.source,
        "generated_by": "scripts/register_asset.py",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "approved_at": None,
        "supersedes": None,
        "notes": args.notes,
    }

    ledger = Path(args.ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
