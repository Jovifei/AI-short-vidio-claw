import json
import tempfile
import unittest
from pathlib import Path

from scripts.fid1_graph_audit import audit


class TestFID1GraphAudit(unittest.TestCase):
    def test_prompt_only_change_is_not_intervention(self):
        base = {
            "1": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"image": "a", "width": 576}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "old"}},
        }
        candidate = {
            "1": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"image": "a", "width": 576}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "identity preserve"}},
        }
        result = audit(base, candidate)
        self.assertFalse(result["structural_change"])
        self.assertFalse(result["production_claim_allowed"])

    def test_new_conditioning_node_is_visible(self):
        base = {
            "1": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"image": "a"}}
        }
        candidate = {
            "1": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"image": "a"}},
            "9": {"class_type": "ReferenceConditioning", "inputs": {"reference": "face"}}
        }
        result = audit(base, candidate)
        self.assertTrue(result["structural_change"])


if __name__ == "__main__":
    unittest.main()
