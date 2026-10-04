# 02 可行性研究报告（2026-10-04 二次复核版）

## 结论

**项目战略可行（GO），当前机器尚未达到“今天即可生产”状态（Current Production NO-GO）。**

核心路线成立，但立即执行路径必须收窄为：

> 单 ComfyUI GPU 进程 + Wan2.2-TI2V-5B + 官方原生 workflow + native offload + 单张 approved keyframe + 最小 API 调用。

完成 P1A 实测后，再决定是否扩展到 FramePack、WanGP、量化 14B 或其他 runner。

## 1. 为什么原路线需要修正

原计划把“Native ComfyUI + Wan2.2”写得过宽，容易把 5B 与 14B 混在一起。

### 官方事实 A：Wan2.2 官方仓库
Wan2.2-TI2V-5B 的 720P 独立推理示例写明至少 24GB VRAM。
Wan2.2-I2V-A14B 独立推理示例写明至少 80GB VRAM。

来源：
https://github.com/Wan-Video/Wan2.2

### 官方事实 B：ComfyUI 官方文档
ComfyUI Wan2.2 官方教程明确写：
“The Wan2.2 5B version should fit well on 8GB vram with the ComfyUI native offloading.”

来源：
https://docs.comfy.org/tutorials/video/wan/wan2_2

这两条不是简单互相否定，而是运行时与 offload 策略不同。因此：
- 不应把官方仓库的 24GB 直接理解成“12GB 一定不能跑 5B”；
- 也不应把 ComfyUI 的 8GB 说明写成“本机 576×1024/3–5 秒一定稳定”。

正确做法是 P1A 本机实测。

## 2. 目标硬件

- Windows
- RTX 4070 Super 12GB
- 系统 RAM 约 32GB
- ComfyUI Desktop
- FFmpeg
- Codex

约 32GB RAM 是重要约束：
- 14B 强 CPU offload/block swap 不是当前最小可靠路线；
- 任何声称“显存只占 5–10GB”的 14B 社区方案，都必须同时测系统 RAM 和 pagefile；
- 不把别人 64GB/128GB RAM 的结果外推到本机。

## 3. 视频路线可行性

### P1A：Wan2.2-TI2V-5B Native ComfyUI

结论：**优先验证，具备现实可行性。**

理由：
- ComfyUI 官方提供原生 5B workflow；
- 官方明确提到 native offloading 和 8GB VRAM；
- 单模型同时支持 T2V/I2V；
- 对现有 ComfyUI 生态侵入最小。

风险：
- 官方未给出本项目 480×832 / 576×1024、49/81 frames 在 4070S 12GB 上的完整数据；
- 因此分辨率、帧数、耗时、RAM 使用都只能靠 P1A 得出。

### Wan2.2 14B

结论：**退出 P1A。**

官方 I2V-A14B 独立推理要求至少 80GB VRAM。
12GB 上可以存在 GGUF/量化/offload 等社区实现，但其风险是：
- 自定义节点；
- 更大系统 RAM 压力；
- 更慢；
- 更多变量；
- 本机 32GB RAM 尚未证明安全。

所以只允许在 P1A 成功以后作为 Lab 候选，且必须独立审批。

### WanVideoWrapper

结论：**保留 Lab，不进入 P1A。**

优点：
- FP8
- GGUF
- block swap
- offload
- 新 Wan 生态功能跟进快

但其 README 明确建议：原生 ComfyUI 已支持时优先 native。

因此生产原则：
native first；wrapper only when needed。

### FramePack

结论：**P1B 可选。**

官方 FramePack：
- RTX 30/40/50
- 最低 6GB VRAM
- 渐进式 next-frame-section

适合：
- 长一点的低动作镜头；
- P1A 质量/速度不满足时作对照。

不作为 P1A 首装，避免同时改变运行栈。

### WanGP

结论：**P1B/P1C 可选 runner。**

WanGP 2026 仍持续更新并针对低显存做大量优化，也支持多种视频模型。
但它是另一套执行环境；社区也存在系统 RAM 不足的案例。

因此：
- 不是当前 ComfyUI 主线；
- P1A 成功后如需要更低显存/新模型再加入；
- 任何 14B / H3 / LTX 结果都必须记录 RAM 峰值。

### LTX-2.x

结论：**不进入当前 P1 原生 ComfyUI最小路径。**

Lightricks 官方 ComfyUI-LTXVideo 当前 README 推荐：
- CUDA GPU
- 32GB+ VRAM
- 100GB+ free disk

来源：
https://github.com/Lightricks/ComfyUI-LTXVideo

即使其他 runner 可做更低显存，不等于本机原生 ComfyUI 路径成立。后续可作为 Lab。

## 4. 图像身份路线

P1 不验证身份模型。

原因：
P1 的问题只有一个：
**这台机器能否稳定把 approved keyframe 变成视频。**

P2 再处理：
- 林黛玉：PuLID / IPAdapter / LoRA
- 孙悟空：LoRA + reference
- 双身份同框：专项

PuLID 官方 12GB 说法与本项目 ComfyUI production path 不是同一件事，必须 P2 本机实测。

## 5. 服务可行性

上游默认：
- ComfyUI：8188
- GPT-SoVITS API v2：9880
- MuseTalk Gradio：7860

但本机 ComfyUI Desktop 曾报告 8000，因此本项目：
- 端口必须 P0R 探测；
- 配置不再写死 8188/8189；
- 12GB 下只有一个 GPU-heavy 服务活动；
- P1 不启 GPT-SoVITS/MuseTalk。

## 6. EP001 可行性

原 EP001 最大问题是把最难动作放进第一批动画：
- 消毒
- 绷带手部特写
- 按手
- 泡沫点鼻子

这些是高遮挡/高接触镜头，不适合拿来验证视频 baseline。

修正：
- 20 张 story keyframe 全做；
- P3 v0.1 只动画 6 个低风险/微动作镜头；
- 高风险镜头先用静态图 + Ken Burns / 景深 / 环境动效；
- 三句台词画外音；
- 不做 lip sync。

## 7. 可行性 Gate

战略 GO 不等于 Production Ready。

顺序：
P0R 环境确认
→ P1A 5B baseline
→ P1A-Q 视觉质量
→ P1B 可选替代
→ P2 双身份
→ P3 First Cut

任何阶段未过 Gate，不进入下一阶段大规模安装/生产。

## 8. 最终结论

原项目方向不需要推翻，但必须撤回四类未测断言：
1. “Wan2.2”不再泛指 5B/14B；
2. 不预设 576×1024 稳定；
3. 不预设双 ComfyUI 服务；
4. 不把单人 identity 方案当双人同框已经解决。

修正后，项目可按阶段继续。
