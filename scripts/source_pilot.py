#!/usr/bin/env python3
"""Offline review/approval/preparation for three EXISTING source-image trials.

This does not create or approve original LOOKREEL/EP001 shots. Review is a human
record, not an identity signature. No network, GPU, or image-generation call.
"""
import argparse
import base64
from datetime import datetime
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from PIL import Image
from approve_asset import approve_reference, approve_keyframe
from preproduction import read_json, write_json, check_plan, prepare, validate_graph, validate_keyframe, _unique
from sync_repo_media import safe, digest, need, verify
from fid1_graph_audit import attach_fid1_anchor
try:
    from .fid1_qa_report import verified_run_output
except ImportError:
    from fid1_qa_report import verified_run_output

PROJECT = 'T1_SOURCE_PILOT'
BASE = 'episodes/' + PROJECT
KIT = BASE + '/source_kit.json'
LOCAL = 'local/production/' + PROJECT
POINTER = LOCAL + '/current_review.json'
SCOPE = 'T1_SOURCE_ONLY'
LABEL = '我批准本卡原图及展示的两个人脸参考、两张服装裁片，仅用于同源保真试拍；不批准EP001、LOOKREEL01或最终定妆。'
FID1_DEPENDENCY_FILES = (
    'scripts/fid1_wan_latent_anchor_node.py',
    'scripts/fid1_graph_audit.py',
    'scripts/preproduction.py',
    'scripts/source_pilot.py',
    'scripts/submit_prepared.py',
    'scripts/p1_comfy_probe.py',
    'scripts/fid1_deploy.py',
    'scripts/fid1_qa_report.py',
    'docs/reviews/20261011-source-fidelity/installed_comfy_source/source_manifest.json',
)
FID1_PREVIOUS_TRIAL = {
    'SH901': ('SH903', 'take04'),
    'SH902': ('SH901', 'take02'),
}


def fid1_dependency_hash(root):
    hashes={rel:digest(safe(root,rel)) for rel in FID1_DEPENDENCY_FILES}
    combined=hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return hashes,combined


def require_previous_fid1_visual_acceptance(root, sid):
    previous=FID1_PREVIOUS_TRIAL.get(sid)
    if previous is None:return
    previous_shot,previous_take=previous
    job_rel=f'{LOCAL}/video/{previous_shot}/jobs/{previous_take}'
    report_path=safe(root,job_rel+'/qa/qa_report.json')
    need(report_path.is_file(),f'{previous_shot} {previous_take} QA and Jovi visual review are required before {sid}')
    need(safe(root,job_rel+'/job.json').is_file() and safe(root,job_rel+'/run_record.json').is_file(),
         f'{previous_shot} {previous_take} prepared job and ComfyUI run record are required before {sid}')
    report=read_json(report_path);review=report.get('visual_review',{})
    previous_job=read_json(safe(root,job_rel+'/job.json'))
    run_record=read_json(safe(root,job_rel+'/run_record.json'))
    output_path, output_record=verified_run_output(root,safe(root,job_rel),run_record)
    need(report.get('scope')==SCOPE and report.get('shot_id')==previous_shot
         and report.get('runtime_success') is True and report.get('media_contract_ok') is True
         and report.get('full_decode')=='PASS',f'{previous_shot} {previous_take} runtime/media QA is not complete')
    need(previous_job.get('shot_id')==previous_shot and previous_job.get('purpose')==SCOPE
         and report.get('profile_id')==previous_job.get('trial_profile',{}).get('profile_id'),
         f'{previous_shot} {previous_take} QA is not bound to its prepared source-only job')
    outputs=run_record.get('outputs')
    need(run_record.get('result')=='success' and run_record.get('prompt_id')
         and isinstance(outputs,list) and len(outputs)==1
         and report.get('output',{}).get('sha256')==outputs[0].get('sha256')==output_record.get('sha256')
         and report.get('output',{}).get('bytes')==output_record.get('bytes')
         and report.get('output',{}).get('path')==output_path.relative_to(safe(root,job_rel)).as_posix(),
         f'{previous_shot} {previous_take} QA does not match a successful ComfyUI output')
    need(review.get('decision')=='ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL'
         and review.get('reviewer')=='Jovi'
         and all(review.get(key)=='PASS' for key in ('full_playback','identity','costume','limbs')),
         f'{previous_shot} {previous_take} requires Jovi visual acceptance before {sid}')
    evidence_path=review.get('evidence_path');evidence_sha=review.get('evidence_sha256')
    need(isinstance(evidence_path,str) and evidence_path.startswith('local/review_evidence/FID1_')
         and isinstance(evidence_sha,str) and len(evidence_sha)==64,'Jovi visual review evidence is missing')
    evidence_file=safe(root,evidence_path)
    need(digest(evidence_file)==evidence_sha,'Jovi visual review evidence hash changed')
    evidence=read_json(evidence_file)
    need(evidence.get('scope')==SCOPE and evidence.get('shot_id')==previous_shot
         and evidence.get('profile_id')==report.get('profile_id')
         and evidence.get('decision')=='ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL'
         and evidence.get('reviewer')=='Jovi'
         and all(evidence.get(key)=='PASS' for key in ('full_playback','identity','costume','limbs'))
         and evidence.get('user_quote')==review.get('user_quote')
         and evidence.get('recorded_at')==review.get('recorded_at')
         and evidence.get('output_sha256')==report.get('output',{}).get('sha256'),
         'visual review is not bound to the actual output')


