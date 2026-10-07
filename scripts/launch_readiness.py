#!/usr/bin/env python3
"""Read-only shooting-input audit. Reuse V5 approvals; never submit or approve.

Checks EVERY planned shot (including STILL), decodes the exact approved bytes,
and distinguishes three valid I2V inputs from a complete episode input package.
No network, ComfyUI, downloads, local environment changes or inferred approvals.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image
from preproduction import (ContractError, check_plan, read_json, relative_file,
                           require, sha256_file, validate_keyframe, write_json)


def inspect_image(path: Path) -> dict:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        require(getattr(image, 'n_frames', 1) == 1, 'animated input is not a single keyframe')
        width, height = image.size
        require(width >= 640 and height >= 960, 'approved input is too small for this project handoff')
        require(abs(width / height - 9 / 16) <= 0.025, 'approved input must be a reviewed portrait crop near 9:16; never auto-stretch')
        return {'width': width, 'height': height, 'format': image.format, 'decoded': True}


def report_project(root: Path, project: str) -> dict:
    require(project in {'LOOKREEL01', 'EP001'}, 'unknown project')
    base = f'episodes/{project}'
    paths = {'plan': f'{base}/production_plan_v5.json',
             'approval': f'{base}/approval_manifest_v5.json',
             'registry': 'assets/registry/generated_assets_v5.json'}
    p, a, r = (relative_file(root, paths[k]) for k in ('plan', 'approval', 'registry'))
    plan, manifest, registry = map(read_json, (p, a, r))
    summary = check_plan(plan)
    require(plan['project_id'] == project, 'plan/project mismatch')
    require(set(manifest.get('shots', {})) == {s['shot_id'] for s in plan['shots']}, 'approval shot IDs do not match plan')
    rows, valid_i2v, valid_still = [], [], []
    missing_artwork, missing_approval = [], []
    for shot in plan['shots']:
        sid = shot['shot_id']; entry = manifest['shots'][sid]
        relative = entry.get('approved_keyframe')
        exists = False
        if isinstance(relative, str) and relative:
            try:
                exists = relative_file(root, relative).is_file()
            except ContractError:
                pass
        row = {'shot_id': sid, 'title': shot.get('title'), 'render_mode': shot['render_mode'],
               'duration_frames': shot['duration_frames'], 'required_costumes': shot['costume_stages'],
               'approved_file_exists': exists, 'input_valid': False,
               'candidate_visual_quality': 'NOT_INFERRED_BY_THIS_SCRIPT'}
        if not exists:
            missing_artwork.append(sid)
        if entry.get('approved_by_user') is not True:
            missing_approval.append(sid)
        try:
            _, bound, image = validate_keyframe(root, plan, manifest, registry, sid)
            row['image'] = inspect_image(image)
            require(sha256_file(image) == bound['sha256'], 'keyframe changed during image inspection')
            row['input_valid'] = True
            (valid_i2v if shot['render_mode'] == 'I2V' else valid_still).append(sid)
        except (ContractError, OSError, ValueError, KeyError, TypeError) as error:
            row['blocker'] = str(error)
        rows.append(row)
    all_inputs = all(s['input_valid'] for s in rows)
    missing_refs = []
    for aid, asset in registry.get('assets', {}).items():
        try:
            path = relative_file(root, asset.get('path'))
            valid = path.is_file() and sha256_file(path) == asset.get('sha256')
        except (ContractError, OSError, TypeError):
            valid = False
        if not valid:
            missing_refs.append(aid)
    return {'project_id': project, 'contract_ok': True, **summary,
            'source_file_hashes': {paths[k]: sha256_file(path) for k, path in zip(('plan', 'approval', 'registry'), (p, a, r))},
            'reference_files_missing_or_changed': missing_refs,
            'valid_i2v_input_shots': valid_i2v, 'valid_still_input_shots': valid_still,
            't1_input_threshold_met': len(valid_i2v) >= 3,
            'whole_project_inputs_ready': all_inputs,
            'ready_input_count': len(valid_i2v) + len(valid_still),
            'approved_files_not_received': missing_artwork,
            'shot_approvals_not_recorded': missing_approval,
            'runtime_verified_by_this_tool': False,
            'final_video_approved_by_this_tool': False,
            'launch_state': ('INPUTS_READY_LOCAL_TRIAL_REQUIRED' if all_inputs else
                             'PARTIAL_T1_INPUTS_READY' if len(valid_i2v) >= 3 else 'REMOTE_MEDIA_OR_APPROVAL_GAP'),
            'next_allowed': ('cpu_static_assembly_candidate_only' if all_inputs and not valid_i2v else 'local_runtime_precheck_then_one_trial' if len(valid_i2v) >= 3 else 'receive_review_and_complete_remote_images'),
            'note': 'Input readiness is not a passed T1, runtime success, image quality proof or final delivery. STILL shots require real approved images too.',
            'shots': rows}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.')
    p.add_argument('--project', choices=['LOOKREEL01', 'EP001', 'all'], default='all')
    p.add_argument('--require', dest='requirement', choices=['none', 't1-inputs', 'whole-project-inputs'], default='none')
    p.add_argument('--out', help='Optional new JSON report under local/; existing report is never overwritten')
    a = p.parse_args()
    try:
        root = Path(a.root).resolve()
        projects = ['LOOKREEL01', 'EP001'] if a.project == 'all' else [a.project]
        result = {'read_only': True, 'network_requests': 0, 'approvals_changed': 0,
                  'projects': [report_project(root, x) for x in projects]}
        if a.out:
            out = relative_file(root, a.out)
            require(out.is_relative_to(root / 'local'), 'reports may only be written under local/')
            require(not out.exists(), 'report exists; use a new review ID')
            write_json(out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if a.requirement == 'none':
            return 0
        field = {'t1-inputs': 't1_input_threshold_met', 'whole-project-inputs': 'whole_project_inputs_ready'}[a.requirement]
        return 0 if all(x[field] for x in result['projects']) else 2
    except Exception as error:
        print(json.dumps({'contract_ok': False, 'error': str(error), 'whole_project_inputs_ready': False}, ensure_ascii=False)); return 2

if __name__ == '__main__':
    raise SystemExit(main())
