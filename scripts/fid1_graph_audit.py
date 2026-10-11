#!/usr/bin/env python3
"""Bounded FID1 graph audit.

A prompt/save-name edit is not a generation intervention. This checks graph
values and links. It does not prove visual identity; GPU QA remains local.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    if isinstance(value, dict):
        return {k: canonical(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [canonical(v) for v in value]
    return value


def graph_signature(graph):
    nodes = {}
    edges = []
    for node_id, node in graph.items():
        inputs = canonical(node.get('inputs', {}))
        nodes[str(node_id)] = {'class_type': node.get('class_type'), 'inputs': inputs}
        for name, value in inputs.items():
            if isinstance(value, list) and len(value) == 2 and str(value[0]) in graph:
                edges.append({'from': str(value[0]), 'to': str(node_id), 'input': name})
    return {'nodes': nodes, 'edges': sorted(edges, key=lambda x:(x['from'], x['to'], x['input']))}


def reach(sig, starts):
    seen = set(starts)
    q = deque(starts)
    while q:
        n = q.popleft()
        for e in sig['edges']:
            if e['from'] == n and e['to'] not in seen:
                seen.add(e['to'])
                q.append(e['to'])
    return seen


def audit(base, candidate):
    before = graph_signature(base)
    after = graph_signature(candidate)
    changed_nodes = [k for k in sorted(set(before['nodes']) | set(after['nodes'])) if before['nodes'].get(k) != after['nodes'].get(k)]
    edge_changed = before['edges'] != after['edges']

    prompt_classes = {'CLIPTextEncode', 'CLIPTextEncodeSDXL'}
    prompt_only = bool(changed_nodes) and not edge_changed and all(
        before['nodes'].get(k, {}).get('class_type') in prompt_classes or
        after['nodes'].get(k, {}).get('class_type') in prompt_classes
        for k in changed_nodes
    )

    refs = [k for k,v in after['nodes'].items() if any(x in str(v).lower() for x in ('reference', 'imageencode'))]
    reached = reach(after, refs) if refs else set()
    sampler = [k for k,v in after['nodes'].items() if 'sampler' in str(v.get('class_type','')).lower()]
    connected = bool(refs and sampler and any(s in reached for s in sampler))

    return {
        'structural_change': bool(edge_changed or changed_nodes),
        'changed_nodes': changed_nodes,
        'prompt_only_suspected': prompt_only,
        'reference_nodes': refs,
        'reference_reaches_sampler': connected,
        'production_claim_allowed': bool((edge_changed or changed_nodes) and connected and not prompt_only),
        'reason': 'Requires a causal graph intervention reaching sampler; text-only changes fail.'
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', required=True)
    p.add_argument('--candidate', required=True)
    a = p.parse_args()
    result = audit(json.loads(Path(a.baseline).read_text()), json.loads(Path(a.candidate).read_text()))
    result['baseline_sha256'] = sha(Path(a.baseline))
    result['candidate_sha256'] = sha(Path(a.candidate))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result['production_claim_allowed'] else 2)


if __name__ == '__main__':
    main()
