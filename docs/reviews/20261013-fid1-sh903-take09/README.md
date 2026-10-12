# SH903 FID1 timestep-aware take09

## Status

- Runtime: **PASS**. One ComfyUI prompt completed successfully.
- Media: **PASS**. H.264, 576×1024, 49 frames, 24fps, 2.041667 seconds; full decode passed.
- Visual acceptance: **PENDING**. Jovi still needs to watch the complete clip and decide identity, costume, limbs/hands, motion and scene quality. The QA template remains unapproved.
- Scope: `T1_SOURCE_ONLY`. This output is not an EP001/LOOKREEL shot and does not unlock SH901, SH902 or the formal 30-shot plan.

## Controlled comparison

Take09 uses the same approved source SHA, positive/negative prompts, seed, Wan2.2-TI2V-5B, 576×1024, 49/24, sampler settings, ROI rectangles and four-cell feather as take07. The only intended change is the anchor strategy: keep Wan's original slot0/future `noise_mask`, apply ROI preservation in the cloned MODEL's KSampler hook, and noise the source latent through the active ModelSamplingSD3 flow schedule at each sigma. The graph validator freezes shift=8, sampling=flow and multiplier=1000.

The alpha=0.25 CPU regression confirms that the latent stores the complete source value where alpha is positive and KSampler applies alpha once; source weight is 0.25, not alpha squared. Comfy's actual `prepare_mask` expands the original one-channel mask to 48 channels; the runtime hook accepts that repeated mask while rejecting batch/time/spatial drift, other channel counts and divergent channel planes.

## Runtime evidence

- Prompt: `1edc8f9a-e40b-445e-b67e-a969a83d53d6`
- Elapsed: 719.809 seconds
- Peak sampled VRAM: 11,808 MiB
- Minimum sampled physical RAM available: 10,821,632 bytes
- Input SHA256: `6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f`
- Output SHA256: `dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8`
- Profile: `SH903_FID1_V005`; Comfy source commit: `6b747c0428c343e1417219641db93a4fb7cb69ae`.

Take05 and take07 remain visual failures: their contact sheets show scene-wide mosaic/pseudo-text artifacts. Take09's contact sheets show the scene remains coherent through all 49 frames without that scene-wide collapse. That comparison is preliminary image inspection, not a human acceptance decision; review the video and exact pixels before updating the pending status.

## Prior take08 attempt

Take08 was submitted once and failed before producing a video because Comfy passed a 48-channel repeated KSampler mask while the first hook version expected the original single channel. Its prompt was not retried. The failure record is summarized in `take08_attempt_summary.json`; take09 uses a new immutable directory after the channel-shape correction.

## Files

- `review.html`: side-by-side playable take05, take07 and take09 clips plus contact sheets.
- `take09.mp4`, `take09_first_middle_last.png`, `take09_all49.png`: candidate output and decoded frames.
- `job.json`, `workflow.json`, `profile.json`, `job_integrity.json`, `run_record.json`, `qa_report.json`: frozen input and execution/QA evidence.
- `take08_attempt_summary.json`: one failed, non-retried attempt summary.
