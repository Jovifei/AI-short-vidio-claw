import unittest

from test_git_media_delivery import ROOT
import source_pilot
from preproduction import read_json

PROFILE_PATHS = {
    "SH901": "config/source_fidelity_trials/SH901_FID1_V001.json",
    "SH902": "config/source_fidelity_trials/SH902_FID1_V001.json",
    "SH903": "config/source_fidelity_trials/SH903_FID1_V002.json",
}
SEEDS = {"SH901": 2026100801, "SH902": 2026100802, "SH903": 2026100803}


class FID1TrialProfileTests(unittest.TestCase):
    def test_each_approved_source_has_its_own_frozen_fid1_profile(self):
        kit = read_json(ROOT / source_pilot.KIT)
        loaded = {}
        for shot_id, relative in PROFILE_PATHS.items():
            try:
                profile, profile_sha = source_pilot.load_trial_profile(ROOT, shot_id, kit, relative)
            except (OSError, ValueError) as exc:
                self.fail(f"{shot_id} has no valid independent FID1 profile: {exc}")
            self.assertEqual(profile["schema_version"], 2)
            self.assertEqual(profile["scope"], "T1_SOURCE_ONLY")
            self.assertEqual(profile["shot_id"], shot_id)
            self.assertEqual(profile["input_sha256"], kit["shots"][shot_id]["sha256"])
            self.assertEqual(profile["seed"], SEEDS[shot_id])
            self.assertEqual((profile["width"], profile["height"], profile["frames"], profile["fps"]), (576, 1024, 49, 24))
            self.assertEqual(profile["anchor_strategy"], "wan22_first_latent_future_roi_v1")
            self.assertGreaterEqual(len(profile["anchor_rois"]), 1)
            self.assertLess(len(profile_sha), 65)
            loaded[shot_id] = profile["anchor_rois"]
        self.assertEqual(len({str(loaded[sid]) for sid in loaded}), 3, "ROIs must be shot-specific")


if __name__ == "__main__":
    unittest.main()
