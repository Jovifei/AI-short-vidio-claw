# AGENTS.md — AI/Codex 接手规则

## 必须先读

1. README.md
2. PROJECT_STATE.md
3. docs/17_TECH_ROUTE_REVALIDATION.md
4. docs/00_PROJECT_CHARTER.md
5. docs/02_FEASIBILITY.md
6. docs/03_TECHNICAL_ARCHITECTURE.md
7. docs/04_SOP.md
8. docs/05_DIRECTORY_STANDARD.md
9. docs/10_QA_ACCEPTANCE.md
10. docs/11_ROADMAP.md
11. docs/13_CODEX_RUNBOOK.md
12. docs/14_DECISION_LOG.md

## 当前最高优先级约束

当前机器：Windows + RTX 4070 Super 12GB + 约 32GB RAM。

**P1A 只允许验证 Wan2.2-TI2V-5B 原生 ComfyUI 路径。**
在 P1A 通过前，不得主动：
- 下载/安装 Wan2.2 14B；
- 把 GGUF 14B / WanVideoWrapper block-swap 当作基线；
- 安装 LTX-2.x 作为 P1 必选；
- 开两个 GPU ComfyUI 常驻；
- 接入 PuLID、FaceID、MuseTalk、GPT-SoVITS；
- 批量渲染 EP001；
- 一次性下载几十 GB 与 P1A 无关的模型。

## 不可违背的工程约束

- 第一性目标：角色一致性、故事连续性、生活感，高于原生高分辨率。
- 默认 Image First → Video Second。
- 每集先有文本事实，媒体结果不能成为唯一事实源。
- GPU heavy concurrency = 1。
- 服务地址必须探测实际端口，不使用未经本机确认的 8188/8189/9881 假设。
- P1 Gate 必须来自本机实测，不允许把目标分辨率写成既成事实。
- 人类/非人角色身份策略分开。
- P2 必须先解决“双身份同框 keyframe”，再宣称角色一致性路线通过。
- 难镜头允许静态图 + 缓慢推拉/景深/雨雪环境动效，不强迫 I2V。
- P3 First Cut 暂不做 lip sync；对白先用画外音。
- 不在 Git 提交模型、LoRA 大文件、cache、成片、密钥。
- 外部模型/节点升级先记录来源、版本、许可证、回退。
- 失败镜头局部返工，不破坏整集基线。
- 不自动模仿具体真实演员、配音演员或影视版受保护造型。

## 每次阶段完成必须同步

- PROJECT_STATE.md
- docs/11_ROADMAP.md
- docs/14_DECISION_LOG.md
- docs/benchmarks/*
- 对应 model/workflow manifest

## Benchmark 必填

- machine
- VRAM/RAM
- driver/CUDA/PyTorch
- ComfyUI commit
- model file + hash
- workflow + hash
- input + hash
- seed
- width/height
- frames
- fps
- peak VRAM
- peak RAM
- elapsed
- result
- error
- visual notes

## 不要做

- 不要为了“更先进”扩张 P1A 候选。
- 不要两个变量同时改。
- 不要先建完整源码包再跑第一条 API job。
- 不要把本地 Desktop 端口猜成上游默认。
- 不要将 14B 能在某社区配置上运行，写成“本机生产可用”。
- 不要将静态角色 identity 与双人同框 identity 混为一谈。
