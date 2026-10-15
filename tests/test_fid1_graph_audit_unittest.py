import json
from pathlib import Path
import unittest

from scripts import fid1_graph_audit


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
    "positive_prompt": "Keep the approved side profile and hand contact; only subtle breathing and cloth motion.",
    "negative_prompt": "No frontal rotation, face redesign, costume change, or identity drift.",
    "hypothesis": "A small future face ROI anchor may reduce identity drift; this is a trial, not acceptance.",
    "anchor_strategy": "wan22_first_latent_future_roi_v1",
    "anchor_rois": [
        {"id": "WUKONG_FACE", "x0": 0.14, "y0": 0.20, "x1": 0.29, "y1": 0.31},
        {"id": "DAIYU_FACE", "x0": 0.72, "y0": 0.20, "x1": 0.85, "y1": 0.31},
    ],
}


def base_graph():
    graph = json.loads((ROOT / "workflows/video/production/VID_wan22_5b_i2v_prod_v001.json").read_text(encoding="utf-8"))
    graph["55"]["inputs"].update(width=PROFILE["width"], height=PROFILE["height"], length=PROFILE["frames"])
    graph["3"]["inputs"]["seed"] = PROFILE["seed"]
    graph["6"]["inputs"]["text"] = PROFILE["positive_prompt"]
    graph["7"]["inputs"]["text"] = PROFILE["negative_prompt"]
    graph["57"]["inputs"]["fps"] = PROFILE["fps"]
    return graph


def timestep_profile():
    profile = json.loads(json.dumps(PROFILE))
    profile.update(
        schema_version=4,
        profile_id="SH903_FID1_V005",
        anchor_strategy="wan22_timestep_aware_future_roi_v2",
        hypothesis="Keep the Wan condition mask unchanged and noise the source ROI at each sampler sigma.",
    )
    profile["anchor_rois"] = [dict(roi, feather_latent=4) for roi in profile["anchor_rois"]]
    return profile


