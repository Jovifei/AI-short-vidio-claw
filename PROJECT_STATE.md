# PROJECT_STATE

更新时间：2026-10-05 00:45 Asia/Shanghai
状态：**Strategic GO / Current Production NO-GO / P0R PASS / P1A L1 T2V 480x832x49 已串行成功 10/10（p50 187.7095 s，p95 264.101 s，采样峰值 10912–11733 MiB）；L2/L3/L4 仍各一次。不是 I2V，不是 PASS**

## L1 十次稳定性（Step 5，T2V）

2026-10-05 00:07:11–00:42:06 Asia/Shanghai，同一 ComfyUI（`http://127.0.0.1:8188`，PID 333664，17:22:43 启动，没有第二进程，没有重启）对 lab 图 `workflows/video/lab/VID_wan22_5b_p1a_v001.json`（SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`，文件未改）串行 submit-and-wait 十次。尺寸 480×832 / 49 frames。正向提示词没有覆盖，仍是图里的地铁乐手基准句，不是悟空故事。种子依次为 4808324901–4808324910。十次都成功，没有 OOM，没有重试。耗时（秒）：306.100、212.769、208.991、203.228、185.792、188.091、176.986、187.328、177.579、175.239。p50 **187.7095 s**，p95 **264.101 s**（Hyndman-Fan type 7）。nvidia-smi 每 5 秒采样，单次峰值 **10912–11733 MiB** / 12282 MiB，全部样本 **3261–11733 MiB**（不是连续硬件最大值）。汇总 `docs/benchmarks/records/p1a_wan22_5b_l1_stability_10x.json`，单次记录 `docs/benchmarks/records/p1a_wan22_5b_l1_stab_01.json` 至 `_10.json`。mp4 不入库。这不是 I2V，也不是 P1A PASS。

## 内容修正（不是新的性能阶梯）

`p1a_wan22_5b_smoke_00001_` 到 `00005_` 是官方模板地铁乐手提示词的性能 smoke，不是剧集画面。L4 的 `00006_` 同样是该模板，也不是 EP001。

2026-10-04 22:29:54–22:33:54 Asia/Shanghai 另交了一条故事向 T2V，没有再跑性能阶梯。lab 文件 `workflows/video/lab/VID_wan22_5b_p1a_v001.json` 未改（SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`），提示词由 `scripts/p1_comfy_probe.py` override。prompt_id `2bc0c584-7862-42a5-8f45-0795cb85f9f0`。480×832 / 49 frames，seed `20261004222901`。Comfy 执行 **239.374 s**。nvidia-smi 采样峰值 **10924 MiB**。输出 `docs/benchmarks/records/p1a_sh001_wukong_home_t2v_480x832x49_media/p1a_wan22_5b_smoke_00007_.mp4`（h264 480x832、49 frames、24 fps、2.041667 s）。记录 `docs/benchmarks/records/p1a_sh001_wukong_home_t2v_480x832x49.json`。

`assets/characters` 仍无 approved 参考图（yaml `approved_refs: []`，无 png/jpg/webp）。workflow 无 LoadImage，本条是文本生成视频，没有人脸锁定。画面只要求孙悟空一人受伤回家；林黛玉不在这一镜。

## 1. 二次复核结论

原路线的核心架构成立：
- Image First → Video Second
- Frozen Keyframe
- 连续性锁
- GPU 串行
- adapter 化
- 每镜可重做
- 两道人类 Gate

但原文档对“这台 4070S 机器今天能直接生产”的表达过于乐观，已修正。

## 2. 本机实测现状（P0R 落盘，见 docs/benchmarks/P1_ENVIRONMENT.md）

