#!/usr/bin/env python3
"""Apply explicit FIX2 gallery choices to existing V5 reference records only.

Default is dry-run. --apply never approves any shot, LoRA, or model sheet.
The JSON is a review record, not cryptographic proof of the reviewer's identity.
"""
import argparse
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import tempfile
from approve_asset import approve_reference
from preproduction import ContractError, require, read_json, sha256_file, relative_file
from receive_delivery_fix2 import check, DeliveryError, SAVED_MANIFEST, DELIVERY_ID

ELIGIBLE = {'DAIYU_FACE_CROP', 'WUKONG_FACE_CROP', 'DAIYU_COSTUME_CROP', 'WUKONG_COSTUME_CROP'}
LABEL = '批准这张为参考（不是批准剧情关键帧）'

def proposal(root, feedback, registry, media):
    require(feedback.get('delivery_id') == DELIVERY_ID, 'Wrong review delivery')
    require(type(feedback.get('production_keyframes_approved')) is int and feedback['production_keyframes_approved'] == 0, 'Gallery may not approve keyframes')
    items = feedback.get('items')
    require(isinstance(items, list) and bool(items), 'Empty review; do not invent approval')
    result = deepcopy(registry); seen = set(); approvals = []; notes = []
    assets = {a['asset_id']: a for a in media['assets']}
    for item in items:
        aid = item.get('asset_id')
        require(aid in assets and aid not in seen, 'Unknown or duplicate asset')
        seen.add(aid)
        require(item.get('sha256') == assets[aid]['sha256'], 'Review refers to different bytes')
        decision = item.get('decision')
        require(decision in {'approve_reference', 'keep_source', 'request_changes', 'reject'}, 'Unsupported review decision')
        t = datetime.fromisoformat(item.get('recorded_at', '').replace('Z', '+00:00'))
        require(t.tzinfo is not None, 'Review time must include timezone')
        if decision == 'approve_reference':
            require(aid in ELIGIBLE and item.get('scope') == 'reference', 'No eligible reference role')
            evidence = {'subject_id': aid, 'sha256': item['sha256'], 'scope': 'reference',
                        'decision': 'approve', 'source': 'FIX2实体素材页的明确选择并主动导出',
                        'recorded_at': item['recorded_at'], 'user_quote': LABEL,
                        'notes': item.get('notes', '')}
            result = approve_reference(root, result, aid, evidence)
            approvals.append(aid)
        else:
            require(item.get('scope') == 'feedback_only', 'Source review is feedback only')
            require(not (decision == 'reject' and result.get('assets', {}).get(aid, {}).get('status') == 'USER_APPROVED'), 'Previously approved reference now rejected; revoke/resolve it explicitly before applying other choices')
            notes.append(item)
    return result, dict(reference_approvals=approvals, source_feedback=notes, keyframes_approved=0, production_ready=False)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.'); p.add_argument('--feedback', required=True)
    p.add_argument('--apply', action='store_true'); a = p.parse_args()
    lock = None; owned = False; temp_path = None
    try:
        root = Path(a.root).resolve(); check(root)
        target = relative_file(root, 'assets/registry/generated_assets_v5.json')
        before = sha256_file(target)
        feedback = read_json(a.feedback)
        updated, result = proposal(root, feedback, read_json(target), read_json(relative_file(root, SAVED_MANIFEST)))
        result['mode'] = 'DRY_RUN'
        if a.apply:
            lock = relative_file(root, 'local/delivery/fix2/.review.lock')
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600); os.close(fd); owned = True
            require(sha256_file(target) == before, 'Registry changed; read the current version before retrying')
            fd, name = tempfile.mkstemp(prefix='.fix2-review-', dir=target.parent)
            temp_path = Path(name)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(updated, f, ensure_ascii=False, indent=2); f.write('\n')
            os.replace(temp_path, target); temp_path = None
            result['mode'] = 'APPLIED_REFERENCE_ONLY'
            receipt = relative_file(root, 'local/delivery/fix2/review_' + sha256_file(a.feedback)[:16] + '.json')
            receipt.write_text(json.dumps({'feedback': feedback, 'result': result}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (ContractError, DeliveryError, OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e), 'production_ready': False}, ensure_ascii=False)); return 2
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        if owned:
            lock.unlink(missing_ok=True)

if __name__ == '__main__':
    raise SystemExit(main())
