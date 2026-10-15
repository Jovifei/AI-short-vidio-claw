import json
import unittest

import torch

from scripts import fid1_wan_latent_anchor_node as fid1


def timestep_node(testcase):
    node_class = getattr(fid1, "FID1WanTimestepAwareROIAnchor", None)
    testcase.assertIsNotNone(node_class, "the timestep-aware FID1 node is missing")
    return node_class


class FlowSampling:
    def __init__(self, noise_scale=0.75):
        self.noise_scale = noise_scale

    def noise_scaling(self, sigma, noise, latent_image, max_denoise=False):
        sigma = torch.as_tensor(sigma, dtype=latent_image.dtype, device=latent_image.device)
        while sigma.ndim < latent_image.ndim:
            sigma = sigma.unsqueeze(-1)
        return sigma * self.noise_scale * noise + (1.0 - sigma) * latent_image


class WAN22:
    def __init__(self):
        self.model_sampling = FlowSampling()

    def scale_latent_inpaint(self, sigma, noise, latent_image, **kwargs):
        return latent_image


class FakeModelPatcher:
    def __init__(self, model):
        self.model = model
        self.load_device = torch.device("cpu")
        self.model_options = {}
        self.object_patches = {}

    def clone(self):
        clone = FakeModelPatcher(self.model)
        clone.load_device = self.load_device
        clone.model_options = dict(self.model_options)
        clone.object_patches = dict(self.object_patches)
        return clone

    def set_model_denoise_mask_function(self, function):
        self.model_options["denoise_mask_function"] = function

    def add_object_patch(self, name, value):
        self.object_patches[name] = value

    def get_model_object(self, name):
        if name in self.object_patches:
            return self.object_patches[name]
        return getattr(self.model, name)


def sample_latent():
    samples = torch.full((1, 48, 13, 4, 6), 99.0, dtype=torch.float32)
    samples[:, :, 0] = torch.arange(48, dtype=torch.float32).view(1, 48, 1, 1)
    noise_mask = torch.ones((1, 1, 13, 4, 6), dtype=torch.float32)
    noise_mask[:, :, 0] = 0.0
    return {
        "samples": samples,
        "noise_mask": noise_mask,
        "batch_index": [0],
        "fid1_test_metadata": {"owner": "wan"},
    }


ROIS = [{"id": "FACE", "x0": 1 / 3, "y0": 1 / 4, "x1": 2 / 3, "y1": 3 / 4}]