- Windows 11 Pro Build 22631
- RTX 4070 SUPER / 12282 MiB VRAM / Driver 595.97 / nvidia-smi CUDA 13.2（无 nvcc）
- System RAM 34164097024 bytes ≈ 31.82 GB；pagefile `D:\pagefile.sys` Allocated 66929 MB
- Disk free at 17:40: C 489.06 GB / D 134.33 GB / E 249.24 GB / F **334.79 GB**. After the three 5B files, F free measured 18:31: **341333843968 bytes (317.89 GB)**
- FFmpeg 8.1.1 可用（WinGet Gyan.FFmpeg）
- **实际 ComfyUI URL：`http://127.0.0.1:8188`**（项目 image 实例 ComfyUI v0.38.0，torch 2.14.1+cu130）
- Desktop：`F:\ComfyUI` basePath；ProductVersion 0.8.35.0；历史端口曾用 8000，**当前勿假设 8000**
- 模型库：`F:\ComfyUI\models` ≈ 18.50 GB；已有 SDXL/SD1.5/VAE/FaceID adapter/clip_vision
- **Wan2.2-TI2V-5B 官方模板三文件已在 `F:\ComfyUI\models` 且 SHA256 匹配**（diffusion 9999658848, vae 1409400960, umt5 6735906897）。2026-10-04 18:36–18:41 Asia/Shanghai 首次 smoke 成功（见 docs/benchmarks/P1_4070S_BASELINE.md）：prompt_id d0d5c325-9e52-4a49-9f89-7d7fd9095b6c；官方模板 video_wan2_2_5B_ti2v.json 转 API；LoadImage mode 4 旁路所以是 T2V；480x832 / 33 frames；执行 330.811 s；nvidia-smi 约 5.2 s 采样峰值 memory.used 11374 MiB；输出 local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00001_.mp4（200534 bytes）。2026-10-04 18:45 Asia/Shanghai 从仍在运行的 ComfyUI history 导出该次 API graph（未重跑、未手工重建、未新开 ComfyUI）：`workflows/video/lab/VID_wan22_5b_p1a_v001.json` SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`，2937 bytes。第二次同图运行 prompt_id `b484e13e-b779-4283-930b-9460122b2c6e`：Comfy 执行 2026-10-04 18:50:34.299–18:57:49.583 Asia/Shanghai，435.284 s；输出 `local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00002_.mp4`（200534 bytes，SHA256 `7256d7908fa095b63577b4b66972d15804a42dacdef64d0583eadd36a07266e7`，ffprobe h264 480x832、33 frames、24/1 fps、时长 1.375 s，mtime 18:57:49 Asia/Shanghai）。这次没有执行中的 nvidia-smi 采样序列；11652 MiB 是一次手动采样，不是峰值。2026-10-04 19:06:20 Asia/Shanghai `scripts/p1_comfy_probe.py --from-prompt-id` 对这个已完成 prompt 做了 history GET、下载校验和一次跑后快照（nvidia-smi memory.used 4304 MiB / 12282 MiB，peak 字段为 null），进程 exit 0，没有 POST /prompt。记录 `docs/benchmarks/records/p1a_wan22_5b_probe_b484e13e.json`。ComfyUI 仍是 17:22:43 启动的 PID 333664，没有第二个进程。2026-10-04 19:10:39.393–19:15:08.117 Asia/Shanghai L1 一次 submit-and-wait 成功：prompt_id `7f4294b9-f811-43c1-bc49-9a62bc90dd66`；lab workflow 文件未改（`workflows/video/lab/VID_wan22_5b_p1a_v001.json` SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`）；history 图为 480x832x49，seed 898471028164125。Comfy 执行 **268.724 s**。输出 `local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00003_.mp4`（326275 bytes，SHA256 `2aa87d8dd76e09361c00b5c4d5cee27d5532d068874e70fd987770c85e655029`，ffprobe h264 480x832、49 frames、24/1 fps、时长 2.041667 s）。记录 `docs/benchmarks/records/p1a_wan22_5b_l1_480x832x49.json`，内有 55 次 nvidia-smi 采样，memory.used 采样峰值 **11165 MiB** / 12282 MiB（不是连续硬件最大值）。这次复查 history 已是 success，队列为空，没有再 POST /prompt。监听 8188 的仍是 PID 333664。2026-10-04 20:57:37.715–21:03:51.785 Asia/Shanghai L2 一次 submit-and-wait 成功：prompt_id `2cd5fc06-3eac-48c7-98f9-cb969cf3b9ae`；lab workflow 文件未改（`workflows/video/lab/VID_wan22_5b_p1a_v001.json` SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`）；history 图为 480x832x81，seed 898471028164125。Comfy 执行 **374.07 s**。输出 `local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00004_.mp4`（373482 bytes，SHA256 `6dfc7e954631b07168015606d7a7d02e5a06c88edfdf8fd12d57490fbff6d41c`，ffprobe h264 480x832、81 frames、24/1 fps、时长 3.375 s）。记录 `docs/benchmarks/records/p1a_wan22_5b_l2_480x832x81.json`，内有 75 次 nvidia-smi 采样，memory.used 采样峰值 **10770 MiB** / 12282 MiB（不是连续硬件最大值）。没有 OOM，没有重试，没有 L3/L4。监听 8188 的仍是 PID 333664。2026-10-04 21:07:24.085–21:13:25.097 Asia/Shanghai L3 一次 submit-and-wait 成功：prompt_id `e16db48e-236f-4d63-8a2b-5cbf6a793df3`；lab workflow 文件未改（`workflows/video/lab/VID_wan22_5b_p1a_v001.json` SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`）；history 图为 576x1024x49，seed 898471028164125。Comfy 执行 **361.012 s**。输出 `local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00005_.mp4`（305602 bytes，SHA256 `a27b59da390b105c042bc854c9532f711d9db0a175876a7dffc90f21e8b51cd9`，ffprobe h264 576x1024、49 frames、24/1 fps、时长 2.041667 s）。记录 `docs/benchmarks/records/p1a_wan22_5b_l3_576x1024x49.json`，内有 73 次 nvidia-smi 采样，memory.used 采样峰值 **10648 MiB** / 12282 MiB（不是连续硬件最大值）。没有 OOM，没有重试，没有 L4。2026-10-04 22:12 Asia/Shanghai 复查该 prompt history 已是 success，队列为空，没有再 POST /prompt。监听 8188 的仍是 PID 333664。2026-10-04 22:17:18.090–22:27:10.073 Asia/Shanghai L4 一次 submit-and-wait 成功：prompt_id `91225eb6-58b8-4850-b014-fa48e66997d1`；lab workflow 文件未改（`workflows/video/lab/VID_wan22_5b_p1a_v001.json` SHA256 `c000f3731824a504ab50c123485ecc97e186d6bab55615bf08e6409a490f5fcb`）；history 图为 576x1024x81，seed 898471028164125。Comfy 执行 **591.983 s**。输出 `local/comfyui/image/ComfyUI/output/video/p1a_wan22_5b_smoke_00006_.mp4`（477455 bytes，SHA256 `4f740cd39712ab7a5f3f21c45b67e3c05f15e72f7b31a00026d1f705f4402d78`，ffprobe h264 576x1024、81 frames、24/1 fps、时长 3.375 s）。记录 `docs/benchmarks/records/p1a_wan22_5b_l4_576x1024x81.json`，内有 118 次 nvidia-smi 采样，memory.used 采样峰值 **11221 MiB** / 12282 MiB（不是连续硬件最大值）。没有 OOM，没有重试，没有 14B。监听 8188 的仍是 PID 333664
- custom_nodes：comfyui_ipadapter_plus、glm_prompt（后者曾 IMPORT FAILED）
- 仓库仍无生产客户端完成件、无 EP001 实体生产目录。Lab API workflow 只有这次 T2V smoke graph，不是生产 workflow
- GPT-SoVITS / MuseTalk / 14B / LTX / FramePack / WanGP **不进 P1A**

