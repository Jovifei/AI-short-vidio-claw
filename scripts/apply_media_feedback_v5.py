#!/usr/bin/env python3
"""Apply a human-exported recovery gallery review. Never approves keyframes.

Without --apply this only validates the explicit choices and prints a preview.
This is an audit record, not cryptographic proof of the reviewer's identity.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import json
import os
from approve_asset import approve_reference
from preproduction import read_json, write_json, require, ContractError, sha256_file, relative_file
from receive_media_v5 import check, DeliveryError, MANIFEST_LOCAL

ALLOWED_REF_IDS = {'DAIYU_FACE_CROP','WUKONG_FACE_CROP','DAIYU_COSTUME_CROP','WUKONG_COSTUME_CROP'}

def proposed(root, feedback, registry, media):
    require(feedback.get('delivery_id') == 'MEDIA_RECOVERY_20261007', 'wrong gallery delivery')
    require(feedback.get('production_keyframes_approved') == 0, 'this gallery cannot approve keyframes')
    items = feedback.get('items'); require(isinstance(items,list) and bool(items), 'empty review')
    assets = {a['asset_id']:a for a in media['assets']}
    result=deepcopy(registry); seen=set(); approved=[]; notes=[]
    for v in items:
        aid=v.get('asset_id'); require(aid in assets and aid not in seen, 'unknown or duplicate review item')
        seen.add(aid); require(v.get('sha256') == assets[aid]['sha256'], 'review bound to another image')
        decision=v.get('decision'); require(decision in {'approve_reference','keep_source','reject'},'unsupported decision')
        stamp=datetime.fromisoformat(v.get('recorded_at','').replace('Z','+00:00'))
        require(stamp.tzinfo is not None,'review timestamp needs timezone')
        require(bool(v.get('source')),'review source missing')
        if decision=='approve_reference':
            require(aid in ALLOWED_REF_IDS and v.get('scope')=='reference','asset has no production reference role')
            evidence={'subject_id':aid,'sha256':v['sha256'],'decision':'approve','scope':'reference',
                      'source':v['source'],'recorded_at':v['recorded_at'],
                      'user_quote':'在实体素材审核页明确选择“批准这张为参考（不是批准剧情关键帧）”并导出。',
                      'user_notes':v.get('notes','')}
            existing=result['assets'][aid]
            if existing.get('status')=='USER_APPROVED':
                require(existing.get('approval_evidence',{}).get('sha256')==v['sha256'],'existing approval conflicts')
            else:
                result=approve_reference(root,result,aid,evidence);approved.append(aid)
        else:
            require(v.get('scope')=='source_review_only','source feedback must not become approval')
            notes.append(v)
    return result, {'reference_approvals':approved,'source_feedback':notes,'keyframes_approved':0,
                    'production_ready':False,'note':'Does not fill missing HOME/rain/EP001 keyframes or override current shot gates.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default='.');p.add_argument('--feedback',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    lock=None; lock_owned=False
    try:
        root=Path(a.root).resolve();check(root)
        registry_path=relative_file(root,'assets/registry/generated_assets_v5.json')
        before=sha256_file(registry_path);feedback=read_json(a.feedback)
        result,r=proposed(root,feedback,read_json(registry_path),read_json(relative_file(root,MANIFEST_LOCAL)))
        if a.apply:
            lock=relative_file(root,'local/delivery/.review-apply.lock')
            fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd);lock_owned=True
            require(sha256_file(registry_path)==before,'registry changed during review; retry after reading current state')
            receipt=relative_file(root,'local/delivery/REVIEW_'+sha256_file(a.feedback)[:16]+'.json')
            write_json(registry_path,result);write_json(receipt,{'feedback':feedback,'result':r})
            r['mode']='APPLIED_REFERENCE_ONLY'
        else:r['mode']='DRY_RUN'
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except (ContractError,DeliveryError,OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'ok':False,'error':str(e),'production_ready':False},ensure_ascii=False));return 2
    finally:
        if lock_owned and lock is not None and lock.exists():lock.unlink()
if __name__=='__main__':raise SystemExit(main())
