#!/usr/bin/env python3
"""Bounded FID1 graph audit.

A prompt change is not an identity intervention. This audit checks graph
structure, input values, and link reachability. It still does not claim visual
identity success; GPU/video QA remains local.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from collections import deque


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_node(node_id, node):
    return {
        "id": str(node_id),
        "class": node.get("class_type"),
        "inputs": node.get("inputs", {}),
    }


def graph_signature(graph: dict):
    nodes = {}
    edges = []
    for k, v in graph.items():
        n = normalize_node(k, v)
        nodes[n["id"]] = {
            "class": n["class"],
            "inputs": n["inputs"],
        }
        for key, value in n["inputs"].items():
            if isinstance(value, list) and len(value) == 2 and str(value[0]) in graph:
                edges.append({"from": str(value[0]), "to": str(k), "input": key})
    return {"nodes": nodes, "edges": sorted(edges, key=lambda x: (x["from"], x["to"], x["input"]))}


def reachable(graph, starts):
    sig = graph_signature(graph)
    seen = set(starts)
    q = deque(starts)
    while q:
        cur = q.popleft()
        for e in sig["edges"]:
            if e["from"] == cur and e["to"] not in seen:
                seen.add(e["to"])
                q.append(e["to"])
    return seen


def audit(base, candidate):
    b = graph_signature(base)
    c = graph_signature(candidate)
    structural = b != c
    changed = []
    for key in sorted(set(b["nodes"]) | set(c["nodes"])):
        if b["nodes"].get(key) != c["nodes"].get(key):
            changed.append(key)
    prompt_only = (b["edges"] == c["edges"] and changed and all(
        b["nodes"].get(x, {}).get("class") == c["nodes"].get(x, {}).get("class")
        for x in changed
    ))
    reference_nodes = [k for k,v in c["nodes"].items() if "image" in str(v).lower() or "reference" in str(v).lower()]
    connected = bool(reference_nodes and reachable(candidate, reference_nodes))
    return {
        "structural_change": structural,
        "prompt_only_suspected": prompt_only,
        "reference_nodes": reference_nodes,
        "reference_reaches_downstream": connected,
        "production_claim_allowed": bool(structural and connected and not prompt_only),
        "reason": "Graph change and reference path are required; prompt/save-name changes are rejected."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', required=True)
    p.add_argument('--candidate', required=True)
    args = p.parse_args()
    b = Path(args.baseline); c = Path(args.candidate)
    result = audit(json.loads(b.read_text()), json.loads(c.read_text()))
    result['baseline_sha256'] = sha(b)
    result['candidate_sha256'] = sha(c)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result['production_claim_allowed']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
