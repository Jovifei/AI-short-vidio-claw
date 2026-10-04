# P1_4070S_BASELINE — Wan2.2 5B first smoke

> measured_at: 2026-10-04 18:36–18:41 Asia/Shanghai
> git_main at run time: b38c235946623708cb807f26e80d803d94932f6c
> This file records one measured run. It is not a P1A PASS (no 10-run stability, no probe script).

## Run

- Result: **success**
- Error: none
- ComfyUI: `http://127.0.0.1:8188` still the existing process PID 333664 (not relaunched, no second server)
- `/system_stats` before submit: comfyui 0.38.0, pytorch 2.14.1+cu130, templates 0.11.70, frontend 1.53.6
- Queue before submit: empty. Queue after: empty
- prompt_id: `d0d5c325-9e52-4a49-9f89-7d7fd9095b6c`
- HTTP POST `/prompt`: 200, `node_errors` {}

## Workflow

- Official template file (shipped in this install, not a repo file): `local/comfyui/image/venv/Lib/site-packages/comfyui_workflow_templates_json/templates/video_wan2_2_5B_ti2v.json`
- Template id: `91f6bbe2-ed41-4fd6-bac7-71d5b5864ecb`
- SHA256: `8c13b61fdb42562052b2d5d867b354f7cf4d5ef528c98ed6847bdddc3ddb3d16`
- Size: 15015 bytes
- Submitted as API prompt converted from that graph. Not a GUI Template Library click. At run time it was not yet saved under `workflows/video/lab/`. The later Step 2 export is recorded below. `scripts/p1_comfy_probe.py` was not written.

## Graph actually executed

Nodes: UNETLoader, CLIPLoader, VAELoader, ModelSamplingSD3, CLIPTextEncode positive, CLIPTextEncode negative, Wan22ImageToVideoLatent, KSampler, VAEDecode, CreateVideo, SaveVideo.

LoadImage (node 56) in the template has `mode` 4 (bypass) and was not included. `start_image` was omitted. This run is the template's text-to-video path, not I2V.

Unchanged from the template widgets:

- diffusion: `wan2.2_ti2v_5B_fp16.safetensors`, weight_dtype `default`
- text encoder: `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, type `wan`, device `default`
- vae: `wan2.2_vae.safetensors`
- ModelSamplingSD3 shift: 8
- KSampler: steps 20, cfg 5, sampler `uni_pc`, scheduler `simple`, denoise 1
- seed: 898471028164125 (template's seed number; template control was `randomize`, this run fixed that one seed)
- CreateVideo fps: 24
- Positive and negative text: the template strings, unchanged

Changed from the template widgets, for this one small run:

- Wan22ImageToVideoLatent: template 1280x704x121 -> **480x832x33**. Both 480 and 832 are legal (`step` 32). 33 is legal (`step` 4, and `(length-1)` divisible by 4).
- SaveVideo `filename_prefix`: template `video/ComfyUI` -> `video/p1a_wan22_5b_smoke`
- format/codec: `auto` / `auto` (same as the template widgets)

## Output

- Path: `E:\project\AI-short-vidio-claw\local\comfyui\image\ComfyUI\output\video\p1a_wan22_5b_smoke_00001_.mp4`
- Size: 200534 bytes
- ffprobe: h264, 480x832, 33 frames, 24/1 fps, duration 1.375 s
- mtime: 2026-10-04 18:41:42 Asia/Shanghai

## Time

- Comfy `execution_start`: 2026-10-04 18:36:11.793 Asia/Shanghai (timestamp 1791110171793)
- Comfy `execution_success`: 2026-10-04 18:41:42.604 Asia/Shanghai (timestamp 1791110502604)
- Elapsed execution: **330.811 s**
- Local poller wall clock until history was observed: 335.2 s

## VRAM / RAM

- GPU: NVIDIA GeForce RTX 4070 SUPER, nvidia-smi memory.total 12282 MiB
- nvidia-smi `memory.used` sampled about every 5.2 s during the run (66 samples)
- First sample, before weights were resident: **3914 MiB**
- Peak sampled `memory.used`: **11374 MiB**
- This is a sample peak, not a continuous hardware max
- Minimum physical RAM available during the run (GlobalMemoryStatusEx ullAvailPhys): **10481664 bytes**
- RAM total: 34164097024 bytes
- Peak system RAM was not measured as a counter; only minimum available physical memory was sampled
- No OOM, no GPU reset, process PID stayed 333664

## API workflow export (stage Step 2)

- exported_at: 2026-10-04 18:45 Asia/Shanghai
- Method: `GET /history/d0d5c325-9e52-4a49-9f89-7d7fd9095b6c`, saved `prompt[2]` (the API graph). Parsed JSON equals the live history object. Not a GUI Save (API Format) click. Not hand-rebuilt. No second job submitted. Listener stayed PID 333664; no second ComfyUI.
- Path: `workflows/video/lab/VID_wan22_5b_p1a_v001.json`
- SHA256: `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`
- Size: 2937 bytes
- Nodes: 37 UNETLoader, 38 CLIPLoader, 39 VAELoader, 48 ModelSamplingSD3, 6 CLIPTextEncode, 7 CLIPTextEncode, 55 Wan22ImageToVideoLatent, 3 KSampler, 8 VAEDecode, 57 CreateVideo, 58 SaveVideo
- Same graph as this smoke, including 480x832x33, seed 898471028164125, and filename_prefix `video/p1a_wan22_5b_smoke`. LoadImage node 56 is absent.
- Sibling metadata required by `workflows/README.md`: `workflows/video/lab/VID_wan22_5b_p1a_v001.yaml`

## Not done

- No second job
- No 14B, GGUF, or WanGP
- No I2V (`start_image` not connected; LoadImage was not added back)
- No `scripts/p1_comfy_probe.py` (stage Step 3; not started)
- No L1-L4 ladder and no 10-run stability
- P1A PASS conditions (10 serial runs, p50/p95) are not met
