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
import os
from pathlib import Path
import shutil
import tempfile
from PIL import Image
from approve_asset import approve_reference, approve_keyframe
from preproduction import read_json, write_json, check_plan, prepare, validate_graph, validate_keyframe
from sync_repo_media import safe, digest, need, verify

PROJECT = 'T1_SOURCE_PILOT'
BASE = 'episodes/' + PROJECT
KIT = BASE + '/source_kit.json'
LOCAL = 'local/production/' + PROJECT
POINTER = LOCAL + '/current_review.json'
SCOPE = 'T1_SOURCE_ONLY'
LABEL = '我批准本卡原图及展示的两个人脸参考、两张服装裁片，仅用于同源保真试拍；不批准EP001、LOOKREEL01或最终定妆。'


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


def prepare_trial(root,sid,seed,out):
    root=Path(root).resolve();kit,plan,_,_=inputs(root)
    pointer=read_json(safe(root,POINTER));need(pointer.get('scope')==SCOPE,'missing scoped review')
    need(pointer['snapshot'].startswith(LOCAL+'/reviews/'),'wrong review path');snap=safe(root,pointer['snapshot'])
    need(set(pointer['files'])=={'registry.json','approval.json','feedback.json'},'bad review snapshot')
    for f,h in pointer['files'].items():need(digest(snap/f)==h,'review snapshot changed')
    choices(root,read_json(snap/'feedback.json'))
    registry=read_json(snap/'registry.json');manifest=read_json(snap/'approval.json')
    for s in kit['shots']:validate_keyframe(root,plan,manifest,registry,s)
    job=prepare(root,safe(root,kit['plan_path']),snap/'approval.json',snap/'registry.json',safe(root,'workflows/video/production/VID_wan22_5b_i2v_prod_v001.json'),sid,seed,safe(root,out))
    directory=safe(root,out);graph=read_json(directory/'workflow.json');ids=validate_graph(graph,['DAIYU','WUKONG'])
    graph[ids['save']]['inputs']['filename_prefix']='video/T1_SOURCE_ONLY/'+sid+'/'+str(seed)
    write_json(directory/'workflow.json',graph)
    job.update(purpose=SCOPE,eligible_for_final_cut=False,workflow_sha256=digest(directory/'workflow.json'))
    for rel in (POINTER,KIT,kit['registry_path'],pointer['snapshot']+'/feedback.json'):
        job['sources'][rel]=digest(safe(root,rel))
    write_json(directory/'job.json',job);return {'prepared':True,'submitted':False,'scope':SCOPE,'job_dir':out,'eligible_for_final_cut':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['review','apply','prepare']);p.add_argument('--root',default='.');p.add_argument('--feedback');p.add_argument('--apply',action='store_true');p.add_argument('--shot');p.add_argument('--seed',type=int,default=2026100801);p.add_argument('--out');a=p.parse_args()
    try:
        if a.command=='review':r=review(a.root)
        elif a.command=='apply':need(bool(a.feedback),'--feedback required');r=apply_review(a.root,a.feedback,a.apply)
        else:need(bool(a.shot) and bool(a.out),'--shot and --out required');r=prepare_trial(a.root,a.shot,a.seed,a.out)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except Exception as e:print(json.dumps({'ok':False,'error':str(e),'production_ready':False},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
