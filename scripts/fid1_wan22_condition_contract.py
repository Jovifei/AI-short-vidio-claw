#!/usr/bin/env python3
"""FID1 Wan22 bounded condition contract.

This does not invent a ReferenceConditioning node. Wan22ImageToVideoLatent
already provides start_image encoding and noise_mask initialization. This
helper verifies that a prepared trial actually carries that existing condition
forward. It rejects metadata-only fidelity claims.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Wan22ConditionReport:
    model: str
    frames: int
    source_sha256: str
    start_image_encoded: bool
    noise_mask_present: bool

    @property
    def allowed(self) -> bool:
        return (
            self.model == "Wan2.2-TI2V-5B"
            and self.frames == 49
            and bool(self.source_sha256)
            and self.start_image_encoded
            and self.noise_mask_present
        )


def validate_trial(report: Wan22ConditionReport):
    if not report.allowed:
        raise ValueError(
            "FID1 requires existing Wan22 image latent condition and noise mask; "
            "prompt-only changes are rejected."
        )
    return True
