import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
import sys,hashlib
S=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(S))
import apply_media_feedback_v5 as app
from preproduction import ContractError

class TestFeedback(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        rel='local/references/generated/20261005_v5/DAIYU_FACE_CROP.png'
        p=self.root/rel;p.parent.mkdir(parents=True);p.write_bytes(b'test-fixture-not-a-real-image')
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        self.asset={'asset_id':'DAIYU_FACE_CROP','path':rel,'sha256':h,'status':'CANDIDATE','character':'DAIYU','roles':['face']}
        self.registry={'schema_version':5,'assets':{'DAIYU_FACE_CROP':dict(self.asset)}}
        self.media={'assets':[dict(self.asset)]}
        self.review={'delivery_id':'MEDIA_RECOVERY_20261007','production_keyframes_approved':0,'items':[{'asset_id':'DAIYU_FACE_CROP','sha256':h,'decision':'approve_reference','scope':'reference','source':'unit-test fixture: not actual user consent','recorded_at':'2026-10-07T12:00:00+08:00','notes':'test fixture'}]}
    def tearDown(self):self.tmp.cleanup()
    def test_scoped_reference_only(self):
        new,report=app.proposed(self.root,self.review,self.registry,self.media)
        self.assertEqual(new['assets']['DAIYU_FACE_CROP']['status'],'USER_APPROVED')
        self.assertEqual(report['keyframes_approved'],0);self.assertFalse(report['production_ready'])
    def test_input_unchanged(self):
        original=copy.deepcopy(self.registry);app.proposed(self.root,self.review,self.registry,self.media);self.assertEqual(self.registry,original)
    def test_wrong_hash_rejected(self):
        self.review['items'][0]['sha256']='0'*64
        with self.assertRaises(ContractError):app.proposed(self.root,self.review,self.registry,self.media)
    def test_keyframe_scope_rejected(self):
        self.review['items'][0]['scope']='keyframe'
        with self.assertRaises(ContractError):app.proposed(self.root,self.review,self.registry,self.media)
    def test_claimed_keyframe_approval_rejected(self):
        self.review['production_keyframes_approved']=1
        with self.assertRaises(ContractError):app.proposed(self.root,self.review,self.registry,self.media)
    def test_duplicate_rejected(self):
        self.review['items'].append(copy.deepcopy(self.review['items'][0]))
        with self.assertRaises(ContractError):app.proposed(self.root,self.review,self.registry,self.media)
    def test_naive_timestamp_rejected(self):
        self.review['items'][0]['recorded_at']='2026-10-07T12:00:00'
        with self.assertRaises(ContractError):app.proposed(self.root,self.review,self.registry,self.media)
    def test_keep_source_not_approval(self):
        self.review['items'][0].update(decision='keep_source',scope='source_review_only')
        new,r=app.proposed(self.root,self.review,self.registry,self.media);self.assertEqual(new,self.registry);self.assertEqual(r['reference_approvals'],[])
    def test_changed_real_file_rejected(self):
        (self.root/self.asset['path']).write_bytes(b'changed')
        with self.assertRaises(ContractError):app.proposed(self.root,self.review,self.registry,self.media)

if __name__=='__main__':unittest.main()
