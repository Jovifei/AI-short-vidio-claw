"""Real CPU Tensor regression for Comfy's intermediate-to-sampling boundary.

The MODEL interface uses the existing test scaffold. No weights, CUDA tensors,
GPU inference, source approvals or visual decisions are created by these tests.
"""
import json
from pathlib import Path
import unittest

import torch
import test_fid1_timestep_aware_node_unittest as fixtures
from scripts import fid1_wan_latent_anchor_node as node

ROIS = json.loads((Path(__file__).resolve().parents[1] /
                   'config/source_fidelity_trials/SH903_FID1_V008.json').read_text())['anchor_rois']


class SamplerBoundaryTests(unittest.TestCase):
    def prepare(self, target=torch.device('cpu')):
        samples = torch.full((1, 48, 13, 64, 36), 99., dtype=torch.float64)
        samples[:, :, 0] = 7.
        mask = torch.ones((1, 1, 13, 64, 36), dtype=torch.float64)
        mask[:, :, 0] = 0.
        latent = {'samples': samples, 'noise_mask': mask, 'boundary_fixture': True}
        patcher = fixtures.FakeModelPatcher(fixtures.WAN22())
        patcher.load_device = target
        model, prepared = node.FID1WanStrengthROIAnchor().anchor(patcher, latent, json.dumps(ROIS))
        return latent, prepared, model

    def test_float32_mask_after_intermediate_float64_is_accepted(self):
        original, prepared, model = self.prepare()
        # Comfy samplers.py: prepare_mask(..., load_device), followed by .float().
        sampling_mask = original['noise_mask'].to(device='cpu', dtype=torch.float32)
        try:
            mask = model.model_options['denoise_mask_function'](.5, sampling_mask)
        except ValueError as exc:
            self.fail('normal Comfy float32 mask migration was rejected: ' + str(exc))
        self.assertEqual(mask.dtype, torch.float32)
        self.assertAlmostEqual(float(mask[0, 0, 1, 16, 7]), .45, places=6)
        self.assertAlmostEqual(float(mask[0, 0, 1, 15, 18]), .35, places=6)
        self.assertTrue(torch.equal(mask[:, :, 0], torch.zeros_like(mask[:, :, 0])))
        self.assertTrue(torch.equal(mask[:, :, 1:, 0, 0], torch.ones_like(mask[:, :, 1:, 0, 0])))
        self.assertIs(prepared['noise_mask'], original['noise_mask'])
        self.assertEqual(original['noise_mask'].dtype, torch.float64)

    def test_float32_latent_noise_after_intermediate_float64_are_accepted(self):
        original, prepared, model = self.prepare()
        # Comfy CFGGuider.outer_sample converts both to load_device/float32.
        samples = prepared['samples'].to(device='cpu', dtype=torch.float32)
        noise = torch.ones_like(samples)
        try:
            scaled = model.object_patches['scale_latent_inpaint'](.25, noise, samples)
        except ValueError as exc:
            self.fail('normal Comfy float32 latent migration was rejected: ' + str(exc))
        expected = model.get_model_object('model_sampling').noise_scaling(.25, noise, samples)
        self.assertTrue(torch.equal(scaled[:, :, 1:, 16, 7], expected[:, :, 1:, 16, 7]))
        self.assertTrue(torch.equal(scaled[:, :, 0], samples[:, :, 0]))
        self.assertTrue(torch.equal(scaled[:, :, 1:, 0, 0], samples[:, :, 1:, 0, 0]))
        self.assertIs(prepared['noise_mask'], original['noise_mask'])

    def test_unknown_sampling_target_is_rejected_before_hooks_are_installed(self):
        for target in (None, 'cpu', torch.device('meta'), torch.device('cuda')):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'load_device'):
                self.prepare(target)

    def test_cpu_tensor_cannot_claim_a_different_model_sampling_device(self):
        # Declaring a CUDA target does not allocate any CUDA tensor or run GPU work.
        original, prepared, model = self.prepare(torch.device('cuda:0'))
        with self.assertRaisesRegex(ValueError, 'dtype/device'):
            model.model_options['denoise_mask_function'](.5, original['noise_mask'].float())
        samples = prepared['samples'].float()
        with self.assertRaisesRegex(ValueError, 'dtype/device'):
            model.object_patches['scale_latent_inpaint'](.25, torch.ones_like(samples), samples)
