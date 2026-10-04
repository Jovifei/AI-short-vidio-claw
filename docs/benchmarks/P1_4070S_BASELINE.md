# P1_4070S_BASELINE — Wan2.2 5B first smoke

> measured_at: 2026-10-04 18:36–18:41 Asia/Shanghai
> git_main at run time: b38c235946623708cb807f26e80d803d94932f6c
> This file records the first smoke plus a second same-graph run. It is not a P1A PASS (no 10-run stability, no I2V).
> step3_recorded_at: 2026-10-04 19:06 Asia/Shanghai
> l1_480x832x49_recorded_at: 2026-10-04 20:55 Asia/Shanghai (job finished 2026-10-04 19:15 Asia/Shanghai). One L1 run only; not a P1A PASS.

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
- Submitted as API prompt converted from that graph. Not a GUI Template Library click. At run time it was not yet saved under `workflows/video/lab/`. The later Step 2 export is recorded below. `scripts/p1_comfy_probe.py` was not written yet (see Step 3 below).

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

## Second run (same API graph)

- Result: **success**
- prompt_id: `b484e13e-b779-4283-930b-9460122b2c6e`
- This job had already finished before the Step 3 probe invocation below. That invocation did not POST `/prompt`.
- Server: `http://127.0.0.1:8188`, still PID 333664 (python, started 2026-10-04 17:22:43 Asia/Shanghai). No second ComfyUI.
- history `prompt[2]` equals `workflows/video/lab/VID_wan22_5b_p1a_v001.json` (SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`, 2937 bytes)
- Same executed graph as the first smoke, including 480x832x33, seed 898471028164125, fps 24, filename_prefix `video/p1a_wan22_5b_smoke`
- `execution_cached` nodes: 37, 38, 39, 48
- Comfy `execution_start`: 2026-10-04 18:50:34.299 Asia/Shanghai (timestamp 1791111034299)
- Comfy `execution_success`: 2026-10-04 18:57:49.583 Asia/Shanghai (timestamp 1791111469583)
- Elapsed execution: **435.284 s**
- Output: `E:\project\AI-short-vidio-claw\local\comfyui\image\ComfyUI\output\video\p1a_wan22_5b_smoke_00002_.mp4`
- Size: 200534 bytes
- SHA256: `7256d7908fa095b63577b4b66972d15804a42dacdef64d0583eadd36a07266e7`
- ffprobe: h264, 480x832, 33 frames, 24/1 fps, duration 1.375 s
- mtime: 2026-10-04 18:57:49 Asia/Shanghai

### VRAM / RAM for the second run

- No during-run nvidia-smi series was kept, so there is no sampled peak
- 11652 MiB was a single manual sample, not a peak. It is not used as peak VRAM
- The Step 3 record's only GPU reading is a post-run snapshot (next section), not a peak

## Step 3 probe record

- Script: `scripts/p1_comfy_probe.py`
- Verified invocation: 2026-10-04 19:06:20.376–19:06:20.607 Asia/Shanghai
- Mode: `--from-prompt-id b484e13e-b779-4283-930b-9460122b2c6e` against `workflows/video/lab/VID_wan22_5b_p1a_v001.json`
- Record: `docs/benchmarks/records/p1a_wan22_5b_probe_b484e13e.json`
- Exit code: **0**
- `queued_new_job`: false. Queue at call time: running 0, pending 0. No new job was submitted
- History was already terminal on the first GET. The wait loop was not used. This invocation does not by itself prove submit-and-wait; the submit path remains in the script and was not re-run here
- `workflow_matches_history_prompt`: true
- Download: GET `/view` copy at `local/p1_probe_media/p1a_wan22_5b_probe_b484e13e/p1a_wan22_5b_smoke_00002_.mp4` (gitignored). 200534 bytes, SHA256 matches the Comfy output above
- Post-run snapshot at 2026-10-04 19:06:20.494 Asia/Shanghai, labeled `post_run_snapshot`: NVIDIA GeForce RTX 4070 SUPER, driver 595.97, nvidia-smi `memory.used` **4304 MiB** / 12282 MiB, GPU utilization 41%. `nvidia_smi_memory_used_mib_peak` is null
- Same snapshot, Win32 GlobalMemoryStatusEx: memory load 99%, `ram_total_bytes` 34164097024, `ram_avail_bytes` 56532992. This is after the job, not a during-run minimum and not a peak
- Server `/system_stats` at that call: comfyui 0.38.0, pytorch 2.14.1+cu130, python 3.12.9
- Sampler change in the script (nvidia-smi + Win32 memory, sample errors non-fatal) was exercised only by this one post-run sample, not across a live generation


## L1 480x832x49 (one submit-and-wait)

- Result: **success**
- Checked again  2026-10-04 20:55 Asia/Shanghai against live `GET /history/7f4294b9-f811-43c1-bc49-9a62bc90dd66` before any new submit. History was already terminal success. Queue running 0, pending 0. No replacement prompt was posted.
- Script: `scripts/p1_comfy_probe.py` submit-and-wait. Probe log `local/p1a/l1_probe.log` (gitignored) ends `result=success` / `EXIT:0`. `queued_new_job`: true. This is one job, not 10 runs, and not L2.
- prompt_id: `7f4294b9-f811-43c1-bc49-9a62bc90dd66`
- Record: `docs/benchmarks/records/p1a_wan22_5b_l1_480x832x49.json` (written by that probe; fields below were checked against history and the mp4, not rewritten)
- Lab workflow file was not edited: `workflows/video/lab/VID_wan22_5b_p1a_v001.json` SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`, 2937 bytes. The submitted history graph is that graph with Wan22ImageToVideoLatent **480x832x49** and seed **898471028164125**. `execution_cached` nodes: 37, 38, 39, 48
- Server: `http://127.0.0.1:8188` still PID 333664 (LISTENING). Probe process is not still running
- Comfy `execution_start`: 2026-10-04 19:10:39.393 Asia/Shanghai (timestamp 1791112239393)
- Comfy `execution_success`: 2026-10-04 19:15:08.117 Asia/Shanghai (timestamp 1791112508117)
- Elapsed execution: **268.724 s**
- Comfy output: `local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00003_.mp4`
- Probe copy (gitignored `*.mp4`): `docs/benchmarks/records/p1a_wan22_5b_l1_480x832x49_media/p1a_wan22_5b_smoke_00003_.mp4`
- Size: **326275 bytes** (both paths)
- SHA256: `2aa87d8dd76e09361c00b5c4d5cee27d5532d068874e70fd987770c85e655029`
- ffprobe on the probe copy: h264, 480x832, 49 frames, 24/1 fps, duration 2.041667 s
- Comfy file mtime: 2026-10-04 19:15:07 Asia/Shanghai

### VRAM / RAM for L1

- Sample log is the `samples` array in the record (55 nvidia-smi samples, interval 5.0 s), not an invented peak
- GPU: NVIDIA GeForce RTX 4070 SUPER, nvidia-smi memory.total 12282 MiB, driver 595.97
- First `memory.used`: **4425 MiB**
- Peak sampled `memory.used`: **11165 MiB**
- Last `memory.used`: **4452 MiB**
- This is a sample peak, not a continuous hardware maximum
- `ram_avail_bytes_min`: 29188096; `ram_total_bytes`: 34164097024
- No OOM in history. `status_str` is success

## Not done

- No fourth job after this L1 success. This check did not POST `/prompt`
- No 14B, GGUF, or WanGP
- No I2V (`start_image` not connected; LoadImage was not added back)
- L1 has one successful 480x832x49 run only. L2–L4 are not done. No 10-run stability, no p50/p95, no recommended default
- P1A PASS conditions are not met
