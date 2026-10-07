"""Synthetic approval fixtures below are tests, never actual user approvals."""
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from launch_readiness import report_project, inspect_image
from preproduction import ContractError, sha256_file
from collect_openart_result import inspect_bytes, collect

def evidence(subject,digest,scope):
    return dict(subject_id=subject,sha256=digest,scope=scope,decision='approve',source='SYNTHETIC_UNIT_TEST',user_quote='TEST ONLY NOT REAL USER APPROVAL',recorded_at='2026-10-07T12:00:00+08:00')

class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.project='LOOKREEL01';self.base=self.root/'episodes'/self.project;self.base.mkdir(parents=True)
        self.reg={'schema_version':5,'visual_target_id':'TEST','assets':{}}
        for role in ['face','costume']:
            aid='WUKONG_'+role;p=self.root/f'local/references/{aid}.png';p.parent.mkdir(parents=True,exist_ok=True)
            Image.new('RGB',(640,1136)).save(p);h=sha256_file(p)
            self.reg['assets'][aid]=dict(path=p.relative_to(self.root).as_posix(),sha256=h,character='WUKONG',roles=[role],status='USER_APPROVED',stage_id='DAILY',approval_evidence=evidence(aid,h,'reference'))
        self.plan={'schema_version':5,'project_id':self.project,'visual_target_id':'TEST','fps':24,'total_frames':240,'shots':[]}
        self.ap={'schema_version':5,'project_id':self.project,'visual_target_id':'TEST','shots':{}}
        for i in range(5):
            sid=f'COMP{i+1:02d}'
            shot=dict(shot_id=sid,title=sid,start_frame=i*48,duration_frames=48,characters=['WUKONG'],costume_stages={'WUKONG':'DAILY'},motion_tier='M1' if i<3 else 'M0',render_mode='I2V' if i<3 else 'STILL',motion_prompt='Subtle breathing',i2v={'width':480,'height':832,'frames':49,'fps':24})
            self.plan['shots'].append(shot)
            p=self.root/f'local/production/{self.project}/approved/{sid}.png';p.parent.mkdir(parents=True,exist_ok=True);Image.new('RGB',(640,1136)).save(p);h=sha256_file(p)
            self.ap['shots'][sid]=dict(status='USER_APPROVED',approved_by_user=True,characters=['WUKONG'],approved_keyframe=p.relative_to(self.root).as_posix(),sha256=h,approval_evidence=evidence(sid,h,'keyframe'),identity_refs={'WUKONG':['WUKONG_face']},costume_refs={'WUKONG':{'asset_id':'WUKONG_costume','stage_id':'DAILY'}})
        self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):
        for p,d in [(self.base/'production_plan_v5.json',self.plan),(self.base/'approval_manifest_v5.json',self.ap),(self.root/'assets/registry/generated_assets_v5.json',self.reg)]:
            p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d),encoding='utf-8')
    def report(self):self.save();return report_project(self.root,self.project)
    def change_image(self,sid,data):
        e=self.ap['shots'][sid];p=self.root/e['approved_keyframe'];p.write_bytes(data);e['sha256']=sha256_file(p);e['approval_evidence']['sha256']=e['sha256']
    def test_all_ready_only_means_inputs(self):
        r=self.report();self.assertTrue(r['whole_project_inputs_ready']);self.assertFalse(r['runtime_verified_by_this_tool']);self.assertFalse(r['final_video_approved_by_this_tool'])
    def test_three_inputs_allow_partial_trial(self):
        for sid in ['COMP04','COMP05']:self.ap['shots'][sid]['status']='DRAFT'
        r=self.report();self.assertTrue(r['t1_input_threshold_met']);self.assertFalse(r['whole_project_inputs_ready']);self.assertEqual(r['launch_state'],'PARTIAL_T1_INPUTS_READY')
    def test_missing_static_not_hidden(self):
        (self.root/self.ap['shots']['COMP05']['approved_keyframe']).unlink();r=self.report();self.assertFalse(r['whole_project_inputs_ready']);self.assertIn('COMP05',r['approved_files_not_received'])
    def test_two_inputs_not_three(self):
        self.ap['shots']['COMP03']['approved_by_user']=False;self.assertFalse(self.report()['t1_input_threshold_met'])
    def test_missing_reference_detected(self):
        (self.root/self.reg['assets']['WUKONG_face']['path']).unlink();r=self.report();self.assertIn('WUKONG_face',r['reference_files_missing_or_changed']);self.assertEqual(r['ready_input_count'],0)
    def test_changed_reference_detected(self):
        (self.root/self.reg['assets']['WUKONG_face']['path']).write_bytes(b'changed');self.assertEqual(self.report()['ready_input_count'],0)
    def test_counterfeit_png_decoded_not_just_extension(self):
        self.change_image('COMP01',b'not a PNG');self.assertFalse(self.report()['shots'][0]['input_valid'])
    def test_landscape_board_rejected(self):
        b=io.BytesIO();Image.new('RGB',(1536,1024)).save(b,format='PNG');self.change_image('COMP01',b.getvalue());self.assertFalse(self.report()['shots'][0]['input_valid'])
    def test_low_resolution_rejected(self):
        b=io.BytesIO();Image.new('RGB',(180,320)).save(b,format='PNG');self.change_image('COMP01',b.getvalue());self.assertFalse(self.report()['shots'][0]['input_valid'])
    def test_approval_wrong_scope(self):
        self.ap['shots']['COMP01']['approval_evidence']['scope']='reference';self.assertFalse(self.report()['shots'][0]['input_valid'])
    def test_approval_wrong_hash(self):
        self.ap['shots']['COMP01']['approval_evidence']['sha256']='0'*64;self.assertFalse(self.report()['shots'][0]['input_valid'])
    def test_wrong_costume_does_not_pass(self):
        self.ap['shots']['COMP01']['costume_refs']['WUKONG']['stage_id']='FORMAL';self.assertFalse(self.report()['shots'][0]['input_valid'])
    def test_cast_only_checks_present_character(self):
        self.assertEqual(self.report()['ready_input_count'],5)
    def test_no_side_effects(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};report_project(self.root,self.project);self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_unknown_project_rejected(self):
        with self.assertRaises(ContractError):report_project(self.root,'../OTHER')
    def test_manifest_mismatch(self):
        self.ap['shots'].pop('COMP05');self.save()
        with self.assertRaises(ContractError):report_project(self.root,self.project)
    def test_all_still_still_requires_assets(self):
        for s in self.plan['shots']:s.update(render_mode='STILL',motion_tier='M0')
        r=self.report();self.assertTrue(r['whole_project_inputs_ready']);self.assertFalse(r['t1_input_threshold_met'])
    def test_cli_threshold_exit(self):
        self.ap['shots']['COMP05']['status']='DRAFT';self.save()
        p=subprocess.run([sys.executable,str(ROOT/'scripts/launch_readiness.py'),'--root',str(self.root),'--project',self.project,'--require','whole-project-inputs'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertFalse(json.loads(p.stdout)['projects'][0]['whole_project_inputs_ready'])
    def test_cli_can_report_expected_gaps_without_crashing(self):
        self.ap['shots']['COMP01']['status']='DRAFT';self.save()
        p=subprocess.run([sys.executable,str(ROOT/'scripts/launch_readiness.py'),'--root',str(self.root),'--project',self.project],capture_output=True,text=True);self.assertEqual(p.returncode,0)

class ProviderCollectorTests(unittest.TestCase):
    def test_metadata_default_no_download(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'never-created';r=collect(p);self.assertFalse(p.exists());self.assertFalse(r['bytes_received']);self.assertEqual(r['new_credits_spent_by_this_script'],0)
    def test_actual_format_not_provider_label(self):
        b=io.BytesIO();Image.new('RGB',(768,1376)).save(b,format='WEBP');self.assertEqual(inspect_bytes(b.getvalue())['actual_format'],'WEBP')
    def test_invalid_bytes_rejected(self):
        for b in [b'',b'no image']:
            with self.assertRaises(Exception):inspect_bytes(b)
    def test_decoding_does_not_prove_single_scene(self):
        b=io.BytesIO();Image.new('RGB',(768,1376)).save(b,format='PNG');self.assertFalse(inspect_bytes(b.getvalue())['layout_semantically_reviewed'])

from prepare_t1_trial import trial

class TrialTests(unittest.TestCase):
    def setUp(self):
        self.f=LaunchTests();self.f.setUp();self.root=self.f.root
        dst=self.root/'workflows/video/production/VID_wan22_5b_i2v_prod_v001.json';dst.parent.mkdir(parents=True)
        dst.write_bytes((ROOT/'workflows/video/production/VID_wan22_5b_i2v_prod_v001.json').read_bytes())
    def tearDown(self):self.f.tearDown()
    def run_trial(self,frames=49):
        return trial(self.root,'LOOKREEL01','COMP01',frames,2026100701,'local/production/LOOKREEL01/video/COMP01/jobs/T1_TEST')
    def test_short_trial_not_full_cut(self):
        r=self.run_trial();self.assertEqual(r['purpose'],'T1_ONLY');self.assertFalse(r['eligible_for_final_cut']);self.assertAlmostEqual(r['trial_seconds'],49/24)
    def test_original_plan_and_approval_unchanged(self):
        paths=[self.f.base/'production_plan_v5.json',self.f.base/'approval_manifest_v5.json'];before=[x.read_bytes() for x in paths];self.run_trial();self.assertEqual(before,[x.read_bytes() for x in paths])
    def test_actual_frozen_graph_shortened(self):
        self.run_trial(33);g=json.loads((self.root/'local/production/LOOKREEL01/video/COMP01/jobs/T1_TEST/workflow.json').read_text());self.assertEqual(g['55']['inputs']['length'],33);self.assertIn('t1_only',g['58']['inputs']['filename_prefix'])
    def test_invalid_frames_rejected(self):
        with self.assertRaises(ContractError):self.run_trial(50)
    def test_unapproved_input_blocked(self):
        self.f.ap['shots']['COMP01']['approved_by_user']=False;self.f.save()
        with self.assertRaises(ContractError):self.run_trial()
        self.assertFalse((self.root/'local/production/LOOKREEL01/video/COMP01/jobs/T1_TEST').exists())
    def test_existing_job_not_overwritten(self):
        self.run_trial()
        with self.assertRaises(ContractError):self.run_trial()
    def test_static_shot_not_sent_to_t1(self):
        with self.assertRaises(ContractError):trial(self.root,'LOOKREEL01','COMP05',49,2,'local/production/LOOKREEL01/video/COMP05/jobs/t1')
    def test_old_validator_also_catches_missing_static(self):
        self.f.ap['shots']['COMP05']['status']='DRAFT';self.f.save()
        p=subprocess.run([sys.executable,str(ROOT/'scripts/validate_production_package.py'),'--root',str(self.root),'--project-dir','episodes/LOOKREEL01','--require-ready'],capture_output=True,text=True)
        r=json.loads(p.stdout);self.assertEqual(len(r['ready']),3);self.assertFalse(r['production_ready']);self.assertEqual(p.returncode,2)

if __name__=='__main__':unittest.main()
