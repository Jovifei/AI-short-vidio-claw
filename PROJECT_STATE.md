# PROJECT_STATE

更新时间：2026-10-04 17:45 Asia/Shanghai
状态：**Strategic GO / Current Production NO-GO / P0R PASS → P1A 下载中**

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
- Disk free: C 489.06 GB / D 134.33 GB / E 249.24 GB / F **334.79 GB**
- FFmpeg 8.1.1 可用（WinGet Gyan.FFmpeg）
- **实际 ComfyUI URL：`http://127.0.0.1:8188`**（项目 image 实例 ComfyUI v0.38.0，torch 2.14.1+cu130）
- Desktop：`F:\ComfyUI` basePath；ProductVersion 0.8.35.0；历史端口曾用 8000，**当前勿假设 8000**
- 模型库：`F:\ComfyUI\models` ≈ 18.50 GB；已有 SDXL/SD1.5/VAE/FaceID adapter/clip_vision
- **Wan2.2-TI2V-5B 三文件全部缺失**（diffusion / vae / umt5）
- custom_nodes：comfyui_ipadapter_plus、glm_prompt（后者曾 IMPORT FAILED）
- 仓库仍无生产客户端完成件、无 API workflow、无 EP001 实体生产目录
- GPT-SoVITS / MuseTalk / 14B / LTX / FramePack / WanGP **不进 P1A**

## 3. 立即路线

### P0R：本地再基线 — **PASS（文档已提交）**
环境探测、路径/端口/磁盘/现有模型盘点完成。

### P1A：最窄视频基线 — **进行中：仅下载官方 5B 三文件**
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