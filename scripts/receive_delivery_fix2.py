#!/usr/bin/env python3
"""Receive the actual FIX2 media ZIP, not the absent earlier recovery ZIP.

Default: verify only. --apply: import under local/. --check: verify an import.
No GPU, network, approval changes, or model downloads. Python standard library.
"""
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

DELIVERY_ID = 'MEDIA_HANDOFF_FIX2_20261007'
MANIFEST_SHA = 'b39e2546ba2af81cefa9a1c751271b322c7294db4857b406a5ace6ce1bb193ed'
SAVED_MANIFEST = 'local/delivery/fix2/MEDIA_MANIFEST.json'
RECEIPT = 'local/delivery/fix2/RECEIPT.json'
PREFIXES = ('local/references/generated/20261005_v5/',
            'local/references/media_handoff_fix2_20261007/')
MAX_BYTES = 256 * 1024 * 1024

class DeliveryError(ValueError):
    pass

def need(condition, message):
    if not condition:
        raise DeliveryError(message)

def hash_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def hash_bytes(value):
    return hashlib.sha256(value).hexdigest()

def unique_object(pairs):
    d = {}
    for key, value in pairs:
        need(key not in d, 'Duplicate JSON key')
        d[key] = value
    return d

def decode(raw):
    return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object)

def parts(value):
    need(isinstance(value, str) and value, 'Missing relative path')
    need(not value.startswith('/') and not PureWindowsPath(value).drive and '\\' not in value, 'Absolute path forbidden')
    result = value.split('/')
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{i}' for p in ('COM', 'LPT') for i in range(1, 10)}
    for part in result:
        need(part not in {'', '.', '..'} and not any(c in part for c in ':<>"|?*'), 'Unsafe path')
        need(not part.endswith((' ', '.')) and not any(ord(c) < 32 for c in part), 'Ambiguous Windows path')
        need(part.split('.')[0].upper() not in reserved, 'Reserved Windows filename')
    return result

def target(root, relative):
    root = Path(root).resolve()
    p = root
    for part in parts(relative):
        p = p / part
        need(not p.is_symlink() and not getattr(p, 'is_junction', lambda: False)(), 'Link/junction target forbidden')
    need(p.resolve().is_relative_to(root), 'Path escapes root')
    return p

def manifest(raw, root):
    need(hash_bytes(raw) == MANIFEST_SHA, 'Wrong manifest: use the FIX2 ZIP, not an older delivery')
    d = decode(raw)
    need(d.get('delivery_id') == DELIVERY_ID and len(d.get('assets', [])) == 32, 'Wrong delivery/count')
    known = decode(target(root, 'assets/registry/generated_assets_v5.json').read_bytes())['assets']
    ids, paths = set(), set()
    originals = 0
    for a in d['assets']:
        need(a['asset_id'] not in ids and a['path'].casefold() not in paths, 'Duplicate asset/path')
        ids.add(a['asset_id']); paths.add(a['path'].casefold())
        need(a['path'].startswith(PREFIXES), 'Only media reference paths may be written')
        target(root, a['path'])
        need(re.fullmatch('[0-9a-f]{64}', a['sha256']), 'Invalid asset hash')
        need(type(a['bytes']) is int and 0 < a['bytes'] <= MAX_BYTES, 'Invalid asset size')
        if a['kind'] == 'V5_ORIGINAL':
            originals += 1
            old = known.get(a['asset_id'], {})
            need(all(old.get(k) == a[k] for k in ('path', 'sha256', 'bytes')), 'V5 registry mismatch')
    need(originals == 17, 'Original V5 set incomplete')
    return d

def archive_prefix(z):
    infos = z.infolist()
    need(len(infos) <= 512 and sum(i.file_size for i in infos) <= MAX_BYTES, 'Archive budget exceeded')
    names = set()
    for i in infos:
        name = i.filename.rstrip('/')
        if not name:
            continue
        parts(name)
        need(name.casefold() not in names, 'Duplicate ZIP member')
        names.add(name.casefold())
        need(not stat.S_ISLNK(i.external_attr >> 16), 'ZIP symlink forbidden')
    candidates = [i.filename for i in infos if i.filename.endswith('/MEDIA_MANIFEST.json') or i.filename == 'MEDIA_MANIFEST.json']
    need(len(candidates) == 1, 'Expected one MEDIA_MANIFEST.json')
    return candidates[0][:-len('MEDIA_MANIFEST.json')]

