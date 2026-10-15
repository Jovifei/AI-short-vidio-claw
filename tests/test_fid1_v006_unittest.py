"""Experiment A contracts. All generated approvals are temporary test fixtures."""
import json
import subprocess
import sys
import unittest

from test_git_media_delivery import ROOT
import test_source_fidelity_profile as fixtures
from preproduction import read_json, write_json
from submit_prepared import job_command
from sync_repo_media import digest


PROFILE = 'config/source_fidelity_trials/SH903_FID1_V006.json'
BASE = 'config/source_fidelity_trials/SH903_FID1_V005.json'


class V006Tests(unittest.TestCase):
    def test_real_profile_changes_exactly_motion_semantics_and_identity(self):
        base, candidate = read_json(ROOT / BASE), read_json(ROOT / PROFILE)
        self.assertEqual(set(base), set(candidate))
        self.assertEqual({key for key in base if base[key] != candidate[key]},
                         {'profile_id', 'hypothesis', 'positive_prompt', 'negative_prompt'})
        self.assertEqual(candidate['profile_id'], 'SH903_FID1_V006')
        self.assertEqual(candidate['schema_version'], 4)

    def test_prompts_allow_bounded_motion_without_broad_freeze_bans(self):
        profile = read_json(ROOT / PROFILE)
        positive = profile['positive_prompt'].lower()
        negative_items = {item.strip().lower() for item in profile['negative_prompt'].split(',')}
        for prohibited in ('almost motionless', 'hold the starting pose throughout', 'motion limited to'):
            self.assertNotIn(prohibited, positive)
        self.assertIn('small observable natural nods', positive)
        for prohibited in ('head rotation', 'pose changes', 'hand movement'):
            self.assertNotIn(prohibited, negative_items)
        for bounded in ('large head rotation', 'unexpected hand separation', 'camera movement', 'wardrobe change'):
            self.assertIn(bounded, negative_items)

    def fixture(self):
        fixture = fixtures.FidelityProfileTests(methodName='test_cli_prepares_profile_without_submitting')
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        fixture.approve()
        profile = read_json(ROOT / PROFILE)
        # This is synthetic fixture admission, never a substitute for real source approval.
        profile['input_sha256'] = read_json(fixture.root / fixtures.pilot.KIT)['shots']['SH903']['sha256']
        fixture.profile_path = PROFILE
        write_json(fixture.root / PROFILE, profile)
        return fixture, profile

    def test_prepare_and_dryrun_freeze_v006_and_real_strategy_graph(self):
        fixture, profile = self.fixture()
        fixture.prepare()
        graph = read_json(fixture.root / fixture.out / 'workflow.json')
        anchor_id, anchor = next((key, value) for key, value in graph.items()
                                 if value['class_type'] == 'FID1WanTimestepAwareROIAnchor')
        sampler = next(value['inputs'] for value in graph.values() if value['class_type'] == 'KSampler')
        self.assertEqual(anchor['inputs']['model'], ['48', 0])
        self.assertEqual(anchor['inputs']['latent'], ['55', 0])
        self.assertEqual(json.loads(anchor['inputs']['roi_boxes_json']), profile['anchor_rois'])
        self.assertEqual(sampler['model'], [anchor_id, 0])
        self.assertEqual(sampler['latent_image'], [anchor_id, 1])
        _, job = job_command(fixture.root, fixture.root / fixture.out, 'http://127.0.0.1:8188')
        self.assertEqual(job['trial_profile'], profile)
        self.assertEqual(job['workflow_sha256'], digest(fixture.root / fixture.out / 'workflow.json'))
        self.assertEqual(job['input_sha256'], profile['input_sha256'])
        self.assertEqual(job['seed'], 2026100803)
        self.assertFalse(job['eligible_for_final_cut'])
        self.assertFalse((fixture.root / fixture.out / 'submission_intent.json').exists())
        write_json(fixture.root / PROFILE, {**profile, 'positive_prompt': 'Changed after freeze'})
        with self.assertRaises(ValueError):
            job_command(fixture.root, fixture.root / fixture.out, 'http://127.0.0.1:8188')

    def test_prepare_and_cli_dryrun_without_torch_import(self):
        fixture, _ = self.fixture()
        code = '''import builtins, runpy, sys
original = builtins.__import__
def guard(name, *args, **kwargs):
    if name == 'torch' or name.startswith('torch.'):
        raise AssertionError('offline Experiment A imported torch')
    return original(name, *args, **kwargs)
builtins.__import__ = guard
script, *args = sys.argv[1:]
sys.path.insert(0, str(__import__('pathlib').Path(script).parent))
sys.argv = [script, *args]
runpy.run_path(script, run_name='__main__')
'''
        commands = [
            ('source_pilot.py', ['prepare', '--root', str(fixture.root), '--shot', 'SH903',
             '--seed', '2026100803', '--out', fixture.out, '--trial-profile', PROFILE]),
            ('submit_prepared.py', ['--root', str(fixture.root), '--job-dir', fixture.out,
             '--url', 'http://127.0.0.1:8188']),
        ]
        for script, args in commands:
            result = subprocess.run([sys.executable, '-c', code, str(ROOT / 'scripts' / script), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((fixture.root / fixture.out / 'submission_intent.json').exists())
        self.assertFalse((fixture.root / fixture.out / 'run_record.json').exists())


if __name__ == '__main__':
    unittest.main()
