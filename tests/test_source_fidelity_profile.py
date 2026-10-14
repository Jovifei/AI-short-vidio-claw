"""Explicit source-quality experiments retain approval and immutable job gates."""
import inspect
import json
import shutil
import subprocess
import sys
import textwrap
from unittest.mock import patch
from pathlib import Path
from test_git_media_delivery import DeliveryFixture, ROOT
import source_pilot as pilot
from preproduction import read_json, write_json
from submit_prepared import job_command
from sync_repo_media import digest
from test_fid1_predecessor_unittest import completed_predecessor_fixture

class FidelityProfileTests(DeliveryFixture):
    def setUp(self):
        super().setUp()
        shutil.copyfile(ROOT/'scripts/source_pilot.py',self.root/'scripts/source_pilot.py')
        for rel in ('scripts/approve_asset.py','scripts/sync_repo_media.py','scripts/preproduction.py','scripts/fid1_graph_audit.py','scripts/fid1_wan_latent_anchor_node.py',
                    'scripts/submit_prepared.py','scripts/p1_comfy_probe.py','scripts/fid1_deploy.py',
                    'scripts/fid1_qa_report.py',
                    'scripts/fid1_predecessor.py','scripts/fid1_review_contract.py','scripts/fid1_job_paths.py',
                    'docs/reviews/20261011-source-fidelity/installed_comfy_source/source_manifest.json'):
            target=self.root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,target)
        self.profile_path='config/source_fidelity_trials/test_profile.json'
        self.out=pilot.LOCAL+'/video/SH903/jobs/take02'

    def profile(self, **updates):
        kit=read_json(self.root/pilot.KIT)
        value=dict(schema_version=1,profile_id='POSE_V2_576',scope=pilot.SCOPE,shot_id='SH903',
                   input_sha256=kit['shots']['SH903']['sha256'],width=576,height=1024,frames=49,fps=24,
                   positive_prompt='The same two subjects hold the exact starting side-profile pose. Locked camera.',
                   negative_prompt='head rotation, identity drift, humanized monkey face, extra person',
                   hypothesis='TEST FIXTURE ONLY: isolate approved-source quality settings, no human approval.')
        value.update(updates);write_json(self.root/self.profile_path,value);return value

    def fid1_profile(self):
        return self.profile(schema_version=2,profile_id='SH903_FID1_TEST_V2',
            seed=2026100803,
            anchor_strategy='wan22_first_latent_future_roi_v1',
            anchor_rois=[{'id':'WUKONG_FACE','x0':0.14,'y0':0.20,'x1':0.29,'y1':0.31},
                         {'id':'DAIYU_FACE','x0':0.72,'y0':0.20,'x1':0.85,'y1':0.31}])

    def prepare(self):
        self.assertIn('trial_profile',inspect.signature(pilot.prepare_trial).parameters,
                      'Source pilot cannot freeze an explicit quality profile')
        return pilot.prepare_trial(self.root,'SH903',2026100803,self.out,trial_profile=self.profile_path)

    def reseal_job(self, job):
        job_path=self.root/self.out/'job.json'
        write_json(job_path,job)
        write_json(self.root/self.out/'job_integrity.json',{
            'schema_version':1,
            'job_sha256':digest(job_path),
            'workflow_sha256':job['workflow_sha256'],
            'input_sha256':job['input_sha256'],
        })

    def downstream_fixture(self):
        self.approve()
        kit=read_json(self.root/pilot.KIT)
        self.profile_path='config/source_fidelity_trials/SH901_FID1_TEST_V2.json'
        self.profile(schema_version=2,profile_id='SH901_FID1_TEST_V2',shot_id='SH901',
                     input_sha256=kit['shots']['SH901']['sha256'],seed=2026100801,
                     anchor_strategy='wan22_first_latent_future_roi_v1',
                     anchor_rois=[{'id':'WUKONG_FACE','x0':0.31,'y0':0.20,'x1':0.53,'y1':0.41},
                                  {'id':'DAIYU_FACE','x0':0.60,'y0':0.25,'x1':0.84,'y1':0.45}])
        self.out=pilot.LOCAL+'/video/SH901/jobs/take02'
        return completed_predecessor_fixture(self.root)

    def test_predecessor_changed_during_prepare_is_not_published(self):
        previous_rel=self.downstream_fixture()
        original=pilot.prepare
        def drift_predecessor(*args,**kwargs):
            result=original(*args,**kwargs)
            path=self.root/previous_rel/'run_record.json'
            path.write_bytes(path.read_bytes()+b' ')
            return result
        with patch.object(pilot,'prepare',side_effect=drift_predecessor):
            with self.assertRaisesRegex(ValueError,'predecessor receipt changed'):
                pilot.prepare_trial(self.root,'SH901',2026100801,self.out,self.profile_path,previous_rel)
        self.assertFalse((self.root/self.out).exists())

    def test_resealed_downstream_job_cannot_tamper_predecessor_receipt(self):
        previous_rel=self.downstream_fixture()
        pilot.prepare_trial(self.root,'SH901',2026100801,self.out,self.profile_path,previous_rel)
        job=read_json(self.root/self.out/'job.json')
        job['fid1_contract']['predecessor']['prompt_id']='fabricated prompt'
        self.reseal_job(job)
        with self.assertRaisesRegex(ValueError,'predecessor receipt changed'):
            job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_legacy_downstream_job_fails_closed_without_overwriting_it(self):
        previous_rel=self.downstream_fixture()
        pilot.prepare_trial(self.root,'SH901',2026100801,self.out,self.profile_path,previous_rel)
        job=read_json(self.root/self.out/'job.json')
        job['fid1_contract']['schema_version']=1
        del job['fid1_contract']['predecessor']
        self.reseal_job(job)
        before=digest(self.root/self.out/'job.json')
        with self.assertRaisesRegex(ValueError,'legacy downstream|new take'):
            job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')
        self.assertEqual(digest(self.root/self.out/'job.json'),before)

    def test_legacy_sh903_contract_remains_valid(self):
        self.approve();self.fid1_profile();self.prepare()
        job=read_json(self.root/self.out/'job.json')
        job['fid1_contract']['schema_version']=1
        del job['fid1_contract']['predecessor']
        self.reseal_job(job)
        job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_execute_checks_predecessor_again_under_lock_before_attempt_marker(self):
        import submit_prepared
        previous_rel=self.downstream_fixture()
        pilot.prepare_trial(self.root,'SH901',2026100801,self.out,self.profile_path,previous_rel)
        real=submit_prepared.job_command
        calls=[]
        def drift_after_first_check(*args,**kwargs):
            result=real(*args,**kwargs); calls.append(True)
            if len(calls)==1:
                path=self.root/previous_rel/'run_record.json'
                path.write_bytes(path.read_bytes()+b' ')
            return result
        with patch.object(sys,'argv',['submit_prepared.py','--root',str(self.root),'--job-dir',self.out,
                                      '--url','http://127.0.0.1:8188','--comfy-root',str(self.root),'--execute']), \
             patch.object(submit_prepared,'job_command',side_effect=drift_after_first_check), \
             patch.object(submit_prepared,'validate_fid1_runtime') as runtime, \
             patch.object(submit_prepared.subprocess,'run') as execute:
            self.assertEqual(submit_prepared.main(),2)
            runtime.assert_not_called();execute.assert_not_called()
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())
        self.assertFalse((self.root/self.out/'run_record.json').exists())
        self.assertFalse((self.root/'local/production/.gpu_submission.lock').exists())

    def test_execute_rechecks_predecessor_after_network_runtime_checks(self):
        import submit_prepared
        previous_rel=self.downstream_fixture()
        pilot.prepare_trial(self.root,'SH901',2026100801,self.out,self.profile_path,previous_rel)
        def drift_during_runtime(*args,**kwargs):
            path=self.root/previous_rel/'run_record.json'
            path.write_bytes(path.read_bytes()+b' ')
            return {'test_fixture_runtime':'no network or GPU was used'}
        with patch.object(sys,'argv',['submit_prepared.py','--root',str(self.root),'--job-dir',self.out,
                                      '--url','http://127.0.0.1:8188','--comfy-root',str(self.root),'--execute']), \
             patch.object(submit_prepared,'validate_fid1_runtime',side_effect=drift_during_runtime) as runtime, \
             patch.object(submit_prepared.subprocess,'run') as execute:
            self.assertEqual(submit_prepared.main(),2)
            runtime.assert_called_once();execute.assert_not_called()
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())
        self.assertFalse((self.root/self.out/'run_record.json').exists())
        self.assertFalse((self.root/'local/production/.gpu_submission.lock').exists())

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

    def test_fid1_profile_interposes_node_and_keeps_trial_scope(self):
        self.approve();profile=self.fid1_profile()
        result=self.prepare()
        self.assertTrue(result['prepared'])
        job=read_json(self.root/self.out/'job.json');graph=read_json(self.root/self.out/'workflow.json')
        fid1=[(node_id,node) for node_id,node in graph.items() if node['class_type']=='FID1WanSourceROIAnchor']
        self.assertEqual(len(fid1),1)
        fid1_id,node=fid1[0]
        sampler=next((node_id,node) for node_id,node in graph.items() if node['class_type']=='KSampler')
        self.assertEqual(node['inputs']['latent'],['55',0])
        self.assertEqual(sampler[1]['inputs']['latent_image'],[fid1_id,0])
        self.assertEqual(json.loads(node['inputs']['roi_boxes_json']),profile['anchor_rois'])
        self.assertEqual(job['purpose'],pilot.SCOPE)
        self.assertFalse(job['eligible_for_final_cut'])
        self.assertEqual(job['fid1_contract']['strategy'],'wan22_first_latent_future_roi_v1')
        job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_fid1_soft_profile_is_serialized_through_prepare_and_submit(self):
        self.approve();profile=self.profile(schema_version=3,profile_id='SH903_FID1_SOFT_TEST_V3',seed=2026100803,
            anchor_strategy='wan22_first_latent_future_roi_v1',
            anchor_rois=[{'id':'WUKONG_FACE','x0':0.14,'y0':0.20,'x1':0.29,'y1':0.31,'feather_latent':4},
                         {'id':'DAIYU_FACE','x0':0.72,'y0':0.20,'x1':0.85,'y1':0.31,'feather_latent':4}])
        result=self.prepare()
        self.assertTrue(result['prepared'])
        job=read_json(self.root/self.out/'job.json');graph=read_json(self.root/self.out/'workflow.json')
        anchor=next(node for node in graph.values() if node['class_type']=='FID1WanSourceROIAnchor')
        self.assertEqual(json.loads(anchor['inputs']['roi_boxes_json']),profile['anchor_rois'])
        self.assertEqual(job['trial_profile'],profile)
        _,command_job=job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')
        self.assertEqual(command_job['trial_profile'],profile)
        self.assertEqual(command_job['status'],'PREPARED_NOT_SUBMITTED')

    def test_fid1_timestep_aware_profile_wires_model_and_latent_through_prepare_and_submit(self):
        self.approve();profile=self.profile(schema_version=4,profile_id='SH903_FID1_TIME_TEST_V005',seed=2026100803,
            anchor_strategy='wan22_timestep_aware_future_roi_v2',
            anchor_rois=[{'id':'WUKONG_FACE','x0':0.14,'y0':0.20,'x1':0.29,'y1':0.31,'feather_latent':4},
                         {'id':'DAIYU_FACE','x0':0.72,'y0':0.20,'x1':0.85,'y1':0.31,'feather_latent':4}])
        result=self.prepare()
        self.assertTrue(result['prepared'])
        job=read_json(self.root/self.out/'job.json');graph=read_json(self.root/self.out/'workflow.json')
        fid1_id,node=next((node_id,node) for node_id,node in graph.items()
                          if node['class_type']=='FID1WanTimestepAwareROIAnchor')
        sampler=next(node for node in graph.values() if node['class_type']=='KSampler')
        self.assertEqual(node['inputs']['model'],['48',0])
        self.assertEqual(node['inputs']['latent'],['55',0])
        self.assertEqual(sampler['inputs']['model'],[fid1_id,0])
        self.assertEqual(sampler['inputs']['latent_image'],[fid1_id,1])
        self.assertEqual(job['fid1_contract']['strategy'],'wan22_timestep_aware_future_roi_v2')
        self.assertEqual(job['fid1_contract']['node_class'],'FID1WanTimestepAwareROIAnchor')
        _,command_job=job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')
        self.assertEqual(command_job['fid1_contract'],job['fid1_contract'])

    def test_fid1_soft_profile_rejects_invalid_feather_before_job(self):
        self.approve();self.profile(schema_version=3,profile_id='SH903_FID1_BAD_FEATHER_TEST_V3',seed=2026100803,
            anchor_strategy='wan22_first_latent_future_roi_v1',
            anchor_rois=[{'id':'WUKONG_FACE','x0':0.14,'y0':0.20,'x1':0.29,'y1':0.31,'feather_latent':5},
                         {'id':'DAIYU_FACE','x0':0.72,'y0':0.20,'x1':0.85,'y1':0.31,'feather_latent':4}])
        with self.assertRaisesRegex(ValueError,'feather_latent'):
            self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_fid1_prepare_records_integrity_for_the_immutable_job_manifest(self):
        self.approve();self.fid1_profile();self.prepare()
        job_path=self.root/self.out/'job.json'
        integrity_path=self.root/self.out/'job_integrity.json'
        self.assertTrue(integrity_path.is_file(),'FID1 prepared jobs need a separate immutable-manifest digest')
        integrity=read_json(integrity_path)
        self.assertEqual(integrity['schema_version'],1)
        self.assertEqual(integrity['job_sha256'],digest(job_path))
        self.assertEqual(integrity['workflow_sha256'],read_json(job_path)['workflow_sha256'])
        self.assertEqual(integrity['input_sha256'],read_json(job_path)['input_sha256'])

    def test_fid1_offline_prepare_succeeds_when_torch_is_unavailable(self):
        self.approve();self.fid1_profile()
        code=textwrap.dedent('''
            import builtins, sys
            original = builtins.__import__
            def no_torch(name, *args, **kwargs):
                if name == "torch" or name.startswith("torch."):
                    raise ImportError("Torch intentionally unavailable for offline-prepare test")
                return original(name, *args, **kwargs)
            builtins.__import__ = no_torch
            root, out, seed, profile = sys.argv[1:]
            sys.path.insert(0, root + "/scripts")
            import source_pilot
            result = source_pilot.prepare_trial(root, "SH903", int(seed), out, trial_profile=profile)
            assert result["prepared"] and not result["submitted"]
        ''')
        result=subprocess.run([sys.executable,'-c',code,str(self.root),self.out,'2026100803',self.profile_path],
                              cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())

    def test_v005_offline_prepare_succeeds_when_torch_is_unavailable(self):
        self.approve();self.profile(schema_version=4,profile_id='SH903_FID1_OFFLINE_V005',seed=2026100803,
            anchor_strategy='wan22_timestep_aware_future_roi_v2',
            anchor_rois=[{'id':'WUKONG_FACE','x0':0.14,'y0':0.20,'x1':0.29,'y1':0.31,'feather_latent':4},
                         {'id':'DAIYU_FACE','x0':0.72,'y0':0.20,'x1':0.85,'y1':0.31,'feather_latent':4}])
        code=textwrap.dedent('''
            import builtins, sys
            original = builtins.__import__
            def no_torch(name, *args, **kwargs):
                if name == "torch" or name.startswith("torch."):
                    raise ImportError("Torch intentionally unavailable for offline-prepare test")
                return original(name, *args, **kwargs)
            builtins.__import__ = no_torch
            root, out, seed, profile = sys.argv[1:]
            sys.path.insert(0, root + "/scripts")
            import source_pilot
            result = source_pilot.prepare_trial(root, "SH903", int(seed), out, trial_profile=profile)
            assert result["prepared"] and not result["submitted"]
        ''')
        result=subprocess.run([sys.executable,'-c',code,str(self.root),self.out,'2026100803',self.profile_path],
                              cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())

    def test_downstream_prepare_and_dry_run_need_no_torch(self):
        previous_rel=self.downstream_fixture()
        profile=read_json(self.root/self.profile_path)
        profile.update(schema_version=4,anchor_strategy='wan22_timestep_aware_future_roi_v2')
        for roi in profile['anchor_rois']:roi['feather_latent']=4
        write_json(self.root/self.profile_path,profile)
        code=textwrap.dedent('''
            import builtins, pathlib, sys
            original = builtins.__import__
            def no_torch(name, *args, **kwargs):
                if name == "torch" or name.startswith("torch."):
                    raise ImportError("Torch intentionally unavailable for downstream test")
                return original(name, *args, **kwargs)
            builtins.__import__ = no_torch
            root, out, profile, predecessor = sys.argv[1:]
            sys.path.insert(0, root + "/scripts")
            import source_pilot, submit_prepared
            result = source_pilot.prepare_trial(root, "SH901", 2026100801, out,
                                               trial_profile=profile, previous_job=predecessor)
            assert result["prepared"] and not result["submitted"]
            command, job = submit_prepared.job_command(root, pathlib.Path(root) / out,
                                                       "http://127.0.0.1:8188")
            assert job["fid1_contract"]["predecessor"]["job_dir"] == predecessor
        ''')
        result=subprocess.run([sys.executable,'-c',code,str(self.root),self.out,self.profile_path,previous_rel],
                              cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())
        self.assertFalse((self.root/self.out/'run_record.json').exists())

    def test_fid1_implementation_drift_during_prepare_is_not_published(self):
        self.approve();self.fid1_profile()
        original=pilot.prepare
        def drift_dependency(*args,**kwargs):
            result=original(*args,**kwargs)
            node=self.root/'scripts/fid1_wan_latent_anchor_node.py'
            node.write_text(node.read_text()+'\n# changed during prepare\n')
            return result
        with patch.object(pilot,'prepare',side_effect=drift_dependency):
            with self.assertRaisesRegex(ValueError,'dependency|implementation|changed|drift'):
                self.prepare()
        self.assertFalse((self.root/self.out).exists())

    def test_sh901_requires_explicit_accepted_previous_job(self):
        self.approve()
        kit=read_json(self.root/pilot.KIT)
        profile_path='config/source_fidelity_trials/SH901_FID1_TEST_V2.json'
        profile=self.profile(schema_version=2,profile_id='SH901_FID1_TEST_V2',shot_id='SH901',
                             input_sha256=kit['shots']['SH901']['sha256'],seed=2026100801,
                             anchor_strategy='wan22_first_latent_future_roi_v1',
                             anchor_rois=[{'id':'WUKONG_FACE','x0':0.31,'y0':0.20,'x1':0.53,'y1':0.41},
                                          {'id':'DAIYU_FACE','x0':0.60,'y0':0.25,'x1':0.84,'y1':0.45}])
        write_json(self.root/profile_path,profile)
        with self.assertRaisesRegex(ValueError,'SH903|visual|review|accept'):
            pilot.prepare_trial(self.root,'SH901',2026100801,pilot.LOCAL+'/video/SH901/jobs/take02',profile_path)

    def test_sh901_opens_only_after_hash_bound_review_of_selected_take09(self):
        self.approve()
        kit=read_json(self.root/pilot.KIT)
        profile_path='config/source_fidelity_trials/SH901_FID1_TEST_V2.json'
        profile=self.profile(schema_version=2,profile_id='SH901_FID1_TEST_V2',shot_id='SH901',
                             input_sha256=kit['shots']['SH901']['sha256'],seed=2026100801,
                             anchor_strategy='wan22_first_latent_future_roi_v1',
                             anchor_rois=[{'id':'WUKONG_FACE','x0':0.31,'y0':0.20,'x1':0.53,'y1':0.41},
                                          {'id':'DAIYU_FACE','x0':0.60,'y0':0.25,'x1':0.84,'y1':0.45}])
        write_json(self.root/profile_path,profile)

        previous_rel=completed_predecessor_fixture(self.root)
        output_path=self.root/previous_rel/'run_record_media/fixture.mp4'
        destination=pilot.LOCAL+'/video/SH901/jobs/take02'
        result=pilot.prepare_trial(self.root,'SH901',2026100801,destination,profile_path,previous_rel)
        self.assertTrue(result['prepared'])
        job=read_json(self.root/destination/'job.json')
        self.assertEqual(job['fid1_contract']['schema_version'],2)
        self.assertEqual(job['fid1_contract']['predecessor']['job_dir'],previous_rel)
        self.assertTrue(all(job['sources'][rel]==sha for rel,sha in job['fid1_contract']['predecessor']['files'].items()))
        job_command(self.root,self.root/destination,'http://127.0.0.1:8188')
        output_path.write_bytes(b'changed after review')
        with self.assertRaises(ValueError):
            job_command(self.root,self.root/destination,'http://127.0.0.1:8188')
        with self.assertRaises(ValueError):
            pilot.prepare_trial(self.root,'SH901',2026100801,pilot.LOCAL+'/video/SH901/jobs/take03',profile_path,previous_rel)

    def test_submit_rejects_sampler_bypass_even_with_updated_workflow_hash(self):
        self.approve();self.fid1_profile();self.prepare()
        workflow_path=self.root/self.out/'workflow.json';graph=read_json(workflow_path)
        sampler=next(node for node in graph.values() if node['class_type']=='KSampler')
        sampler['inputs']['latent_image']=['55',0]
        write_json(workflow_path,graph)
        job_path=self.root/self.out/'job.json';job=read_json(job_path)
        job['workflow_sha256']=digest(workflow_path);self.reseal_job(job)
        with self.assertRaisesRegex(ValueError,'latent_image|connection|FID1'):
            job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_submit_rejects_fid1_dependency_manifest_rewrite(self):
        self.approve();self.fid1_profile();self.prepare()
        node_path=self.root/'scripts/fid1_wan_latent_anchor_node.py'
        node_path.write_text(node_path.read_text()+'\n')
        job_path=self.root/self.out/'job.json';job=read_json(job_path)
        job['sources']['scripts/fid1_wan_latent_anchor_node.py']=digest(node_path)
        self.reseal_job(job)
        with self.assertRaisesRegex(ValueError,'dependency|fid1|source'):
            job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_submit_rejects_seed_rewrite_even_when_graph_and_job_match(self):
        self.approve();profile=self.fid1_profile();self.prepare()
        workflow_path=self.root/self.out/'workflow.json';graph=read_json(workflow_path)
        sampler=next(node for node in graph.values() if node['class_type']=='KSampler')
        sampler['inputs']['seed']=1
        write_json(workflow_path,graph)
        job_path=self.root/self.out/'job.json';job=read_json(job_path)
        job['seed']=1;job['workflow_sha256']=digest(workflow_path);self.reseal_job(job)
        with self.assertRaisesRegex(ValueError,'seed|profile'):
            job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')

    def test_fid1_execute_requires_verified_comfy_root_before_attempt_marker(self):
        self.approve();self.fid1_profile();self.prepare()
        result=subprocess.run([sys.executable,str(ROOT/'scripts/submit_prepared.py'),'--root',str(self.root),
                               '--job-dir',self.out,'--url','http://127.0.0.1:8188','--execute'],
                              cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertIn('--comfy-root is required',result.stdout)
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())

    def test_new_fid1_prepare_refuses_noncanonical_or_wrong_shot_before_creation(self):
        self.approve();self.fid1_profile()
        for out in (pilot.LOCAL+'/video/SH903/jobs/quality_take02',
                    pilot.LOCAL+'/video/SH902/jobs/take02',
                    pilot.LOCAL+'/video/SH903/jobs/take02/../take03'):
            with self.subTest(out=out),self.assertRaises(ValueError):
                pilot.prepare_trial(self.root,'SH903',2026100803,out,self.profile_path)
            self.assertFalse((self.root/out).exists())

    def test_submit_refuses_moved_schema2_job_even_if_integrity_still_matches(self):
        self.approve();self.fid1_profile();self.prepare()
        moved=self.root/pilot.LOCAL/'video/SH902/jobs/take88';moved.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(self.root/self.out,moved)
        with self.assertRaisesRegex(ValueError,'canonical|shot|path'):
            job_command(self.root,moved,'http://127.0.0.1:8188')
        self.assertFalse((moved/'submission_intent.json').exists())

    def test_temporal_v3_profile_prepares_frozen_schedule_and_uses_both_sampler_ports(self):
        self.approve()
        profile=read_json(ROOT/'config/source_fidelity_trials/SH903_FID1_V007.json')
        profile['input_sha256']=read_json(self.root/pilot.KIT)['shots']['SH903']['sha256']
        write_json(self.root/self.profile_path,profile)
        self.prepare()
        graph=read_json(self.root/self.out/'workflow.json')
        anchor_id,anchor=next((k,v) for k,v in graph.items() if v['class_type']=='FID1WanTemporalROIAnchor')
        sampler=next(n['inputs'] for n in graph.values() if n['class_type']=='KSampler')
        self.assertEqual(sampler['model'],[anchor_id,0])
        self.assertEqual(sampler['latent_image'],[anchor_id,1])
        self.assertEqual(json.loads(anchor['inputs']['temporal_anchor_schedule_json']),profile['temporal_anchor_schedule'])
        _,job=job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')
        self.assertEqual(job['fid1_contract']['node_class'],'FID1WanTemporalROIAnchor')
        self.assertEqual(job['trial_profile'],profile)

    def test_temporal_schedule_invalidates_existing_prepared_job_without_resubmission(self):
        self.approve()
        profile=read_json(ROOT/'config/source_fidelity_trials/SH903_FID1_V007.json')
        profile['input_sha256']=read_json(self.root/pilot.KIT)['shots']['SH903']['sha256']
        write_json(self.root/self.profile_path,profile);self.prepare()
        profile['temporal_anchor_schedule']=[1]*12
        write_json(self.root/self.profile_path,profile)
        with self.assertRaises(ValueError):job_command(self.root,self.root/self.out,'http://127.0.0.1:8188')
        self.assertFalse((self.root/self.out/'submission_intent.json').exists())
