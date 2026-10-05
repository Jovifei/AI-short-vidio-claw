#!/usr/bin/env python3
"""Report document-contract readiness separately from media/render readiness."""
import argparse
import json
from pathlib import Path
from preproduction import check_plan, queue, read_json, relative_file, require


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
        result={'contract_ok':True,**summary,**queue(root,plan,approval,registry),
                'note':'contract_ok does not mean images exist or production is approved.'}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if a.require_ready and not result['production_ready'] else 0
    except Exception as exc:
        print(json.dumps({'contract_ok':False,'production_ready':False,'error':str(exc)},ensure_ascii=False));return 2

if __name__=='__main__':
    raise SystemExit(main())
