import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEGACY_PROFILE = ROOT / "config/source_fidelity_trials/SH903_FID1_V001.json"


class FID1TrialProfileContractTests(unittest.TestCase):
    def test_legacy_quality_profile_remains_source_trial_only(self):
        profile = json.loads(LEGACY_PROFILE.read_text(encoding="utf-8"))
        self.assertEqual(profile["scope"], "T1_SOURCE_ONLY")
        self.assertEqual(profile["shot_id"], "SH903")
        self.assertEqual((profile["frames"], profile["fps"]), (49, 24))
        self.assertNotIn("EP001", profile["shot_id"])
        self.assertNotIn("LOOKREEL", profile["scope"])
        text = LEGACY_PROFILE.read_text(encoding="utf-8")
        self.assertNotIn("14B", text)
        self.assertNotIn("LoRA", text)
        self.assertNotIn("platform", text.lower())


if __name__ == "__main__":
    unittest.main()
