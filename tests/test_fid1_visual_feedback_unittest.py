"""Synthetic contract fixtures never write real project approvals or run the GPU."""
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import sys
import textwrap
from unittest.mock import patch

from PIL import Image

ui = importlib.import_module('scripts.fid1_visual_feedback')
qa = importlib.import_module('scripts.fid1_qa_report')


def save(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding='utf-8')


class FeedbackPageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.job_rel = f'local/production/{ui.PROJECT}/video/SH903/jobs/take09'
        self.job_dir = self.root/self.job_rel
        self.job_dir.mkdir(parents=True)
        self.out = ui.SESSIONS+'/SYNTHETIC_ONLY'
        source = self.job_dir/'source.png'
        Image.new('RGB', (16, 28), 'blue').save(source)
        self.source = source
        self.source_sha = ui.sha256_file(source)
        self.output = self.job_dir/'run_record_media'/'synthetic.mp4'
        self.output.parent.mkdir()
        self.output.write_bytes(b'SYNTHETIC CONTRACT FIXTURE; NOT A VIDEO OR HUMAN APPROVAL')
        self.output_sha = ui.sha256_file(self.output)
        (self.job_dir/'qa').mkdir()
        for name in ('first_middle_last.png', 'all49.png'):
            Image.new('RGB', (16, 28), 'blue').save(self.job_dir/'qa'/name)
        decoded = self.job_dir/'qa/all49'
        decoded.mkdir()
        for number in range(1, 50):
            Image.new('RGB', (576, 1024), (number, 0, 0)).save(decoded/f'frame_{number:02d}.png')
        registry_rel = f'local/production/{ui.PROJECT}/reviews/'+'a'*64+'/registry.json'
        refs = {name: {'path': self.job_rel+'/source.png', 'sha256': self.source_sha}
                for name in ('WF','DF','WC','DC')}
        save(self.root/registry_rel, {'assets': refs})
        kit = {'shots': {'SH903': {'bindings': {'identity_refs': {'WUKONG':['WF'], 'DAIYU':['DF']},
                 'costume_refs': {'WUKONG': {'asset_id':'WC'}, 'DAIYU': {'asset_id':'DC'}}}}}}
        save(self.root/ui.KIT, kit)
        save(self.job_dir/'workflow.json', {'SYNTHETIC_ONLY': True})
        self.workflow_sha = ui.sha256_file(self.job_dir/'workflow.json')
        profile = {'profile_id':'SH903_FID1_SYNTHETIC', 'width':576,'height':1024,'frames':49,'fps':24}
        self.job = {'project_id':ui.PROJECT, 'purpose':ui.SCOPE,'eligible_for_final_cut':False,
                    'shot_id':'SH903','seed':2026100803,'input_file':'source.png','input_sha256':self.source_sha,
                    'workflow_sha256':self.workflow_sha,'trial_profile':profile,
                    'fid1_contract':{'schema_version':1,'strategy':'wan22_timestep_aware_future_roi_v2',
                                     'node_class':'FID1WanTimestepAwareROIAnchor'},
                    'sources': {ui.KIT:ui.sha256_file(self.root/ui.KIT),
                                registry_rel:ui.sha256_file(self.root/registry_rel)}}
        save(self.job_dir/'job.json', self.job)
        save(self.job_dir/'job_integrity.json', {'schema_version':1,
             'job_sha256':ui.sha256_file(self.job_dir/'job.json'),
             'workflow_sha256':self.workflow_sha,'input_sha256':self.source_sha})
        save(self.job_dir/'run_record.json', {'result':'success','queued_new_job':True,
             'prompt_id':'SYNTHETIC_ONLY','workflow_sha256':self.workflow_sha,
             'outputs':[{'saved_path':str(self.output),'sha256':self.output_sha,'bytes':self.output.stat().st_size}]})
        self.report = {'schema_version':1,'scope':ui.SCOPE,'shot_id':'SH903',
             'profile_id':profile['profile_id'],'runtime_success':True,'media_contract_ok':True,'full_decode':'PASS',
             'workflow_sha256':self.workflow_sha,'seed':2026100803,
             'input':{'path':'source.png','sha256':self.source_sha},
             'output':{'path':'run_record_media/synthetic.mp4','sha256':self.output_sha,'bytes':self.output.stat().st_size},
             'media':{'width':576,'height':1024,'frame_count':49,'fps':24},
             'frames':{'count':49,'first_middle_last':'qa/first_middle_last.png','all49_contact_sheet':'qa/all49.png'},
             'visual_review':qa.pending_visual_review()}
        save(self.job_dir/'qa/qa_report.json', self.report)

    def build(self):
        return ui.build_review_page(self.root, self.job_rel, self.out)

    def test_default_feedback_is_unselected_and_bound_to_real_job_bytes(self):
        before = {p.relative_to(self.root).as_posix():ui.sha256_file(p) for p in self.job_dir.rglob('*') if p.is_file()}
        result = self.build()
        self.assertEqual(result['default_approvals'], 0)
        page = Path(result['review_page']).read_text(encoding='utf-8')
        self.assertEqual(page.count('<option value="">请选择</option>'), 5)
        self.assertNotIn(' selected', page)
        self.assertNotIn('autoplay', page)
        self.assertIn(self.output_sha, page)
        self.assertEqual(page.count('<figcaption>悟空'), 2)
        receipt = json.loads(Path(result['receipt']).read_text())
        self.assertEqual(receipt['page_sha256'], ui.sha256_file(Path(result['review_page'])))
        self.assertEqual(receipt['sources'][self.job_rel+'/run_record_media/synthetic.mp4'], self.output_sha)
        self.assertEqual(before, {p.relative_to(self.root).as_posix():ui.sha256_file(p) for p in self.job_dir.rglob('*') if p.is_file()})
        self.assertFalse((self.root/'local/review_evidence').exists())

    def test_rejects_existing_page_session(self):
        self.build()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.build()

    def test_review_page_runs_in_subprocess_with_torch_import_blocked(self):
        code=textwrap.dedent('''
            import builtins,sys
            original=builtins.__import__
            def blocked(name,*args,**kwargs):
                if name=='torch' or name.startswith('torch.'):
                    raise ImportError('SYNTHETIC no-Torch contract')
                return original(name,*args,**kwargs)
            builtins.__import__=blocked
            try:import torch
            except ImportError:pass
            else:raise AssertionError('Torch was not blocked')
            from scripts.fid1_visual_feedback import build_review_page
            result=build_review_page(sys.argv[1],sys.argv[2],sys.argv[3])
            assert result['default_approvals']==0 and result['approval_records_changed']==0
        ''')
        result=subprocess.run([sys.executable,'-c',code,str(self.root),self.job_rel,self.out],
                              cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_real_first_middle_last_numbers_and_times_are_sent_to_drawing(self):
        with patch.object(ui, '_contact_sheet', wraps=ui._contact_sheet) as draw:
            result = self.build()
        first, all_frames = draw.call_args_list
        self.assertEqual(first.kwargs['frame_numbers'], [1, 25, 49])
        self.assertEqual(first.kwargs['fps'], 24)
        self.assertEqual([path.name for path in first.args[0]], ['frame_01.png','frame_25.png','frame_49.png'])
        self.assertEqual(all_frames.kwargs['frame_numbers'], list(range(1,50)))
        receipt = json.loads(Path(result['receipt']).read_text())
        mapping = receipt['frames']['first_middle_last']
        self.assertEqual([item['frame_number'] for item in mapping], [1,25,49])
        self.assertEqual([item['time_seconds'] for item in mapping], [0,1,2])
        self.assertEqual(receipt['frames']['output_sha256'], self.output_sha)
        for item in receipt['frames']['source_frames']:
            self.assertEqual(item['sha256'], ui.sha256_file(self.root/item['path']))
        for name, digest in receipt['frames']['derivatives'].items():
            self.assertEqual(digest, ui.sha256_file(Path(result['receipt']).parent/name))
        page = Path(result['review_page']).read_text(encoding='utf-8')
        self.assertIn('实际帧号：1 / 25 / 49', page)
        self.assertIn('帧时间：0 / 1 / 2 秒', page)

    def test_missing_legacy_frames_cpu_decode_verified_video_into_new_session_only(self):
        shutil.rmtree(self.job_dir/'qa/all49')
        before = {p.relative_to(self.root).as_posix():ui.sha256_file(p) for p in self.job_dir.rglob('*') if p.is_file()}
        def decode(command, **kwargs):
            self.assertEqual(Path(command[command.index('-i')+1]), self.output)
            self.assertEqual(ui.sha256_file(self.output), self.output_sha)
            self.assertNotIn('-hwaccel', command)
            target = Path(command[-1]).parent
            for number in range(1,50):
                Image.new('RGB',(576,1024),(number,0,0)).save(target/f'frame_{number:02d}.png')
            return subprocess.CompletedProcess(command,0,'','')
        with patch.object(ui.shutil,'which',return_value='SYNTHETIC_ffmpeg'), patch.object(ui.subprocess,'run',side_effect=decode):
            result = self.build()
        receipt = json.loads(Path(result['receipt']).read_text())
        self.assertEqual(receipt['frames']['origin'],'VERIFIED_MP4_CPU_DECODE')
        for item in receipt['frames']['source_frames']:
            self.assertEqual(item['sha256'],ui.sha256_file(Path(result['receipt']).parent/item['path']))
        self.assertEqual(before,{p.relative_to(self.root).as_posix():ui.sha256_file(p) for p in self.job_dir.rglob('*') if p.is_file()})

    def test_bad_decoded_frame_shape_or_failed_cpu_decode_cannot_publish(self):
        Image.new('RGB',(16,28)).save(self.job_dir/'qa/all49/frame_25.png')
        with self.assertRaisesRegex(ValueError,'dimensions'):
            self.build()
        self.assertFalse((self.root/self.out).exists())
        shutil.rmtree(self.job_dir/'qa/all49')
        with patch.object(ui.shutil,'which',return_value='SYNTHETIC_ffmpeg'), patch.object(ui.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','SYNTHETIC decode failure')):
            with self.assertRaisesRegex(ValueError,'extraction failed'):
                self.build()
        self.assertFalse((self.root/self.out).exists())

    def test_decoded_frame_drift_during_render_cannot_publish(self):
        original = ui.render_feedback_page
        def changed(*args):
            page = original(*args)
            (self.job_dir/'qa/all49/frame_25.png').write_bytes(b'SYNTHETIC FRAME DRIFT')
            return page
        with patch.object(ui,'render_feedback_page',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'changed during'):
                self.build()
        self.assertFalse((self.root/self.out).exists())

    def test_rejects_tampered_output_job_workflow_or_reference(self):
        for target in (self.output, self.job_dir/'job.json', self.job_dir/'workflow.json', self.source):
            raw = target.read_bytes()
            with self.subTest(target=target.name):
                target.write_bytes(raw+b'CHANGED')
                with self.assertRaises((ValueError, json.JSONDecodeError)):
                    self.build()
                self.assertFalse((self.root/self.out).exists())
                target.write_bytes(raw)

    def test_rejects_qa_mismatch_or_preexisting_human_decision(self):
        for key, value in [('seed',1), ('shot_id','SH901'), ('visual_review',{'decision':'ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL'})]:
            with self.subTest(key=key):
                save(self.job_dir/'qa/qa_report.json', {**self.report,key:value})
                with self.assertRaisesRegex(ValueError, 'bound|feedback'):
                    self.build()
        save(self.job_dir/'qa/qa_report.json', self.report)

    def test_rejects_noncanonical_paths_and_other_output_scopes(self):
        for job, out in [(self.job_rel+'/../take09', self.out), (self.job_rel, 'docs/review-output'),
                         (self.job_rel.replace('SH903','SH901'),self.out)]:
            with self.subTest(job=job,out=out), self.assertRaises((ValueError,FileNotFoundError)):
                ui.build_review_page(self.root,job,out)

    def test_material_drift_during_render_prevents_publication(self):
        original=ui.render_feedback_page
        def changed(*args):
            result=original(*args)
            self.source.write_bytes(b'DRIFT DURING GENERATION')
            return result
        with patch.object(ui,'render_feedback_page',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'changed during'):
                self.build()
        self.assertFalse((self.root/self.out).exists())

    @unittest.skipUnless(shutil.which('node'), 'Node runtime unavailable for isolated client contract test')
    def test_client_collects_actual_choices_and_refuses_missing_or_inconsistent_feedback(self):
        result=self.build()
        page=Path(result['review_page']).read_text(encoding='utf-8')
        script=re.search(r'<script>\n(.*?)</script>',page,re.S).group(1)
        fixed={'schema_version':1,'scope':ui.SCOPE,'shot_id':'SH903','profile_id':'SH903_FID1_SYNTHETIC','output_sha256':self.output_sha}
        harness='''const fs=require('fs'),vm=require('vm');const data=JSON.parse(fs.readFileSync(0,'utf8'));
const elements={};for(const field of ['full_playback','identity','costume','limbs','decision','reviewer','user_quote']) elements[field]={value:'',addEventListener(){}};
elements['fixed-review-metadata']={textContent:JSON.stringify(data.fixed)};
for(const id of ['trial-video','play-video','export-feedback','playback-status','feedback-status']) elements[id]={addEventListener(){},play(){return Promise.resolve()}};
global.document={getElementById:id=>elements[id]};vm.runInThisContext(data.script);
let refused=false;try{collectFeedback()}catch(e){refused=true}if(!refused)throw Error('default approved');
for(const key of ['full_playback','identity','costume','limbs'])elements[key].value='PASS';
elements.reviewer.value='Jovi';elements.user_quote.value='SYNTHETIC TEST ONLY: 核验字段';elements.decision.value='ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL';
const result=collectFeedback();if(result.output_sha256!==data.fixed.output_sha256||result.user_quote!==elements.user_quote.value||!result.recorded_at.endsWith('Z'))throw Error('wrong binding');
elements.limbs.value='NOT_RUN';refused=false;try{collectFeedback()}catch(e){refused=true}if(!refused)throw Error('partial accept');
elements.decision.value='CHANGES_REQUIRED';const changes=collectFeedback();if(changes.limbs!=='NOT_RUN')throw Error('criterion altered');
process.stdout.write(JSON.stringify(result));'''
        run=subprocess.run([shutil.which('node'),'-e',harness],input=json.dumps({'fixed':fixed,'script':script}),
                           text=True,capture_output=True,timeout=20)
        self.assertEqual(run.returncode,0,run.stderr)
        exported=json.loads(run.stdout)
        from scripts.fid1_review_contract import validate_visual_review_payload
        self.assertTrue(validate_visual_review_payload(exported,scope=ui.SCOPE,shot_id='SH903',
                        profile_id=fixed['profile_id'],output_sha256=self.output_sha))
