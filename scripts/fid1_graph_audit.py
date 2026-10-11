#!/usr/bin/env python3
"""Bounded FID1 graph audit.

This does not claim identity locking. It verifies that a trial graph actually
contains a declared intervention beyond prompt/save-name changes.

GPU is intentionally not called here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def node_fingerprint(graph: dict) -> dict:
    return {
        "nodes": sorted(
            {
                "id": str(k),
                "class": v.get("class_type"),
                "inputs": sorted(v.get("inputs", {}).keys()),
            }
            for k, v in graph.items()
        , key=lambda x: x["id"])
    }


def audit(base: dict, candidate: dict) -> dict:
    b = node_fingerprint(base)
    c = node_fingerprint(candidate)
    changed_nodes = []
    for before, after in zip(b["nodes"], c["nodes"]):
        if before != after:
            changed_nodes.append({"before": before, "after": after})

    text_only = True
    structural = False
    if b["nodes"] != c["nodes"]:
        structural = True
        text_only = False

    return {
        "structural_change": structural,
        "text_only_change": text_only,
        "changed_nodes": changed_nodes,
        "production_claim_allowed": False,
        "reason": "A FID1 candidate must demonstrate a causal graph intervention before GPU testing."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", required=True)
    p.add_argument("--candidate", required=True)
    args = p.parse_args()
    result = audit(json.loads(Path(args.baseline).read_text()), json.loads(Path(args.candidate).read_text()))
    result["baseline_sha256"] = sha(Path(args.baseline))
    result["candidate_sha256"] = sha(Path(args.candidate))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
