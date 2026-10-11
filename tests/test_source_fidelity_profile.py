"""Explicit source-quality experiments retain approval and immutable job gates."""
import inspect
import shutil
import subprocess
import sys
from unittest.mock import patch
from pathlib import Path
from test_git_media_delivery import DeliveryFixture, ROOT
import source_pilot as pilot
from preproduction import read_json, write_json
from submit_prepared import job_command
from sync_repo_media import digest

class FidelityProfileTests(DeliveryFixture):
    def setUp(self):
        super().setUp()
        shutil.copyfile(ROOT/'scripts/source_pilot.py',self.root/'scripts/source_pilot.py')
        self.profile_path='config/source_fidelity_trials/test_profile.json'
        self.out=pilot.LOCAL+'/video/SH903/jobs/quality_take02'

    def profile(self, **updates):
        kit=read_json(self.root/pilot.KIT)
        value=dict(schema_version=1,profile_id='POSE_V2_576',scope=pilot.SCOPE,shot_id='SH903',
                   input_sha256=kit['shots']['SH903']['sha256'],width=576,height=1024,frames=49,fps=24,
                   positive_prompt='The same two subjects hold the exact starting side-profile pose. Locked camera.',
                   negative_prompt='head rotation, identity drift, humanized monkey face, extra person',
                   hypothesis='TEST FIXTURE ONLY: isolate approved-source quality settings, no human approval.')
        value.update(updates);write_json(self.root/self.profile_path,value);return value

    def prepare(self):
        self.assertIn('trial_profile',inspect.signature(pilot.prepare_trial).parameters,
                      'Source pilot cannot freeze an explicit quality profile')
        return pilot.prepare_trial(self.root,'SH903',2026100803,self.out,trial_profile=self.profile_path)

    def test_quality_profile_changes_graph_without_touching_source_plan_or_approvals(self):
        self.approve();profile=self.profile()
        protected={p:digest(self.root/p) for p in [pilot.BASE+'/production_plan_v5.json',*self.protected]}
        self.prepare();job=read_json(self.root/self.out/'job.json');g=read_json(self.root/self.out/'workflow.json')
        latent=next(n['inputs'] for n in g.values() if n['class_type']=='Wan22ImageToVideoLatent')
        self.assertEqual((latent['width'],latent['height'],latent['length']),(576,1024,49))
        sampler=next(n['inputs'] for n in g.values() if n['class_type']=='KSampler')
        self.assertEqual((sampler['steps'],sampler['cfg'],sampler['denoise']),(20,5,1))
        self.assertEqual(g[str(sampler['positive'][0])]['inputs']['text'],profile['positive_prompt'])
        self.assertEqual(job['trial_profile'],profile)
        self.assertEqual(job['purpose'],pilot.SCOPE);self.assertFalse(job['eligible_for_final_cut'])
        self.assertEqual(protected,{p:digest(self.root/p) for p in protected})

    def test_profile_change_invalidates_prepared_job(self):
        self.approve();self.profile();self.prepare()
        job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')
        (self.root/self.profile_path).write_text((self.root/self.profile_path).read_text()+' ')
        with self.assertRaises(ValueError):job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_profile_changed_during_prepare_is_not_published(self):
        self.approve();self.profile()
        original=pilot.prepare
        def change_profile(*args,**kwargs):
            result=original(*args,**kwargs)
            self.profile(positive_prompt='Concurrent different pose prompt')
            return result
        with patch.object(pilot,'prepare',side_effect=change_profile):
            with self.assertRaises(ValueError):self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_wrong_approved_pixels_rejected_without_job(self):
        self.approve();self.profile(input_sha256='0'*64)
        with self.assertRaises(ValueError):self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_duplicate_profile_keys_rejected(self):
        self.approve();self.profile()
        p=self.root/self.profile_path
        p.write_text(p.read_text().replace('"schema_version": 1','"schema_version": 1, "schema_version": 1'))
        with self.assertRaises(ValueError):self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_quality_profile_cannot_change_model_or_frame_budget(self):
        self.approve()
        for update in ({'model':'14B'},{'denoise':0.5},{'frames':81},{'width':704,'height':1248},{'scope':'EP001'}):
            with self.subTest(update=update):
                self.profile(**update)
                with self.assertRaises(ValueError):self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_quality_profile_does_not_bypass_three_explicit_approvals(self):
        self.approve(('SH901','SH902'));self.profile()
        with self.assertRaises(ValueError):self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_existing_quality_job_not_overwritten(self):
        self.approve();self.profile();self.prepare();before=digest(self.root/self.out/'job.json')
        with self.assertRaises(ValueError):self.prepare()
        self.assertEqual(before,digest(self.root/self.out/'job.json'))

    def test_cli_prepares_profile_without_submitting(self):
        self.approve();self.profile()
        p=subprocess.run([sys.executable,str(ROOT/'scripts/source_pilot.py'),'prepare','--root',str(self.root),
                          '--shot','SH903','--seed','2026100803','--out',self.out,'--trial-profile',self.profile_path],
                         capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr+p.stdout)
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())
