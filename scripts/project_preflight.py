#!/usr/bin/env python3
"""V2 product-route preflight.

Checks repository facts and approval gates before local rendering.
It is intentionally fail-closed: missing approvals are blockers, not warnings.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


REQUIRED_DOCS = [
    "AGENTS.md",
    "PROJECT_STATE.md",
    "docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md",
    "docs/19_ACTIVE_VISUAL_SPEC.md",
    "docs/21_PRODUCTION_SOP_V2.md",
    "docs/25_CHARACTER_MODELING_REVIEW_SPEC.md",
    "docs/30_VISUAL_DIRECTION_BIBLE.md",
    "docs/31_CINEMATOGRAPHY_GRAMMAR.md",
    "docs/32_CHARACTER_PERFORMANCE_BIBLE.md",
]

REQUIRED_FILES = [
    "assets/style/ACTIVE_VISUAL_TARGET.yaml",
    "assets/characters/daiyu/character.yaml",
    "assets/characters/wukong/character.yaml",
    "assets/characters/daiyu/canonical_visual.yaml",
    "assets/characters/wukong/canonical_visual.yaml",
    "config/stage_gate_matrix.yaml",
    "config/quality_gates.yaml",
    "workflows/video/production/VID_wan22_5b_i2v_prod_v001.json",
]


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument(
        "--stage",
        choices=["MODEL_REVIEW", "V0", "K1", "T1", "E0", "E1"],
        default="MODEL_REVIEW",
    )
    args = p.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_DOCS + REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")

    visual_target = root / "assets/style/ACTIVE_VISUAL_TARGET.yaml"
    if visual_target.is_file():
        data = read_yaml(visual_target) or {}
        if data.get("status") not in {
            "PREPROD_APPROVED_PENDING_LOCAL_REFERENCE_HASH",
            "ACTIVE",
            "USER_APPROVED",
        }:
            warnings.append(f"unexpected visual target status: {data.get('status')}")

    daiyu_review = root / "assets/characters/daiyu/modeling_review.yaml"
    wukong_review = root / "assets/characters/wukong/modeling_review.yaml"

    reviews = {}
    for char, path in [("DAIYU", daiyu_review), ("WUKONG", wukong_review)]:
        if not path.is_file():
            errors.append(f"missing modeling review: {path.relative_to(root)}")
            continue
        reviews[char] = read_yaml(path) or {}

    if args.stage in {"V0", "K1", "T1", "E0", "E1"}:
        for char, review in reviews.items():
            if review.get("golden_model_status") != "APPROVED":
                errors.append(
                    f"{char} golden_model_status={review.get('golden_model_status')!r}; V0+ requires APPROVED"
                )

    if args.stage in {"K1", "T1", "E0", "E1"}:
        for char, rel in [
            ("DAIYU", "assets/characters/daiyu/reference_manifest.yaml"),
            ("WUKONG", "assets/characters/wukong/reference_manifest.yaml"),
        ]:
            path = root / rel
            if not path.is_file():
                errors.append(f"missing {rel}")
                continue
            manifest = read_yaml(path) or {}
            if manifest.get("status") not in {"USER_APPROVED", "PRODUCTION_READY"}:
                errors.append(f"{char} reference manifest not user-approved")
            if not manifest.get("golden_face_refs"):
                errors.append(f"{char} golden_face_refs empty")
            if not manifest.get("golden_costume_refs"):
                errors.append(f"{char} golden_costume_refs empty")

    if args.stage in {"T1", "E0", "E1"}:
        approval = root / "episodes/LOOKREEL01/approval_manifest.json"
        if not approval.is_file():
            errors.append("missing LOOKREEL01 approval manifest")
        else:
            data = json.loads(approval.read_text(encoding="utf-8"))
            approved = [
                shot_id
                for shot_id, shot in (data.get("shots") or {}).items()
                if shot.get("status") in {"USER_APPROVED", "PRODUCTION_READY"}
                and shot.get("approved_by_user") is True
            ]
            if len(approved) < 3 and args.stage == "T1":
                errors.append(f"T1 requires >=3 approved LOOKREEL keyframes; found {len(approved)}")
            if args.stage in {"E0", "E1"} and len(approved) < 10:
                errors.append(f"E0/E1 requires 10 approved LOOKREEL keyframes; found {len(approved)}")

    result = {
        "root": str(root),
        "stage": args.stage,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