class TestFID1GraphAudit(unittest.TestCase):
    def test_timestep_aware_node_interposes_both_model_and_latent_edges(self):
        profile = timestep_profile()
        base = base_graph()
        candidate = base_graph()

        try:
            node_id = fid1_graph_audit.attach_fid1_anchor(candidate, CAST, profile)
        except ValueError as exc:
            self.fail(f"timestep-aware FID1 graph strategy is missing: {exc}")

        self.assertEqual(candidate[node_id]["class_type"], "FID1WanTimestepAwareROIAnchor")
        self.assertEqual(candidate[node_id]["inputs"]["model"], base["3"]["inputs"]["model"])
        self.assertEqual(candidate[node_id]["inputs"]["latent"], ["55", 0])
        self.assertEqual(candidate["3"]["inputs"]["model"], [node_id, 0])
        self.assertEqual(candidate["3"]["inputs"]["latent_image"], [node_id, 1])
        report = fid1_graph_audit.audit_fid1_graph(base, candidate, CAST, profile)
        self.assertTrue(report["fid1_graph_valid"])
        self.assertEqual(len(report["active_edges"]), 4)

    def test_timestep_aware_audit_rejects_model_or_latent_bypass(self):
        profile = timestep_profile()
        base = base_graph()
        audit = fid1_graph_audit.audit_fid1_graph

        bypass_model = base_graph()
        try:
            fid1_graph_audit.attach_fid1_anchor(bypass_model, CAST, profile)
        except ValueError as exc:
            self.fail(f"timestep-aware FID1 graph strategy is missing: {exc}")
        bypass_model["3"]["inputs"]["model"] = base["3"]["inputs"]["model"]
        with self.assertRaisesRegex(ValueError, "model|connection|FID1"):
            audit(base, bypass_model, CAST, profile)

        bypass_latent = base_graph()
        try:
            fid1_graph_audit.attach_fid1_anchor(bypass_latent, CAST, profile)
        except ValueError as exc:
            self.fail(f"timestep-aware FID1 graph strategy is missing: {exc}")
        bypass_latent["3"]["inputs"]["latent_image"] = ["55", 0]
        with self.assertRaisesRegex(ValueError, "latent|connection|FID1"):
            audit(base, bypass_latent, CAST, profile)

    def test_anchor_node_is_on_the_live_wan_to_sampler_path(self):
        graph = base_graph()
        attach = getattr(fid1_graph_audit, "attach_fid1_anchor", None)
        self.assertTrue(callable(attach), "FID1 graph construction must be explicit and testable")

        node_id = attach(graph, CAST, PROFILE)

        self.assertEqual(graph[node_id]["class_type"], "FID1WanSourceROIAnchor")
        self.assertEqual(graph[node_id]["inputs"]["latent"], ["55", 0])
        self.assertEqual(graph["3"]["inputs"]["latent_image"], [node_id, 0])
        self.assertEqual(json.loads(graph[node_id]["inputs"]["roi_boxes_json"]), PROFILE["anchor_rois"])
        self.assertEqual(len(graph), 13)

    def test_source_trial_graph_rejects_sampler_budget_changes(self):
        graph = base_graph()
        fid1_graph_audit.attach_fid1_anchor(graph, CAST, PROFILE)
        graph["3"]["inputs"]["steps"] = 14
        with self.assertRaisesRegex(ValueError, "sampler|steps|CFG|denoise"):
            from scripts.preproduction import validate_graph
            validate_graph(graph, CAST, fid1_profile=PROFILE)

    def test_source_trial_graph_rejects_wan_flow_shift_drift(self):
        from scripts.preproduction import validate_graph
        mutations = (("shift", 4.0), ("sampling", "img_to_img_velocity"), ("multiplier", 500))
        for profile in (PROFILE, timestep_profile()):
            for field, value in mutations:
                with self.subTest(strategy=profile["anchor_strategy"], field=field):
                    graph = base_graph()
                    fid1_graph_audit.attach_fid1_anchor(graph, CAST, profile)
                    sampling_node = next(node for node in graph.values() if node["class_type"] == "ModelSamplingSD3")
                    sampling_node["inputs"][field] = value
                    with self.assertRaisesRegex(ValueError, "shift|sampling|multiplier"):
                        validate_graph(graph, CAST, fid1_profile=profile)

    def test_source_trial_graph_rejects_length_seed_and_prompt_drift(self):
        from scripts.preproduction import validate_graph
        mutations = (
            ("length", lambda graph: graph["55"]["inputs"].update(length=41), "frame|length|dimension"),
            ("seed", lambda graph: graph["3"]["inputs"].update(seed=1), "seed"),
            ("positive_prompt", lambda graph: graph["6"]["inputs"].update(text="different prompt"), "prompt"),
            ("negative_prompt", lambda graph: graph["7"]["inputs"].update(text="different negative"), "prompt"),
        )
        for name, mutate, message in mutations:
            with self.subTest(name=name):
                graph = base_graph()
                fid1_graph_audit.attach_fid1_anchor(graph, CAST, PROFILE)
                mutate(graph)
                with self.assertRaisesRegex(ValueError, message):
                    validate_graph(graph, CAST, fid1_profile=PROFILE)

    def test_audit_rejects_a_named_but_unconnected_or_wrong_roi_node(self):
        base = base_graph()
        candidate = base_graph()
        node_id = fid1_graph_audit.attach_fid1_anchor(candidate, CAST, PROFILE)
        audit = getattr(fid1_graph_audit, "audit_fid1_graph", None)
        self.assertTrue(callable(audit), "FID1 audit must validate exact graph edges and values")
        report = audit(base, candidate, CAST, PROFILE)
        self.assertTrue(report["fid1_graph_valid"])

        bypassed = base_graph()
        bypass_id = fid1_graph_audit.attach_fid1_anchor(bypassed, CAST, PROFILE)
        bypassed["3"]["inputs"]["latent_image"] = ["55", 0]
        with self.assertRaisesRegex(ValueError, "latent_image|connection|FID1"):
            audit(base, bypassed, CAST, PROFILE)

        wrong_roi = base_graph()
        wrong_id = fid1_graph_audit.attach_fid1_anchor(wrong_roi, CAST, PROFILE)
        wrong_roi[wrong_id]["inputs"]["roi_boxes_json"] = "[]"
        with self.assertRaisesRegex(ValueError, "ROI"):
            audit(base, wrong_roi, CAST, PROFILE)


if __name__ == "__main__":
    unittest.main()
