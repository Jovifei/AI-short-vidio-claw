# FID1 SH903 take04 audit bundle

Scope: `T1_SOURCE_ONLY`. This is a local Wan2.2-TI2V-5B diagnostic take for SH903; it is not an EP001/LOOKREEL shot and grants no production approval.

## Run evidence

- Source: approved `REFB02_01.png`, SHA256 `6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f`
- Profile: `SH903_FID1_V002`, seed `2026100803`, 576×1024, 49 frames / 24fps
- Runtime: ComfyUI 0.38.0 at source commit `6b747c0428c343e1417219641db93a4fb7cb69ae`; `FID1WanSourceROIAnchor` loaded and connected between Wan latent node 55 and KSampler node 3
- Result: Comfy reported success; elapsed 531.376 seconds; sampled peak GPU use 10,668MiB; minimum available RAM 39,043,072 bytes
- Media contract: H.264, 576×1024, 49 decoded frames, 24fps, 2.041667 seconds; full FFmpeg decode passed
- Output SHA256: `74ee23338678bc971042037a0ffb803be841a83db2387d14d12960287326fc72`

## Visual status

The assistant's all49 contact sheet and selected frames show severe mosaic/block artifacts from frame 2 onward and static rectangular character patches. The visual result is `CHANGES_REQUIRED`; Jovi's full playback and visual decision remain `PENDING`. The next-shot gate is closed, so SH901/SH902 are not prepared from this result.

The take03 comparison is not fully controlled: take04's profile uses a revised prompt as well as the new latent/mask intervention. Do not attribute the artifacts to the mask alone until a controlled review isolates that change.

This bundle is an audit copy only. `qa_report.json` and `runtime_evidence.json` keep runtime/media evidence separate from human acceptance. `visual_review_template.json` is blank and unapproved.
