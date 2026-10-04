# 08 模型与工作流选型矩阵（2026-10-04 复核版）

## 状态定义

- REQUIRED：当前阶段必测
- OPTIONAL：当前主线通过后可测
- DEFERRED：暂不进入本机主线
- REJECTED：当前阶段明确不做

## 1. P1 视频

| 路线 | 状态 | 原因 |
|---|---|---|
| Native ComfyUI + Wan2.2-TI2V-5B | REQUIRED / P1A | ComfyUI 官方写 5B + native offload 可适配 8GB 级 VRAM；必须本机验证 |
| FramePack | OPTIONAL / P1B | 官方最低 6GB，适合长/低动作；先不增加变量 |
| WanGP | OPTIONAL / P1B/P1C | 低显存 runner，2026 持续更新；但另起执行栈且 32GB RAM 需实测 |
| WanVideoWrapper | OPTIONAL LAB | FP8/GGUF/block swap 强；原生可用时不优先 |
| Wan2.2 A14B FP16 native | REJECTED for P1 | 官方独立 I2V 至少 80GB |
| A14B GGUF / 强 offload | DEFERRED | 12GB VRAM 可有社区路径，但 32GB RAM 与稳定性未证 |
| LTX-2.x official ComfyUI | DEFERRED | 官方 ComfyUI-LTXVideo 当前推荐 32GB+ VRAM |
| Wan2.2 Animate/S2V 14B | DEFERRED | 不是 MVP 依赖 |

## 2. P2 图像身份

| 能力 | 候选 | 状态 |
|---|---|---|
| 林黛玉单人 identity | PuLID / IPAdapter FaceID / LoRA | P2 benchmark |
| 孙悟空单人 identity | LoRA / reference conditioning | P2 benchmark |
| 双身份同框 | regional/two-pass/LoRA+ref/Hero Lane | P2 highest priority |
| Pose/Depth | ControlNet 类 | 根据图像基座决定 |

FaceID 当前不进入 P1：
本机报告 InsightFace 模型目录为空，且悟空本来就不使用 FaceID。

## 3. P3 First Cut

- keyframe：20 张 approved
- animated shots：先 6 个
- static motion：Ken Burns / subtle zoom / rain / light / steam
- dialogue：voice-over
- lip sync：disabled

## 4. P5 音频

| 能力 | 方案 | 备注 |
|---|---|---|
| TTS | GPT-SoVITS | 上游 API v2 默认 9880，进入 P5 才部署 |
| 人脸 LipSync | MuseTalk 1.5 | Gradio 默认 7860；需要单独 adapter，不能把 UI 端口当 production API |
| Wukong LipSync | TBD | 专项 benchmark |

## 5. 后期

FFmpeg/ffprobe 继续作为确定项。

插帧、放大：
- 不在 P1A 之前决定；
- P1A 结束先确定实际 source fps；
- P3 前完成“原始片 → final delivery”的一条可测链。

## 6. Production/Lab

Production：
- 固定版本
- 固定 workflow
- 有本机 benchmark
- 有 rollback

Lab：
- 新模型
- 新节点
- 新 runner
- 新量化

Lab 不因“能启动”就升级 Production。

## 7. 当前官方来源

- Wan2.2：
  https://github.com/Wan-Video/Wan2.2
- ComfyUI Wan2.2：
  https://docs.comfy.org/tutorials/video/wan/wan2_2
- WanVideoWrapper：
  https://github.com/kijai/ComfyUI-WanVideoWrapper
- FramePack：
  https://github.com/lllyasviel/FramePack
- WanGP：
  https://github.com/deepbeepmeep/Wan2GP
- LTX ComfyUI：
  https://github.com/Lightricks/ComfyUI-LTXVideo
- MuseTalk：
  https://github.com/TMElyralab/MuseTalk
- GPT-SoVITS：
  https://github.com/RVC-Boss/GPT-SoVITS
