import unittest
import torch

from scripts.fid1_wan_latent_anchor_node import merge_source_roi


class TestFID1WanLatentAnchorNode(unittest.TestCase):
    def test_preserves_non_roi_generation(self):
        source = torch.zeros((1, 48, 13, 8, 8))
        generated = torch.ones_like(source)
        mask = torch.zeros((1, 1, 13, 8, 8))
        mask[:, :, :, 2:4, 2:4] = 1
        out = merge_source_roi(source, generated, mask)
        self.assertEqual(float(out[:, :, :, 2, 2].mean()), 0)
        self.assertEqual(float(out[:, :, :, 0, 0].mean()), 1)

    def test_rejects_nan(self):
        source = torch.zeros((1, 48, 13, 8, 8))
        generated = torch.zeros_like(source)
        generated[0, 0, 0, 0, 0] = float('nan')
        mask = torch.zeros((1, 1, 13, 8, 8))
        with self.assertRaises(ValueError):
            merge_source_roi(source, generated, mask)

    def test_rejects_full_freeze(self):
        source = torch.zeros((1, 48, 13, 8, 8))
        generated = torch.ones_like(source)
        mask = torch.ones((1, 1, 13, 8, 8))
        with self.assertRaises(ValueError):
            merge_source_roi(source, generated, mask)


if __name__ == '__main__':
    unittest.main()
