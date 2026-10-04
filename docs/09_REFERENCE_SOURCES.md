# 09 技术来源、参考仓库与借鉴方法

更新时间：2026-10-04

本项目不凭空发明流程。下面列出已核验的主要公开来源，并明确“参考什么、不要照搬什么”。

## 1. Drama Skills

仓库：
https://github.com/zenstory-ai/drama-skills

专题：
https://github.com/zenstory-ai/drama-skills/blob/main/docs/open-source-short-drama-pipeline.md

许可证：MIT。

重点参考：
- 文本优先的短剧生产事实；
- 剧本 → 视觉设定 → 图片提示词/分镜 → 视频提示词；
- continuity locks；
- IMG / PLAN / REF 三层 reference 状态；
- frozen keyframe；
- preview → explicit confirmation → production；
- review 与 production 分离。

本项目如何用：
- 借鉴生产事实和 gate 思路；
- 不把五份 Markdown 的具体格式当不可变标准；
- 增加机器 manifest、GPU benchmark、ComfyUI adapter 和本地大文件目录。

## 2. Story Claw

仓库：
https://github.com/ZC89757/story-claw

许可证：MIT。

重点参考：
- stage-aware character/scene assets；
- 跨集 voice map；
- 每镜生成后 VLM 质量检查；
- 失败 clip 自动重跑；
- workspace 分集归档；
- 本地 ComfyUI 视频后端；
- 脚本、资产、分镜、渲染分阶段。

本项目如何用：
- 学习“长系列资产如何演进”和“自动 QC”；
- 不直接绑定其 LTX backend；
- 不采用其完整 Electron 产品作为当前工程核心；
- 先做轻量 CLI + Codex。

## 3. Wan2.2

官方仓库：
https://github.com/Wan-Video/Wan2.2

许可证：Apache-2.0（代码仓库；权重仍需单独核对对应模型条款）。

已核验能力：
- T2V / I2V / TI2V；
- 5B TI2V；
- ComfyUI 集成；
- Animate 14B；
- S2V 14B。

本项目如何用：
- 当前主视频族；
- MVP 只要求短镜 I2V；
- Animate/S2V 作为未来可选，不写死。

## 4. ComfyUI-WanVideoWrapper

仓库：
https://github.com/kijai/ComfyUI-WanVideoWrapper

重点参考：
- FP8 scaled；
- GGUF；
- block swapping / offload；
- 新 Wan 生态模型快速支持；
- 12GB/低显存实验路线。

关键原则：
其 README 明确建议“native ComfyUI 已支持时优先 native”。因此本项目把 Wrapper 放 Lab/low-VRAM 通道，不把它变成唯一 production 依赖。

## 5. FramePack

仓库：
https://github.com/lllyasviel/FramePack

许可证：Apache-2.0。

官方 README 说明：
- next-frame-section progressive generation；
- 上下文计算量不随视频长度线性增长；
- RTX 30/40/50 系列；
- 最低 6GB GPU memory；
- 可做长视频。

本项目如何用：
- 长镜头和低动作回退；
- 不是所有镜头默认使用；
- 重点 benchmark 漂移和速度。

## 6. PuLID

仓库：
https://github.com/ToTheBeginning/PuLID

许可证：Apache-2.0。

已核验：
- SDXL；
- PuLID-FLUX；
- 官方 README 说明 FLUX local demo 支持 12GB。

本项目如何用：
- 林黛玉人脸身份参考；
- 先 reference，再决定是否训练 LoRA。

## 7. ComfyUI IPAdapter Plus

仓库：
https://github.com/cubiq/ComfyUI_IPAdapter_plus

许可证：GPL-3.0。

已核验：
- IPAdapter reference implementation；
- FaceID；
- style/subject conditioning；
- 2025-04-14 起作者声明 maintenance-only。

本项目如何用：
- 可作为成熟参考能力；
- 不把未来开发押在该插件；
- 若分发/修改 GPL 代码，必须评估 GPL 义务；
- 优先把它作为外部安装依赖而非复制进仓库。

## 8. MuseTalk

仓库：
https://github.com/TMElyralab/MuseTalk

许可证：MIT，另有依赖许可证清单。

已核验：
- 1.5；
- 多语言，包括中文；
- audio-driven lip sync；
- 训练/推理代码开放。

本项目如何用：
- 标准人脸对白镜头；
- 非标准猿猴脸需单独验证。

## 9. GPT-SoVITS

仓库：
https://github.com/RVC-Boss/GPT-SoVITS

许可证：MIT（仍需按所用权重/数据核对条款）。

已核验：
- zero-shot TTS；
- few-shot TTS；
- 中文等多语言；
- Windows 支持；
- 官方给出消费级 GPU 推理数据。

本项目如何用：
- 角色固定 voice map；
- 只使用拥有权利的训练/参考声音。

## 10. ComfyUI

仓库：
https://github.com/comfyanonymous/ComfyUI

本项目如何用：
- 核心媒体执行引擎；
- workflow JSON 是可版本化生产配置；
- 通过本地服务队列让 Codex/CLI 调度，而不是依赖人工逐节点点击。

## 11. 借鉴规则

允许：
- 学习架构；
- 学习目录；
- 学习流程；
- 在许可证允许下调用依赖；
- 在许可证允许下复用/改造代码并履行义务。

不做：
- 复制他人 demo 的人物和美术资产；
- 复制现代影视演员脸；
- 复制具体影视服装设计；
- 把第三方代码许可证忽略掉；
- 把第三方模型“代码许可证”等同于“权重商业许可证”。

## 12. 每次技术升级的固定动作

Codex 在引入新项目时必须记录：
- source_url
- commit/release
- license
- model_license
- vram_claim
- 本机实测
- 替代对象
- rollback
- 是否进入 Lab 或 Production

未经本机 benchmark 不允许直接替换主线。
