# 17 技术路线再次复核与最终执行裁决

日期：2026-10-04
裁决：**Strategic GO / Immediate Production NO-GO / Approve P0R→P1A**

## 1. 为什么再次复核

项目收到两类审核意见：

A. 战略审核：
认为核心路线可行，但应增加 14B GGUF、LTX-2.x、WanGP 等候选，并补双身份、fps、存储和速度预算。

B. 本机审核：
认为当前 4070S 12GB + ~32GB RAM 尚不能按原文档直接开工，必须把 P1 收窄到 Wan2.2 TI2V-5B、单 ComfyUI、无 identity/TTS/lipsync。

两者不是完全冲突：
- A 更像“未来候选矩阵”；
- B 更像“今天这台机器应该先做什么”。

本裁决把战略与执行分开。

## 2. 复核事实

### F1 5B 不是简单的“24GB 才能跑”
Wan2.2 官方 standalone 720P 示例写至少 24GB。
ComfyUI 官方原生教程同时写 5B + native offloading 应能适配 8GB VRAM。

裁决：
**5B 是 12GB 的合理首测对象，但任何具体尺寸/帧数都必须本机验证。**

### F2 14B 不能写成 12GB 原生默认
Wan2.2 官方 I2V-A14B standalone 写至少 80GB。
ComfyUI 社区有 GGUF/量化路径，但这不是“纯原生 12GB 生产默认”。

裁决：
**14B 退出 P1A。**

### F3 32GB RAM 使重 offload 风险更高
低 VRAM 不代表低总内存。
WanVideoWrapper / WanGP 社区都有 RAM/共享内存相关报告。

裁决：
P1A 不引入 14B block-swap。
P1B 如测试必须记录 peak RAM。

### F4 LTX-2.x 不适合直接加入本机 P1A
Lightricks ComfyUI-LTXVideo 当前 README 推荐 32GB+ VRAM、100GB+ disk。

裁决：
上传审核报告 R1 中“把 LTX-2.x 纳入 P1 候选”不作为立即批准项。
可以未来通过低显存 runner 重新评估，但不进入当前原生 ComfyUI baseline。

### F5 WanGP 值得保留，但不是第一步
WanGP 2026 面向低显存、支持多个新模型，技术上值得关注。
但它会增加第二套环境和变量。

裁决：
P1B optional。

### F6 服务端口必须以本机发现为准
ComfyUI 上游默认 8188。
GPT-SoVITS api_v2 默认 9880。
MuseTalk Gradio app 默认 7860。
本机 Desktop 曾报告 8000。

裁决：
P0R 探测，不硬编码。

### F7 双身份同框是最大内容技术风险
已有文档只写了“黛玉怎么锁”“悟空怎么锁”，没有证明“同一帧如何同时锁”。

裁决：
P2 的第一 Gate 就是双身份同框，而不是 LoRA 训练本身。

## 3. 对两份审核的裁决

### 本机审核：批准的大部分意见
批准：
- P1 只保留 5B 最小路；
- 单 ComfyUI；
- keyframe 人工先行；
- P1 不做 FaceID/PuLID；
- P1/P3 v0.1 不做 lipsync；
- 高风险镜头允许静态；
- 控制面先最小 probe；
- P1 Gate 改成实测。

保留意见：
“今天不能提交任何 I2V”只对“当前 prerequisite 未满足”成立；完成 P0R、下载官方 5B、GUI workflow 成功后，就应提交 P1A 测试，而不是长期停留在文档。

### 16 号战略审核：部分批准
批准：
- fps/upscale/storage/speed budget 必须补；
- 双身份同框专项；
- WanGP 进入未来候选；
- 修正 14B 原生边界。

不批准作为当前 P1A：
- LTX-2.x native；
- 大规模 14B GGUF matrix；
- 同时 benchmark 太多 runner。

理由：
目标是降低变量，而不是证明社区所有路线都能跑。

## 4. 最终生产路线

### Phase 0R
环境事实。

### Phase 1A
Wan2.2-TI2V-5B Native ComfyUI。

### Phase 1B
只有 1A 有明确缺陷才加 FramePack 或 WanGP。

### Phase 2
双身份 keyframe。

### Phase 3
EP001 First Cut：20 still + 6 motion + voice-over。

### Phase 4
完整 Codex/CLI 自动化。

### Phase 5
TTS / LipSync / 音效 / 插帧 / 放大。

### Phase 6
一键单集 + 两个人工 Gate。

### Phase 7
系列化。

## 5. 冻结原则

本文件发布后，在 P1A benchmark 结束前：
- 不再讨论“哪一个 14B 更好”作为主任务；
- 不新增视频模型主线；
- 不同时安装多个 runner；
- 不开始角色 LoRA；
- 不开始 lip sync；
- 不做 UI。

除非 P1A 被客观 blocker 卡死，再开启替代路线。
