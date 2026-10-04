# 08 模型与工作流选型矩阵

本文件记录“当前推荐”，不是永恒真理。新模型进入前必须跑本项目 benchmark。

## 1. 图像/身份

| 能力 | 当前候选 | 本项目定位 | 注意 |
|---|---|---|---|
| 人脸身份 | PuLID | 林黛玉 reference identity | 官方说明 FLUX 本地 demo 可支持 12GB |
| 图像参考 | IPAdapter | 风格/主体/脸参考 | ComfyUI_IPAdapter_plus 已 maintenance-only |
| 长期角色 | Character LoRA | 两位主角最终稳定方案 | 定妆未稳定前不要训练 |
| Pose/Depth | ControlNet 类 | 动作和构图控制 | 按实际图像基座选择 |

## 2. 视频

| 路线 | 优先级 | 场景 | 12GB 策略 |
|---|---|---|---|
| Native ComfyUI + Wan2.2 | P0 主线 | 3–5 秒 I2V | 低分辨率、短帧、必要时量化/offload |
| ComfyUI-WanVideoWrapper | P0 实验/低显存 | 原生缺失功能、新模型、FP8/GGUF/block swap | 只保留经过 benchmark 的 production workflow |
| FramePack | P1 回退 | 长镜头、低动作、渐进生成 | 官方最低 6GB，速度换显存 |
| Wan2.2 Animate | Future | 动作复制/角色动画 | 14B，先验证再决定 |
| Wan2.2 S2V | Future | 音频驱动视频 | 14B，12GB 上不是 MVP 依赖 |

## 3. 语音/口型

| 能力 | 主线 | 说明 |
|---|---|---|
| TTS | GPT-SoVITS | 中文、few-shot、角色 voice map |
| 人脸 lip sync | MuseTalk 1.5 | 林黛玉等标准人脸 |
| 孙悟空 lip sync | TBD | 非标准脸需专项验证，不能直接承诺 |

## 4. 后期

| 能力 | 当前策略 |
|---|---|
| 剪辑/拼接 | FFmpeg |
| 探测 | ffprobe |
| 插帧 | P1/P2 benchmark 决定 |
| 放大 | P1/P2 benchmark 决定 |
| 字幕 | ASS/SRT + FFmpeg |
| 音频响度 | FFmpeg loudnorm |
| QC | 规则 + VLM + 人工 |

## 5. 为什么不把一个“一键短剧仓库”直接当核心

Story Claw、Drama Skills 非常值得借鉴，但本项目目标硬件和创作方式不同：

- 我们要保留 ChatGPT 人工精修关键帧通道；
- 我们首要问题是双角色身份与生活互动；
- 12GB 显存必须更严格调度；
- 我们需要可替换视频模型；
- 我们不希望一体化工具升级困难。

因此参考它们的“生产思想和数据结构”，自行做轻量控制平面。

## 6. Production / Lab 双轨

Production workflow：
- 版本固定；
- 可复现；
- 通过 benchmark；
- 不自动追最新。

Lab workflow：
- 尝试新模型；
- 新 custom node；
- 新量化；
- 新加速。

只有 Lab 明显胜出并通过回归，才升级 Production。