def summary(mode, imported, existing):
    return dict(delivery_id=DELIVERY_ID, mode=mode, verified_files=32,
                imported_files=imported, already_present=existing,
                materials_received=mode in {'IMPORTED', 'CHECKED'},
                approvals_changed=0, exact_EP001_keyframes_delivered=0,
                production_ready=False, full_remote_request_complete=False)

def receive(root, bundle, apply=False):
    root = Path(root).resolve()
    need(Path(bundle).is_file(), 'ZIP missing; git pull cannot transfer the conversation media attachment')
    with zipfile.ZipFile(bundle) as z:
        prefix = archive_prefix(z)
        raw = z.read(prefix + 'MEDIA_MANIFEST.json')
        d = manifest(raw, root)
        pending, existing = [], 0
        # Validate every source and every destination before any write.
        for a in d['assets']:
            data = z.read(prefix + 'payload/' + a['path'])
            need(len(data) == a['bytes'] and hash_bytes(data) == a['sha256'], 'Corrupt payload: ' + a['asset_id'])
            dst = target(root, a['path'])
            if dst.exists():
                need(dst.is_file() and hash_file(dst) == a['sha256'], 'Local conflict; not overwritten: ' + a['path'])
                existing += 1
            else:
                pending.append(a)
        saved = target(root, SAVED_MANIFEST)
        if saved.exists():
            need(saved.read_bytes() == raw, 'Existing FIX2 manifest differs')
        if not apply:
            r = summary('DRY_RUN', 0, existing)
            r['planned_imports'] = len(pending)
            return r
        local = target(root, 'local'); local.mkdir(parents=True, exist_ok=True)
        lock = target(root, 'local/.media-fix2.lock')
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        work = None; created = []
        try:
            work = Path(tempfile.mkdtemp(prefix='.media-fix2-', dir=local))
            for n, a in enumerate(pending):
                stage = work / str(n)
                stage.write_bytes(z.read(prefix + 'payload/' + a['path']))
                need(hash_file(stage) == a['sha256'], 'Staging hash mismatch')
                dst = target(root, a['path']); dst.parent.mkdir(parents=True, exist_ok=True)
                os.link(stage, dst)  # atomic no-overwrite; NTFS/POSIX, same volume
                created.append((dst, a['sha256']))
            for project in ('LOOKREEL01', 'EP001'):
                for folder in ('candidates', 'approved', 'video', 'audio', 'edit'):
                    target(root, f'local/production/{project}/{folder}').mkdir(parents=True, exist_ok=True)
            saved.parent.mkdir(parents=True, exist_ok=True)
            if not saved.exists():
                with saved.open('xb') as f:
                    f.write(raw)
            r = summary('IMPORTED', len(created), existing)
            r['bundle_sha256'] = hash_file(bundle)
            receipt = target(root, RECEIPT)
            temp = work / 'receipt.json'
            temp.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(temp, receipt)
            return r
        except Exception:
            for dst, expected in reversed(created):
                if dst.is_file() and hash_file(dst) == expected:
                    dst.unlink()
            raise
        finally:
            if work:
                shutil.rmtree(work, ignore_errors=True)
            lock.unlink(missing_ok=True)

def check(root):
    raw = target(root, SAVED_MANIFEST).read_bytes()
    d = manifest(raw, root)
    for a in d['assets']:
        p = target(root, a['path'])
        need(p.is_file() and p.stat().st_size == a['bytes'] and hash_file(p) == a['sha256'], 'Missing/changed: ' + a['asset_id'])
    return summary('CHECKED', 0, 32)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.'); p.add_argument('--bundle')
    p.add_argument('--apply', action='store_true'); p.add_argument('--check', action='store_true')
    a = p.parse_args()
    try:
        need(not (a.check and (a.bundle or a.apply)), '--check cannot be combined with --bundle or --apply')
        r = check(a.root) if a.check else receive(a.root, a.bundle or '', a.apply)
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0
    except (DeliveryError, OSError, ValueError, zipfile.BadZipFile, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e), 'production_ready': False}, ensure_ascii=False)); return 2

if __name__ == '__main__':
    raise SystemExit(main())
