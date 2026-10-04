# P1_ENVIRONMENT — P0R 本机实测

> measured_at: 2026-10-04 17:40 Asia/Shanghai  
> git_main: be981c8854a7b29b7391badb4be5c2916aa4a68c  
> 本文件只记录实测事实，不写猜测。

## Machine

- Manufacturer/Model: ASUS / System Product Name
- CPU: Intel(R) Core(TM) i5-14600KF
- OS: Microsoft Windows 11 Professional 10.0.22631 (Build 22631) 64-bit

## GPU / VRAM

- GPU: NVIDIA GeForce RTX 4070 SUPER
- Dedicated VRAM: 12282 MiB (`nvidia-smi`)
- ComfyUI `system_stats` vram_total: 12878086144 bytes
- NVIDIA Driver: 595.97
- `nvidia-smi` reported CUDA Version: 13.2
- `nvcc`: not found（未安装/未入 PATH 的 CUDA Toolkit）
- `CUDA_PATH`: empty

## RAM / pagefile

- System RAM total: 34164097024 bytes ≈ **31.82 GB**
- Pagefile: `D:\pagefile.sys`
  - Allocated: 66929 MB
  - CurrentUsage (at measure): 10629 MB
  - PeakUsage (at measure): 16457 MB
  - Win32_PageFileSetting Initial/Maximum: 0/0（系统管理）

## Disk

| Drive | Label | Total GB | Free GB |
|-------|-------|----------|---------|
| C: | 系统 | 953.56 | 489.06 |
| D: | software | 788.78 | 134.33 |
| E: | Game | 953.87 | 249.24 |
| F: | 电影 | 1074.22 | 334.79 |

- ComfyUI models library (`F:\ComfyUI\models`) total occupied (excl. incomplete cache noise counted in tree): **≈18.50 GB** measured sum of files under models
- Project disk E: free **249.24 GB**
- Models disk F: free **334.79 GB**
- P1A 5B 预计下载合计 ≈ **16.89 GB**（见 Missing for P1A）；下载后 F: 仍预计 >300 GB 空闲
- 建议安全余量：模型盘至少保留 ≥50 GB；临时视频/缓存另留 ≥20 GB（建议，非硬限制）

## Python

- Default `python`: `D:\Python\Python3.14\python.exe` — **3.14.2**
- Also: `C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe` — **3.12.10**
- Conda: not found

## PyTorch / CUDA

| Env | Path | torch | torch.cuda | cuda.is_available |
|-----|------|-------|------------|-------------------|
| System py3.14 | `D:\Python\Python3.14\python.exe` | 2.11.0+cu128 | 12.8 | True |
| Desktop venv | `F:\ComfyUI\.venv\Scripts\python.exe` | 2.7.1+cu128 | 12.8 | True |
| **Active project image instance** | `E:\project\AI-short-vidio-claw\local\comfyui\image\venv\Scripts\python.exe` | **2.14.1+cu130** | **13.0** | True |

## FFmpeg

- `ffmpeg`: `C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe`
- version: **8.1.1-full_build-www.gyan.dev**
- `ffprobe`: same `bin\ffprobe.exe` (8.1.1)

## ComfyUI actual URL

```
COMFYUI_URL=http://127.0.0.1:8188
```

- Measured LISTENING: `127.0.0.1:8188` PID 333664
- Process: uv cpython 3.12.9 running `ComfyUI/main.py --port 8188 --listen 127.0.0.1`
- Parent/venv: `E:\project\AI-short-vidio-claw\local\comfyui\image\venv\Scripts\python.exe`
- Instance root: `E:\project\AI-short-vidio-claw\local\comfyui\image\ComfyUI`
- Instance git: `6b747c0428c343e1417219641db93a4fb7cb69ae` (ComfyUI v0.38.0)
- `/system_stats`: comfyui_version **0.38.0**, pytorch **2.14.1+cu130**, templates **0.11.70**, frontend **1.53.6**
- Desktop app: `C:\Users\Admin\AppData\Local\Programs\@comfyorgcomfyui-electron\ComfyUI.exe` ProductVersion **0.8.35.0**
- Desktop `basePath`: `F:\ComfyUI`
- Desktop extra config: `C:\Users\Admin\AppData\Roaming\ComfyUI\extra_models_config.yaml` → `base_path: F:\ComfyUI`
- Project instance also maps `F:/ComfyUI/models` via `E:\project\AI-short-vidio-claw\local\comfyui\image\ComfyUI\extra_model_paths.yaml`
- Note: Desktop electron historically used `--port 8000`; **do not assume 8000**. Current real port is **8188**.

