#!/usr/bin/env python3
"""Record explicit, asset-scoped human approval; a YES flag alone is not evidence.

This is an audit helper, not proof of a person's identity. Never manufacture the
user quote or promote a new asset based on an earlier general style approval.
"""
import argparse
from copy import deepcopy
from pathlib import Path
from preproduction import (ContractError, approval_evidence, checked_asset, read_json,
    relative_file, require, sha256_file, validate_keyframe, write_json)


def approve_reference(root, registry, asset_id, evidence):
    result = deepcopy(registry)
    asset = result.get('assets', {}).get(asset_id)
    require(isinstance(asset, dict), 'unknown reference id')
    require(asset.get('character') in {'DAIYU', 'WUKONG'}, 'reference needs a known character')
    require(set(asset.get('roles', [])) & {'face', 'costume'}, 'whole design boards/scenes cannot act as face references')
    checked_asset(root, asset['path'], asset['sha256'])
    approval_evidence(evidence, asset_id, asset['sha256'])
    require(evidence['scope'] == 'reference', 'wrong evidence scope')
    asset.update(status='USER_APPROVED', approval_evidence=evidence)
    return result


def approve_keyframe(root, plan, manifest, registry, sid, relative, bindings, evidence):
    result = deepcopy(manifest)
    require(sid in result.get('shots', {}), 'unknown shot')
    image = relative_file(root, relative)
    require(image.is_file(), 'keyframe does not exist')
    digest = sha256_file(image)
    approval_evidence(evidence, sid, digest)
    require(evidence['scope'] == 'keyframe', 'wrong evidence scope')
    entry = result['shots'][sid]
    entry.update(status='USER_APPROVED', approved_by_user=True,
                 approved_keyframe=relative, sha256=digest, approval_evidence=evidence,
                 identity_refs=bindings.get('identity_refs', {}), costume_refs=bindings.get('costume_refs', {}))
    # Validate the prospective record before replacing anything on disk.
    validate_keyframe(root, plan, result, registry, sid)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('kind', choices=['reference', 'keyframe'])
    p.add_argument('--root', default='.')
    p.add_argument('--registry', required=True)
    p.add_argument('--evidence', required=True)
    p.add_argument('--id', required=True)
    p.add_argument('--user-confirmed', required=True, choices=['YES'])
    p.add_argument('--plan'); p.add_argument('--manifest'); p.add_argument('--image'); p.add_argument('--bindings')
    a = p.parse_args()
    import json
    try:
        registry_path = relative_file(a.root, a.registry)
        registry, evidence = read_json(registry_path), read_json(relative_file(a.root, a.evidence))
        if a.kind == 'reference':
            value = approve_reference(a.root, registry, a.id, evidence)
            target = registry_path
        else:
            target = relative_file(a.root, a.manifest)
            value = approve_keyframe(a.root, read_json(relative_file(a.root, a.plan)), read_json(target),
                 registry, a.id, a.image, read_json(relative_file(a.root, a.bindings)), evidence)
        write_json(target, value)
        print(json.dumps({'updated': str(target), 'subject': a.id}, ensure_ascii=False)); return 0
    except (ContractError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 2

if __name__ == '__main__':
    raise SystemExit(main())
