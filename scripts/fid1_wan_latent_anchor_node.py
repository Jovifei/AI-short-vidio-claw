"""Bounded Wan5B latent ROI anchoring primitive.

This is a narrow numerical intervention only:
- works on real Comfy LATENT dictionaries;
- preserves metadata;
- copies selected encoded source ROI into selected latent time regions;
- returns explicit noise_mask;
- rejects unsafe tensors.

It is not identity locking, reference conditioning, face swap, or visual QA.
"""
from __future__ import annotations

EXPECTED_CHANNELS = 48


def _shape5(x, name):
    if not hasattr(x, "shape") or len(x.shape) != 5:
        raise ValueError(f"{name} latent must be [B,48,T,H,W]")
    if x.shape[1] != EXPECTED_CHANNELS:
        raise ValueError(f"{name} latent channel must be 48")


def _finite(x, name):
    if not hasattr(x, "isfinite") or not bool(x.isfinite().all()):
        raise ValueError(f"{name} contains non-finite values")


def validate(source, generated, noise_mask):
    _shape5(source, "source")
    _shape5(generated, "generated")
    if source.shape != generated.shape:
        raise ValueError("source/generated latent shape mismatch")
    expected = (source.shape[0], 1, source.shape[2], source.shape[3], source.shape[4])
    if noise_mask.shape != expected:
        raise ValueError("noise mask shape mismatch")
    if source.dtype != generated.dtype or source.device != generated.device:
        raise ValueError("latent dtype/device mismatch")
    _finite(source, "source")
    _finite(generated, "generated")
    _finite(noise_mask, "noise_mask")
    if float(noise_mask.min()) < 0 or float(noise_mask.max()) > 1:
        raise ValueError("noise mask outside [0,1]")
    if bool((noise_mask == 1).all()):
        raise ValueError("full latent freeze is not allowed")


def anchor_future_roi(source_first_temporal, generated, noise_mask):
    """Initialize only selected future ROI with source encoded latent.

    The mask is supplied by graph construction. Unmasked regions remain
    generated so temporal motion is not replaced by a frozen full frame.
    """
    return merge_source_roi(source_first_temporal, generated, noise_mask)


def merge_source_roi(source, generated, noise_mask):
    validate(source, generated, noise_mask)
    return source * noise_mask + generated * (1 - noise_mask)


class FID1LatentROIMerge:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"source_latent": ("LATENT",), "generated_latent": ("LATENT",), "noise_mask": ("MASK",)}}

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "merge"
    CATEGORY = "FID1"

    def merge(self, source_latent, generated_latent, noise_mask):
        result = dict(generated_latent)
        result["samples"] = merge_source_roi(
            source_latent["samples"],
            generated_latent["samples"],
            noise_mask,
        )
        result["noise_mask"] = noise_mask
        return (result,)


NODE_CLASS_MAPPINGS = {"FID1LatentROIMerge": FID1LatentROIMerge}