def inputs(root):
    root = Path(root).resolve(); verify(root, True)
    kit = read_json(safe(root, KIT)); need(kit.get('scope') == SCOPE, 'wrong pilot scope')
    need(set(kit.get('shots', {})) == {'SH901', 'SH902', 'SH903'}, 'unexpected pilot shots')
    need(kit['plan_path'] == BASE+'/production_plan_v5.json' and kit['registry_path'] == BASE+'/reference_registry_candidate.json'
         and kit['approval_path'] == BASE+'/approval_manifest_v5.json', 'pilot paths cannot target other episodes')
    plan = read_json(safe(root, kit['plan_path'])); check_plan(plan)
    need(plan['project_id'] == PROJECT and plan['visual_target_id'] == 'T1_SOURCE_REVIEW_20261008', 'wrong trial identity')
    need({s['shot_id'] for s in plan['shots']} == set(kit['shots']), 'trial plan/kit mismatch')
    registry = read_json(safe(root, kit['registry_path']))
    for s in kit['shots'].values():
        need(s['repo_path'].startswith('assets/media/source_library/'), 'source outside Git media')
        need(digest(safe(root, s['repo_path'])) == s['sha256'], 'source hash changed')
        for aid in ref_ids(s):
            a = registry['assets'][aid]
            need(digest(safe(root, a['path'])) == a['sha256'], 'reference changed: '+aid)
        with Image.open(safe(root, s['repo_path'])) as im:
            im.load(); need(im.n_frames == 1 and im.width >= 768 and im.height > im.width, 'not an independent vertical source')
    hashes = {rel:digest(safe(root, rel)) for rel in (KIT, kit['plan_path'], kit['registry_path'], kit['approval_path'])}
    bundle = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return kit, plan, registry, bundle


def ref_ids(shot):
    b = shot['bindings']
    return [a for c in ('DAIYU','WUKONG') for a in b['identity_refs'][c]] + [b['costume_refs'][c]['asset_id'] for c in ('DAIYU','WUKONG')]


def thumbnail(path, size):
    with Image.open(path) as im:
        im = im.convert('RGB'); im.thumbnail(size); out=io.BytesIO(); im.save(out,'JPEG',quality=88)
    return 'data:image/jpeg;base64,'+base64.b64encode(out.getvalue()).decode()


