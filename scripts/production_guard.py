#!/usr/bin/env python3
"""Fail-closed gate for Production I2V jobs.

This script does not submit a ComfyUI job. It validates that the requested
start image is explicitly user-approved and that the workflow is truly I2V.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


class GuardError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GuardError(f"cannot read JSON {path}: {exc}") from exc


def find_i2v_connection(graph: dict) -> tuple[str, str]:
    load_nodes = {
        str(node_id)
        for node_id, node in graph.items()
        if isinstance(node, dict) and node.get("class_type") == "LoadImage"
    }
    if not load_nodes:
        raise GuardError("workflow has no LoadImage node")

    latent_nodes = []
    for node_id, node in graph.items():
        if not isinstance(node, dict) or node.get("class_type") != "Wan22ImageToVideoLatent":
            continue
        start = (node.get("inputs") or {}).get("start_image")
        if isinstance(start, list) and len(start) >= 1 and str(start[0]) in load_nodes:
            latent_nodes.append((str(node_id), str(start[0])))

    if len(latent_nodes) != 1:
        raise GuardError(
            f"expected exactly one Wan22ImageToVideoLatent.start_image connected to LoadImage; got {latent_nodes}"
        )
    return latent_nodes[0]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--approval-manifest", required=True)
    p.add_argument("--shot", required=True)
    p.add_argument("--image", required=True)
    p.add_argument("--workflow", required=True)
    p.add_argument("--record", default=None)
    args = p.parse_args()

    result = {
        "ok": False,
        "shot": args.shot,
        "image": args.image,
        "workflow": args.workflow,
        "checks": [],
    }

    try:
        manifest_path = Path(args.approval_manifest)
        image_path = Path(args.image)
        workflow_path = Path(args.workflow)

        manifest = load_json(manifest_path)
        shots = manifest.get("shots") or {}
        shot = shots.get(args.shot)
        if not isinstance(shot, dict):
            raise GuardError(f"shot {args.shot} not found in manifest")

        if shot.get("status") not in {"USER_APPROVED", "PRODUCTION_READY"}:
            raise GuardError(f"shot status is {shot.get('status')!r}, not USER_APPROVED/PRODUCTION_READY")
        if shot.get("approved_by_user") is not True:
            raise GuardError("approved_by_user is not true")

        if not image_path.is_file():
            raise GuardError(f"image not found: {image_path}")
        actual_hash = sha256_file(image_path)
        expected_hash = shot.get("sha256")
        if not expected_hash:
            raise GuardError("approved shot has no sha256")
        if actual_hash.lower() != str(expected_hash).lower():
            raise GuardError(f"image sha256 mismatch: {actual_hash} != {expected_hash}")

        approved_name = shot.get("approved_keyframe")
        if approved_name:
            expected_name = Path(str(approved_name)).name
            if image_path.name != expected_name:
                raise GuardError(f"image filename mismatch: {image_path.name} != {expected_name}")

        identities = shot.get("identity_refs") or {}
        for character in ("DAIYU", "WUKONG"):
            refs = identities.get(character)
            if not isinstance(refs, list) or not refs:
                raise GuardError(f"{character} identity_refs empty")

        costumes = shot.get("costume_refs") or {}
        for character in ("DAIYU", "WUKONG"):
            if not costumes.get(character):
                raise GuardError(f"{character} costume ref missing")

        graph = load_json(workflow_path)
        latent_id, load_id = find_i2v_connection(graph)

        result["checks"] = [
            "manifest_shot_exists",
            "user_approved",
            "image_exists",
            "sha256_matches",
            "identity_refs_present",
            "costume_refs_present",
            "load_image_present",
            "start_image_connected",
        ]
        result["image_sha256"] = actual_hash
        result["load_image_node"] = load_id
        result["i2v_latent_node"] = latent_id
        result["ok"] = True

    except GuardError as exc:
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)

    if args.record:
        path = Path(args.record)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")

    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
