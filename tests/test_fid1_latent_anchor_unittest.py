import unittest
import torch

from scripts.fid1_latent_anchor import ROI, roi_mask, anchor_source_latent


class TestFID1LatentAnchor(unittest.TestCase):
    def test_wan_shape_and_roi_mask(self):
        latent = torch.zeros((1, 48, 13, 64, 36))
        mask = roi_mask(latent, ROI(0.1, 0.1, 0.3, 0.3))
        self.assertEqual(tuple(mask.shape), (1, 1, 13, 64, 36))
        self.assertGreater(float(mask.mean()), 0)
        self.assertLess(float(mask.mean()), 1)

    def test_anchor_only_changes_masked_region(self):
        generated = torch.ones((1, 48, 13, 8, 8))
        source = torch.zeros_like(generated)
        mask = torch.zeros((1, 1, 13, 8, 8))
        mask[:, :, :, 2:4, 2:4] = 1
        out = anchor_source_latent(generated, source, mask)
        self.assertEqual(float(out[:, :, :, 2, 2].mean()), 0)
        self.assertEqual(float(out[:, :, :, 0, 0].mean()), 1)

    def test_reject_wrong_channels(self):
        with self.assertRaises(ValueError):
            roi_mask(torch.zeros((1, 16, 13, 8, 8)), ROI(0, 0, 1, 1))

    def test_reject_shape_mismatch(self):
        with self.assertRaises(ValueError):
            anchor_source_latent(torch.zeros((1, 48, 13, 8, 8)), torch.zeros((1, 48, 13, 7, 8)), torch.zeros((1, 1, 13, 8, 8)))


if __name__ == '__main__':
    unittest.main()
