"""Offline delivery and isolated source-pilot tests; approvals are fixtures only."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import sync_repo_media as sync
import source_pilot as pilot
from preproduction import read_json, write_json, check_plan, validate_keyframe
from submit_prepared import job_command

class DeliveryFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        media=read_json(ROOT/sync.MANIFEST);reg=read_json(ROOT/'assets/registry/generated_assets_v5.json')
        kit=read_json(ROOT/pilot.KIT);pr=read_json(ROOT/pilot.BASE/'reference_registry_candidate.json')
        for i,a in enumerate(media['assets']):
            p=self.root/a['repo_path'];p.parent.mkdir(parents=True,exist_ok=True)
            Image.new('RGB',(800,1424),(i*7%256,i*11%256,i*13%256)).save(p)
            a.update(sha256=sync.digest(p),bytes=p.stat().st_size,width=800,height=1424)
            aid=a['asset_id']
            if aid in reg['assets']:reg['assets'][aid].update(sha256=a['sha256'],bytes=a['bytes'],width=800,height=1424)
            if aid in pr['assets']:pr['assets'][aid].update(sha256=a['sha256'],bytes=a['bytes'],width=800,height=1424)
            for s in kit['shots'].values():
                if s['source_asset']==aid:s['sha256']=a['sha256']
        write_json(self.root/sync.MANIFEST,media);write_json(self.root/'assets/registry/generated_assets_v5.json',reg)
        for name,value in [('source_kit.json',kit),('reference_registry_candidate.json',pr)]:write_json(self.root/pilot.BASE/name,value)
        for rel in [pilot.BASE+'/production_plan_v5.json',pilot.BASE+'/approval_manifest_v5.json','workflows/video/production/VID_wan22_5b_i2v_prod_v001.json','episodes/EP001/approval_manifest_v5.json','episodes/LOOKREEL01/approval_manifest_v5.json']:
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
        (self.root/'scripts').mkdir();(self.root/'scripts/p1_comfy_probe.py').write_text('# fixture-only probe; never executed\n')
        self.protected={p:sync.digest(self.root/p) for p in ['assets/registry/generated_assets_v5.json','episodes/EP001/approval_manifest_v5.json','episodes/LOOKREEL01/approval_manifest_v5.json']}
    def tearDown(self):self.tmp.cleanup()
    def synced(self):sync.run(self.root,apply=True)
    def feedback(self,ids=('SH901','SH902','SH903')):
        kit,_,_,bundle=pilot.inputs(self.root)
        return dict(scope=pilot.SCOPE,bundle_sha256=bundle,items=[dict(shot_id=s,sha256=kit['shots'][s]['sha256'],decision='approve_trial',scope=pilot.SCOPE,user_quote=pilot.LABEL,notes='TEST FIXTURE ONLY, NOT HUMAN APPROVAL',recorded_at=datetime.now(timezone.utc).isoformat()) for s in ids])
    def approve(self,ids=('SH901','SH902','SH903')):
        self.synced();f=self.root/'test_feedback.json';write_json(f,self.feedback(ids));return pilot.apply_review(self.root,f,True)

class TestGitMediaSync(DeliveryFixture):
    def test_dry_run_no_local(self):
        r=sync.run(self.root);self.assertEqual(r['repo_files'],32);self.assertFalse((self.root/'local').exists())
    def test_first_import_32(self):
        r=sync.run(self.root,True);self.assertEqual(r['copied'],32);self.assertFalse(r['network_used']);self.assertFalse(r['production_ready'])
    def test_repeat_no_write(self):
        self.synced();r=sync.run(self.root,True);self.assertEqual(r['copied'],0);self.assertEqual(r['already_present'],32)
    def test_check_requires_local(self):
        with self.assertRaises(ValueError):sync.run(self.root,check=True)
    def test_check_after_sync(self):
        self.synced();self.assertEqual(sync.run(self.root,check=True)['missing_local'],0)
    def test_last_source_corrupt_no_write(self):
        d=read_json(self.root/sync.MANIFEST);(self.root/d['assets'][-1]['repo_path']).write_bytes(b'broken')
        with self.assertRaises(ValueError):self.synced()
        self.assertFalse((self.root/'local').exists())
    def test_missing_source_not_downloaded(self):
        d=read_json(self.root/sync.MANIFEST);(self.root/d['assets'][-1]['repo_path']).unlink()
        with self.assertRaises(ValueError):self.synced()
    def test_local_conflict_preserved(self):
        d=read_json(self.root/sync.MANIFEST);p=self.root/d['assets'][-1]['local_path'];p.parent.mkdir(parents=True);p.write_bytes(b'USER FILE')
        with self.assertRaises(ValueError):self.synced()
        self.assertEqual(p.read_bytes(),b'USER FILE')
    def test_approvals_untouched(self):
        self.synced();self.assertEqual(self.protected,{p:sync.digest(self.root/p) for p in self.protected})
    def test_duplicate_entry(self):
        d=read_json(self.root/sync.MANIFEST);d['assets'].append(d['assets'][0]);write_json(self.root/sync.MANIFEST,d)
        with self.assertRaises(ValueError):self.synced()
    def test_symlink_rejected(self):
        outside=self.root/'outside';outside.mkdir()
        try:(self.root/'local').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('symlinks not permitted')
        with self.assertRaises(ValueError):self.synced()
        self.assertEqual(list(outside.iterdir()),[])
    def test_windows_paths_rejected(self):
        for rel in ['C:/bad','../x','local/NUL.png','local/a:stream','local/x.','local/x\\y']:
            with self.assertRaises(ValueError):sync.safe(self.root,rel)
    def test_lock_not_deleted_by_other_writer(self):
        p=self.root/'local';p.mkdir();(p/'.git-media-sync.lock').write_text('other')
        with self.assertRaises(FileExistsError):self.synced()
        self.assertTrue((p/'.git-media-sync.lock').exists())
    def test_registry_mismatch(self):
        d=read_json(self.root/'assets/registry/generated_assets_v5.json');d['assets']['MODEL_DAIYU']['sha256']='0'*64;write_json(self.root/'assets/registry/generated_assets_v5.json',d)
        with self.assertRaises(ValueError):self.synced()

class TestSourcePilot(DeliveryFixture):
    def test_plan_valid_and_isolated(self):
        p=read_json(self.root/pilot.BASE/'production_plan_v5.json');check_plan(p);self.assertEqual(p['project_id'],'T1_SOURCE_PILOT');self.assertEqual(p['total_frames'],147)
    def test_review_default_unapproved(self):
        self.synced();r=pilot.review(self.root);s=Path(r['review_page']).read_text();self.assertEqual(s.count('type="checkbox"'),3);self.assertNotIn(' checked',s);self.assertFalse((self.root/pilot.POINTER).exists())
    def test_apply_dry_no_approval(self):
        self.synced();f=self.root/'feedback.json';write_json(f,self.feedback());r=pilot.apply_review(self.root,f);self.assertEqual(r['mode'],'DRY_RUN');self.assertFalse((self.root/pilot.POINTER).exists())
    def test_wrong_scope_rejected(self):
        self.synced();f=self.feedback();f['scope']='EP001'
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_other_shot_rejected(self):
        self.synced();f=self.feedback();f['items'][0]['shot_id']='SH001'
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_other_pixels_rejected(self):
        self.synced();f=self.feedback();f['items'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_duplicate_choices_rejected(self):
        self.synced();f=self.feedback();f['items'][1]=deepcopy(f['items'][0])
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_no_choices_rejected(self):
        self.synced();f=self.feedback();f['items']=[]
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_direction_not_specific_approval(self):
        self.synced();f=self.feedback();f['items'][0]['user_quote']='感觉可以'
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_missing_reference_blocks(self):
        self.synced();reg=read_json(self.root/pilot.BASE/'reference_registry_candidate.json');(self.root/next(iter(reg['assets'].values()))['path']).unlink()
        with self.assertRaises(ValueError):pilot.review(self.root)
    def test_naive_time_rejected(self):
        self.synced();f=self.feedback();f['items'][0]['recorded_at']='2026-10-08T12:00:00'
        with self.assertRaises(ValueError):pilot.choices(self.root,f)
    def test_original30_unchanged_after_pilot_approval(self):
        self.approve();self.assertEqual(self.protected,{p:sync.digest(self.root/p) for p in self.protected})
    def test_all_three_prepare(self):
        self.approve();r=pilot.prepare_trial(self.root,'SH901',42,pilot.LOCAL+'/video/SH901/jobs/take01');self.assertTrue(r['prepared']);self.assertFalse(r['submitted']);self.assertFalse(r['eligible_for_final_cut'])
    def test_only_two_cannot_prepare(self):
        self.approve(('SH901','SH902'))
        with self.assertRaises(ValueError):pilot.prepare_trial(self.root,'SH901',42,pilot.LOCAL+'/video/SH901/jobs/take01')
    def test_unapproved_cannot_prepare(self):
        self.synced()
        with self.assertRaises(ValueError):pilot.prepare_trial(self.root,'SH901',42,pilot.LOCAL+'/video/SH901/jobs/take01')
    def test_modified_snapshot_rejected(self):
        self.approve();p=read_json(self.root/pilot.POINTER);s=self.root/p['snapshot']/'registry.json';s.write_text(s.read_text()+' ')
        with self.assertRaises(ValueError):pilot.prepare_trial(self.root,'SH901',42,pilot.LOCAL+'/video/SH901/jobs/take01')
    def test_output_not_overwritten(self):
        self.approve();out=pilot.LOCAL+'/video/SH901/jobs/take01';pilot.prepare_trial(self.root,'SH901',42,out)
        with self.assertRaises(ValueError):pilot.prepare_trial(self.root,'SH901',43,out)
    def test_prepared_uses_existing_probe_without_execution(self):
        self.approve();out=pilot.LOCAL+'/video/SH901/jobs/take01';pilot.prepare_trial(self.root,'SH901',42,out)
        command,job=job_command(self.root,self.root/out,'http://127.0.0.1:8188');self.assertIn('--image',command);self.assertEqual(job['purpose'],'T1_SOURCE_ONLY');self.assertFalse((self.root/out/'submission_intent.json').exists())
    def test_review_pointer_changes_invalidate_job(self):
        self.approve();out=pilot.LOCAL+'/video/SH901/jobs/take01';pilot.prepare_trial(self.root,'SH901',42,out);p=self.root/pilot.POINTER;p.write_text(p.read_text()+' ')
        with self.assertRaises(ValueError):job_command(self.root,self.root/out,'http://127.0.0.1:8188')
    def test_changed_plan_invalidates_exported_feedback(self):
        self.synced();f=self.feedback();p=self.root/pilot.BASE/'production_plan_v5.json';p.write_text(p.read_text()+' ')
        with self.assertRaises(ValueError):pilot.choices(self.root,f)

if __name__=='__main__':unittest.main()
