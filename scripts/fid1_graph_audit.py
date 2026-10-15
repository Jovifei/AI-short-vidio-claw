#!/usr/bin/env python3
"""Strict, offline validation for the source-only FID1 ComfyUI graph."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .preproduction import FID1_NODE_CLASS_BY_STRATEGY, validate_graph
except ImportError:
    from preproduction import FID1_NODE_CLASS_BY_STRATEGY, validate_graph


def attach_fid1_anchor(graph, cast, profile):
    """Interpose the FID1 node in the live Wan latent-to-KSampler edge."""
    ids = validate_graph(graph, cast)
    if not isinstance(profile, dict) or profile.get("scope") != "T1_SOURCE_ONLY":
        raise ValueError("FID1 anchor can only be attached to a source-only trial")
    strategy = profile.get("anchor_strategy")
    node_class = FID1_NODE_CLASS_BY_STRATEGY.get(strategy)
    if node_class is None:
        raise ValueError("unsupported FID1 anchor strategy")
    try:
        next_id = str(max(int(key) for key in graph) + 1)
    except (TypeError, ValueError) as exc:
        raise ValueError("Comfy graph node ids must be numeric strings") from exc
    roi_json = json.dumps(profile.get("anchor_rois"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    inputs = {"latent": [ids["latent"], 0], "roi_boxes_json": roi_json}
    if strategy in {"wan22_timestep_aware_future_roi_v2", "wan22_timestep_aware_future_roi_v3", "wan22_timestep_aware_roi_strength_v4"}:
        inputs["model"] = [ids["sample_model"], 0]
        if strategy == "wan22_timestep_aware_future_roi_v3":
            inputs["temporal_anchor_schedule_json"] = json.dumps(profile["temporal_anchor_schedule"], separators=(",", ":"))
        graph[next_id] = {"class_type": node_class, "inputs": inputs}
        graph[ids["sampler"]]["inputs"]["model"] = [next_id, 0]
        graph[ids["sampler"]]["inputs"]["latent_image"] = [next_id, 1]
    else:
        graph[next_id] = {"class_type": node_class, "inputs": inputs}
        graph[ids["sampler"]]["inputs"]["latent_image"] = [next_id, 0]
    return validate_graph(graph, cast, fid1_profile=profile)["fid1"]


def canonical(value):
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def graph_signature(graph):
    nodes = {}
    edges = []
    for node_id, node in graph.items():
        inputs = canonical(node.get("inputs", {}))
        nodes[str(node_id)] = {"class_type": node.get("class_type"), "inputs": inputs}
        for name, value in inputs.items():
            if isinstance(value, list) and len(value) == 2 and str(value[0]) in graph:
                edges.append({"from": str(value[0]), "to": str(node_id), "input": name})
    return {"nodes": nodes, "edges": sorted(edges, key=lambda edge: (edge["from"], edge["to"], edge["input"]))}


def audit_fid1_graph(base, candidate, cast, profile):
    """Validate exact API graph edges and frozen profile values; no text heuristics."""
    base_ids = validate_graph(base, cast)
    candidate_ids = validate_graph(candidate, cast, fid1_profile=profile)
    before = graph_signature(base)
    after = graph_signature(candidate)
    sampler = candidate[candidate_ids["sampler"]]
    anchor = candidate[candidate_ids["fid1"]]
    strategy = profile.get("anchor_strategy")
    anchor_edge = anchor["inputs"].get("latent")
    if strategy == "wan22_first_latent_future_roi_v1":
        require_live_edges = (
            sampler["inputs"].get("latent_image") == [candidate_ids["fid1"], 0]
            and anchor_edge == [candidate_ids["latent"], 0]
        )
        active_edges = [
            {"from": candidate_ids["latent"], "to": candidate_ids["fid1"], "input": "latent"},
            {"from": candidate_ids["fid1"], "to": candidate_ids["sampler"], "input": "latent_image"},
        ]
    elif strategy in {"wan22_timestep_aware_future_roi_v2", "wan22_timestep_aware_future_roi_v3", "wan22_timestep_aware_roi_strength_v4"}:
        require_live_edges = (
            anchor_edge == [candidate_ids["latent"], 0]
            and anchor["inputs"].get("model") == [candidate_ids["sample_model"], 0]
            and sampler["inputs"].get("model") == [candidate_ids["fid1"], 0]
            and sampler["inputs"].get("latent_image") == [candidate_ids["fid1"], 1]
        )
        active_edges = [
            {"from": candidate_ids["sample_model"], "to": candidate_ids["fid1"], "input": "model"},
            {"from": candidate_ids["latent"], "to": candidate_ids["fid1"], "input": "latent"},
            {"from": candidate_ids["fid1"], "to": candidate_ids["sampler"], "input": "model"},
            {"from": candidate_ids["fid1"], "to": candidate_ids["sampler"], "input": "latent_image"},
        ]
    else:
        raise ValueError("unsupported FID1 anchor strategy")
    if not require_live_edges:
        raise ValueError("FID1 node is not connected on the live Wan-to-KSampler path")
    if before["edges"] == after["edges"]:
        raise ValueError("FID1 graph did not change the active sampler edge")
    return {
        "fid1_graph_valid": True,
        "scope": profile["scope"],
        "fid1_node_id": candidate_ids["fid1"],
        "base_latent_node_id": base_ids["latent"],
        "sampler_node_id": candidate_ids["sampler"],
        "active_edges": active_edges,
        "profile_rois": profile["anchor_rois"],
        "base_graph_sha256": hashlib.sha256(json.dumps(canonical(base), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "candidate_graph_sha256": hashlib.sha256(json.dumps(canonical(candidate), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--cast", required=True, help="comma-separated character ids from the source trial plan")
    args = parser.parse_args(argv)
    baseline_path = Path(args.baseline)
    candidate_path = Path(args.candidate)
    profile_path = Path(args.profile)
    result = audit_fid1_graph(
        json.loads(baseline_path.read_text(encoding="utf-8")),
        json.loads(candidate_path.read_text(encoding="utf-8")),
        [item.strip() for item in args.cast.split(",") if item.strip()],
        json.loads(profile_path.read_text(encoding="utf-8")),
    )
    result["baseline_file_sha256"] = hashlib.sha256(baseline_path.read_bytes()).hexdigest()
    result["candidate_file_sha256"] = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    result["profile_sha256"] = hashlib.sha256(profile_path.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
