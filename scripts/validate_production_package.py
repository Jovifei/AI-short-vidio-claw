#!/usr/bin/env python3
"""Validate a LOOKREEL/episode production package without rendering."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project-dir", required=True)
    p.add_argument("--approval-manifest", default="approval_manifest.json")
    args = p.parse_args()

    root = Path(args.project_dir)
    errors = []
    warnings = []

    required_any = [
        ("plan/episode", ["plan.yaml", "episode.yaml"]),
        ("image prompts", ["image_prompts.md"]),
        ("video prompts", ["video_prompts.md"]),
        ("edit plan", ["edit_plan.md"]),
    ]
    for label, choices in required_any:
        if not any((root / name).is_file() for name in choices):
            errors.append(f"missing {label}: one of {choices}")

    manifest_path = root / args.approval_manifest
    if not manifest_path.is_file():
        errors.append(f"missing approval manifest: {manifest_path}")
        manifest = None
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid approval manifest JSON: {exc}")
            manifest = None

    counts = {"shots": 0, "approved": 0, "production_ready": 0}
    if isinstance(manifest, dict):
        shots = manifest.get("shots")
        if not isinstance(shots, dict) or not shots:
            errors.append("approval manifest has no shots")
        else:
            counts["shots"] = len(shots)
            for shot_id, shot in shots.items():
                if not isinstance(shot, dict):
                    errors.append(f"{shot_id}: shot entry not object")
                    continue
                status = shot.get("status")
                if status in {"USER_APPROVED", "PRODUCTION_READY"}:
                    counts["approved"] += 1
                    if not shot.get("sha256"):
                        errors.append(f"{shot_id}: approved but sha256 missing")
                    refs = shot.get("identity_refs") or {}
                    for char in ("DAIYU", "WUKONG"):
                        if not refs.get(char):
                            errors.append(f"{shot_id}: approved but {char} identity refs missing")
                    costumes = shot.get("costume_refs") or {}
                    for char in ("DAIYU", "WUKONG"):
                        if not costumes.get(char):
                            errors.append(f"{shot_id}: approved but {char} costume ref missing")
                if status == "PRODUCTION_READY":
                    counts["production_ready"] += 1

    if counts["approved"] == 0:
        warnings.append("no user-approved keyframes yet; rendering must remain blocked")

    report = {
        "project_dir": str(root),
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
