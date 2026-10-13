"""CPU-only fixtures: none of these review payloads represents a user decision."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_git_media_delivery import ROOT  # Adds the existing scripts directory to sys.path.
from preproduction import read_json, write_json
from sync_repo_media import digest
import fid1_predecessor as predecessor
from fid1_review_contract import validate_visual_review_payload


def completed_predecessor_fixture(root, shot='SH903', take='take09'):
    root = Path(root)
    rel = f'{predecessor.LOCAL}/video/{shot}/jobs/{take}'
    directory = root / rel
    (directory / 'qa').mkdir(parents=True)
    (directory / 'run_record_media').mkdir()
    image = directory / 'fixture.png'; image.write_bytes(b'fixture approved image bytes')
    workflow = directory / 'workflow.json'; write_json(workflow, {'fixture': 'CPU fixture only'})
    output = directory / 'run_record_media/fixture.mp4'; output.write_bytes(b'fixture output bytes')
    profile = {'profile_id': f'{shot}_FID1_V005', 'scope': predecessor.SCOPE, 'shot_id': shot,
               'input_sha256': digest(image), 'seed': 2026100803,
               'width': 576, 'height': 1024, 'frames': 49, 'fps': 24,
               'anchor_strategy': 'wan22_timestep_aware_future_roi_v2'}
    job = {'project_id': predecessor.PROJECT, 'shot_id': shot, 'purpose': predecessor.SCOPE,
           'eligible_for_final_cut': False, 'input_file': image.name, 'input_sha256': digest(image),
           'workflow_sha256': digest(workflow), 'seed': profile['seed'], 'trial_profile': profile,
           'fid1_contract': {'schema_version': 1, 'strategy': profile['anchor_strategy'],
                             'node_class': 'FID1WanTimestepAwareROIAnchor'}}
    write_json(directory / 'job.json', job)
    write_json(directory / 'job_integrity.json', {'schema_version': 1, 'job_sha256': digest(directory / 'job.json'),
               'workflow_sha256': job['workflow_sha256'], 'input_sha256': job['input_sha256']})
    run = {'result': 'success', 'prompt_id': 'fixture-prompt', 'workflow_sha256': job['workflow_sha256'],
           'workflow': str(workflow), 'args': {'image': str(image)}, 'queued_new_job': True,
           'outputs': [{'saved_path': str(output), 'bytes': output.stat().st_size, 'sha256': digest(output)}]}
    write_json(directory / 'run_record.json', run)
    evidence_rel = f'local/review_evidence/FID1_{shot}_fixture_VISUAL_REVIEW.json'
    evidence = {'schema_version': 1, 'scope': predecessor.SCOPE, 'shot_id': shot,
                'profile_id': profile['profile_id'], 'output_sha256': digest(output),
                'decision': 'ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL', 'full_playback': 'PASS',
                'identity': 'PASS', 'costume': 'PASS', 'limbs': 'PASS', 'reviewer': 'Jovi',
                'user_quote': 'TEST FIXTURE ONLY: not a real human judgement.',
                'recorded_at': '2026-10-13T10:00:00+08:00'}
    write_json(root / evidence_rel, evidence)
    review = {key: evidence[key] for key in ('decision', 'full_playback', 'identity', 'costume', 'limbs',
                                            'reviewer', 'user_quote', 'recorded_at')}
    review.update(evidence_path=evidence_rel, evidence_sha256=digest(root / evidence_rel))
    report = {'scope': predecessor.SCOPE, 'shot_id': shot, 'profile_id': profile['profile_id'],
              'runtime_success': True, 'media_contract_ok': True, 'full_decode': 'PASS',
              'input': {'path': image.name, 'sha256': job['input_sha256']},
              'workflow_sha256': job['workflow_sha256'], 'seed': job['seed'],
              'media': {'width': 576, 'height': 1024, 'frame_count': 49, 'fps': 24},
              'output': {'path': 'run_record_media/fixture.mp4', 'bytes': output.stat().st_size,
                         'sha256': digest(output)}, 'visual_review': review}
    write_json(directory / 'qa/qa_report.json', report)
    return rel


class PredecessorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.rel = completed_predecessor_fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_selected_take09_is_frozen_and_failed_take04_irrelevant(self):
        receipt = predecessor.validate_predecessor(self.root, 'SH901', self.rel)
        self.assertEqual(receipt['job_dir'], self.rel)
        self.assertEqual(len(receipt['files']), 8)
        self.assertEqual(predecessor.validate_predecessor_receipt(self.root, 'SH901', receipt), receipt)

    def test_shot_order_and_explicit_path(self):
        for sid, rel in [('SH901', None), ('SH902', self.rel), ('SH903', self.rel),
                         ('SH901', self.rel + '/..'), ('SH901', str(self.root / self.rel))]:
            with self.subTest(sid=sid, rel=rel), self.assertRaises(ValueError):
                predecessor.validate_predecessor(self.root, sid, rel)
        self.assertIsNone(predecessor.validate_predecessor(self.root, 'SH903', None))
        accepted_sh901 = completed_predecessor_fixture(self.root, 'SH901', 'take03')
        self.assertEqual(predecessor.validate_predecessor(self.root, 'SH902', accepted_sh901)['shot_id'], 'SH901')

    def test_linked_job_or_media_is_rejected(self):
        image = self.root / self.rel / 'fixture.png'
        real = Path.is_symlink
        def linked(path):
            return path == image or real(path)
        # Exercise admission on hosts without permission to create real Windows symlinks.
        with patch.object(Path, 'is_symlink', linked):
            with self.assertRaisesRegex(ValueError, 'link|junction'):
                predecessor.validate_predecessor(self.root, 'SH901', self.rel)

    def test_each_predecessor_file_drift_is_detected(self):
        receipt = predecessor.validate_predecessor(self.root, 'SH901', self.rel)
        for rel in receipt['files']:
            path = self.root / rel; before = path.read_bytes()
            with self.subTest(path=rel):
                path.write_bytes(before + b' ')
                with self.assertRaises(ValueError):
                    predecessor.validate_predecessor_receipt(self.root, 'SH901', receipt)
                path.write_bytes(before)

    def test_legacy_python_reparse_attribute_fallback_rejects_before_read(self):
        import stat
        from types import SimpleNamespace
        flagged=self.root/self.rel/'run_record_media/fixture.mp4'
        original=Path.lstat
        def reparse_attributes(path, *args, **kwargs):
            if path==flagged:
                return SimpleNamespace(st_file_attributes=getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400))
            return original(path,*args,**kwargs)
        def unavailable_detector(path):
            raise AttributeError('is_junction is absent in older Python')
        # Hide the newer detector; the deployment helper must consult Windows reparse attributes.
        with patch.object(Path,'is_junction',property(unavailable_detector),create=True), \
             patch.object(Path,'is_symlink',return_value=False), \
             patch.object(Path,'lstat',reparse_attributes):
            with self.assertRaisesRegex(ValueError,'junction/reparse'):
                predecessor.validate_predecessor(self.root,'SH901',self.rel)

    def test_resealed_job_and_receipt_cannot_change_prompt_identity(self):
        receipt = predecessor.validate_predecessor(self.root, 'SH901', self.rel)
        altered = copy.deepcopy(receipt); altered['prompt_id'] = 'different'
        with self.assertRaisesRegex(ValueError, 'receipt changed'):
            predecessor.validate_predecessor_receipt(self.root, 'SH901', altered)
        path = self.root / self.rel / 'job.json'; job = read_json(path); job['seed'] += 1; write_json(path, job)
        seal = self.root / self.rel / 'job_integrity.json'; integrity = read_json(seal)
        integrity['job_sha256'] = digest(path); write_json(seal, integrity)
        with self.assertRaisesRegex(ValueError, 'seed|binding'):
            predecessor.validate_predecessor(self.root, 'SH901', self.rel)

    def test_resealed_predecessor_profile_budget_and_strategy_still_require_match(self):
        path=self.root/self.rel/'job.json';before=path.read_bytes()
        seal=self.root/self.rel/'job_integrity.json';seal_before=seal.read_bytes()
        changes=[('trial_profile','frames',81),('trial_profile','fps',30),
                 ('trial_profile','width',704),('trial_profile','fps',True),
                 ('fid1_contract','node_class','FID1WanSourceROIAnchor'),
                 ('fid1_contract','strategy','unknown')]
        for section,key,value in changes:
            with self.subTest(section=section,key=key,value=value):
                job=read_json(path);job[section][key]=value;write_json(path,job)
                integrity=read_json(seal);integrity['job_sha256']=digest(path);write_json(seal,integrity)
                with self.assertRaises(ValueError):
                    predecessor.validate_predecessor(self.root,'SH901',self.rel)
                path.write_bytes(before);seal.write_bytes(seal_before)

    def test_stale_runtime_qa_input_workflow_or_failed_run_is_rejected(self):
        changes = [('run_record.json', 'result', 'error'),
                   ('run_record.json', 'queued_new_job', False),
                   ('run_record.json', 'workflow_sha256', '0' * 64),
                   ('run_record.json', 'workflow', 'wrong.json'),
                   ('run_record.json', 'args', {'image': 'wrong.png'}),
                   ('qa/qa_report.json', 'full_decode', 'NOT_RUN'),
                   ('qa/qa_report.json', 'seed', 0),
                   ('qa/qa_report.json', 'media', {'width':576,'height':1024,'frame_count':81,'fps':24}),
                   ('qa/qa_report.json', 'profile_id', 'OTHER')]
        for name, key, value in changes:
            path = self.root / self.rel / name; before = path.read_bytes(); data = read_json(path)
            with self.subTest(name=name, key=key):
                data[key] = value; write_json(path, data)
                with self.assertRaises(ValueError):
                    predecessor.validate_predecessor(self.root, 'SH901', self.rel)
                path.write_bytes(before)

    def test_pending_rejected_and_missing_evidence_does_not_accept(self):
        path = self.root / self.rel / 'qa/qa_report.json'; before = path.read_bytes(); data = read_json(path)
        data['visual_review'] = {'decision': 'PENDING'}; write_json(path, data)
        with self.assertRaises(ValueError):
            predecessor.validate_predecessor(self.root, 'SH901', self.rel)
        path.write_bytes(before)
        evidence=self.root/read_json(path)['visual_review']['evidence_path']
        evidence_bytes=evidence.read_bytes();evidence.unlink()
        with self.assertRaises(ValueError):
            predecessor.validate_predecessor(self.root, 'SH901', self.rel)
        evidence.write_bytes(evidence_bytes)
        # Explicit failed/no-output take08 must never be treated as the successful selected take.
        run_path = self.root / self.rel / 'run_record.json'; run = read_json(run_path)
        run.update(result='error', outputs=[]); write_json(run_path, run)
        with self.assertRaises(ValueError):
            predecessor.validate_predecessor(self.root, 'SH901', self.rel)

    def test_input_change_after_hash_validation_cannot_enter_receipt(self):
        original=predecessor.digest
        image=self.root/self.rel/'fixture.png'
        changed=[]
        def change_after_digest(path):
            sha=original(path)
            if Path(path)==image and not changed:
                changed.append(True);image.write_bytes(b'concurrent input change')
            return sha
        with patch.object(predecessor,'digest',side_effect=change_after_digest):
            with self.assertRaisesRegex(ValueError,'changed during validation'):
                predecessor.validate_predecessor(self.root,'SH901',self.rel)

    def test_concurrent_change_during_validation_is_detected(self):
        original = predecessor.validate_visual_review_payload
        def change_during_validation(*args, **kwargs):
            result = original(*args, **kwargs)
            path = self.root / self.rel / 'run_record.json'
            path.write_bytes(path.read_bytes() + b' ')
            return result
        with patch.object(predecessor, 'validate_visual_review_payload', side_effect=change_during_validation):
            with self.assertRaisesRegex(ValueError, 'changed during validation'):
                predecessor.validate_predecessor(self.root, 'SH901', self.rel)

    def test_strict_visual_feedback_fields(self):
        evidence = read_json(self.root / 'local/review_evidence/FID1_SH903_fixture_VISUAL_REVIEW.json')
        context = {'scope': evidence['scope'], 'shot_id': evidence['shot_id'],
                   'profile_id': evidence['profile_id'], 'output_sha256': evidence['output_sha256']}
        self.assertTrue(validate_visual_review_payload(evidence, **context))
        for changes in [{'user_quote': ''}, {'recorded_at': '2026-10-13T10:00:00'},
                        {'user_quote': ' ' * 2048 + 'x'}, {'identity': []}, {'decision': []},
                        {'recorded_at': None}, {'schema_version': True}, {'identity': 'PENDING'},
                        {'full_playback': 'NOT_RUN'}, {'decision': 'PENDING'}, {'scope': 'EP001'},
                        {'output_sha256': '0' * 64}, {'unexpected': True},
                        {'decision': 'CHANGES_REQUIRED'}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_visual_review_payload(evidence | changes, **context)
        self.assertTrue(validate_visual_review_payload(evidence | {'decision': 'CHANGES_REQUIRED',
                                         'limbs': 'CHANGES_REQUIRED'}, **context))


if __name__ == '__main__':
    unittest.main()
