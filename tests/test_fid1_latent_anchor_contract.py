import unittest

import torch

from scripts.fid1_wan_latent_anchor_node import anchor_future_rois


ROI = [{"id": "face", "x0": 0.25, "y0": 0.25, "x1": 0.50, "y1": 0.50}]


def wan_latent(time_slots=13, channels=48):
    samples = torch.zeros((1, channels, time_slots, 8, 8), dtype=torch.float32)
    samples[:, :, 0] = 2
    samples[:, :, 1:] = 4
    mask = torch.ones((1, 1, time_slots, 8, 8), dtype=torch.float32)
    mask[:, :, 0] = 0
    return {"samples": samples, "noise_mask": mask, "metadata": {"type": "Wan22"}}


class TestFID1LatentAnchorContract(unittest.TestCase):
    def test_accepts_real_wan_latent_and_preserves_source_metadata(self):
        result = anchor_future_rois(wan_latent(), ROI)
        self.assertEqual(tuple(result["samples"].shape), (1, 48, 13, 8, 8))
        self.assertEqual(result["metadata"], {"type": "Wan22"})
        self.assertEqual(float(result["samples"][:, :, 1:, 2:4, 2:4].mean()), 2.0)

    def test_rejects_video_frame_count_as_latent_time(self):
        with self.assertRaisesRegex(ValueError, "13 Wan latent"):
            anchor_future_rois(wan_latent(time_slots=49), ROI)

    def test_rejects_wrong_wan_channel_count(self):
        with self.assertRaisesRegex(ValueError, "48 Wan latent channels"):
            anchor_future_rois(wan_latent(channels=16), ROI)

    def test_rejects_mask_shape_mismatch(self):
        latent = wan_latent()
        latent["noise_mask"] = torch.ones((1, 1, 13, 8, 7), dtype=torch.float32)
        with self.assertRaisesRegex(ValueError, "noise_mask shape"):
            anchor_future_rois(latent, ROI)


if __name__ == "__main__":
    unittest.main()
