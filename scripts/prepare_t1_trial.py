#!/usr/bin/env python3
"""Freeze an approved-image T1 probe; never modify the production timeline.

Reuses V5 prepare/identity/file checks. Only frames change to 33/49/81.
A T1_ONLY job is not an accepted episode clip. No submission or approvals.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from preproduction import (prepare, read_json, relative_file, require, sha256_file,
                           validate_graph, write_json)


def trial(root, project, shot, frames, seed, relative_out):
    root=Path(root).resolve()
    require(project in {'LOOKREEL01','EP001'},'unknown project')
    require(type(frames) is int and frames in {33,49,81},'T1 frames must be 33,49,81')
    dest=relative_file(root,relative_out)
    parent=relative_file(root,f'local/production/{project}')
    require(dest.is_relative_to(parent),'T1 job must be under the same project')
    require(not dest.exists(),'job output exists; choose a new trial ID')
    dest.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.t1-build-',dir=dest.parent))
    try:
        plan_path=relative_file(root,f'episodes/{project}/production_plan_v5.json')
        approval_path=relative_file(root,f'episodes/{project}/approval_manifest_v5.json')
        registry_path=relative_file(root,'assets/registry/generated_assets_v5.json')
        workflow_path=relative_file(root,'workflows/video/production/VID_wan22_5b_i2v_prod_v001.json')
        packet=prepare(root,plan_path,approval_path,registry_path,workflow_path,shot,seed,stage/'job')
        graph=read_json(stage/'job/workflow.json')
        spec=next(s for s in read_json(plan_path)['shots'] if s['shot_id']==shot)
        ids=validate_graph(graph,spec['characters'])
        graph[ids['latent']]['inputs']['length']=frames
        graph[ids['save']]['inputs']['filename_prefix']=f'video/t1_only/{project}/{shot}/frames{frames}_seed{seed}'
        validate_graph(graph,spec['characters'])
        write_json(stage/'job/workflow.json',graph)
        packet.update(purpose='T1_ONLY',workflow_sha256=sha256_file(stage/'job/workflow.json'),
                      trial_source_frames=frames,source_fps=24,trial_seconds=frames/24,
                      original_cut_frames=spec['duration_frames'],eligible_for_final_cut=False,
                      note='Approved input bytes retained. Trial profile only; no production timeline or approval changed. Do not put this trial in the final edit without separate duration/visual acceptance.')
        write_json(stage/'job/job.json',packet)
        require(not dest.exists(),'concurrent job writer detected')
        os.rename(stage/'job',dest)
        return packet
    finally:
        shutil.rmtree(stage,ignore_errors=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='.')
    p.add_argument('--project',required=True,choices=['LOOKREEL01','EP001'])
    p.add_argument('--shot',required=True)
    p.add_argument('--frames',type=int,default=49,choices=[33,49,81])
    p.add_argument('--seed',required=True,type=int)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        print(json.dumps(trial(a.root,a.project,a.shot,a.frames,a.seed,a.out),ensure_ascii=False,indent=2));return 0
    except Exception as e:
        print(json.dumps({'prepared':False,'submitted':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
