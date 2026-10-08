#!/usr/bin/env python3
"""Copy byte-verified committed images into existing local V5 paths. Offline.

Default dry-run. --apply writes missing files only. --check checks local files.
No download, generation, registry/approval change, or GPU use.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import tempfile

MANIFEST = 'assets/media/git_media_manifest.json'
LOCAL_PREFIXES = ('local/references/generated/20261005_v5/', 'local/references/received_sources_20261007/', 'local/references/pilot_source_crops/')

def need(ok, message):
    if not ok: raise ValueError(message)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def safe(root, relative):
    need(isinstance(relative,str) and relative, 'missing path')
    parts=relative.split('/')
    need(not PureWindowsPath(relative).drive and not relative.startswith('/') and '\\' not in relative,'absolute/backslash path')
    reserved={'CON','PRN','AUX','NUL'}|{f'{a}{b}' for a in ['COM','LPT'] for b in range(1,10)}
    need(all(p not in {'','.','..'} and not any(c in p for c in ':<>"|?*') and not p.endswith((' ','.')) and p.split('.')[0].upper() not in reserved and all(ord(c)>=32 for c in p) for p in parts),'unsafe path')
    root=Path(root).resolve(); p=root
    for part in parts:
        p=p/part
        need(not p.is_symlink() and not getattr(p,'is_junction',lambda:False)(),'link/junction rejected')
    need(p.resolve().is_relative_to(root),'escaped project');return p

def verify(root, check_local=False):
    root=Path(root).resolve(); d=json.loads(safe(root,MANIFEST).read_text(encoding='utf-8'))
    need(d.get('delivery_id')=='GIT_MEDIA_20261008' and d.get('media_in_git') is True,'wrong manifest')
    assets=d.get('assets'); need(isinstance(assets,list) and 17<=len(assets)<=64,'unexpected media count')
    seen=set(); seen_paths=set(); originals=0; missing=[]
    registry=json.loads(safe(root,'assets/registry/generated_assets_v5.json').read_text(encoding='utf-8'))['assets']
    for a in assets:
        aid=a['asset_id'];need(aid not in seen,'duplicate asset');seen.add(aid)
        for key,prefixes in [('repo_path',('assets/media/source_library/',)),('local_path',LOCAL_PREFIXES)]:
            rel=a[key]; need(rel.startswith(prefixes),'wrong destination prefix')
            token=(key,rel.casefold());need(token not in seen_paths,'duplicate target path');seen_paths.add(token)
            safe(root,rel)
        need(re.fullmatch('[a-f0-9]{64}',a['sha256']) is not None,'bad hash')
        need(type(a['bytes']) is int and 0<a['bytes']<=10*1024*1024,'bad file length')
        source=safe(root,a['repo_path']);need(source.is_file(),f'Git PNG missing: {a["repo_path"]}; pull the media commit, not an old code-only commit')
        need(source.stat().st_size==a['bytes'] and digest(source)==a['sha256'],'Git media corrupt: '+aid)
        if a.get('original_registry_id'):
            old=registry.get(aid,{});need(old.get('path')==a['local_path'] and old.get('sha256')==a['sha256'],'V5 registry differs: '+aid); originals+=1
        local=safe(root,a['local_path'])
        if local.exists(): need(local.is_file() and digest(local)==a['sha256'],'local conflict, will not overwrite: '+aid)
        else: missing.append(a)
    need(originals==17,'original V5 set incomplete')
    if check_local: need(not missing,'local media missing: '+','.join(a['asset_id'] for a in missing))
    return d,missing

def run(root='.', apply=False, check=False):
    root=Path(root).resolve();d,missing=verify(root,check)
    result=dict(mode='CHECKED' if check else 'DRY_RUN',repo_files=len(d['assets']),missing_local=len(missing),copied=0,already_present=len(d['assets'])-len(missing),approvals_changed=0,production_ready=False,network_used=False)
    if not apply:return result
    local=safe(root,'local');local.mkdir(parents=True,exist_ok=True)
    lock=safe(root,'local/.git-media-sync.lock');fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
    temp=None;created=[]
    try:
        d,missing=verify(root)
        temp=Path(tempfile.mkdtemp(prefix='.git-media-',dir=local))
        for i,a in enumerate(missing):
            staged=temp/str(i);shutil.copyfile(safe(root,a['repo_path']),staged)
            need(digest(staged)==a['sha256'],'staging changed')
        for i,a in enumerate(missing):
            dst=safe(root,a['local_path']);dst.parent.mkdir(parents=True,exist_ok=True)
            os.link(temp/str(i),dst);created.append((dst,a['sha256']))
        for project in ('LOOKREEL01','EP001','T1_SOURCE_PILOT'):
            for name in ('candidates','approved','video','audio','edit'):
                safe(root,f'local/production/{project}/{name}').mkdir(parents=True,exist_ok=True)
        verify(root,True)
        result.update(mode='IMPORTED',copied=len(created),missing_local=0,already_present=len(d['assets'])-len(created))
        receipt=safe(root,'local/reports/git_media_receipt.json');receipt.parent.mkdir(parents=True,exist_ok=True)
        staged=temp/'receipt.json';staged.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(staged,receipt)
        return result
    except Exception:
        for path,h in reversed(created):
            if path.is_file() and digest(path)==h:path.unlink()
        raise
    finally:
        if temp:shutil.rmtree(temp,ignore_errors=True)
        lock.unlink(missing_ok=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default='.');g=p.add_mutually_exclusive_group();g.add_argument('--apply',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
    try: print(json.dumps(run(a.root,a.apply,a.check),ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as e: print(json.dumps({'ok':False,'error':str(e),'production_ready':False},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