def review(root):
    root=Path(root).resolve(); kit, plan, registry, bundle=inputs(root); cards=[]
    for sid,s in kit['shots'].items():
        refs=''.join('<figure><img src="'+thumbnail(safe(root,registry['assets'][a]['path']),(350,450))+'"><figcaption>'+html.escape(a)+'</figcaption></figure>' for a in ref_ids(s))
        cards.append('<section><h2>'+sid+' '+html.escape(s['title'])+'</h2><img class="main" src="'+thumbnail(safe(root,s['repo_path']),(720,1280))+'"><div class="refs">'+refs+'</div><label><input type="checkbox" id="'+sid+'">'+html.escape(LABEL)+'</label><p><textarea id="n_'+sid+'" placeholder="具体修改意见（勾选才是批准；未勾选保持不批准）"></textarea></p></section>')
    meta={'scope':SCOPE,'bundle_sha256':bundle,'shots':{sid:{'sha256':s['sha256']} for sid,s in kit['shots'].items()}}
    js='''const meta=__META__;const quote=__QUOTE__;function save(){const items=Object.entries(meta.shots).filter(([id])=>document.getElementById(id).checked).map(([id,s])=>({shot_id:id,sha256:s.sha256,decision:'approve_trial',scope:meta.scope,user_quote:quote,notes:document.getElementById('n_'+id).value,recorded_at:new Date().toISOString()}));if(!items.length){alert('未勾选任何图片，没有批准记录。');return;}const d={scope:meta.scope,bundle_sha256:meta.bundle_sha256,items};const u=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='T1_SOURCE_REVIEW.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}'''.replace('__META__',json.dumps(meta)).replace('__QUOTE__',json.dumps(LABEL,ensure_ascii=False))
    page='<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>三张现有源图试拍审核</title><style>body{max-width:1100px;margin:auto;padding:24px;font:17px system-ui}section{border-top:2px solid #aaa;margin:32px 0;padding-top:20px}.main{max-width:100%;max-height:850px}.refs{display:flex;flex-wrap:wrap}figure{width:21%;margin:1%;overflow-wrap:anywhere}figure img{width:100%;max-height:320px;object-fit:contain}textarea{width:95%;min-height:70px}button{padding:16px;font-size:20px}input{width:24px;height:24px}</style><h1>源图保真试拍：不是30镜开拍验收</h1><p>三张是已有来源，不是新制作的EP001/LOOKREEL镜头。每条只做49帧/24fps≈2.04秒，姿势、手部和脸保持不动。参考裁片较小，仅作为可见细节检查，不用于宣称独立定妆完成。逐卡查看脸和古装；不满意不要勾选。</p>'+''.join(cards)+'<button onclick="save()">导出已勾选图片的明确批准</button><p>未勾选即未批准。请将下载的T1_SOURCE_REVIEW.json交本地Codex。此页不联网、不调用GPU。</p><script>'+js+'</script></html>'
    p=safe(root,LOCAL+'/review.html');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(page,encoding='utf-8')
    return {'review_page':str(p),'default_approvals':0,'original_episode_approvals_changed':0}


def choices(root, feedback):
    kit,plan,registry,bundle=inputs(root)
    need(feedback.get('scope')==SCOPE and feedback.get('bundle_sha256')==bundle,'feedback scope/bundle mismatch')
    items=feedback.get('items');need(isinstance(items,list) and 0<len(items)<=3,'no explicit choices')
    seen=set()
    for item in items:
        sid=item.get('shot_id');need(sid in kit['shots'] and sid not in seen,'unknown/duplicate shot');seen.add(sid)
        need(item.get('decision')=='approve_trial' and item.get('scope')==SCOPE and item.get('user_quote')==LABEL,'not explicit trial approval')
        need(item.get('sha256')==kit['shots'][sid]['sha256'],'wrong approved pixels')
        t=datetime.fromisoformat(item.get('recorded_at','').replace('Z','+00:00'));need(t.tzinfo is not None,'timestamp needs timezone')
    return kit,plan,registry,items


def evidence(subject,h,scope,item):
    return dict(subject_id=subject,sha256=h,scope=scope,decision='approve',user_quote=item['user_quote'],source='Offline source pilot review; exact displayed card',recorded_at=item['recorded_at'],trial_scope=SCOPE,notes=item.get('notes',''))


