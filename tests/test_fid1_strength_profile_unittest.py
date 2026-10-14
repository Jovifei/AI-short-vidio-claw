"""Offline v4 strength profile/graph tests; no real trial or human approval."""
import copy
import hashlib
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw
from test_git_media_delivery import ROOT
import test_fid1_v006_unittest as fixtures
from preproduction import read_json, write_json, validate_graph
from fid1_geometry_gate import verify_geometry_evidence
import submit_prepared
from submit_prepared import job_command, validate_fid1_object_info

PROFILE='config/source_fidelity_trials/SH903_FID1_V008.json'


def profile_eol_hashes(raw):
    lf=raw.replace(b'\r\n',b'\n')
    crlf=lf.replace(b'\n',b'\r\n')
    return {'LF':hashlib.sha256(lf).hexdigest(),'CRLF':hashlib.sha256(crlf).hexdigest()}


class StrengthProfileTests(unittest.TestCase):
    def install_synthetic_geometry(self, fixture, profile, status='LOCAL_GEOMETRY_PASS'):
        kit=read_json(fixture.root/fixtures.fixtures.pilot.KIT)
        source_rel=kit['shots']['SH903']['repo_path']
        source_path=fixture.root/source_rel
        geometry_rel='docs/reviews/SYNTHETIC_FIXTURE/SH903_V008_geometry.json'
        overlay_rel='docs/reviews/SYNTHETIC_FIXTURE/SH903_V008_overlay.png'
        geometry_path=fixture.root/geometry_rel
        overlay_path=fixture.root/overlay_rel
        geometry_path.parent.mkdir(parents=True,exist_ok=True)
        overlay_path.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(source_path) as source:
            image=source.convert('RGB')
        draw=ImageDraw.Draw(image)
        width,height=image.size
        latent_width,latent_height=profile['width']//16,profile['height']//16
        mapping=[]
        for roi in profile['anchor_rois']:
            x0,y0,x1,y1=(roi[k] for k in ('x0','y0','x1','y1'))
            mapping.append({
                'id':roi['id'],
                'latent_xyxy':[math.floor(x0*latent_width),math.floor(y0*latent_height),
                               math.ceil(x1*latent_width),math.ceil(y1*latent_height)],
                'feather':roi['feather_latent'],
                'strength':roi['preserve_strength'],
            })
            draw.rectangle((int(x0*width),int(y0*height),int(x1*width),int(y1*height)),outline='red',width=2)
        image.save(overlay_path,format='PNG')
        source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()
        profile_eols=profile_eol_hashes((fixture.root/PROFILE).read_bytes())
        roi_sha=hashlib.sha256(json.dumps(profile['anchor_rois'],sort_keys=True,separators=(',',':'),
                                         ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()
        geometry={
            'source_path':source_rel,
            'source_sha256':source_sha,
            'source_size':[width,height],
            'latent_size':[latent_width,latent_height],
            'geometry_mapping':mapping,
            'human_acceptance':False,
            'review':status,
            'local_observation':'SYNTHETIC_FIXTURE_ONLY; generated rectangles exercise geometry binding.',
            'candidate_prepare':'SYNTHETIC_FIXTURE_ONLY',
        }
        write_json(geometry_path,geometry)
        entry={
            'profile_id':profile['profile_id'],
            'profile_path':PROFILE,
            'profile_byte_sha256':profile_eols,
            'source_type':'SYNTHETIC_FIXTURE',
            'source_path':source_rel,
            'source_sha256':source_sha,
            'canonical_roi_sha256':roi_sha,
            'status':status,
            'review_layer':'INPUT_GEOMETRY_ONLY',
            'observer':'TEST_FIXTURE_ONLY',
            'human_accepted':False,
            'geometry_path':geometry_rel,
            'geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),
            'overlay_path':overlay_rel,
            'overlay_sha256':hashlib.sha256(overlay_path.read_bytes()).hexdigest(),
        }
        write_json(fixture.root/'config/source_fidelity_trials/geometry_manifest.json',
                   {'schema_version':1,'entries':[entry]})
        return entry

    def reject_prepare_without_output_dir(self, fixture):
        destination=fixture.root/fixture.out
        with self.assertRaises(ValueError):
            fixture.prepare()
        self.assertFalse(destination.exists())
        self.assertFalse(destination.parent.exists())

    def fixture(self):
        owner=fixtures.V006Tests();fixture,_=owner.fixture();self.addCleanup(owner.doCleanups)
        profile=read_json(ROOT/PROFILE)
        profile['input_sha256']=read_json(fixture.root/fixtures.fixtures.pilot.KIT)['shots']['SH903']['sha256']
        fixture.profile_path=PROFILE;write_json(fixture.root/PROFILE,profile)
        self.install_synthetic_geometry(fixture,profile)
        return fixture,profile

    def test_real_v008_is_independent_combined_candidate(self):
        a=read_json(ROOT/fixtures.PROFILE);b=read_json(ROOT/PROFILE)
        self.assertEqual(set(a),set(b));self.assertNotIn('temporal_anchor_schedule',b)
        self.assertEqual({k for k in a if a[k]!=b[k]}, {'schema_version','profile_id','hypothesis','anchor_strategy','anchor_rois'})
        self.assertEqual([r['preserve_strength'] for r in b['anchor_rois']],[.55,.55,.65])
        self.assertEqual(b['schema_version'],6)

    def test_committed_v008_geometry_evidence_is_blocked_and_hash_bound(self):
        profile=read_json(ROOT/PROFILE)
        source_path='assets/media/source_library/REFB02_01.png'
        with self.assertRaisesRegex(ValueError,'GEOMETRY_BLOCKED|geometry evidence is blocked'):
            verify_geometry_evidence(ROOT,PROFILE,profile,source_path)

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

    def test_missing_unknown_and_blocked_geometry_refuse_before_staging(self):
        fixture,_=self.fixture()
        (fixture.root/'config/source_fidelity_trials/geometry_manifest.json').unlink()
        self.reject_prepare_without_output_dir(fixture)

        fixture,_=self.fixture()
        manifest_path=fixture.root/'config/source_fidelity_trials/geometry_manifest.json'
        manifest=read_json(manifest_path);manifest['entries'][0]['status']='GEOMETRY_PENDING'
        write_json(manifest_path,manifest)
        self.reject_prepare_without_output_dir(fixture)

        fixture,profile=self.fixture()
        self.install_synthetic_geometry(fixture,profile,status='GEOMETRY_BLOCKED')
        self.reject_prepare_without_output_dir(fixture)

    def test_geometry_manifest_schema_and_missing_entry_fail_closed(self):
        mutations=(
            lambda m: m['entries'].clear(),
            lambda m: m['entries'][0].pop('overlay_sha256'),
            lambda m: m['entries'][0].update(unreviewed_override=True),
            lambda m: m['entries'][0].update(observer='TEST_FIXTURE_ONLY',source_type='REAL_SOURCE'),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                fixture,_=self.fixture()
                manifest_path=fixture.root/'config/source_fidelity_trials/geometry_manifest.json'
                manifest=read_json(manifest_path);mutate(manifest);write_json(manifest_path,manifest)
                self.reject_prepare_without_output_dir(fixture)

    def test_profile_source_roi_evidence_and_path_drift_fail_closed(self):
        scenarios=('profile','profile_raw_byte','profile_mixed_eol','source_hash','roi_hash','geometry_hash','overlay_hash','path_escape',
                   'geometry_mapping','source_size','overlay_size')
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                fixture,profile=self.fixture()
                manifest_path=fixture.root/'config/source_fidelity_trials/geometry_manifest.json'
                manifest=read_json(manifest_path);entry=manifest['entries'][0]
                if scenario=='profile':
                    profile['positive_prompt']+=' changed'
                    write_json(fixture.root/PROFILE,profile)
                elif scenario=='profile_raw_byte':
                    profile_file=fixture.root/PROFILE
                    raw=profile_file.read_bytes()
                    profile_file.write_bytes(raw.replace(b': ',b':  ',1))
                elif scenario=='profile_mixed_eol':
                    profile_file=fixture.root/PROFILE
                    lf=profile_file.read_bytes().replace(b'\r\n',b'\n')
                    profile_file.write_bytes(lf.replace(b'\n',b'\r\n',1))
                elif scenario=='source_hash':
                    entry['source_sha256']='0'*64
                    write_json(manifest_path,manifest)
                elif scenario=='roi_hash':
                    entry['canonical_roi_sha256']='0'*64
                    write_json(manifest_path,manifest)
                elif scenario=='geometry_hash':
                    geometry_path=fixture.root/entry['geometry_path']
                    geometry=read_json(geometry_path);geometry['local_observation']+=' changed'
                    write_json(geometry_path,geometry)
                elif scenario=='overlay_hash':
                    (fixture.root/entry['overlay_path']).write_bytes(b'changed overlay bytes')
                elif scenario=='path_escape':
                    entry['overlay_path']='../../outside.png'
                    write_json(manifest_path,manifest)
                elif scenario=='geometry_mapping':
                    geometry_path=fixture.root/entry['geometry_path']
                    geometry=read_json(geometry_path);geometry['geometry_mapping'][0]['latent_xyxy'][0]+=1
                    write_json(geometry_path,geometry)
                    entry['geometry_sha256']=hashlib.sha256(geometry_path.read_bytes()).hexdigest()
                    write_json(manifest_path,manifest)
                elif scenario=='source_size':
                    geometry_path=fixture.root/entry['geometry_path']
                    geometry=read_json(geometry_path);geometry['source_size'][0]+=1
                    write_json(geometry_path,geometry)
                    entry['geometry_sha256']=hashlib.sha256(geometry_path.read_bytes()).hexdigest()
                    write_json(manifest_path,manifest)
                elif scenario=='overlay_size':
                    overlay_path=fixture.root/entry['overlay_path']
                    Image.new('RGB',(10,10),'white').save(overlay_path,format='PNG')
                    entry['overlay_sha256']=hashlib.sha256(overlay_path.read_bytes()).hexdigest()
                    write_json(manifest_path,manifest)
                self.reject_prepare_without_output_dir(fixture)

    def test_profile_lf_and_crlf_registered_forms_are_accepted(self):
        for label in ('LF','CRLF'):
            with self.subTest(line_endings=label):
                fixture,_=self.fixture()
                profile_file=fixture.root/PROFILE
                lf=profile_file.read_bytes().replace(b'\r\n',b'\n')
                profile_bytes=lf if label=='LF' else lf.replace(b'\n',b'\r\n')
                profile_file.write_bytes(profile_bytes)
                fixture.prepare()
                job=read_json(fixture.root/fixture.out/'job.json')
                receipt=job['fid1_contract']['geometry_receipt']
                self.assertEqual(receipt['profile_sha256'],hashlib.sha256(profile_bytes).hexdigest())
                self.assertEqual(receipt['profile_byte_sha256'],profile_eol_hashes(profile_bytes))
                self.assertEqual(job['sources'][PROFILE],receipt['profile_sha256'])

    def test_geometry_receipt_drift_is_rechecked_by_submit(self):
        fixture,_=self.fixture();fixture.prepare()
        job_path=fixture.root/fixture.out/'job.json';job=read_json(job_path)
        receipt=job['fid1_contract']['geometry_receipt']
        self.assertEqual(receipt['source_type'],'SYNTHETIC_FIXTURE')
        self.assertEqual(receipt['status'],'LOCAL_GEOMETRY_PASS')
        self.assertEqual(receipt['profile_byte_sha256'],profile_eol_hashes((fixture.root/PROFILE).read_bytes()))
        self.assertFalse(receipt['human_accepted'])
        self.assertEqual(receipt['review_layer'],'INPUT_GEOMETRY_ONLY')
        self.assertNotIn('user_quote',receipt);self.assertNotIn('reviewer',receipt)
        receipt['canonical_roi_sha256']='0'*64
        fixture.reseal_job(job)
        with self.assertRaisesRegex(ValueError,'geometry receipt'):
            job_command(fixture.root,fixture.root/fixture.out,'http://127.0.0.1:8188')
        self.assertFalse((fixture.root/fixture.out/'submission_intent.json').exists())

    def test_geometry_evidence_is_rechecked_before_staged_job_publish(self):
        fixture,_=self.fixture();pilot=fixtures.fixtures.pilot
        original=pilot.prepare
        def drift_geometry(*args,**kwargs):
            result=original(*args,**kwargs)
            manifest=read_json(fixture.root/'config/source_fidelity_trials/geometry_manifest.json')
            geometry_path=fixture.root/manifest['entries'][0]['geometry_path']
            geometry=read_json(geometry_path);geometry['local_observation']+=' changed during prepare'
            write_json(geometry_path,geometry)
            return result
        with patch.object(pilot,'prepare',side_effect=drift_geometry):
            with self.assertRaisesRegex(ValueError,'geometry JSON hash|geometry evidence changed'):
                fixture.prepare()
        self.assertFalse((fixture.root/fixture.out).exists())
        self.assertFalse((fixture.root/fixture.out/'submission_intent.json').exists())

    def test_synthetic_geometry_fixture_cannot_execute_or_create_attempt_marker(self):
        fixture,_=self.fixture();fixture.prepare()
        with patch.object(sys,'argv',['submit_prepared.py','--root',str(fixture.root),
                '--job-dir',fixture.out,'--url','http://127.0.0.1:8188','--comfy-root',str(fixture.root),'--execute']), \
             patch.object(submit_prepared,'urlopen') as network, \
             patch.object(submit_prepared.subprocess,'run') as post:
            self.assertEqual(submit_prepared.main(),2)
        network.assert_not_called();post.assert_not_called()
        self.assertFalse((fixture.root/fixture.out/'submission_intent.json').exists())
        self.assertFalse((fixture.root/fixture.out/'run_record.json').exists())

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
