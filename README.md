# AI-short-vidio-claw

> 本地优先、角色一致、可复现的 AI 竖屏短剧生产线。当前首个样片方向：**“林黛玉 × 孙悟空”生活感 CP 短剧**。

## 1. 项目最终要实现什么

把“一个故事想法”稳定地变成一条 **45–90 秒、9:16、10–20 镜头**的 AI 小短剧，并且做到：

- 角色跨镜一致：脸、体型、发型、毛发、服装、道具状态不随镜头随机漂移。
- 生活感优先：包扎、打伞、浇花、翻冰箱、刷牙、做饭、坐公交、逛菜场等真实情侣动作，而不是连续摆拍。
- 先图后视频：先冻结每个镜头的关键帧，再做图生视频，降低双人镜头失控概率。
- 本地优先：RTX 4070 Super 12GB + ComfyUI 为主，本地完成大部分视频、语音、口型和合成。
- 可替换模型：Wan、FramePack、PuLID、IPAdapter、MuseTalk、GPT-SoVITS 都通过 adapter/workflow 层接入，不把项目绑死在某一个模型。
- 可由 Codex 接管：项目事实、阶段、SOP、目录、验收标准、参考来源全部写进仓库，后续 AI 不需要重新猜项目来龙去脉。
- 可追溯：每集从剧本、视觉设定、分镜、关键帧、视频、音频到成片都有对应文件和版本记录。

## 2. 当前技术决策

主路线：

```text
故事/选题
  ↓
剧本与角色连续性锁
  ↓
分镜 + 冻结关键帧
  ↓
关键帧生成（ChatGPT 人工精修 / 本地 ComfyUI 批量）
  ↓
图像 QC
  ↓
ComfyUI 图生视频
  ├─ 主：原生 ComfyUI + Wan2.2
  ├─ 低显存/实验：ComfyUI-WanVideoWrapper
  └─ 长镜头/低动作回退：FramePack
  ↓
TTS（GPT-SoVITS）
  ↓
口型（MuseTalk，适用于人脸对白镜头）
  ↓
BGM/SFX/环境音
  ↓
FFmpeg 剪辑、字幕、响度、导出
  ↓
VLM/规则 QC
  ↓
最终短剧
```

**重要优化：原生 ComfyUI 能完成的功能优先原生实现。** WanVideoWrapper 作者本人也建议：当功能已经进入 ComfyUI 原生实现时优先原生，Wrapper 主要用于实验能力、特殊模型和显存优化。

## 3. 4070S 的定位

RTX 4070 Super 12GB **足够做本项目的 MVP 和持续生产**，但生产设计必须围绕 12GB 显存：

- GPU 重任务串行，不让多个大模型同时常驻显存。
- 原生工作分辨率优先 480×832 / 576×1024，最终再插帧与放大。
- 单镜头优先 3–5 秒、49–81 帧。
- Wan 使用 FP8 / GGUF / offload / block swap 等低显存策略（仅在需要时启用）。
- FramePack 作为长镜头或低显存回退。
- 角色一致性比原始分辨率优先级更高。

## 4. 文档阅读顺序

新接手本项目的 AI / Codex 应按以下顺序阅读：

1. [AGENTS.md](AGENTS.md)
2. [PROJECT_STATE.md](PROJECT_STATE.md)
3. [项目章程](docs/00_PROJECT_CHARTER.md)
4. [产品需求 PRD](docs/01_PRD.md)
5. [可行性研究](docs/02_FEASIBILITY.md)
6. [技术架构](docs/03_TECHNICAL_ARCHITECTURE.md)
7. [生产 SOP](docs/04_SOP.md)
8. [目录规范](docs/05_DIRECTORY_STANDARD.md)
9. [角色一致性系统](docs/06_CHARACTER_SYSTEM.md)
10. [单集工程规范](docs/07_EPISODE_STANDARD.md)
11. [模型与工作流矩阵](docs/08_MODEL_AND_WORKFLOW_MATRIX.md)
12. [技术来源与参考](docs/09_REFERENCE_SOURCES.md)
13. [质量验收](docs/10_QA_ACCEPTANCE.md)
14. [阶段路线图](docs/11_ROADMAP.md)
15. [风险与合规](docs/12_RISK_AND_COMPLIANCE.md)
16. [Codex 执行手册](docs/13_CODEX_RUNBOOK.md)
17. [架构决策记录](docs/14_DECISION_LOG.md)
18. [EP001 试播集计划](docs/15_EP001_PILOT_PLAN.md)

## 5. 仓库不是“模型仓库”

GitHub 只保存：

- 代码
- 配置模板
- ComfyUI workflow JSON
- 提示词
- 剧本/分镜/质量报告
- 模型清单与哈希
- 少量经授权的参考素材

**不提交**大模型权重、LoRA 大文件、缓存、原始批量帧、成片和密钥。它们放在 `local/` 或外部数据盘，由 manifest 记录版本。

## 6. 当前阶段

当前为 **P0：产品与工程基线建立**。

下一阶段是 **P1：4070S 基准验证**：用同一组冻结角色参考图，实测 Wan2.2 原生、WanVideoWrapper 低显存配置、FramePack 的显存、耗时、身份漂移和动作质量，形成可量化选型结论。

详细状态见 [PROJECT_STATE.md](PROJECT_STATE.md)。
