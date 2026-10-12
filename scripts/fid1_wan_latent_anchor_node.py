"""ComfyUI node for preserving a small source ROI in Wan2.2 image-to-video."""
from __future__ import annotations

import json
import math

import torch


EXPECTED_CHANNELS = 48
EXPECTED_TIME_SLOTS = 13


def _validate_rois(rois, width, height):
    if not isinstance(rois, list) or not rois:
        raise ValueError("at least one normalized ROI is required")

    parsed = []
    seen = set()
    for roi in rois:
        if not isinstance(roi, dict) or set(roi) != {"id", "x0", "y0", "x1", "y1"}:
            raise ValueError("ROI must contain exactly id, x0, y0, x1, y1")
        name = roi["id"]
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("ROI ids must be non-empty and unique")
        seen.add(name)
        coords = tuple(roi[key] for key in ("x0", "y0", "x1", "y1"))
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in coords):
            raise ValueError("ROI coordinates must be finite numbers")
        x0, y0, x1, y1 = coords
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            raise ValueError("ROI bounds must be ordered within [0,1]")
        left = max(0, min(width - 1, math.floor(x0 * width)))
        top = max(0, min(height - 1, math.floor(y0 * height)))
        right = max(left + 1, min(width, math.ceil(x1 * width)))
        bottom = max(top + 1, min(height, math.ceil(y1 * height)))
        parsed.append((left, top, right, bottom))
    return parsed


def anchor_future_rois(latent, rois):
    """Copy the encoded first latent into future ROIs and freeze only those cells.

    ComfyUI treats ``noise_mask`` as a denoise mask: 1 samples the model output;
    0 preserves the latent. Wan22ImageToVideoLatent provides a zero first slot
    and ones for the future slots. This operation keeps that first-slot lock,
    writes source values into selected future cells, and multiplies the base
    denoise mask by the inverse anchor mask.
    """
    if not isinstance(latent, dict):
        raise ValueError("expected a ComfyUI LATENT dictionary")
    samples = latent.get("samples")
    noise_mask = latent.get("noise_mask")
    if not isinstance(samples, torch.Tensor) or samples.ndim != 5:
        raise ValueError("samples must be a rank-5 Wan tensor [B,48,T,H,W]")
    if samples.shape[0] != 1 or samples.shape[1] != EXPECTED_CHANNELS:
        raise ValueError("FID1 requires batch 1 and 48 Wan latent channels")
    if samples.shape[2] != EXPECTED_TIME_SLOTS:
        raise ValueError("49 video frames must use 13 Wan latent time slots")
    if not samples.is_floating_point() or not bool(torch.isfinite(samples).all()):
        raise ValueError("samples must be finite floating-point values")
    expected_mask_shape = (samples.shape[0], 1, samples.shape[2], samples.shape[3], samples.shape[4])
    if not isinstance(noise_mask, torch.Tensor) or tuple(noise_mask.shape) != expected_mask_shape:
        raise ValueError("Wan noise_mask shape must be [1,1,13,H,W]")
    if noise_mask.device != samples.device or noise_mask.dtype != samples.dtype:
        raise ValueError("samples and noise_mask dtype/device must match")
    if not noise_mask.is_floating_point() or not bool(torch.isfinite(noise_mask).all()):
        raise ValueError("noise_mask must contain finite floating-point values")
    if bool((noise_mask < 0).any()) or bool((noise_mask > 1).any()):
        raise ValueError("noise_mask values must be within [0,1]")
    if not bool((noise_mask[:, :, 0] == 0).all()) or not bool((noise_mask[:, :, 1:] == 1).all()):
        raise ValueError("Wan source mask must preserve time slot 0 and denoise future slots")

    regions = _validate_rois(rois, samples.shape[4], samples.shape[3])
    anchor_mask = torch.zeros_like(noise_mask)
    anchored_samples = samples.clone()
    source_first = samples[:, :, :1]
    for left, top, right, bottom in regions:
        anchor_mask[:, :, 1:, top:bottom, left:right] = 1
        anchored_samples[:, :, 1:, top:bottom, left:right] = source_first[:, :, :, top:bottom, left:right].expand(
            -1, -1, EXPECTED_TIME_SLOTS - 1, -1, -1
        )

    anchored_noise_mask = noise_mask * (1 - anchor_mask)
    if not bool((anchored_noise_mask[:, :, 1:] > 0).any()):
        raise ValueError("ROI anchors would freeze all future denoise positions")
    if not bool(((noise_mask > 0) & (anchored_noise_mask == 0)).any()):
        raise ValueError("ROI anchors did not freeze any future source positions")

    result = dict(latent)
    result["samples"] = anchored_samples
    result["noise_mask"] = anchored_noise_mask
    return result


class FID1WanSourceROIAnchor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT",),
                "roi_boxes_json": ("STRING", {"default": "[]", "multiline": False}),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "anchor"
    CATEGORY = "FID1/Source Fidelity"

    def anchor(self, latent, roi_boxes_json):
        try:
            rois = json.loads(roi_boxes_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("roi_boxes_json must be valid JSON") from exc
        return (anchor_future_rois(latent, rois),)


NODE_CLASS_MAPPINGS = {"FID1WanSourceROIAnchor": FID1WanSourceROIAnchor}
NODE_DISPLAY_NAME_MAPPINGS = {"FID1WanSourceROIAnchor": "FID1 Wan Source ROI Anchor"}
