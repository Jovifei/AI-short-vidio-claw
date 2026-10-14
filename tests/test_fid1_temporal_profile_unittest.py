"""Offline conditional B profile/graph tests; no real trial or human approval."""
import copy
import json
import subprocess
import sys
import unittest
from test_git_media_delivery import ROOT
import test_fid1_v006_unittest as fixtures
from preproduction import read_json, write_json, validate_graph
from submit_prepared import job_command, validate_fid1_object_info

PROFILE='config/source_fidelity_trials/SH903_FID1_V007.json'


class TemporalProfileTests(unittest.TestCase):
    def fixture(self):
        owner=fixtures.V006Tests();fixture,_=owner.fixture();self.addCleanup(owner.doCleanups)
        profile=read_json(ROOT/PROFILE)
        profile['input_sha256']=read_json(fixture.root/fixtures.fixtures.pilot.KIT)['shots']['SH903']['sha256']
        fixture.profile_path=PROFILE;write_json(fixture.root/PROFILE,profile)
        return fixture,profile

    def test_real_v007_preserves_prompts_source_seed_and_roi(self):
        a=read_json(ROOT/fixtures.PROFILE);b=read_json(ROOT/PROFILE)
        self.assertEqual(set(b)-set(a),{'temporal_anchor_schedule'})
        self.assertEqual({k for k in a if a[k]!=b[k]}, {'schema_version','profile_id','hypothesis','anchor_strategy'})
        self.assertEqual(b['temporal_anchor_schedule'],[1,1,1,1,.9,.8,.7,.6,.6,.6,.6,.6])

    def test_prepare_freezes_schedule_graph_and_dryrun_rejects_drift(self):
        fixture,profile=self.fixture();fixture.prepare()
        graph=read_json(fixture.root/fixture.out/'workflow.json')
        ident,anchor=next((k,v) for k,v in graph.items() if v['class_type']=='FID1WanTemporalROIAnchor')
        self.assertEqual(json.loads(anchor['inputs']['temporal_anchor_schedule_json']),profile['temporal_anchor_schedule'])
        sampler=next(v['inputs'] for v in graph.values() if v['class_type']=='KSampler')
        self.assertEqual(sampler['model'],[ident,0]);self.assertEqual(sampler['latent_image'],[ident,1])
        _,job=job_command(fixture.root,fixture.root/fixture.out,'http://127.0.0.1:8188')
        self.assertEqual(job['trial_profile'],profile)
        graph[ident]['inputs']['temporal_anchor_schedule_json']='[1,1,1,1,1,1,1,1,1,1,1,1]'
        with self.assertRaisesRegex(ValueError,'temporal schedule'):
            validate_graph(graph,job['characters'],fid1_profile=profile)
        write_json(fixture.root/PROFILE,{**profile,'temporal_anchor_schedule':[1]*12})
        with self.assertRaises(ValueError):job_command(fixture.root,fixture.root/fixture.out,'http://127.0.0.1:8188')

    def test_strict_schedule_profile_and_runtime_ports(self):
        fixture,profile=self.fixture();pilot=fixtures.fixtures.pilot
        kit=read_json(fixture.root/pilot.KIT)
        for schedule in ([1]*11,[True]*12,[1,float('nan')]+[.6]*10,[.9]*12,[1,.6,.7]+[.6]*9):
            write_json(fixture.root/PROFILE,{**profile,'temporal_anchor_schedule':schedule})
            with self.assertRaises(ValueError):pilot.load_trial_profile(fixture.root,'SH903',kit,PROFILE)
        name='FID1WanTemporalROIAnchor'
        info={name:{'input':{'required':{'model':['MODEL'],'latent':['LATENT'],'roi_boxes_json':['STRING'],
                  'temporal_anchor_schedule_json':['STRING']}},'output':['MODEL','LATENT']}}
        self.assertTrue(validate_fid1_object_info(info,name))
        missing=copy.deepcopy(info);del missing[name]['input']['required']['temporal_anchor_schedule_json']
        with self.assertRaises(ValueError):validate_fid1_object_info(missing,name)
        with self.assertRaises(ValueError):validate_fid1_object_info({},name)

    def test_no_torch_prepare_and_dryrun_subprocess(self):
        fixture,_=self.fixture()
        code='''import builtins,runpy,sys,pathlib
old=builtins.__import__
def guard(name,*a,**k):
    if name=='torch' or name.startswith('torch.'):raise AssertionError('offline B imported torch')
    return old(name,*a,**k)
builtins.__import__=guard
script,*args=sys.argv[1:];sys.path.insert(0,str(pathlib.Path(script).parent));sys.argv=[script,*args]
runpy.run_path(script,run_name='__main__')
'''
        for script,args in [('source_pilot.py',['prepare','--root',str(fixture.root),'--shot','SH903','--seed','2026100803',
             '--out',fixture.out,'--trial-profile',PROFILE]),('submit_prepared.py',['--root',str(fixture.root),
             '--job-dir',fixture.out,'--url','http://127.0.0.1:8188'])]:
            result=subprocess.run([sys.executable,'-c',code,str(ROOT/'scripts'/script),*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((fixture.root/fixture.out/'submission_intent.json').exists())
