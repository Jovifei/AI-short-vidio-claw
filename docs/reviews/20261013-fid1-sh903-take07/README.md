# FID1 SH903 take07 soft-ROI comparison

Scope: `T1_SOURCE_ONLY`. This is a local diagnostic, not an EP001/LOOKREEL shot, final-cut asset, or user approval.

## Experiment

- Control is SH903 take05 (`SH903_FID1_V003`, hard binary ROI). Treatment is take07 (`SH903_FID1_V004`, 4-latent-cell feathered ROI).
- The approved source/hash, positive and negative prompts, seed 2026100803, Wan2.2-TI2V-5B, 576x1024, 49 frames / 24fps, ROI bounds, and sampler budget are unchanged. Only the ROI alpha edge treatment changes. The SaveVideo filename prefix is the take label.
- Feather alpha is 0 at the outer ROI border, then 0.25/0.5/0.75 inward, and 1 in the core. The pinned sampler uses continuous floating-point denoise masks.

## Runtime and media QA

- ComfyUI reported success for prompt id `933cd47e-9454-48ad-85bd-35e819d8be90`. Elapsed `377.966` seconds; sampled peak VRAM `10665 MiB; minimum sampled available RAM `109285376 bytes.
- Output SHA256 `f802325c659be0c72861c6360527818f9aa43ce356ef323f7c2b817bfd437062`; ffprobe contract and full decode passed.

## Visual status

The soft edge changes the hard face-tile seams, but the scene still collapses from frame 2 onward into dense calligraphic/speckled patterns and blurred character/background fragments. The result remains `CHANGES_REQUIRED`; Jovi playback and visual acceptance are pending. SH901 and SH902 remain blocked.

This bundle includes both control and treatment MP4s and all49 contact sheets. `review.html` plays the videos side by side when supported. The local full-playback field remains PENDING.