def apply_review(root, feedback_path, apply=False):
    root=Path(root).resolve();fb=read_json(feedback_path);kit,plan,registry,items=choices(root,fb)
    result={'mode':'DRY_RUN','selected':[v['shot_id'] for v in items],'original_episode_approvals_changed':0,'production_ready':False}
    if not apply:return result
    base=safe(root,LOCAL);base.mkdir(parents=True,exist_ok=True)
    lock=safe(root,LOCAL+'/.review.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    temp=None;created=[]
    try:
        kit,plan,registry,items=choices(root,fb)
        manifest=read_json(safe(root,kit['approval_path']))
        fbh=hashlib.sha256(json.dumps(fb,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        snapshot=safe(root,LOCAL+'/reviews/'+fbh)
        need(not snapshot.exists(),'review already recorded; use current review or export a new explicit decision')
        for v in items:
            s=kit['shots'][v['shot_id']];dst=safe(root,s['approved_path'])
            if dst.exists():need(dst.is_file() and digest(dst)==s['sha256'],'approved path conflicts; not overwritten')
        temp=Path(tempfile.mkdtemp(prefix='.source-review-',dir=base))
        for v in items:
            sid=v['shot_id'];s=kit['shots'][sid];dst=safe(root,s['approved_path']);dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists():
                staged=temp/(sid+'.png');shutil.copyfile(safe(root,s['repo_path']),staged)
                need(digest(staged)==s['sha256'],'source changed while copying');os.link(staged,dst);created.append((dst,s['sha256']))
            for aid in ref_ids(s):
                a=registry['assets'][aid];registry=approve_reference(root,registry,aid,evidence(aid,a['sha256'],'reference',v))
            manifest=approve_keyframe(root,plan,manifest,registry,sid,s['approved_path'],s['bindings'],evidence(sid,s['sha256'],'keyframe',v))
        for name,value in [('registry.json',registry),('approval.json',manifest),('feedback.json',fb)]:write_json(temp/name,value)
        for p in temp.glob('SH*.png'):p.unlink()
        snapshot.parent.mkdir(parents=True,exist_ok=True);os.rename(temp,snapshot);temp=None
        pointer={'scope':SCOPE,'snapshot':str(snapshot.relative_to(root)).replace('\\','/'),'files':{name:digest(snapshot/name) for name in ('registry.json','approval.json','feedback.json')}}
        write_json(safe(root,POINTER),pointer)
        result.update(mode='APPLIED_SOURCE_TRIAL_ONLY',snapshot=pointer['snapshot']);return result
    except Exception:
        for p,h in reversed(created):
            if p.is_file() and digest(p)==h:p.unlink()
        raise
    finally:
        if temp:shutil.rmtree(temp,ignore_errors=True)
        lock.unlink(missing_ok=True)


def load_trial_profile(root, sid, kit, relative):
    if relative is None:
        return None
    need(isinstance(relative,str) and relative.startswith('config/source_fidelity_trials/') and relative.endswith('.json'),
         'trial profile must be a reviewed config/source_fidelity_trials JSON')
    raw=safe(root,relative).read_bytes()
    profile=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=_unique)
    base_fields={'schema_version','profile_id','scope','shot_id','input_sha256','width','height','frames','fps',
                 'positive_prompt','negative_prompt','hypothesis'}
    schema=profile.get('schema_version')
    need(type(schema) is int,'trial profile schema_version must be an integer')
    if schema==1:
        need(set(profile)==base_fields,'unexpected/missing trial profile fields; model and sampler overrides are not allowed')
    elif schema in (2,3):
        need(set(profile)==base_fields|{'seed','anchor_strategy','anchor_rois'},
             'unexpected/missing FID1 profile fields; model and sampler overrides are not allowed')
    else:
        need(False,'unsupported trial profile schema')
    need(profile['scope']==SCOPE,'wrong trial profile schema/scope')
    need(profile['shot_id']==sid and profile['input_sha256']==kit['shots'][sid]['sha256'],'profile belongs to other approved pixels')
    need(isinstance(profile['profile_id'],str) and re.fullmatch(r'[A-Z0-9_]{1,64}',profile['profile_id']),'invalid profile_id')
    need(all(type(profile[k]) is int for k in ('width','height','frames','fps')),'profile sizes must be integers')
    need((profile['width'],profile['height']) in {(480,832),(576,1024)},'only existing 5B candidate size tiers are allowed')
    need(profile['frames']==49 and profile['fps']==24,'source trial remains 49 frames / 24 fps')
    need(all(isinstance(profile[k],str) and 0<len(profile[k].strip())<=4096
             for k in ('positive_prompt','negative_prompt','hypothesis')),'missing/oversized quality experiment text')
    if schema in (2,3):
        need(type(profile['seed']) is int and 0<=profile['seed']<2**63,'FID1 profile seed must be a non-negative 63-bit integer')
        need(profile['anchor_strategy']=='wan22_first_latent_future_roi_v1','unsupported FID1 anchor strategy')
        rois=profile['anchor_rois'];need(isinstance(rois,list) and 1<=len(rois)<=8,'FID1 profile needs 1–8 explicit ROI boxes')
        seen=set();area=0.0
        for roi in rois:
            roi_fields={'id','x0','y0','x1','y1'}
            if schema==3:roi_fields.add('feather_latent')
            need(isinstance(roi,dict) and set(roi)==roi_fields,'FID1 ROI fields do not match the profile schema')
            name=roi['id'];need(isinstance(name,str) and re.fullmatch(r'[A-Z0-9_]{1,32}',name) and name not in seen,'invalid/duplicate FID1 ROI id');seen.add(name)
            coords=[roi[k] for k in ('x0','y0','x1','y1')]
            need(all(type(v) in (int,float) and math.isfinite(v) for v in coords),'FID1 ROI coordinates must be finite numbers')
            x0,y0,x1,y1=coords
            need(0<=x0<x1<=1 and 0<=y0<y1<=1,'FID1 ROI bounds must be ordered within [0,1]')
            if schema==3:
                need(type(roi['feather_latent']) is int and 1<=roi['feather_latent']<=4,
                     'FID1 feather_latent must be an integer from 1 to 4')
            area+=(x1-x0)*(y1-y0)
        need(area<0.5,'FID1 ROIs cover too much of the frame')
    return profile, hashlib.sha256(raw).hexdigest()


def prepare_trial(root,sid,seed,out,trial_profile=None):
    root=Path(root).resolve();kit,plan,_,_=inputs(root)
    pointer=read_json(safe(root,POINTER));need(pointer.get('scope')==SCOPE,'missing scoped review')
    need(pointer['snapshot'].startswith(LOCAL+'/reviews/'),'wrong review path');snap=safe(root,pointer['snapshot'])
    need(set(pointer['files'])=={'registry.json','approval.json','feedback.json'},'bad review snapshot')
    for f,h in pointer['files'].items():need(digest(snap/f)==h,'review snapshot changed')
    choices(root,read_json(snap/'feedback.json'))
    registry=read_json(snap/'registry.json');manifest=read_json(snap/'approval.json')
    for s in kit['shots']:validate_keyframe(root,plan,manifest,registry,s)
    need(sid in kit['shots'],'unknown source trial shot')
    shot=next(s for s in plan['shots'] if s['shot_id']==sid)
    loaded_profile=load_trial_profile(root,sid,kit,trial_profile)
    profile,profile_hash=loaded_profile if loaded_profile else (None,None)
    fid1_dependencies_at_start=None
    if profile and profile.get('anchor_strategy'):
        need(seed==profile['seed'],'FID1 run seed differs from the shot-specific frozen profile')
        require_previous_fid1_visual_acceptance(root,sid)
        fid1_dependencies_at_start=fid1_dependency_hash(root)
    destination=safe(root,out)
    need(destination.is_relative_to(root/LOCAL),'job outside source pilot')
    need(not destination.exists(),'job directory already exists; choose a new take')
    stage=None
    if profile:
        destination.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(prefix='.quality-prepare-',dir=destination.parent))
    directory=stage/'job' if stage else destination
    try:
        job=prepare(root,safe(root,kit['plan_path']),snap/'approval.json',snap/'registry.json',safe(root,'workflows/video/production/VID_wan22_5b_i2v_prod_v001.json'),sid,seed,directory)
        graph=read_json(directory/'workflow.json');ids=validate_graph(graph,['DAIYU','WUKONG'])
        prefix='video/T1_SOURCE_ONLY/'+sid+'/'
        job['characters']=shot['characters']
        if profile:
            graph[ids['latent']]['inputs'].update(width=profile['width'],height=profile['height'],length=profile['frames'])
            graph[ids['positive']]['inputs']['text']=profile['positive_prompt']
            negative=str(graph[ids['sampler']]['inputs']['negative'][0])
            graph[negative]['inputs']['text']=profile['negative_prompt']
            graph[ids['video']]['inputs']['fps']=profile['fps']
            prefix+=profile['profile_id']+'/'
            if profile.get('anchor_strategy'):
                attach_fid1_anchor(graph,shot['characters'],profile)
                validate_graph(graph,shot['characters'],fid1_profile=profile)
            else:
                validate_graph(graph,shot['characters'])
            job['trial_profile']=profile
            job['trial_profile_path']=Path(trial_profile).as_posix()
            job['original_render_profile']=next(s['i2v'] for s in plan['shots'] if s['shot_id']==sid)
            need(digest(safe(root,trial_profile))==profile_hash,'trial profile changed during preparation')
            job['sources'][trial_profile]=profile_hash
            job['sources']['scripts/source_pilot.py']=digest(safe(root,'scripts/source_pilot.py'))
            job['sources']['scripts/preproduction.py']=digest(safe(root,'scripts/preproduction.py'))
            if profile.get('anchor_strategy'):
                dependency_hashes,dependency_hash=fid1_dependencies_at_start
                job['sources'].update(dependency_hashes)
                job['fid1_contract']={
                    'schema_version':1,
                    'strategy':profile['anchor_strategy'],
                    'node_class':'FID1WanSourceROIAnchor',
                    'node_source_sha256':dependency_hashes['scripts/fid1_wan_latent_anchor_node.py'],
                    'profile_sha256':profile_hash,
                    'dependency_sha256':dependency_hash,
                    'dependency_files':dependency_hashes,
                    'noise_mask_semantics':'1=denoise;0=preserve',
                }
        graph[ids['save']]['inputs']['filename_prefix']=prefix+str(seed)
        write_json(directory/'workflow.json',graph)
        job.update(purpose=SCOPE,eligible_for_final_cut=False,workflow_sha256=digest(directory/'workflow.json'))
        for rel in (POINTER,KIT,kit['registry_path'],pointer['snapshot']+'/feedback.json'):
            job['sources'][rel]=digest(safe(root,rel))
        write_json(directory/'job.json',job)
        if job.get('fid1_contract'):
            write_json(directory/'job_integrity.json',{
                'schema_version':1,
                'job_sha256':digest(directory/'job.json'),
                'workflow_sha256':job['workflow_sha256'],
                'input_sha256':job['input_sha256'],
            })
        if stage:
            need(digest(safe(root,trial_profile))==profile_hash,'trial profile changed before publication')
            if fid1_dependencies_at_start is not None:
                need(fid1_dependency_hash(root)==fid1_dependencies_at_start,
                     'FID1 implementation/dependency changed during preparation')
            need(not destination.exists(),'concurrent quality job writer')
            os.rename(directory,destination)
        return {'prepared':True,'submitted':False,'scope':SCOPE,'job_dir':out,'eligible_for_final_cut':False,
                'trial_profile':profile['profile_id'] if profile else None}
    finally:
        if stage and stage.exists():shutil.rmtree(stage)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['review','apply','prepare']);p.add_argument('--root',default='.');p.add_argument('--feedback');p.add_argument('--apply',action='store_true');p.add_argument('--shot');p.add_argument('--seed',type=int,default=2026100801);p.add_argument('--out');p.add_argument('--trial-profile',help='Reviewed source-only quality experiment config; never changes the original plan');a=p.parse_args()
    try:
        if a.command=='review':r=review(a.root)
        elif a.command=='apply':need(bool(a.feedback),'--feedback required');r=apply_review(a.root,a.feedback,a.apply)
        else:need(bool(a.shot) and bool(a.out),'--shot and --out required');r=prepare_trial(a.root,a.shot,a.seed,a.out,a.trial_profile)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except Exception as e:print(json.dumps({'ok':False,'error':str(e),'production_ready':False},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
