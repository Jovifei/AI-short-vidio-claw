# 09 技术来源、参考仓库与使用边界

更新时间：2026-10-04

原则：
**官方文档负责“候选资格”，本机 benchmark 负责“生产资格”。**

## 1. ComfyUI Wan2.2 官方教程

https://docs.comfy.org/tutorials/video/wan/wan2_2

已核验：
- 官方提供 Wan2.2 5B/14B native workflow；
- 5B 页面写明 native offloading 下“should fit well on 8GB vram”；
- 5B template 使用 `wan2.2_ti2v_5B_fp16.safetensors`、Wan2.2 VAE、FP8 UMT5 encoder；
- 可以在节点中调 size 和 length。

本项目：
P1A 唯一首测来源。

## 2. Wan2.2 官方仓库

https://github.com/Wan-Video/Wan2.2

已核验：
- TI2V-5B
- I2V/T2V A14B
- standalone 5B 720P offload 示例至少 24GB VRAM
- I2V-A14B standalone 至少 80GB VRAM

结论：
不同 runtime/offload 的硬件数字不能互相替代。
14B 不进入 P1A。

## 3. ComfyUI-WanVideoWrapper

https://github.com/kijai/ComfyUI-WanVideoWrapper

参考：
- FP8
- GGUF
- block swap
- offload
- 新 Wan 生态快速支持

作者明确说明：
native 已支持时不应默认使用 Wrapper。

定位：
Lab only，除非 P1A 出现明确问题。

## 4. FramePack

https://github.com/lllyasviel/FramePack

官方：
- RTX 30/40/50
- 至少 6GB GPU memory

但社区亦有低 VRAM + 大量 shared/system RAM 后失败的报告：
https://github.com/lllyasviel/FramePack/issues/774

定位：
P1B optional；必须记录 VRAM + RAM。

## 5. WanGP

https://github.com/deepbeepmeep/Wan2GP

2026 仍活跃，支持多种视频/图像/音频模型，面向 low-VRAM。

同时社区存在：
- 12GB VRAM + 32GB RAM profile 使用经验；
- RAM 不足 issue；
- 大模型可占用大量系统 RAM。

定位：
P1B/P1C optional runner，不是当前 ComfyUI baseline。

## 6. LTX ComfyUI

https://github.com/Lightricks/ComfyUI-LTXVideo

官方当前 prerequisites：
- CUDA GPU
- 32GB+ VRAM
- 100GB+ disk

定位：
不进入 4070S 12GB 的 P1A/P1B 原生 ComfyUI最小路径。
其他低显存 runner 以后作为独立 Lab 评估。

## 7. Drama Skills

https://github.com/zenstory-ai/drama-skills

参考：
- text-first production truth
- continuity lock
- IMG/PLAN/REF
- frozen keyframe
- preview/confirm/produce
- review 分离

不照搬：
具体供应商和文件数量限制。

## 8. Story Claw

https://github.com/ZC89757/story-claw

参考：
- stage-aware asset
- voice map
- VLM clip QC
- reroll
- episode workspace

不照搬：
完整 Electron/LTX 产品。

## 9. PuLID

https://github.com/ToTheBeginning/PuLID

官方同时存在：
- FLUX 16GB 描述
- local gradio 12GB 支持描述

因此不能直接写成“本项目 ComfyUI 12GB production verified”。

定位：
P2 benchmark。

## 10. IPAdapter Plus

https://github.com/cubiq/ComfyUI_IPAdapter_plus

- GPL-3.0
- maintenance-only

定位：
外部依赖候选，不 vendor。

## 11. MuseTalk

https://github.com/TMElyralab/MuseTalk

MuseTalk 1.5：
- 多语言 lip sync
- app.py Gradio 默认 port 7860

定位：
P5 标准人脸 lip sync。
Gradio port 不是本项目 API contract，需要 adapter。

## 12. GPT-SoVITS

https://github.com/RVC-Boss/GPT-SoVITS

api_v2.py：
- 默认 bind 127.0.0.1
- 默认 port 9880

定位：
P5 TTS。

## 13. 每次新技术进入项目必须记录

- source URL
- commit/release
- license
- model license
- advertised hardware
- 本机 VRAM/RAM
- disk
- workflow
- elapsed
- quality
- rollback

没有本机数据，不升级 Production。
