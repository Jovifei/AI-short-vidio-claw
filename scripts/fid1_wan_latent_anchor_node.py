"""Bounded Wan5B latent ROI anchoring primitive.

This is intentionally isolated from core ComfyUI. It does not freeze the full
frame and does not claim identity locking. It only replaces selected latent
regions with source latent values before sampling.
"""
from __future__ import annotations


def _check_torch(t):
    if t is None:
        raise RuntimeError("torch is required only when executing latent anchoring")


def validate_latent_shape(source, generated, mask):
    for name, x in (("source", source), ("generated", generated)):
        if len(x.shape) != 5:
            raise ValueError(f"{name} latent must be [B,48,T,H,W]")
        if x.shape[1] != 48:
            raise ValueError(f"{name} latent channel must be 48")
    if source.shape != generated.shape:
        raise ValueError("source/generated latent shape mismatch")
    if mask.shape != (source.shape[0], 1, source.shape[2], source.shape[3], source.shape[4]):
        raise ValueError("mask shape mismatch")
    if source.dtype != generated.dtype or source.device != generated.device:
        raise ValueError("latent dtype/device mismatch")


def anchor(source_latent, generated_latent, roi_mask):
    validate_latent_shape(source_latent, generated_latent, roi_mask)
    if roi_mask.min() < 0 or roi_mask.max() > 1:
        raise ValueError("mask outside [0,1]")
    return source_latent * roi_mask + generated_latent * (1 - roi_mask)


class FID1LatentROIMerge:
    """Optional Comfy custom-node wrapper.

    Input/output are plain latent tensors. The workflow must connect this node
    explicitly between Wan latent preparation and sampling. It cannot be
    enabled by prompt changes alone.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"source_latent": ("LATENT",), "generated_latent": ("LATENT",), "roi_mask": ("MASK",)}}

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "merge"
    CATEGORY = "FID1"

    def merge(self, source_latent, generated_latent, roi_mask):
        latent = anchor(source_latent["samples"], generated_latent["samples"], roi_mask)
        return ({"samples": latent},)


NODE_CLASS_MAPPINGS = {"FID1LatentROIMerge": FID1LatentROIMerge}