## 3. 立即路线

### P0R：本地再基线 — **PASS（文档已提交）**
环境探测、路径/端口/磁盘/现有模型盘点完成。

### P1A：最窄视频基线 — **L1 480×832 / 49 frames T2V 已串行 10/10（2026-10-05 00:07–00:42 Asia/Shanghai，p50 187.7095 s，p95 264.101 s，单次采样峰值 10912–11733 MiB，全部样本 3261–11733 MiB）。L2/L3/L4 仍各一次。不是 PASS。I2V 未做**
仅：
- 一个 ComfyUI GPU 进程
- 官方原生 Wan2.2 5B 模板
- Wan2.2-TI2V-5B
- native offloading
- 一张 approved keyframe
- 一个最小 API workflow
- 一个最小提交/轮询脚本

不做：
- 14B / GGUF 14B / Wrapper 14B
- PuLID/FaceID
- TTS/LipSync
- EP001 批量生产

## 4. P1A 参数阶梯

不把任何一级写成“必然稳定”。

L0：只完成模型加载与最小 workflow dry-run；
L1：480×832 / 49 frames；
L2：480×832 / 81 frames；
L3：576×1024 / 49 frames（只在 L1/L2 健康才试）；
L4：576×1024 / 81 frames（可选，不是 P1A 必须）。

若实测 workflow 对尺寸/帧数有约束，以官方模板和日志为准，修改必须记录。

## 5. P1A 通过条件

全部满足：
1. 至少一组 I2V 配置在本机连续成功 10 次；
2. OOM = 0 或仅 1 次且能解释可复现；
3. 每次输出可由 workflow + seed + input + model version 追溯；
4. peak VRAM、peak RAM、elapsed 都被记录；
5. 单 ComfyUI 进程稳定，无需同时常驻第二 GPU 服务；
6. 能通过脚本执行：探活 → 提交 → 轮询 → 返回输出路径；
7. 能根据本机实测给出“推荐默认参数”，而不是预设 576×1024。

质量 Gate 与性能 Gate 分开：
- P1A 先证明基础可运行；
- P1A-Q 再对 3 张 keyframe 做 motion/identity 视觉评分。

## 6. P1B 可选对照

只有 P1A 通过并获得用户确认后：
- FramePack
- WanGP 选定单一候选

不默认：
- LTX-2.x 原生 ComfyUI（官方 ComfyUI-LTXVideo 当前推荐 32GB+ VRAM）
- 14B 原生/量化大范围矩阵
- 多个低显存 runner 同时安装

## 7. P2 首要课题

“双身份同框 keyframe”。

林黛玉单人 identity 与孙悟空单人 identity 都不是最终 Gate。
真正 Gate 是：
- 两人同框
- 两边 identity 都守住
- 服装/身高/手部关系合理
- 10 个固定生活场景 ≥80% approved

高风险镜头允许 Hero Lane。

## 8. P3 First Cut

先完成：
- 20 张 approved story keyframe
- 其中 6 个低风险镜头 I2V
- 其余静态/缓慢推拉/轻环境动效
- 三句台词先画外音
- 不做 lip sync

先做出 45–90 秒可看的 v0.1，再逐镜增加动态。

## 9. 尚未决定

- 本地图像基座
- 双身份本地 workflow
- 林黛玉/悟空 LoRA 训练方案
- 最终插帧/放大器
- VLM QC
- 孙悟空口音
- 是否引入 WanGP 作为第二 executor
- 个人 ConfyUI 工作流可借用点（不改 P1A）：见 docs/workflows/BORROW_FROM_CONFYUI.md
