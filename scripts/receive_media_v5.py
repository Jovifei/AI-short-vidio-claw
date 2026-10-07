#!/usr/bin/env python3
"""Receive the 20261007 media-recovery bundle. No rendering and no approvals.

Default is a dry run. --apply imports verified files under local/ only.
--check verifies a previous import without requiring the source ZIP.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PureWindowsPath

DELIVERY_ID = 'MEDIA_RECOVERY_20261007'
MANIFEST_SHA256 = '18c4e0ca528254b052cfdc92763450e895aa7a74c598353be3b5241df0aa4fff'
MANIFEST_LOCAL = 'local/delivery/MEDIA_MANIFEST_20261007.json'
RECEIPT_LOCAL = 'local/delivery/RECEIPT_20261007.json'
ALLOWED = ('local/references/generated/20261005_v5/', 'local/references/recovery_20261007/')
MAX_BYTES = 256 * 1024 * 1024

class DeliveryError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise DeliveryError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, f'Duplicate JSON key: {key}')
        result[key] = value
    return result

def decode(data):
    try:
        return json.loads(data.decode('utf-8-sig'), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as e:
        raise DeliveryError(f'Invalid JSON: {e}') from e

def clean_relative(value):
    need(isinstance(value, str) and bool(value), 'Missing relative path')
    need('\\' not in value, 'Backslashes are not allowed in bundle paths')
    parts = value.split('/')
    need(not PureWindowsPath(value).drive and not value.startswith('/'), 'Absolute/drive path forbidden')
    need(all(p not in {'', '.', '..'} and ':' not in p for p in parts), 'Unsafe relative path')
    need(all(not p.endswith((' ', '.')) for p in parts), 'Windows ambiguous path')
    return parts

def under(root, relative):
    root = Path(root).resolve()
    parts = clean_relative(relative)
    p = root
    for part in parts:
        p = p / part
        need(not p.is_symlink(), f'Symlink path is not allowed: {relative}')
    need(p.resolve().is_relative_to(root), 'Path escapes repository')
    return p

def validate_manifest(raw, root):
    need(digest(raw) == MANIFEST_SHA256, 'Unexpected media manifest; do not import another release with this script')
    d = decode(raw)
    need(d.get('delivery_id') == DELIVERY_ID, 'Wrong delivery ID')
    assets = d.get('assets', [])
    need(len(assets) == 32, 'Expected 32 real files, not a 30-shot production package')
    seen_ids, seen_paths = set(), set()
    for a in assets:
        need(a['asset_id'] not in seen_ids, 'Duplicate asset ID')
        key = a['path'].casefold()
        need(key not in seen_paths, 'Duplicate/case-colliding target path')
        seen_ids.add(a['asset_id']); seen_paths.add(key)
        clean_relative(a['path'])
        need(a['path'].startswith(ALLOWED), 'Only this delivery reference directories may be written')
        under(root, a['path'])
        need(re.fullmatch('[0-9a-f]{64}', a.get('sha256', '')) is not None, 'Invalid SHA256')
        need(type(a.get('bytes')) is int and 0 < a['bytes'] <= MAX_BYTES, 'Invalid asset length')
    registry_path = under(root, 'assets/registry/generated_assets_v5.json')
    need(registry_path.is_file(), 'Run in the V5 repository root: assets/registry/generated_assets_v5.json is missing')
    reg = decode(registry_path.read_bytes())
    originals = [a for a in assets if a['kind'] == 'V5_ORIGINAL']
    need(len(originals) == 17, 'V5 original set is incomplete')
    for a in originals:
        known = reg.get('assets', {}).get(a['asset_id'], {})
        need(all(known.get(k) == a[k] for k in ('path', 'sha256', 'bytes')), f'Repository registry mismatch: {a["asset_id"]}')
    return d

def inspect_archive(z):
    infos = z.infolist()
    need(len(infos) <= 512, 'Unexpectedly large archive member count')
    need(sum(i.file_size for i in infos) <= MAX_BYTES, 'Archive exceeds recovery budget')
    seen = set()
    for i in infos:
        name = i.filename.rstrip('/')
        if not name:
            continue
        clean_relative(name)
        need(name.casefold() not in seen, 'Duplicate archive member')
        seen.add(name.casefold())
        need(not stat.S_ISLNK(i.external_attr >> 16), 'Archive symlinks are forbidden')
    choices = [i.filename for i in infos if i.filename.endswith('/MEDIA_MANIFEST.json') or i.filename == 'MEDIA_MANIFEST.json']
    need(len(choices) == 1, 'Expected exactly one MEDIA_MANIFEST.json')
    return choices[0]

def report(d, verified, imported=0, already=0):
    return {'delivery_id': DELIVERY_ID, 'verified_files': verified, 'v5_original_files': 17,
            'additional_source_options': 15, 'imported_files': imported, 'already_present': already,
            'materials_received': verified == len(d['assets']), 'approvals_changed': 0,
            'new_EP001_exact_keyframes': 0, 'production_ready': False,
            'remaining_owner': 'REMOTE_PREPARATION',
            'note': 'Media recovery is not completion of the 30-shot production images. Do not submit I2V solely because this import passed.'}

def receive(root, bundle, apply=False):
    root = Path(root).resolve(); bundle = Path(bundle)
    need(bundle.is_file(), f'Material ZIP is missing: {bundle}. A git pull does not transfer the conversation attachment.')
    with zipfile.ZipFile(bundle) as z:
        manifest_name = inspect_archive(z)
        prefix = manifest_name[:-len('MEDIA_MANIFEST.json')]
        raw = z.read(manifest_name); d = validate_manifest(raw, root)
        todo, already = [], 0
        # Verify all source and destination files BEFORE making any output.
        for a in d['assets']:
            name = prefix + 'payload/' + a['path']
            try:
                data = z.read(name)
            except KeyError as e:
                raise DeliveryError(f'Missing payload file: {a["asset_id"]}') from e
            need(len(data) == a['bytes'] and digest(data) == a['sha256'], f'Corrupt payload: {a["asset_id"]}')
            dst = under(root, a['path'])
            if dst.exists():
                need(dst.is_file() and file_hash(dst) == a['sha256'], f'Conflicting local file, not overwritten: {a["path"]}')
                already += 1
            else:
                todo.append((a, data))
        if not apply:
            r = report(d, len(d['assets']), already=already)
            r.update(mode='DRY_RUN', materials_received=False, planned_imports=len(todo))
            return r
        local = under(root, 'local'); local.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix='.media-receive-', dir=local))
        created = []
        try:
            # Stage completely verified bytes, then exclusively publish whole files.
            for n, (a, data) in enumerate(todo):
                staged = work / str(n); staged.write_bytes(data)
                need(file_hash(staged) == a['sha256'], 'Staged file failed verification')
            for n, (a, _) in enumerate(todo):
                dst = under(root, a['path']); dst.parent.mkdir(parents=True, exist_ok=True)
                os.link(work / str(n), dst)  # atomic no-overwrite on the same NTFS/POSIX volume
                created.append((dst, a['sha256']))
            for project in ('LOOKREEL01', 'EP001'):
                for folder in ('candidates', 'approved', 'video', 'audio', 'edit'):
                    under(root, f'local/production/{project}/{folder}').mkdir(parents=True, exist_ok=True)
            dst = under(root, MANIFEST_LOCAL); dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                need(dst.read_bytes() == raw, 'Existing delivery manifest conflicts')
            else:
                with dst.open('xb') as f: f.write(raw)
            r = report(d, len(d['assets']), len(created), already)
            r['bundle_sha256'] = file_hash(bundle); r['mode'] = 'IMPORTED'
            receipt = under(root, RECEIPT_LOCAL)
            temp = work / 'receipt.json'; temp.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            os.replace(temp, receipt)
            return r
        except Exception:
            for dst, expected in reversed(created):
                if dst.is_file() and file_hash(dst) == expected: dst.unlink()
            raise
        finally:
            shutil.rmtree(work, ignore_errors=True)

def check(root):
    root = Path(root).resolve(); m = under(root, MANIFEST_LOCAL)
    need(m.is_file(), 'No import receipt yet. Import the media ZIP with --bundle ... --apply first.')
    d = validate_manifest(m.read_bytes(), root)
    for a in d['assets']:
        p = under(root, a['path'])
        need(p.is_file() and file_hash(p) == a['sha256'], f'Missing/changed asset: {a["asset_id"]}')
    r = report(d, len(d['assets']), already=len(d['assets'])); r['mode'] = 'CHECKED'; return r

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.'); p.add_argument('--bundle'); p.add_argument('--apply', action='store_true'); p.add_argument('--check', action='store_true')
    a = p.parse_args()
    try:
        need(not (a.check and (a.bundle or a.apply)), '--check cannot be combined with --bundle/--apply')
        result = check(a.root) if a.check else receive(a.root, a.bundle or '', a.apply)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (DeliveryError, OSError, zipfile.BadZipFile, KeyError, TypeError) as e:
        print(json.dumps({'ok':False, 'error':str(e), 'production_ready':False}, ensure_ascii=False)); return 2
if __name__ == '__main__':
    raise SystemExit(main())
