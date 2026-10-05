#!/usr/bin/env python3
"""Verify and import a previously unpacked review bundle. Never overwrite or approve."""
import argparse
import os
from pathlib import Path
from preproduction import ContractError, checked_asset, read_json, relative_file, require, sha256_file


def import_bundle(source, target, registry):
    source, target = Path(source).resolve(), Path(target).resolve()
    todo, skipped = [], []
    require(registry.get('schema_version') == 5, 'expected v5 asset registry')
    # Validate the ENTIRE bundle before the first write.
    for aid, asset in registry['assets'].items():
        src = checked_asset(source, asset['path'], asset['sha256'])
        dst = relative_file(target, asset['path'])
        if dst.exists():
            require(dst.is_file() and sha256_file(dst) == asset['sha256'], f'conflicting existing asset: {aid}')
            skipped.append(aid)
        else:
            todo.append((aid, src, dst, asset['sha256']))
    for aid, src, dst, digest in todo:
        data = src.read_bytes()
        import hashlib
        require(hashlib.sha256(data).hexdigest() == digest, f'source changed after preflight: {aid}')
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open('xb') as stream:
            stream.write(data)
    return {'imported': len(todo), 'already_present': len(skipped), 'approvals_changed': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', required=True)
    p.add_argument('--repo-root', default='.')
    p.add_argument('--registry', default='assets/registry/generated_assets_v5.json')
    a = p.parse_args()
    import json
    try:
        result = import_bundle(a.source_root, a.repo_root, read_json(relative_file(a.repo_root, a.registry)))
        print(json.dumps(result, ensure_ascii=False)); return 0
    except (ContractError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 2

if __name__ == '__main__':
    raise SystemExit(main())
