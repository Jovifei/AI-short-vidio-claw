"""Offline regression tests. Synthetic fixture approvals are not production approvals."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from preproduction import *
from approve_asset import approve_keyframe, approve_reference
from import_reference_bundle import import_bundle
from submit_prepared import job_command


def evidence(subject, digest, scope='reference'):
    return {'subject_id':subject, 'sha256':digest, 'scope':scope, 'decision':'approve',
            'source':'SYNTHETIC_TEST_ONLY', 'user_quote':'TEST FIXTURE NOT USER APPROVAL',
            'recorded_at':'2026-10-06T10:00:00+08:00'}


class Contracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        s = copy.deepcopy(read_json(ROOT/'episodes/EP001/production_plan_v5.json')['shots'][1])
        s.update(shot_id='SH001', start_frame=0, duration_frames=48)
        s['i2v']['frames']=49
        self.plan={'schema_version':5,'project_id':'EPTEST','visual_target_id':'TEST','fps':24,'total_frames':48,'shots':[s]}
        self.graph=read_json(ROOT/'workflows/video/production/VID_wan22_5b_i2v_prod_v001.json')
        rel='local/production/EPTEST/approved/SH001.png'
        p=self.root/rel;p.parent.mkdir(parents=True);p.write_bytes(b'fixture image bytes')
        digest=sha256_file(p)
        self.registry={'schema_version':5,'visual_target_id':'TEST','assets':{}}
        identities={};costumes={}
        for char in s['characters']:
            for role in ('face','costume'):
                aid=f'{char}_{role}';rp=f'local/references/{aid}.png'
                ap=self.root/rp;ap.parent.mkdir(parents=True,exist_ok=True);ap.write_bytes(aid.encode())
                h=sha256_file(ap)
                self.registry['assets'][aid]={'path':rp,'sha256':h,'character':char,'roles':[role],
                    'stage_id':s['costume_stages'][char] if role=='costume' else None,
                    'status':'USER_APPROVED','approval_evidence':evidence(aid,h)}
            identities[char]=[f'{char}_face']
            costumes[char]={'asset_id':f'{char}_costume','stage_id':s['costume_stages'][char]}
        entry={'characters':s['characters'][:],'status':'USER_APPROVED','approved_by_user':True,
               'approved_keyframe':rel,'sha256':digest,'approval_evidence':evidence('SH001',digest,'keyframe'),
               'identity_refs':identities,'costume_refs':costumes}
        self.manifest={'schema_version':5,'project_id':'EPTEST','visual_target_id':'TEST','shots':{'SH001':entry}}

    def tearDown(self):self.tmp.cleanup()
    def valid(self):return validate_keyframe(self.root,self.plan,self.manifest,self.registry,'SH001')
    def fail(self):
        with self.assertRaises(ContractError):self.valid()
    def test_valid_dual(self):self.valid()
    def test_single_character_is_valid_without_other_character_refs(self):
        s=self.plan['shots'][0];s['characters']=['WUKONG'];s['costume_stages'].pop('DAIYU')
        e=self.manifest['shots']['SH001'];e['characters']=['WUKONG'];e['identity_refs'].pop('DAIYU');e['costume_refs'].pop('DAIYU')
        self.valid()
    def test_draft_blocked(self):self.manifest['shots']['SH001']['status']='DRAFT';self.fail()
    def test_false_user_approval(self):self.manifest['shots']['SH001']['approved_by_user']=False;self.fail()
    def test_string_true_rejected(self):self.manifest['shots']['SH001']['approved_by_user']='true';self.fail()
    def test_asset_changed(self):
        (self.root/self.manifest['shots']['SH001']['approved_keyframe']).write_bytes(b'changed');self.fail()
    def test_missing_keyframe(self):
        (self.root/self.manifest['shots']['SH001']['approved_keyframe']).unlink();self.fail()
    def test_candidate_dir_rejected_even_with_hash(self):
        e=self.manifest['shots']['SH001'];old=self.root/e['approved_keyframe'];new=self.root/'local/production/EPTEST/candidates/SH001.png'
        new.parent.mkdir();new.write_bytes(old.read_bytes());e['approved_keyframe']=str(new.relative_to(self.root));self.fail()
    def test_missing_face(self):self.manifest['shots']['SH001']['identity_refs']['DAIYU']=[];self.fail()
    def test_ref_id_not_in_registry(self):self.manifest['shots']['SH001']['identity_refs']['DAIYU']=['invented'];self.fail()
    def test_ref_wrong_character(self):self.registry['assets']['DAIYU_face']['character']='WUKONG';self.fail()
    def test_ref_wrong_role(self):self.registry['assets']['DAIYU_face']['roles']=['design_board'];self.fail()
    def test_ref_draft(self):self.registry['assets']['DAIYU_face']['status']='CANDIDATE';self.fail()
    def test_ref_changed(self):
        (self.root/self.registry['assets']['DAIYU_face']['path']).write_bytes(b'changed');self.fail()
    def test_wrong_costume(self):self.manifest['shots']['SH001']['costume_refs']['DAIYU']['stage_id']='WRONG';self.fail()
    def test_wrong_target(self):self.registry['visual_target_id']='old';self.fail()
    def test_wrong_project(self):self.manifest['project_id']='OTHER';self.fail()
    def test_wrong_cast(self):self.manifest['shots']['SH001']['characters']=['WUKONG'];self.fail()
    def test_missing_evidence(self):self.manifest['shots']['SH001']['approval_evidence']=None;self.fail()
    def test_general_approval_not_specific(self):self.manifest['shots']['SH001']['approval_evidence']['subject_id']='STYLE';self.fail()
    def test_wrong_approval_hash(self):self.manifest['shots']['SH001']['approval_evidence']['sha256']='0'*64;self.fail()
    def test_no_timezone(self):self.manifest['shots']['SH001']['approval_evidence']['recorded_at']='2026-10-06T01:00:00';self.fail()
    def test_workflow_valid(self):validate_graph(self.graph,['DAIYU','WUKONG'])
    def test_no_start_image(self):
        del self.graph['55']['inputs']['start_image']
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_unused_image_does_not_prove_i2v(self):
        self.graph['3']['inputs']['latent_image']=['55',1]
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_wrong_save_chain(self):
        self.graph['58']['inputs']['video']=['8',0]
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_loadimage_mask_output_rejected(self):
        self.graph['55']['inputs']['start_image']=['56',1]
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_unknown_node(self):
        self.graph['100']={'class_type':'UnknownScript','inputs':{}}
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_14b_rejected(self):
        self.graph['37']['inputs']['unet_name']='14B.safetensors'
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_wrong_vae_rejected(self):
        self.graph['39']['inputs']['vae_name']='wan_2.1_vae.safetensors'
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_dual_negative_exclusion(self):
        self.graph['7']['inputs']['text']='no second person, 人脸'
        with self.assertRaises(ContractError):validate_graph(self.graph,['DAIYU','WUKONG'])
    def test_subway_prompt_rejected(self):
        self.graph['6']['inputs']['text']='1970 subway musician'
        with self.assertRaises(ContractError):validate_graph(self.graph,['WUKONG'])
    def test_m0_not_queued(self):
        self.plan['shots'][0].update(render_mode='STILL',motion_tier='M0')
        q=queue(self.root,self.plan,self.manifest,self.registry);self.assertEqual(q['ready'],[]);self.assertEqual(q['static'],['SH001'])
    def test_m3_i2v_invalid(self):
        self.plan['shots'][0]['motion_tier']='M3'
        with self.assertRaises(ContractError):check_plan(self.plan)
    def test_queue_requires_hash_verification(self):
        self.manifest['shots']['SH001']['sha256']='f'*64
        q=queue(self.root,self.plan,self.manifest,self.registry);self.assertEqual(len(q['blocked']),1)
    def test_bad_resolution(self):
        self.plan['shots'][0]['i2v']['width']=481
        with self.assertRaises(ContractError):check_plan(self.plan)
    def test_bad_source_frames(self):
        self.plan['shots'][0]['i2v']['frames']=50
        with self.assertRaises(ContractError):check_plan(self.plan)
    def test_source_too_short(self):
        self.plan['shots'][0]['duration_frames']=72;self.plan['total_frames']=72
        with self.assertRaises(ContractError):check_plan(self.plan)
    def test_timeline_gap(self):
        self.plan['shots'][0]['start_frame']=1
        with self.assertRaises(ContractError):check_plan(self.plan)
    def test_timeline_total(self):
        self.plan['total_frames']=49
        with self.assertRaises(ContractError):check_plan(self.plan)
    def test_path_traversals(self):
        for path in ['../foo','/etc/passwd','C:\\images\\x.png','\\\\server\\x.png','local/../x.png','local/a.png:stream']:
            with self.subTest(path=path),self.assertRaises(ContractError):relative_file(self.root,path)
    def test_duplicate_json_key(self):
        p=self.root/'dupe.json';p.write_text('{"shots": {}, "shots": {}}')
        with self.assertRaises(ContractError):read_json(p)
    def test_prepare_is_offline_immutable(self):
        for n,v in [('plan',self.plan),('approval',self.manifest),('registry',self.registry),('workflow',self.graph)]:write_json(self.root/f'{n}.json',v)
        out=self.root/'local/production/EPTEST/video/SH001/jobs/t01'
        packet=prepare(self.root,*[self.root/f'{n}.json' for n in ['plan','approval','registry','workflow']],'SH001',42,out)
        self.assertEqual(packet['status'],'PREPARED_NOT_SUBMITTED')
        prepared=read_json(out/'workflow.json');self.assertEqual(prepared['3']['inputs']['seed'],42)
        self.assertEqual(prepared['55']['inputs']['length'],49)
        with self.assertRaises(ContractError):prepare(self.root,*[self.root/f'{n}.json' for n in ['plan','approval','registry','workflow']],'SH001',42,out)
    def test_approve_no_partial_write_on_missing_bindings(self):
        before=copy.deepcopy(self.manifest);e=before['shots']['SH001'];e['status']='DRAFT'
        original=copy.deepcopy(before)
        with self.assertRaises(ContractError):approve_keyframe(self.root,self.plan,before,self.registry,'SH001',e['approved_keyframe'],{},e['approval_evidence'])
        self.assertEqual(before,original)
    def test_reference_board_not_face_approval(self):
        self.registry['assets']['DAIYU_face']['roles']=['design_board']
        with self.assertRaises(ContractError):approve_reference(self.root,self.registry,'DAIYU_face',self.registry['assets']['DAIYU_face']['approval_evidence'])
    def test_import_idempotent(self):
        self.assertEqual(import_bundle(self.root,self.root,self.registry)['imported'],0)
    def test_import_preflights_all_before_write(self):
        target=self.root/'target';target.mkdir()
        (self.root/self.registry['assets']['WUKONG_costume']['path']).unlink()
        with self.assertRaises(ContractError):import_bundle(self.root,target,self.registry)
        self.assertEqual(list(target.iterdir()),[])
    def test_local_endpoint_only(self):
        with self.assertRaises(ContractError):job_command(self.root,self.root/'local/production/job','https://example.com')


class ProductionData(unittest.TestCase):
    def test_ep001_exact_60s(self):
        p=read_json(ROOT/'episodes/EP001/production_plan_v5.json')
        self.assertEqual(check_plan(p)['frames'],1440)
        self.assertEqual(sum(s['render_mode']=='I2V' for s in p['shots']),6)
    def test_lookreel_exact_27s(self):
        p=read_json(ROOT/'episodes/LOOKREEL01/production_plan_v5.json')
        self.assertEqual(check_plan(p)['frames'],648)
        self.assertEqual(sum(s['render_mode']=='I2V' for s in p['shots']),4)
    def test_committed_approvals_are_draft(self):
        for project in ('EP001','LOOKREEL01'):
            m=read_json(ROOT/f'episodes/{project}/approval_manifest_v5.json')
            self.assertTrue(all(s['status']=='DRAFT' and s['approved_by_user'] is False for s in m['shots'].values()))
    def test_actual_assets_candidate_and_unique(self):
        r=read_json(ROOT/'assets/registry/generated_assets_v5.json')
        self.assertEqual(len(r['assets']),17)
        self.assertTrue(all(s['status']=='CANDIDATE' for s in r['assets'].values()))
        self.assertEqual(len({a['path'] for a in r['assets'].values()}),17)
    def test_subtitle_cues_in_bounds(self):
        c=read_json(ROOT/'episodes/EP001/audio_cues_v5.json')['dialogue']
        for e in c:self.assertTrue(0<=e['start_frame']<e['end_frame']<=1440)

if __name__=='__main__':unittest.main()
