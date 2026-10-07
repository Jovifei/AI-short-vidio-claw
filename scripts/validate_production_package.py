#!/usr/bin/env python3
"""Report document-contract readiness separately from media/render readiness."""
import argparse
import json
from pathlib import Path
from preproduction import check_plan, queue, read_json, relative_file, require, validate_keyframe


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='.')
    p.add_argument('--project-dir',required=True)
    p.add_argument('--registry',default='assets/registry/generated_assets_v5.json')
    p.add_argument('--require-ready',action='store_true')
    a=p.parse_args()
    try:
        root=Path(a.root).resolve(); project=relative_file(root,a.project_dir)
        plan=read_json(project/'production_plan_v5.json')
        approval=read_json(project/'approval_manifest_v5.json')
        registry=read_json(relative_file(root,a.registry))
        summary=check_plan(plan)
        require(set(approval.get('shots',{}))=={s['shot_id'] for s in plan['shots']},'plan/approval shot IDs differ')
        require(approval.get('schema_version')==5 and approval.get('project_id')==plan['project_id'],'approval schema/project mismatch')
        result={'contract_ok':True,**summary,**queue(root,plan,approval,registry)}
        # queue() only schedules I2V; it must not certify missing STILL inputs.
        all_blocked=[]; all_valid=[]
        for shot in plan['shots']:
            try:
                validate_keyframe(root,plan,approval,registry,shot['shot_id'])
                all_valid.append(shot['shot_id'])
            except Exception as exc:
                all_blocked.append({'shot_id':shot['shot_id'],'render_mode':shot['render_mode'],'reason':str(exc)})
        result.update(all_keyframe_inputs_ready=not all_blocked,
                      all_valid_keyframe_shots=all_valid,all_keyframe_blockers=all_blocked,
                      production_ready=not all_blocked,
                      note='production_ready here means V5 input contracts only, including STILL shots; not a passed GPU trial, image-decode QA or final approval. Use launch_readiness.py for full media input checks.')
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if a.require_ready and not result['production_ready'] else 0
    except Exception as exc:
        print(json.dumps({'contract_ok':False,'production_ready':False,'error':str(exc)},ensure_ascii=False));return 2

if __name__=='__main__':
    raise SystemExit(main())
