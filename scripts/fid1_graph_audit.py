#!/usr/bin/env python3
"""Bounded FID1 graph audit.

This is a safety gate, not an identity success metric. A prompt change,
save-prefix change, or disconnected reference node is rejected.
GPU/video QA remains local.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from collections import deque


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_value(value):
    if isinstance(value, dict):
        return {k: _json_value(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_json_value(x) for x in value]
    return value


def graph_signature(graph: dict):
    nodes = {}
    edges = []
    for node_id, node in graph.items():
        inputs = _json_value(node.get("inputs", {}))
        nodes[str(node_id)] = {
            "class_type": node.get("class_type"),
            "inputs": inputs,
        }
        for name, value in inputs.items():
            if isinstance(value, list) and len(value) == 2 and str(value[0]) in graph:
                edges.append({"from": str(value[0]), "to": str(node_id), "input": name})
    return {"nodes": nodes, "edges": sorted(edges, key=lambda x: (x["from"], x["to"], x["input"]))}


def reachable(signature, starts):
    seen = set(starts)
    queue = deque(starts)
    while queue:
        current = queue.popleft()
        for edge in signature["edges"]:
            if edge["from"] == current and edge["to"] not in seen:
                seen.add(edge["to"])
                queue.append(edge["to"])
    return seen


def audit(base, candidate):
    before = graph_signature(base)
    after = graph_signature(candidate)
    changed = before != after
    changed_nodes = [k for k in sorted(set(before["nodes"]) | set(after["nodes"])) if before["nodes"].get(k) != after["nodes"].get(k)]
    prompt_classes = {"CLIPTextEncode", "CLIPTextEncodeSDXL"}
    only_text_changed = bool(changed_nodes) and all(
        before["nodes"].get(k, {}).get("class_type") in prompt_classes or after["nodes"].get(k, {}).get("class_type") in prompt_classes
        for k in changed_nodes
    ) and before["edges"] == after["edges"]
    reference_nodes = [k for k, v in after["nodes"].items() if any(x in str(v).lower() for x in ("reference", "imageencode", "image"))]
    path = reachable(after, reference_nodes) if reference_nodes else set()
    downstream_sampler = any("sampler" in str(v.get("class_type", "")).lower() for v in after["nodes"].values() if v)
    connected_reference = bool(reference_nodes and path and downstream_sampler and len(path) > len(reference_nodes))
    return {
        "structural_change": changed,
        "changed_nodes": changed_nodes,
        "prompt_only_suspected": only_text_changed,
        "reference_nodes": reference_nodes,
        "reference_reaches_downstream": connected_reference,
        "production_claim_allowed": bool(changed and connected_reference and not only_text_changed),
        "reason": "Require causal graph intervention and connected reference path; prompt-only edits are rejected."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    base = Path(args.baseline)
    candidate = Path(args.candidate)
    result = audit(json.loads(base.read_text()), json.loads(candidate.read_text()))
    result['baseline_sha256'] = sha(base)
    result['candidate_sha256'] = sha(candidate)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result['production_claim_allowed']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
