"""Offline v4 strength profile/graph tests; no real trial or human approval."""
import copy
import json
import subprocess
import sys
import unittest
from test_git_media_delivery import ROOT
import test_fid1_v006_unittest as fixtures
from preproduction import read_json, write_json, validate_graph
from submit_prepared import job_command, validate_fid1_object_info

PROFILE='config/source_fidelity_trials/SH903_FID1_V008.json'


class StrengthProfileTests(unittest.TestCase):
    def fixture(self):
        owner=fixtures.V006Tests();fixture,_=owner.fixture();self.addCleanup(owner.doCleanups)
        profile=read_json(ROOT/PROFILE)
        profile['input_sha256']=read_json(fixture.root/fixtures.fixtures.pilot.KIT)['shots']['SH903']['sha256']
        fixture.profile_path=PROFILE;write_json(fixture.root/PROFILE,profile)
        return fixture,profile

    def test_real_v008_is_independent_combined_candidate(self):
        a=read_json(ROOT/fixtures.PROFILE);b=read_json(ROOT/PROFILE)
        self.assertEqual(set(a),set(b));self.assertNotIn('temporal_anchor_schedule',b)
        self.assertEqual({k for k in a if a[k]!=b[k]}, {'schema_version','profile_id','hypothesis','anchor_strategy','anchor_rois'})
        self.assertEqual([r['preserve_strength'] for r in b['anchor_rois']],[.55,.55,.65])
        self.assertEqual(b['schema_version'],6)

    def test_prepare_freezes_strength_graph_and_dryrun_rejects_drift(self):
        fixture,profile=self.fixture();fixture.prepare()
        graph=read_json(fixture.root/fixture.out/'workflow.json')
        ident,anchor=next((k,v) for k,v in graph.items() if v['class_type']=='FID1WanStrengthROIAnchor')
        self.assertEqual(json.loads(anchor['inputs']['roi_boxes_json']),profile['anchor_rois'])
        sampler=next(v['inputs'] for v in graph.values() if v['class_type']=='KSampler')
        self.assertEqual(sampler['model'],[ident,0]);self.assertEqual(sampler['latent_image'],[ident,1])
        _,job=job_command(fixture.root,fixture.root/fixture.out,'http://127.0.0.1:8188')
        self.assertEqual(job['trial_profile'],profile)
        graph[ident]['inputs']['temporal_anchor_schedule_json']='[]'
        with self.assertRaises(ValueError):
            validate_graph(graph,job['characters'],fid1_profile=profile)
        profile['anchor_rois'][0]['preserve_strength']=.6
        write_json(fixture.root/PROFILE,profile)
        with self.assertRaises(ValueError):job_command(fixture.root,fixture.root/fixture.out,'http://127.0.0.1:8188')

    def test_strict_strength_profile_and_runtime_ports(self):
        fixture,profile=self.fixture();pilot=fixtures.fixtures.pilot;kit=read_json(fixture.root/pilot.KIT)
        for value in (True,0,1,.2,.81,float('nan'),float('inf'),'0.55'):
            bad=copy.deepcopy(profile);bad['anchor_rois'][0]['preserve_strength']=value
            write_json(fixture.root/PROFILE,bad)
            with self.assertRaises(ValueError):pilot.load_trial_profile(fixture.root,'SH903',kit,PROFILE)
        bad=copy.deepcopy(profile);bad['temporal_anchor_schedule']=[1]*12
        write_json(fixture.root/PROFILE,bad)
        with self.assertRaises(ValueError):pilot.load_trial_profile(fixture.root,'SH903',kit,PROFILE)
        name='FID1WanStrengthROIAnchor'
        info={name:{'input':{'required':{'model':['MODEL'],'latent':['LATENT'],'roi_boxes_json':['STRING']}},'output':['MODEL','LATENT']}}
        self.assertTrue(validate_fid1_object_info(info,name))
        bad=copy.deepcopy(info);bad[name]['input']['required']['temporal_anchor_schedule_json']=['STRING']
        with self.assertRaises(ValueError):validate_fid1_object_info(bad,name)
        with self.assertRaises(ValueError):validate_fid1_object_info({},name)

    def test_no_torch_prepare_and_dryrun_subprocess(self):
        fixture,_=self.fixture()
        code='''import builtins,runpy,sys,pathlib
old=builtins.__import__
def guard(name,*a,**k):
    if name=='torch' or name.startswith('torch.'):raise AssertionError('offline v4 imported torch')
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

    def test_wrong_schema_overlap_and_sampler_bypass_are_refused(self):
        fixture,profile=self.fixture();pilot=fixtures.fixtures.pilot;kit=read_json(fixture.root/pilot.KIT)
        for change in ('schema','strategy','overlap','duplicate','missing'):
            bad=copy.deepcopy(profile)
            if change=='schema':bad['schema_version']=5
            if change=='strategy':bad['anchor_strategy']='wan22_timestep_aware_future_roi_v3'
            if change=='overlap':bad['anchor_rois'][2].update(x0=.12,x1=.30,y0=.21,y1=.32)
            if change=='duplicate':bad['anchor_rois'][2]['id']='WUKONG_FACE'
            if change=='missing':del bad['anchor_rois'][0]['preserve_strength']
            write_json(fixture.root/PROFILE,bad)
            with self.subTest(change=change),self.assertRaises(ValueError):pilot.load_trial_profile(fixture.root,'SH903',kit,PROFILE)
        write_json(fixture.root/PROFILE,profile);fixture.prepare()
        graph=read_json(fixture.root/fixture.out/'workflow.json');job=read_json(fixture.root/fixture.out/'job.json')
        sampler_id=next(k for k,v in graph.items() if v['class_type']=='KSampler')
        for port,edge in (('model',['48',0]),('latent_image',['55',0])):
            bad=copy.deepcopy(graph);bad[sampler_id]['inputs'][port]=edge
            with self.assertRaises(ValueError):validate_graph(bad,job['characters'],fid1_profile=profile)
