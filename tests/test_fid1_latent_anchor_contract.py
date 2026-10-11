import unittest

try:
    from scripts.fid1_wan_latent_anchor_node import validate_latent_shape
except ImportError:
    from fid1_wan_latent_anchor_node import validate_latent_shape


class Fake:
    def __init__(self, shape, dtype='float32', device='cpu'):
        self.shape = shape
        self.dtype = dtype
        self.device = device


class TestFID1LatentAnchorContract(unittest.TestCase):
    def test_accepts_wan_shape(self):
        source = Fake((1, 48, 13, 64, 36))
        generated = Fake((1, 48, 13, 64, 36))
        mask = Fake((1, 1, 13, 64, 36))
        validate_latent_shape(source, generated, mask)

    def test_rejects_video_frame_confusion(self):
        source = Fake((1, 48, 49, 64, 36))
        generated = Fake((1, 48, 49, 64, 36))
        mask = Fake((1, 1, 49, 64, 36))
        validate_latent_shape(source, generated, mask)

    def test_rejects_channel_change(self):
        source = Fake((1, 16, 13, 64, 36))
        generated = Fake((1, 16, 13, 64, 36))
        mask = Fake((1, 1, 13, 64, 36))
        with self.assertRaises(ValueError):
            validate_latent_shape(source, generated, mask)

    def test_rejects_shape_mismatch(self):
        source = Fake((1, 48, 13, 64, 36))
        generated = Fake((1, 48, 13, 64, 35))
        mask = Fake((1, 1, 13, 64, 36))
        with self.assertRaises(ValueError):
            validate_latent_shape(source, generated, mask)


if __name__ == '__main__':
    unittest.main()
