#!/usr/bin/env python3
"""Bounded FID1 latent anchoring primitive.

This module does NOT claim identity locking. It implements only a measurable
candidate intervention for Wan22ImageToVideoLatent experiments:
- keep a source-encoded latent ROI for selected face regions
- leave non-ROI latent areas available for generation
- produce explicit shape/mask diagnostics

GPU execution remains local. This file never replaces generated frames or does
post-process face swapping.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Tuple

import torch


@dataclass(frozen=True)
class ROI:
    x0: float
    y0: float
    x1: float
    y1: float

    def validate(self) -> None:
        values = (self.x0, self.y0, self.x1, self.y1)
        if not all(0.0 <= v <= 1.0 for v in values):
            raise ValueError("ROI must be normalized")
        if not (self.x0 < self.x1 and self.y0 < self.y1):
            raise ValueError("invalid ROI bounds")


def source_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def roi_mask(latent: torch.Tensor, roi: ROI) -> torch.Tensor:
    """Create [B,1,T,H,W] mask for Wan latent shape [B,48,T,H,W]."""
    roi.validate()
    if latent.ndim != 5 or latent.shape[1] != 48:
        raise ValueError("expected Wan22 latent [B,48,T,H,W]")
    b, _, t, h, w = latent.shape
    mask = torch.zeros((b, 1, t, h, w), device=latent.device, dtype=latent.dtype)
    x0, x1 = int(w * roi.x0), max(int(w * roi.x1), int(w * roi.x0) + 1)
    y0, y1 = int(h * roi.y0), max(int(h * roi.y1), int(h * roi.y0) + 1)
    mask[:, :, :, y0:y1, x0:x1] = 1
    return mask


def anchor_source_latent(noised_latent: torch.Tensor, source_latent: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Apply bounded latent anchor.

    The caller controls when this is used during sampling. It does not freeze
    the whole frame. mask=1 keeps source latent, mask=0 keeps generated latent.
    """
    if noised_latent.shape != source_latent.shape:
        raise ValueError("latent shape mismatch")
    if mask.shape != (noised_latent.shape[0], 1, *noised_latent.shape[2:]):
        raise ValueError("mask shape mismatch")
    return source_latent * mask + noised_latent * (1.0 - mask)


def diagnostics(latent: torch.Tensor, mask: torch.Tensor) -> dict:
    if latent.ndim != 5:
        raise ValueError("invalid latent rank")
    return {
        "shape": list(latent.shape),
        "channels": latent.shape[1],
        "frames": latent.shape[2],
        "mask_shape": list(mask.shape),
        "anchored_ratio": float(mask.mean().item()),
    }
