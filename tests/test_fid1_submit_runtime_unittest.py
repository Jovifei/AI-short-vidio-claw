import unittest

from test_git_media_delivery import ROOT
import submit_prepared


class FID1SubmitRuntimeTests(unittest.TestCase):
    def test_comfy_object_info_validates_timestep_aware_model_and_latent_ports(self):
        validate = submit_prepared.validate_fid1_object_info
        payload = {
            "FID1WanTimestepAwareROIAnchor": {
                "input": {"required": {
                    "model": ["MODEL"],
                    "latent": ["LATENT"],
                    "roi_boxes_json": ["STRING", {"default": "[]"}],
                }},
                "output": ["MODEL", "LATENT"],
            }
        }
        try:
            self.assertTrue(validate(payload, "FID1WanTimestepAwareROIAnchor"))
        except TypeError as exc:
            self.fail(f"runtime schema validator must select the contract's node class: {exc}")
        with self.assertRaisesRegex(ValueError, "MODEL|schema|socket|FID1"):
            validate({"FID1WanTimestepAwareROIAnchor": {
                "input": {"required": {"model": ["IMAGE"], "latent": ["LATENT"], "roi_boxes_json": ["STRING"]}},
                "output": ["MODEL", "LATENT"],
            }}, "FID1WanTimestepAwareROIAnchor")

    def test_comfy_object_info_must_expose_the_real_fid1_node_contract(self):
        validate = getattr(submit_prepared, "validate_fid1_object_info", None)
        self.assertTrue(callable(validate), "FID1 execute must verify the loaded ComfyUI node schema")
        payload = {
            "FID1WanSourceROIAnchor": {
                "input": {"required": {"latent": ["LATENT"], "roi_boxes_json": ["STRING", {"default": "[]"}]}},
                "output": ["LATENT"],
            }
        }
        self.assertTrue(validate(payload))
        with self.assertRaisesRegex(ValueError, "FID1|node"):
            validate({})
        with self.assertRaisesRegex(ValueError, "LATENT|STRING|socket|schema"):
            validate({"FID1WanSourceROIAnchor": {"input": {"required": {"latent": ["IMAGE"]}}, "output": ["IMAGE"]}})

    def test_execute_preflight_requires_an_empty_comfy_queue(self):
        validate = getattr(submit_prepared, "validate_fid1_queue", None)
        self.assertTrue(callable(validate), "FID1 execute must reject a non-empty ComfyUI queue before writing an attempt marker")
        self.assertEqual(validate({"queue_running": [], "queue_pending": []}), {"running": 0, "pending": 0})
        with self.assertRaisesRegex(ValueError, "queue|job"):
            validate({"queue_running": [{"prompt_id": "busy"}], "queue_pending": []})


if __name__ == "__main__":
    unittest.main()
