import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import apply_delivery_feedback_fix2 as app
from preproduction import ContractError

class TestFix2Feedback(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        p=self.root/'local/references/test.png';p.parent.mkdir(parents=True);p.write_bytes(b'test-only')
        self.asset=dict(asset_id='DAIYU_FACE_CROP',path='local/references/test.png',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),character='DAIYU',roles=['face'],status='CANDIDATE')
        self.reg={'schema_version':5,'assets':{'DAIYU_FACE_CROP':dict(self.asset)}}
        self.media={'assets':[dict(self.asset)]}
        self.feedback={'delivery_id':app.DELIVERY_ID,'production_keyframes_approved':0,'items':[{'asset_id':'DAIYU_FACE_CROP','sha256':self.asset['sha256'],'decision':'approve_reference','scope':'reference','recorded_at':'2026-10-07T12:00:00+08:00','notes':'unit-test only, not actual consent'}]}
    def tearDown(self):self.tmp.cleanup()
    def test_reference_only(self):
        d,r=app.proposal(self.root,self.feedback,self.reg,self.media)
        self.assertEqual(d['assets']['DAIYU_FACE_CROP']['status'],'USER_APPROVED');self.assertEqual(r['keyframes_approved'],0);self.assertFalse(r['production_ready'])
    def test_input_unchanged(self):
        old=copy.deepcopy(self.reg);app.proposal(self.root,self.feedback,self.reg,self.media);self.assertEqual(self.reg,old)
    def test_hash_binding(self):
        self.feedback['items'][0]['sha256']='0'*64
        with self.assertRaises(ContractError):app.proposal(self.root,self.feedback,self.reg,self.media)
    def test_keyframe_scope_blocked(self):
        self.feedback['items'][0]['scope']='keyframe'
        with self.assertRaises(ContractError):app.proposal(self.root,self.feedback,self.reg,self.media)
    def test_nonzero_keyframes_blocked(self):
        self.feedback['production_keyframes_approved']=1
        with self.assertRaises(ContractError):app.proposal(self.root,self.feedback,self.reg,self.media)
    def test_duplicate_blocked(self):
        self.feedback['items'].append(copy.deepcopy(self.feedback['items'][0]))
        with self.assertRaises(ContractError):app.proposal(self.root,self.feedback,self.reg,self.media)
    def test_source_choice_no_approval(self):
        self.feedback['items'][0].update(decision='keep_source',scope='feedback_only')
        d,r=app.proposal(self.root,self.feedback,self.reg,self.media);self.assertEqual(d,self.reg);self.assertEqual(r['reference_approvals'],[])
    def test_file_changed_blocked(self):
        (self.root/self.asset['path']).write_bytes(b'changed')
        with self.assertRaises(ContractError):app.proposal(self.root,self.feedback,self.reg,self.media)
    def test_reject_previous_approval_requires_revoke(self):
        self.reg['assets']['DAIYU_FACE_CROP']['status']='USER_APPROVED'
        self.feedback['items'][0].update(decision='reject',scope='feedback_only')
        with self.assertRaises(ContractError):app.proposal(self.root,self.feedback,self.reg,self.media)

if __name__=='__main__':unittest.main()
