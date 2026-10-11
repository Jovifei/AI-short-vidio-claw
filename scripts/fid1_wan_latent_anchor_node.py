"""Bounded Wan5B latent ROI anchoring primitive.

The node is intentionally conservative:
- operates on real Comfy LATENT dictionaries;
- preserves LATENT metadata;
- initializes only selected future ROI regions from encoded source latent;
- returns an explicit noise mask for downstream sampling constraints;
- rejects invalid tensors instead of silently freezing or producing NaN.

This is not identity locking, reference conditioning, face swap, or a
replacement for visual QA.
"""
from __future__ import annotations

import math


EXPECTED_CHANNELS = 48


def _shape5(x, name):
    if not hasattr(x, "shape") or len(x.shape) != 5:
        raise ValueError(f"{name} latent must be [B,48,T,H,W]")
    if x.shape[1] != EXPECTED_CHANNELS:
        raise ValueError(f"{name} latent channel must be 48")


def _finite(x, name):
    try:
        if not bool(x.isfinite().all()):
            raise ValueError(f"{name} contains non-finite values")
    except AttributeError:
        raise ValueError(f"{name} must be a tensor")


def validate(source, generated, mask):
    _shape5(source, "source")
    _shape5(generated, "generated")
    if source.shape != generated.shape:
        raise ValueError("source/generated latent shape mismatch")
    if mask.shape != (source.shape[0], 1, source.shape[2], source.shape[3], source.shape[4]):
        raise ValueError("noise mask shape mismatch")
    if source.dtype != generated.dtype or source.device != generated.device:
        raise ValueError("latent dtype/device mismatch")
    _finite(source, "source")
    _finite(generated, "generated")
    _finite(mask, "mask")
    if float(mask.min()) < 0 or float(mask.max()) > 1:
        raise ValueError("mask outside [0,1]")
    if bool((mask == 1).all()):
        raise ValueError("full latent freeze is not allowed")


def merge_source_roi(source, generated, noise_mask):
    """Anchor only selected latent areas.

    mask=1 selects source encoded latent; mask=0 leaves generated latent.
    The returned tensor keeps future non-ROI generation available.
    """
    validate(source, generated, noise_mask)
    return source * noise_mask + generated * (1 - noise_mask)


class FID1LatentROIMerge:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_latent": ("LATENT",),
                "generated_latent": ("LATENT",),
                "noise_mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "merge"
    CATEGORY = "FID1"

    def merge(self, source_latent, generated_latent, noise_mask):
        samples = merge_source_roi(
            source_latent["samples"],
            generated_latent["samples"],
            noise_mask,
        )
        result = dict(generated_latent)
        result["samples"] = samples
        result["noise_mask"] = noise_mask
        return (result,)


NODE_CLASS_MAPPINGS = {"FID1LatentROIMerge": FID1LatentROIMerge}