## Existing models (`F:\ComfyUI\models`)

| name | size bytes | category |
|------|------------|----------|
| sd_xl_base_1.0.safetensors | 6938078334 | checkpoints |
| v1-5-pruned-emaonly-fp16.safetensors | 2132696762 | checkpoints |
| Juggernaut-XL-10.safetensors | 29 (stub/broken) | checkpoints |
| model.safetensors | 3944552236 | clip_vision |
| ip-adapter-faceid-plusv2_sdxl.bin | 1487555181 | ipadapter |
| sdxl_vae.safetensors | 334641164 | vae |

- Incomplete unrelated download observed: `F:\ComfyUI\models\checkpoints\.cache\huggingface\download\*.incomplete` (~5.03 GB, Juggernaut) — **not** P1A
- **No** `wan2.2_*` / `umt5_xxl*` files under `F:\ComfyUI\models` or `E:\project\AI-short-vidio-claw\local`

## Existing nodes

| name | path | notes |
|------|------|-------|
| comfyui_ipadapter_plus | `F:\ComfyUI\custom_nodes\comfyui_ipadapter_plus` | present |
| glm_prompt | `F:\ComfyUI\custom_nodes\glm_prompt` | present; earlier Desktop log showed IMPORT FAILED (missing sniffio) |

P0R 未安装任何新 custom node。

## Missing for P1A（官方 ComfyUI Wan2.2 5B template）

来源：Comfy-Org/Wan_2.2_ComfyUI_Repackaged `split_files/` + docs/stages/P1A_WAN22_5B_BASELINE.md

| file | size bytes | HF LFS SHA256 | source URL | destination | present? |
|------|------------|---------------|------------|-------------|----------|
| wan2.2_ti2v_5B_fp16.safetensors | 9999658848 | 456f901338bd9eadbded3828b819109a9b68e8a525ca5cf8d0049a69fcfeca1e | https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors | `F:\ComfyUI\models\diffusion_models\wan2.2_ti2v_5B_fp16.safetensors` | **NO** |
| wan2.2_vae.safetensors | 1409400960 | e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156 | https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors | `F:\ComfyUI\models\vae\wan2.2_vae.safetensors` | **NO** |
| umt5_xxl_fp8_e4m3fn_scaled.safetensors | 6735906897 | c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68 | https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors | `F:\ComfyUI\models\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors` | **NO** |

- free disk before (F:): **334.79 GB**
- free disk after estimate: ≈ **317.9 GB**（334.79 − 16.89）

**明确不下载**：14B、LTX、FramePack、WanGP、LoRA、PuLID、MuseTalk、GPT-SoVITS。

## Risks

1. 当前服务端口是项目 image 实例 8188，不是 Desktop 历史 8000；脚本/文档必须用实测 URL。
2. Desktop venv torch 2.7.1+cu128 与项目实例 torch 2.14.1+cu130 不一致；P1A 应以当前 LISTENING 实例为准。
3. `glm_prompt` 导入失败（缺 sniffio）——与 P1A 无关，但说明 Desktop 节点环境不完整。
4. Juggernaut 残留 incomplete 占盘，勿误认为 Wan 权重。
5. 系统未装 nvcc/CUDA Toolkit；依赖 PyTorch 自带 CUDA runtime。
6. 系统默认 Python 3.14 与 Comfy 实例 3.12.9 不同，自动化脚本应指向实例 venv。

## Gate (P0R)

- [x] 实际 ComfyUI URL 已知 → `http://127.0.0.1:8188`
- [x] 磁盘空闲已知
- [x] Python/FFmpeg 可定位
- [x] 现有模型/节点清单已知（`local/p0r/*.csv`，不提交）
- [x] 能明确列出 P1A 需要下载什么（上表三文件，全部缺失）

P0R PASS → 进入 P1A 仅下载上述三文件。

## Raw artifacts (not in git)

- `local/p0r/system_inventory.json`
- `local/p0r/models_inventory.csv`
- `local/p0r/custom_nodes_inventory.csv`