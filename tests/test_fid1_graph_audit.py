import json
from pathlib import Path
import unittest

from scripts.preproduction import validate_graph


ROOT = Path(__file__).resolve().parents[1]
CAST = ["DAIYU", "WUKONG"]
PROFILE = {
    "schema_version": 2,
    "profile_id": "SH903_FID1_V002",
    "scope": "T1_SOURCE_ONLY",
    "shot_id": "SH903",
    "input_sha256": "6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f",
    "width": 576,
    "height": 1024,
    "frames": 49,
    "fps": 24,
    "seed": 2026100803,
    "positive_prompt": "Preserve the side profile and hand contact.",
    "negative_prompt": "No frontal rotation or identity drift.",
    "anchor_strategy": "wan22_first_latent_future_roi_v1",
    "anchor_rois": [{"id": "WUKONG_FACE", "x0": 0.14, "y0": 0.20, "x1": 0.29, "y1": 0.31}],
}


class TestFID1GraphAudit(unittest.TestCase):
    def test_profile_cannot_claim_fid1_without_a_live_anchor_node(self):
        graph = json.loads((ROOT / "workflows/video/production/VID_wan22_5b_i2v_prod_v001.json").read_text(encoding="utf-8"))
        graph["55"]["inputs"].update(width=PROFILE["width"], height=PROFILE["height"], length=PROFILE["frames"])
        graph["57"]["inputs"]["fps"] = PROFILE["fps"]
        graph["3"]["inputs"]["seed"] = PROFILE["seed"]
        graph["6"]["inputs"]["text"] = PROFILE["positive_prompt"]
        graph["7"]["inputs"]["text"] = PROFILE["negative_prompt"]
        with self.assertRaisesRegex(ValueError, "FID1|anchor|node"):
            validate_graph(graph, CAST, fid1_profile=PROFILE)


if __name__ == "__main__":
    unittest.main()
