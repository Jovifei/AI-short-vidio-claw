# 03 技术架构（收窄执行版）

## 1. 架构原则

继续保持四层：

### Creative Truth
Markdown/YAML/JSON：
剧本、角色、stage、continuity、shot。

### Control Plane
P1 只有最小脚本；
P4 才升级为完整 CLI。

### Media Plane
P1A：单 ComfyUI + Wan2.2-TI2V-5B。
以后通过 adapter 接：
FramePack / WanGP / TTS / LipSync。

### Storage Plane
Git 保存事实；local 保存模型和大媒体。

## 2. 当前有效数据流

```text
Episode/Shot 文本事实
  ↓
Approved Keyframe
  ↓
单一 ComfyUI 服务（实际端口 P0R 探测）
  ↓
Wan2.2-TI2V-5B Native Workflow
  ↓
短视频输出
  ↓
P1 metadata / benchmark
```

P1A 到此为止。

P2/P3 才扩展：

```text
Character Assets
  ↓
Dual-identity Keyframe
  ↓
Approved Keyframe
  ↓
Video
  ↓
First Cut
```

P5 才进入：

```text
TTS → LipSync → SFX/BGM → FFmpeg
```

## 3. 单 ComfyUI 进程原则

原“8188 image + 8189 video”只是一种未来部署模式，不再是当前架构要求。

目标硬件只有 12GB VRAM，因此当前规定：
- GPU-heavy active process = 1；
- ComfyUI 实际 URL 由 P0R 探测；
- 不因上游默认端口就覆盖 Desktop 配置；
- 需要切环境时显式 stop → verify GPU memory released → start next。

未来如果验证“同一个 ComfyUI 环境能完成 image/video”，优先一个实例完成。

## 4. P1A API 边界

只需要一个脚本：
`scripts/p1_comfy_probe.py`

职责：
1. 读取 COMFYUI_URL；
2. health check；
3. 读取已导出的 API workflow JSON；
4. 注入：
   - input image
   - prompt
   - seed
   - width/height
   - frames
5. 提交任务；
6. 轮询/监听；
7. 找到输出；
8. 写 benchmark JSON。

不实现：
- episode state machine
- adapters framework
- TTS
- lipsync
- scheduler
- multi-worker
- UI

这些留到 P4。

## 5. P1A 模型边界

Production Candidate A：
Wan2.2-TI2V-5B only。

明确排除 P1A：
- A14B
- GGUF 14B
- Wrapper 14B
- LTX-2.x
- Animate
- S2V

## 6. 参数阶梯

一次只改一个变量。

Baseline:
- 480×832
- 49 frames
- 官方模板默认其他参数

然后：
A. 同尺寸 → 81 frames
B. 回到 49 frames → 576×1024
C. 只有 A/B 都稳定才试更高组合

如果官方 template 约束不同，以实际工作流为准并记录。

## 7. P1A-Q 视觉质量

基础运行通过后，固定 3 个 approved keyframe：
- 单人微动作
- 双人无接触
- 双人低接触但不涉及手部特写

每个 3 takes。

评分：
- identity preservation
- anatomy
- motion readability
- background stability
- camera stability

高风险手部交互不用于决定 5B 能否作为基础引擎。

## 8. P2 双身份架构

P2 要解决的是同一张关键帧内同时锁：
- DAIYU
- WUKONG

候选方法作为实验，不预先批准：
- dual reference conditioning
- regional mask / regional conditioning
- two-pass inpaint/composite
- character LoRA + human identity reference
- Hero Lane manual generation

Gate 看最终图，不看“用了多少模型”。

## 9. Executor 扩展

P1A 后如果需要：
- FramePackAdapter
- WanGPAdapter
- WanVideoWrapperAdapter

只有 benchmark 胜出才加入 production registry。

## 10. 视频与音频串行

P5 以后：
video model unload
→ verify VRAM release
→ TTS/lipsync
→ unload
→ next GPU stage

32GB RAM 下避免同时把大模型留在内存。
