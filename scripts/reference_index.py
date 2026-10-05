#!/usr/bin/env python3
"""Index local visual reference files and calculate SHA256.

This script never marks an asset approved. Human approval must be written
separately into the Git-tracked reference manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_ref_id(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    pieces = [p.upper().replace("-", "_").replace(" ", "_") for p in rel.parts]
    return "REF_" + "_".join(pieces)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"reference root not found: {root}")

    items = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        items.append(
            {
                "ref_id": make_ref_id(root, path),
                "relative_path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "approved_by_user": False,
                "type": None,
                "angle": None,
                "notes": "",
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "count": len(items),
        "warning": "Index only. approved_by_user is intentionally false until explicit user approval.",
        "references": items,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(items), "out": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
