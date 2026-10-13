import json
from pathlib import Path
import tempfile
import unittest

from test_git_media_delivery import ROOT
import source_pilot as pilot
from preproduction import read_json, write_json


class FID1ProfileSchemaTests(unittest.TestCase):
    def test_next_shot_v002_profiles_preserve_each_own_source_seed_prompts_and_roi(self):
        kit = read_json(ROOT / pilot.KIT)
        for shot in ("SH901", "SH902"):
            with self.subTest(shot=shot):
                previous = read_json(ROOT / f"config/source_fidelity_trials/{shot}_FID1_V001.json")
                rel = f"config/source_fidelity_trials/{shot}_FID1_V002.json"
                profile, digest = pilot.load_trial_profile(ROOT, shot, kit, rel)
                self.assertEqual(profile["schema_version"], 4)
                self.assertEqual(profile["anchor_strategy"], "wan22_timestep_aware_future_roi_v2")
                for key in ("shot_id", "input_sha256", "seed", "positive_prompt", "negative_prompt", "width", "height", "frames", "fps", "scope"):
                    self.assertEqual(profile[key], previous[key])
                self.assertEqual(profile["input_sha256"], kit["shots"][shot]["sha256"])
                self.assertEqual([{k:v for k,v in roi.items() if k!="feather_latent"} for roi in profile["anchor_rois"]], previous["anchor_rois"])
                self.assertTrue(all(roi["feather_latent"] == 4 for roi in profile["anchor_rois"]))
                self.assertEqual(len(digest), 64)

    def test_v005_freezes_take07_inputs_and_changes_only_anchor_strategy(self):
        previous = json.loads((ROOT / "config/source_fidelity_trials/SH903_FID1_V004.json").read_text(encoding="utf-8"))
        candidate = json.loads((ROOT / "config/source_fidelity_trials/SH903_FID1_V005.json").read_text(encoding="utf-8"))
        allowed_changes = {"schema_version", "profile_id", "hypothesis", "anchor_strategy"}
        self.assertEqual({key: value for key, value in candidate.items() if key not in allowed_changes},
                         {key: value for key, value in previous.items() if key not in allowed_changes})
        self.assertEqual(candidate["anchor_strategy"], "wan22_timestep_aware_future_roi_v2")

    def test_v4_profile_loads_timestep_aware_roi_strategy(self):
        kit = read_json(ROOT / pilot.KIT)
        shot = kit["shots"]["SH903"]
        profile = {
            "schema_version": 4,
            "profile_id": "SH903_FID1_TEST_V005",
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
            "hypothesis": "TEST FIXTURE ONLY: keep Wan's base condition mask and noise the ROI source at each sigma.",
            "anchor_strategy": "wan22_timestep_aware_future_roi_v2",
            "anchor_rois": [
                {"id": "WUKONG_FACE", "x0": 0.14, "y0": 0.20, "x1": 0.29, "y1": 0.31, "feather_latent": 4},
                {"id": "DAIYU_FACE", "x0": 0.72, "y0": 0.20, "x1": 0.85, "y1": 0.31, "feather_latent": 4},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = "config/source_fidelity_trials/SH903_FID1_TEST_V005.json"
            write_json(root / rel, profile)
            try:
                loaded, digest = pilot.load_trial_profile(root, "SH903", kit, rel)
            except ValueError as exc:
                self.fail(f"valid FID1 v4 profile was rejected: {exc}")
        self.assertEqual(loaded, profile)
        self.assertEqual(len(digest), 64)

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
