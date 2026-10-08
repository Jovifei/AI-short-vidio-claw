#!/usr/bin/env python3
"""One-time remote bootstrap: byte-check existing chat assets into Git.

Network is opt-in and only used by the bounded staging workflow. Local users
consume committed PNGs using sync_repo_media.py, never CDN or a chat ZIP.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
from PIL import Image

REGISTRY = 'assets/registry/generated_assets_v5.json'
CONFIG = 'config/git_media_bootstrap.json'
MANIFEST = 'assets/media/git_media_manifest.json'
MEDIA = 'assets/media/source_library'
PREFIX = 'https://cdn.openart.ai/openart-uploads/production/attachment-transfers/'
MAX_BYTES = 10 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def fetch(suffix):
    need(re.fullmatch(r'[a-f0-9]{64}\.png', suffix) is not None, 'unexpected CDN key')
    url = PREFIX + suffix
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Jovi-media-receipt/1'}), timeout=60) as response:
        need(response.url == url, 'redirect not permitted')
        result = response.read(MAX_BYTES + 1)
    need(len(result) <= MAX_BYTES, 'image exceeds size budget')
    return result


def build(root, get_bytes=fetch):
    root = Path(root).resolve()
    config = json.loads((root / CONFIG).read_text(encoding='utf-8'))
    registry = json.loads((root / REGISTRY).read_text(encoding='utf-8'))['assets']
    need(len(registry) == 17, 'V5 registry changed; re-review this one-time bootstrap')
    entries = dict(registry)
    for key, a in config.get('additional_sources', {}).items():
        need(key not in entries, 'duplicate source ID')
        entries[key] = a
    images, records = {}, []
    for aid, a in sorted(entries.items(), key=lambda v: ('parent_asset' in v[1], v[0])):
        need(re.fullmatch(r'[A-Z0-9_]+', aid) is not None, 'unsafe asset ID')
        path = a['path']
        need(path.startswith(('local/references/generated/20261005_v5/', 'local/references/received_sources_20261007/', 'local/references/pilot_source_crops/')), 'not an approved local destination')
        need('..' not in path.split('/') and '\\' not in path and ':' not in path, 'unsafe path')
        existing = root/f'{MEDIA}/{aid}.png'
        if existing.is_file() and sha(existing.read_bytes()) == a['sha256']:
            data = existing.read_bytes()
        elif 'parent_asset' in a:
            parent = a['parent_asset']; need(parent in images, 'missing crop parent')
            need(sha(images[parent]) == a['parent_sha256'], 'wrong crop parent bytes')
            with Image.open(io.BytesIO(images[parent])) as im:
                out = io.BytesIO(); im.crop(a['crop_box_xyxy']).save(out, format='PNG')
                data = out.getvalue()
        else:
            need(aid in config['sources'], 'missing upload for ' + aid)
            data = get_bytes(config['sources'][aid])
        need(len(data) == a['bytes'] and sha(data) == a['sha256'], 'source hash/length mismatch: ' + aid)
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            need(im.format == 'PNG' and im.n_frames == 1, 'not a single PNG')
            need(im.size == (a['width'], a['height']), 'wrong dimensions')
        images[aid] = data
        records.append(dict(asset_id=aid, repo_path=f'{MEDIA}/{aid}.png', local_path=path,
                            sha256=a['sha256'], bytes=a['bytes'], width=a['width'], height=a['height'],
                            original_registry_id=aid if aid in registry else None,
                            status='SOURCE_CANDIDATE', provenance=a.get('provenance', 'existing_conversation_generated_image')))
    for item in records:
        p = root/item['repo_path']
        need(not p.is_symlink(), 'symlink destination')
        if p.exists(): need(p.is_file() and sha(p.read_bytes()) == item['sha256'], 'existing Git media conflicts')
    for item in records:
        p = root/item['repo_path']; p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists(): p.write_bytes(images[item['asset_id']])
    manifest = dict(schema_version=1, delivery_id='GIT_MEDIA_20261008',
                    media_in_git=True, registry_approvals_changed=0, generation_jobs=0,
                    local_requires_cdn=False, local_requires_attachment=False,
                    exact_new_episode_keyframes=0, assets=records)
    (root/MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return dict(real_png_count=len(records), bytes=sum(a['bytes'] for a in records),
                original_registry_count=len(registry), production_ready=False, approvals_changed=0)


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root', default='.'); p.add_argument('--fetch', action='store_true'); args=p.parse_args()
    if not args.fetch: p.error('remote bootstrap only: explicit --fetch required; local users run sync_repo_media.py')
    print(json.dumps(build(args.root), ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
