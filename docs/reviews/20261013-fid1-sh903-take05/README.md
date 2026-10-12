# FID1 SH903 take05 controlled comparison

Scope: `T1_SOURCE_ONLY`. This is a local source-fidelity diagnostic, not an EP001/LOOKREEL shot, final-cut asset, or approval.

## Control design

- Baseline: SH903 take03 (`POSE_V2_576`) with the same approved source SHA, positive/negative prompts, seed 2026100803, Wan2.2-TI2V-5B, 576x1024, 49 frames / 24fps, and sampler budget. Baseline workflow SHA: `4b6172484b33c3de3998a986118250deced15f9743b036c781d8d29188947d9c`.
- Treatment: SH903 take05 (`SH903_FID1_V003`) adds only the FID1 face-ROI future-latent anchor. The only workflow graph changes are the FID1 node and Wan-latent-to-FID1-to-KSampler connection; the SaveVideo prefix names the take.
- take04 is retained as the earlier confounded comparison: it changed the prompt as well as enabling FID1.

## Runtime and media QA

- ComfyUI reported `success`; prompt id `f5658cf7-ffcb-498e-8c88-0b91049cd785`; seed 2026100803; Wan2.2-TI2V-5B; 576x1024; 49 frames / 24fps.
- Elapsed `359.032` seconds; sampled peak VRAM `11395 MiB`; minimum sampled available RAM `877928448 bytes`.
- Output SHA256 `68bd4119f675628358244d27e81d867ed69983895f4168a6819a330958ef4403`; ffprobe contract and full decode passed. Automated QA does not grant visual acceptance.

## Visual result

Assistant review of all49 and first/middle/last sheets finds severe speckled mosaic across the scene from frame 2 onward, with the two face regions appearing as static rectangular patches. This is `CHANGES_REQUIRED` and materially worse than take03's coherent scene. Jovi full-playback review is still pending; no human approval is recorded. SH901 and SH902 remain blocked and were not run.

The contact sheets and take03 control are included for review. `review.html` plays both MP4 files side by side when a local browser supports them.
