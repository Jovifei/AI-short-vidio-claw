import unittest

import torch

from scripts import fid1_wan_latent_anchor_node as fid1


def sample_latent():
    samples = torch.full((1, 48, 13, 4, 6), 99.0, dtype=torch.float32)
    samples[:, :, 0] = torch.arange(48, dtype=torch.float32).view(1, 48, 1, 1)
    noise_mask = torch.ones((1, 1, 13, 4, 6), dtype=torch.float32)
    noise_mask[:, :, 0] = 0
    return {
        "samples": samples,
        "noise_mask": noise_mask,
        "batch_index": [0],
        "fid1_test_metadata": {"owner": "wan"},
    }


class TestFID1WanLatentAnchorNode(unittest.TestCase):
    def test_feathered_roi_blends_latent_and_sampler_mask_by_distance(self):
        latent = sample_latent()
        latent["samples"] = torch.full((1, 48, 13, 14, 14), 99.0, dtype=torch.float32)
        latent["samples"][:, :, 0] = 7.0
        latent["noise_mask"] = torch.ones((1, 1, 13, 14, 14), dtype=torch.float32)
        latent["noise_mask"][:, :, 0] = 0.0
        original = latent["samples"].clone()
        rois = [{"id": "face", "x0": 1/14, "y0": 1/14, "x1": 13/14, "y1": 13/14,
                 "feather_latent": 4}]

        result = fid1.anchor_future_rois(latent, rois)

        self.assertTrue(torch.equal(result["samples"][:, :, 0], original[:, :, 0]))
        self.assertTrue(torch.allclose(result["samples"][0, 0, 1, 6, 1:6], torch.tensor([99.0, 76.0, 53.0, 30.0, 7.0])))
        self.assertTrue(torch.allclose(result["noise_mask"][0, 0, 1, 6, 1:6], torch.tensor([1.0, .75, .5, .25, 0.0])))
        self.assertEqual(float(result["samples"][0, 0, 1, 0, 0]), 99.0)
        self.assertEqual(float(result["noise_mask"][0, 0, 1, 0, 0]), 1.0)
        self.assertTrue(torch.equal(latent["samples"], original))
        self.assertEqual(result["batch_index"], latent["batch_index"])
        self.assertEqual(result["fid1_test_metadata"], latent["fid1_test_metadata"])

    def test_rejects_invalid_feather_width(self):
        for feather in (0.5, -1, 5, True):
            with self.subTest(feather=feather), self.assertRaisesRegex(ValueError, "feather_latent"):
                fid1.anchor_future_rois(sample_latent(), [{
                    "id": "face", "x0": 0.2, "y0": 0.2, "x1": 0.6, "y1": 0.6,
                    "feather_latent": feather,
                }])

    def test_copies_first_source_roi_to_future_latents_and_freezes_only_that_roi(self):
        latent = sample_latent()
        original = latent["samples"].clone()
        rois = [{"id": "face", "x0": 1 / 3, "y0": 1 / 4, "x1": 2 / 3, "y1": 3 / 4}]
        anchor = getattr(fid1, "anchor_future_rois", None)
        self.assertTrue(callable(anchor), "the FID1 future-ROI anchor operation is missing")

        result = anchor(latent, rois)

        self.assertTrue(torch.equal(result["samples"][:, :, 0], original[:, :, 0]))
        self.assertTrue(torch.equal(result["samples"][:, :, 1:, 1:3, 2:4], original[:, :, :1, 1:3, 2:4].expand(-1, -1, 12, -1, -1)))
        self.assertTrue(torch.equal(result["samples"][:, :, 1:, 0, 0], original[:, :, 1:, 0, 0]))
        self.assertTrue(torch.equal(result["noise_mask"][:, :, 0], latent["noise_mask"][:, :, 0]))
        self.assertTrue(torch.equal(result["noise_mask"][:, :, 1:, 1:3, 2:4], torch.zeros((1, 1, 12, 2, 2))))
        self.assertTrue(torch.equal(result["noise_mask"][:, :, 1:, 0, 0], torch.ones((1, 1, 12))))
        self.assertTrue(torch.equal(latent["samples"], original), "the input latent must remain unchanged")
        self.assertEqual(result["batch_index"], latent["batch_index"])
        self.assertEqual(result["fid1_test_metadata"], latent["fid1_test_metadata"])
        self.assertTrue(torch.any(result["noise_mask"] > 0), "non-ROI positions must remain generatable")

    def test_rejects_a_full_frame_anchor_that_would_freeze_the_video(self):
        latent = sample_latent()
        anchor = getattr(fid1, "anchor_future_rois", None)
        self.assertTrue(callable(anchor), "the FID1 future-ROI anchor operation is missing")
        with self.assertRaisesRegex(ValueError, "freeze|denoise|ROI"):
            anchor(latent, [{"id": "everything", "x0": 0, "y0": 0, "x1": 1, "y1": 1}])

    def test_rejects_invalid_tensor_values_and_shapes(self):
        anchor = getattr(fid1, "anchor_future_rois", None)
        self.assertTrue(callable(anchor), "the FID1 future-ROI anchor operation is missing")
        for value in (float("nan"), float("inf")):
            latent = sample_latent()
            latent["samples"][0, 0, 1, 0, 0] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite|non-finite"):
                anchor(latent, [{"id": "face", "x0": 0.2, "y0": 0.2, "x1": 0.4, "y1": 0.4}])

        bad_channel = sample_latent()
        bad_channel["samples"] = bad_channel["samples"][:, :16]
        with self.assertRaisesRegex(ValueError, "channel|48"):
            anchor(bad_channel, [{"id": "face", "x0": 0.2, "y0": 0.2, "x1": 0.4, "y1": 0.4}])

        bad_mask = sample_latent()
        bad_mask["noise_mask"] = bad_mask["noise_mask"][:, :, :, :, :-1]
        with self.assertRaisesRegex(ValueError, "shape"):
            anchor(bad_mask, [{"id": "face", "x0": 0.2, "y0": 0.2, "x1": 0.4, "y1": 0.4}])

    def test_rejects_bad_roi_and_full_freeze_mask(self):
        anchor = getattr(fid1, "anchor_future_rois", None)
        self.assertTrue(callable(anchor), "the FID1 future-ROI anchor operation is missing")
        with self.assertRaisesRegex(ValueError, "ROI|roi"):
            anchor(sample_latent(), [{"id": "bad", "x0": 0.8, "y0": 0.2, "x1": 0.4, "y1": 0.5}])

        frozen = sample_latent()
        frozen["noise_mask"].zero_()
        with self.assertRaisesRegex(ValueError, "freeze|denoise|source"):
            anchor(frozen, [{"id": "face", "x0": 0.2, "y0": 0.2, "x1": 0.4, "y1": 0.4}])


if __name__ == "__main__":
    unittest.main()
