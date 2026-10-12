import json
from pathlib import Path
import tempfile
import unittest

from test_git_media_delivery import ROOT
import source_pilot as pilot
from preproduction import read_json, write_json


class FID1ProfileSchemaTests(unittest.TestCase):
    def test_v2_profile_loads_explicit_normalized_source_rois(self):
        kit = read_json(ROOT / pilot.KIT)
        shot = kit["shots"]["SH903"]
        profile = {
            "schema_version": 2,
            "profile_id": "SH903_FID1_TEST_V2",
            "scope": "T1_SOURCE_ONLY",
            "shot_id": "SH903",
            "input_sha256": shot["sha256"],
            "width": 576,
            "height": 1024,
            "frames": 49,
            "fps": 24,
            "seed": 2026100803,
            "positive_prompt": "Preserve approved identities and side profile; subtle breathing only.",
            "negative_prompt": "No face redesign, costume change, or frontal rotation.",
            "hypothesis": "TEST FIXTURE ONLY: face ROIs are copied from the first encoded latent into future slots.",
            "anchor_strategy": "wan22_first_latent_future_roi_v1",
            "anchor_rois": [
                {"id": "WUKONG_FACE", "x0": 0.14, "y0": 0.20, "x1": 0.29, "y1": 0.31},
                {"id": "DAIYU_FACE", "x0": 0.72, "y0": 0.20, "x1": 0.85, "y1": 0.31},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = "config/source_fidelity_trials/SH903_FID1_TEST_V2.json"
            write_json(root / rel, profile)
            try:
                loaded, digest = pilot.load_trial_profile(root, "SH903", kit, rel)
            except ValueError as exc:
                self.fail(f"valid FID1 v2 profile was rejected: {exc}")
        self.assertEqual(loaded, profile)
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
