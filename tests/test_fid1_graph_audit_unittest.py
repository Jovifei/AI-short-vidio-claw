import importlib.util
import tempfile
import json
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('audit', 'scripts/fid1_graph_audit.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class TestFID1GraphAudit(unittest.TestCase):
    def test_prompt_only_is_not_intervention(self):
        a={'1':{'class_type':'WanSampler','inputs':{'text':['2',0]}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':'a'}}}
        b={'1':{'class_type':'WanSampler','inputs':{'text':['2',0]}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':'keep identity'}}}
        r=MOD.audit(a,b)
        self.assertTrue(r['prompt_only_suspected'])
        self.assertFalse(r['production_claim_allowed'])

    def test_unconnected_reference_is_not_valid(self):
        a={'1':{'class_type':'WanSampler','inputs':{}},'2':{'class_type':'ReferenceImage','inputs':{}}}
        r=MOD.audit(a,a)
        self.assertFalse(r['production_claim_allowed'])

    def test_structure_and_reference_path_can_pass_audit(self):
        g={'1':{'class_type':'WanSampler','inputs':{'image':['2',0]}},'2':{'class_type':'ReferenceImage','inputs':{}}}
        r=MOD.audit({},g)
        self.assertTrue(r['structural_change'])
        self.assertTrue(r['reference_reaches_downstream'])

if __name__ == '__main__':
    unittest.main()
