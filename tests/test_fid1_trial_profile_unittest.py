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
TAKE03_POSITIVE = (
    "An almost motionless portrait of the same two subjects in the reference image. The red-and-gold dressed "
    "monkey subject on the left keeps the original left-facing side profile and gaze. The lavender-dressed woman "
    "on the right keeps the original right-facing side profile and gaze. Their joined hands, facial proportions, "
    "clothing and ornaments hold the starting pose throughout. Locked camera. Motion limited to faint water ripples "
    "and tiny fabric breathing."
)
TAKE03_NEGATIVE = (
    "head rotation, front-facing face, looking at camera, moving lips, talking, opening mouth, pose changes, hand "
    "movement, walking, identity drift, face redesign, facial proportion change, humanized monkey face, species "
    "change, costume changes, extra people, extra limbs, deformed hands, unstable background"
)


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

    def test_sh903_v003_is_a_controlled_take03_prompt_comparison(self):
        kit = read_json(ROOT / source_pilot.KIT)
        v3_path = "config/source_fidelity_trials/SH903_FID1_V003.json"
        profile, _ = source_pilot.load_trial_profile(ROOT, "SH903", kit, v3_path)
        v2 = read_json(ROOT / "config/source_fidelity_trials/SH903_FID1_V002.json")
        self.assertEqual(profile["positive_prompt"], TAKE03_POSITIVE)
        self.assertEqual(profile["negative_prompt"], TAKE03_NEGATIVE)
        for field in ("input_sha256", "width", "height", "frames", "fps", "seed", "anchor_strategy", "anchor_rois"):
            self.assertEqual(profile[field], v2[field], f"controlled comparison changed {field}")

    def test_sh903_v004_changes_only_the_roi_feather_from_v003(self):
        kit = read_json(ROOT / source_pilot.KIT)
        v4, _ = source_pilot.load_trial_profile(ROOT, "SH903", kit, "config/source_fidelity_trials/SH903_FID1_V004.json")
        v3 = read_json(ROOT / "config/source_fidelity_trials/SH903_FID1_V003.json")
        self.assertEqual(v4["schema_version"], 3)
        for field in ("input_sha256", "width", "height", "frames", "fps", "seed", "positive_prompt", "negative_prompt", "anchor_strategy"):
            self.assertEqual(v4[field], v3[field], f"soft-feather comparison changed {field}")
        self.assertEqual(len(v4["anchor_rois"]), len(v3["anchor_rois"]))
        for soft, hard in zip(v4["anchor_rois"], v3["anchor_rois"]):
            self.assertEqual({key: value for key, value in soft.items() if key != "feather_latent"}, hard)
            self.assertEqual(soft["feather_latent"], 4)


if __name__ == "__main__":
    unittest.main()
