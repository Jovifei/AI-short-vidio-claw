import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import remote_image_packets as m
from preproduction import ContractError
REPO = Path(__file__).resolve().parents[1]

class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for rel in [m.CONFIG, 'episodes/EP001/production_plan_v5.json', 'episodes/LOOKREEL01/production_plan_v5.json']:
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, target)
        registry = {'schema_version': 5, 'assets': {}}
        for i, aid in enumerate([*m.FACE.values(), 'DAIYU_COSTUME_CROP', 'WUKONG_COSTUME_CROP']):
            rel = f'local/source/{aid}.png'
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', (80, 120), (i * 50, 120, 200)).save(p)
            registry['assets'][aid] = {'path': rel, 'sha256': m.sha256_file(p), 'status': 'CANDIDATE'}
        m.dump(self.root / m.REGISTRY, registry)
        self.registry_bytes = (self.root / m.REGISTRY).read_bytes()
        self.index = m.build(self.root, 'local/pack')
        self.pack = self.root / 'local/pack'

    def tearDown(self):
        self.temp.cleanup()

    def image(self, name, w=720, h=1280):
        p = self.pack / f'outputs/{name}.png'
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (w, h), tuple(hashlib.sha256(name.encode()).digest()[:3])).save(p)
        return p

    def accept(self, tid):
        p = self.image(tid)
        qa = {'task_id': tid, 'image_sha256': m.sha256_file(p),
              'reviewer': 'unit-test-not-human-approval', 'method': 'synthetic-fixture'}
        qa.update({k: True for k in m.SEMANTIC_KEYS})
        m.dump(self.pack / f'qa/{tid}.json', qa)
        return m.inspect_result(self.pack, tid, f'outputs/{tid}.png', f'qa/{tid}.json')

    def test_counts_and_no_media_claim(self):
        self.assertEqual(self.index['image_request_count'], 42)
        self.assertEqual(self.index['generated_images'], 0)
        self.assertFalse(self.index['production_ready'])

    def test_three_base_requests_ready(self):
        ready = [x['id'] for x in self.index['tasks'] if m.prepare_request(self.pack, x['id'])['ready_to_request']]
        self.assertEqual(set(ready), {'WARD_W_DAILY', 'WARD_W_FORMAL', 'WARD_D_OUTDOOR'})

    def test_single_person_no_other_face(self):
        r = m.prepare_request(self.pack, 'WARD_W_DAILY')
        self.assertEqual([a['id'] for a in r['reference_images']], ['WUKONG_FACE_CROP'])

    def test_formal_not_daily(self):
        r = m.prepare_request(self.pack, 'WARD_W_FORMAL')
        self.assertIn('WUKONG_COSTUME_CROP', [a['id'] for a in r['reference_images']])
        r = m.prepare_request(self.pack, 'WARD_W_DAILY')
        self.assertNotIn('WUKONG_COSTUME_CROP', [a['id'] for a in r['reference_images']])

    def test_blocks_missing_home(self):
        r = m.prepare_request(self.pack, 'EP001_SH006')
        self.assertFalse(r['ready_to_request'])
        self.assertIsNone(r['prompt'])
        self.assertEqual(r['reference_images'], [])

    def test_only_single_image_requested(self):
        r = m.prepare_request(self.pack, 'WARD_W_DAILY')
        self.assertEqual(r['n'], 1)
        self.assertLess(len(r['prompt'].encode()), 4000)

    def test_comp10_split_no_collage_request(self):
        ids = [x['id'] for x in self.index['tasks']]
        self.assertNotIn('LOOKREEL01_COMP10', ids)
        self.assertEqual(len([x for x in ids if x.startswith('LOOKREEL01_COMP10_')]), 4)

    def test_source_shots_preserved(self):
        for project in ('EP001', 'LOOKREEL01'):
            p = m.read_json(self.root / f'episodes/{project}/production_plan_v5.json')
            for shot in p['shots']:
                tid = f'{project}_{shot["shot_id"]}' + ('_P1' if shot['shot_id'] == 'COMP10' else '')
                _, t, _ = m.load_task(self.pack, tid)
                self.assertEqual(t['source_shot'], shot)

    def test_after_bandage_dependency(self):
        _, a, _ = m.load_task(self.pack, 'EP001_SH004')
        _, b, _ = m.load_task(self.pack, 'EP001_SH005')
        self.assertIn('STATE_W_HAND_PRE', a['depends_on'])
        self.assertIn('STATE_W_HAND_BANDAGED', b['depends_on'])

    def test_plan_bytes_unchanged(self):
        self.assertEqual((self.root / m.REGISTRY).read_bytes(), self.registry_bytes)
        for p in ('EP001', 'LOOKREEL01'):
            rel = f'episodes/{p}/production_plan_v5.json'
            self.assertEqual((self.root / rel).read_bytes(), (REPO / rel).read_bytes())

    def test_task_tamper_blocked(self):
        (self.pack / 'tasks/WARD_W_DAILY/task.json').write_text('{}')
        with self.assertRaises(ContractError):
            m.prepare_request(self.pack, 'WARD_W_DAILY')

    def test_source_tamper_blocked(self):
        (self.pack / 'inputs/WUKONG_FACE_CROP.png').write_bytes(b'wrong')
        with self.assertRaises(ContractError):
            m.prepare_request(self.pack, 'WARD_W_DAILY')

    def test_landscape_board_rejected(self):
        p = self.image('board', 1536, 1024)
        with self.assertRaises(ContractError):
            m.image_check(p, {'width': 1080, 'height': 1920, 'min_short_edge': 720, 'aspect_tolerance': 0.02})

    def test_tiny_crop_rejected(self):
        p = self.image('thumb', 180, 320)
        with self.assertRaises(ContractError):
            m.image_check(p, {'width': 1080, 'height': 1920, 'min_short_edge': 720, 'aspect_tolerance': 0.02})

    def test_legal_portrait_shape_passes(self):
        self.assertEqual(m.image_check(self.image('portrait'), {'width': 1080, 'height': 1920, 'min_short_edge': 720, 'aspect_tolerance': 0.02})['height'], 1280)

    def test_no_user_approval_from_art_qa(self):
        r = self.accept('WARD_W_DAILY')
        self.assertFalse(r['user_approved'])
        self.assertFalse(r['production_ready'])

    def test_parent_result_unlocks_home_candidate_only(self):
        self.accept('WARD_W_DAILY')
        r = m.prepare_request(self.pack, 'WARD_W_HOME')
        self.assertTrue(r['ready_to_request'])
        self.assertFalse(r['production_ready'])

    def test_changed_parent_image_blocked(self):
        self.accept('WARD_W_DAILY')
        self.image('WARD_W_DAILY', 721, 1280)
        with self.assertRaises(ContractError):
            m.prepare_request(self.pack, 'WARD_W_HOME')

    def test_semantic_not_automatically_inferred(self):
        p = self.image('WARD_W_DAILY')
        q = {'task_id': 'WARD_W_DAILY', 'image_sha256': m.sha256_file(p), 'reviewer': 'test', 'method': 'fixture'}
        m.dump(self.pack / 'qa/test.json', q)
        with self.assertRaises(ContractError):
            m.inspect_result(self.pack, 'WARD_W_DAILY', 'outputs/WARD_W_DAILY.png', 'qa/test.json')

    def test_output_not_overwritten(self):
        with self.assertRaises(ContractError):
            m.build(self.root, 'local/pack')

    def test_result_not_overwritten(self):
        self.accept('WARD_W_DAILY')
        with self.assertRaises(ContractError):
            self.accept('WARD_W_DAILY')

    def test_paths_escape_blocked(self):
        for p in ('../out', 'C:/out', '/tmp/out', 'local/../out'):
            with self.assertRaises(ContractError):
                m.safe(self.root, p)

    def test_assemble_requires_real_panels(self):
        with self.assertRaises(ContractError):
            m.assemble_comp10(self.pack)

    def test_four_grid_is_explicit_cpu_not_i2v(self):
        self.accept('WARD_W_DAILY')
        self.accept('WARD_D_OUTDOOR')
        for i in range(1, 5):
            self.accept(f'LOOKREEL01_COMP10_P{i}')
        r = m.assemble_comp10(self.pack)
        self.assertFalse(r['i2v_eligible'])
        self.assertFalse(r['user_approved'])
        with Image.open(self.pack / r['path']) as im:
            self.assertEqual(im.size, (1080, 1920))

    def test_parent_lineage_rechecked(self):
        self.accept('WARD_W_DAILY')
        self.accept('WARD_W_HOME')
        (self.pack / 'results/WARD_W_DAILY.json').unlink()
        with self.assertRaises(ContractError):
            m.checked_result(self.pack, 'WARD_W_HOME')

    def test_dependency_cycle(self):
        with self.assertRaises(ContractError):
            m.validate_dag([{'id': 'A', 'depends_on': ['B']}, {'id': 'B', 'depends_on': ['A']}])

    def test_dependency_missing(self):
        with self.assertRaises(ContractError):
            m.validate_dag([{'id': 'A', 'depends_on': ['B']}])

    def test_duplicate_task(self):
        with self.assertRaises(ContractError):
            m.validate_dag([{'id': 'A', 'depends_on': []}, {'id': 'A', 'depends_on': []}])

if __name__ == '__main__':
    unittest.main()