class TestFID1TimestepAwareROIAnchor(unittest.TestCase):
    def test_node_declares_model_and_latent_ports(self):
        node = timestep_node(self)
        self.assertEqual(node.RETURN_TYPES, ("MODEL", "LATENT"))
        required = node.INPUT_TYPES()["required"]
        self.assertEqual(required["model"], ("MODEL",))
        self.assertEqual(required["latent"], ("LATENT",))
        self.assertEqual(required["roi_boxes_json"][0], "STRING")

    def test_preserves_wan_mask_and_latent_metadata_while_copying_only_future_roi(self):
        node = timestep_node(self)
        latent = sample_latent()
        original_samples = latent["samples"].clone()
        original_mask = latent["noise_mask"].clone()
        original_patcher = FakeModelPatcher(WAN22())

        model_out, latent_out = node().anchor(original_patcher, latent, json.dumps(ROIS))

        self.assertIsNot(model_out, original_patcher)
        self.assertEqual(original_patcher.model_options, {})
        self.assertIs(latent_out["noise_mask"], latent["noise_mask"])
        self.assertTrue(torch.equal(latent_out["noise_mask"], original_mask))
        self.assertTrue(torch.equal(latent_out["samples"][:, :, 0], original_samples[:, :, 0]))
        self.assertTrue(torch.equal(latent_out["samples"][:, :, 1:, 1:3, 2:4], original_samples[:, :, :1, 1:3, 2:4].expand(-1, -1, 12, -1, -1)))
        self.assertTrue(torch.equal(latent_out["samples"][:, :, 1:, 0, 0], original_samples[:, :, 1:, 0, 0]))
        self.assertEqual(latent_out["batch_index"], latent["batch_index"])
        self.assertIs(latent_out["fid1_test_metadata"], latent["fid1_test_metadata"])

    def test_runtime_denoise_mask_is_roi_local_and_does_not_mutate_wan_condition_mask(self):
        node = timestep_node(self)
        latent = sample_latent()
        base_mask = latent["noise_mask"].clone()
        model_out, _ = node().anchor(FakeModelPatcher(WAN22()), latent, json.dumps(ROIS))
        mask_function = model_out.model_options["denoise_mask_function"]

        sampler_mask = mask_function(torch.tensor([0.5]), base_mask, extra_options={})

        self.assertTrue(torch.equal(base_mask, latent["noise_mask"]))
        self.assertTrue(torch.equal(sampler_mask[:, :, 0], torch.zeros_like(sampler_mask[:, :, 0])))
        self.assertTrue(torch.equal(sampler_mask[:, :, 1:, 1:3, 2:4], torch.zeros((1, 1, 12, 2, 2))))
        self.assertTrue(torch.equal(sampler_mask[:, :, 1:, 0, 0], torch.ones((1, 1, 12))))
        expanded_mask = base_mask.repeat(1, 48, 1, 1, 1)
        try:
            expanded_sampler_mask = mask_function(torch.tensor([0.5]), expanded_mask, extra_options={})
        except ValueError as exc:
            self.fail(f"ComfyUI expanded one-channel denoise mask to latent channels: {exc}")
        self.assertEqual(tuple(expanded_sampler_mask.shape), tuple(expanded_mask.shape))
        self.assertTrue(torch.equal(expanded_sampler_mask[:, :, 1:, 1:3, 2:4], torch.zeros((1, 48, 12, 2, 2))))
        self.assertTrue(torch.equal(expanded_sampler_mask[:, :, 1:, 0, 0], torch.ones((1, 48, 12))))
        with self.assertRaisesRegex(ValueError, "shape"):
            mask_function(torch.tensor([0.5]), base_mask[:, :, :, :, :-1], extra_options={})
        with self.assertRaisesRegex(ValueError, "channel"):
            mask_function(torch.tensor([0.5]), base_mask.repeat(1, 47, 1, 1, 1), extra_options={})
        divergent_channels = base_mask.repeat(1, 48, 1, 1, 1)
        divergent_channels[:, 1, 2, 0, 0] = 0.0
        with self.assertRaisesRegex(ValueError, "repeated"):
            mask_function(torch.tensor([0.5]), divergent_channels, extra_options={})
        invalid = base_mask.clone()
        invalid[:, :, 2, 0, 0] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            mask_function(torch.tensor([0.5]), invalid, extra_options={})

    def test_scale_latent_inpaint_uses_flow_noise_at_current_sigma_only_for_future_roi(self):
        node = timestep_node(self)
        latent = sample_latent()
        model_out, latent_out = node().anchor(FakeModelPatcher(WAN22()), latent, json.dumps(ROIS))
        noise = torch.full_like(latent_out["samples"], 2.0)
        sigma = torch.tensor([0.25])
        patch = model_out.object_patches["scale_latent_inpaint"]

        result = patch(sigma, noise, latent_out["samples"])
        expected = model_out.model.model_sampling.noise_scaling(sigma, noise, latent_out["samples"])

        self.assertTrue(torch.equal(result[:, :, 0], latent_out["samples"][:, :, 0]))
        self.assertTrue(torch.equal(result[:, :, 1:, 1:3, 2:4], expected[:, :, 1:, 1:3, 2:4]))
        self.assertTrue(torch.equal(result[:, :, 1:, 0, 0], latent_out["samples"][:, :, 1:, 0, 0]))
        with self.assertRaisesRegex(ValueError, "shape"):
            patch(sigma, noise[:, :, :, :, :-1], latent_out["samples"])

    def test_uses_modelpatcher_sampling_object_patch_from_model_sampling_sd3(self):
        node = timestep_node(self)
        latent = sample_latent()
        original_patcher = FakeModelPatcher(WAN22())
        effective_sampling = FlowSampling(noise_scale=0.25)
        original_patcher.add_object_patch("model_sampling", effective_sampling)
        model_out, latent_out = node().anchor(original_patcher, latent, json.dumps(ROIS))
        patch = model_out.object_patches["scale_latent_inpaint"]
        sigma = torch.tensor([0.25])
        noise = torch.full_like(latent_out["samples"], 2.0)

        result = patch(sigma, noise, latent_out["samples"])
        expected = effective_sampling.noise_scaling(sigma, noise, latent_out["samples"])

        self.assertTrue(torch.equal(result[:, :, 1:, 1:3, 2:4], expected[:, :, 1:, 1:3, 2:4]))

    def test_feather_alpha_is_applied_once_to_source_and_sampler_preservation(self):
        node = timestep_node(self)
        samples = torch.full((1, 48, 13, 14, 14), 99.0, dtype=torch.float32)
        samples[:, :, 0] = 7.0
        noise_mask = torch.ones((1, 1, 13, 14, 14), dtype=torch.float32)
        noise_mask[:, :, 0] = 0.0
        latent = {"samples": samples, "noise_mask": noise_mask, "owner": "test"}
        rois = [{"id": "FACE", "x0": 1/14, "y0": 1/14, "x1": 13/14, "y1": 13/14, "feather_latent": 4}]
        model_out, latent_out = node().anchor(FakeModelPatcher(WAN22()), latent, json.dumps(rois))
        mask_fn = model_out.model_options["denoise_mask_function"]
        sampler_mask = mask_fn(torch.tensor([0.5]), latent_out["noise_mask"], extra_options={})

        # At (t=1,y=2,x=6), alpha=0.25; source bytes stay complete and
        # KSampler's post-CFG blend applies that alpha once.
        self.assertEqual(float(latent_out["samples"][0, 0, 1, 2, 6]), 7.0)
        self.assertEqual(float(sampler_mask[0, 0, 1, 2, 6]), 0.75)
        model_x0 = torch.zeros_like(latent_out["samples"])
        ksampler_out = model_x0 * sampler_mask + latent_out["samples"] * (1.0 - sampler_mask)
        self.assertAlmostEqual(float(ksampler_out[0, 0, 1, 2, 6]), 1.75)

        scale = model_out.object_patches["scale_latent_inpaint"]
        sigma = torch.tensor([0.25])
        noise = torch.full_like(latent_out["samples"], 2.0)
        noised = scale(sigma, noise, latent_out["samples"])
        expected_source = model_out.get_model_object("model_sampling").noise_scaling(sigma, noise, latent_out["samples"])
        self.assertTrue(torch.equal(noised[0, 0, 1, 2, 6], expected_source[0, 0, 1, 2, 6]))
        self.assertEqual(float(latent_out["samples"][0, 0, 1, 1, 1]), 99.0)

    def test_rejects_non_wan_model_and_changed_base_mask(self):
        node = timestep_node(self)

        class OtherModel:
            model_sampling = FlowSampling()

            def scale_latent_inpaint(self, sigma, noise, latent_image, **kwargs):
                return latent_image

        with self.assertRaisesRegex(ValueError, "WAN22|Wan2.2"):
            node().anchor(FakeModelPatcher(OtherModel()), sample_latent(), json.dumps(ROIS))

        latent = sample_latent()
        latent["noise_mask"][:, :, 3, 0, 0] = 0.5
        with self.assertRaisesRegex(ValueError, "noise_mask|mask"):
            node().anchor(FakeModelPatcher(WAN22()), latent, json.dumps(ROIS))


if __name__ == "__main__":
    unittest.main()
