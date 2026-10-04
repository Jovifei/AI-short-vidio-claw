# AI-short-vidio-claw

> 本地优先、角色一致、可复现的 AI 竖屏短剧生产线。目标硬件：Windows + RTX 4070 Super 12GB + 约 32GB RAM + ComfyUI + Codex。

## 当前技术状态

**战略结论：GO。当前机器生产就绪度：NO-GO，先完成 P0R/P1A。**

本项目核心方法仍成立：
- Image First → Video Second；
- 角色/造型/道具连续性先冻结，再生成视频；
- GPU 重任务串行；
- 每镜可追溯、可重跑；
- 两道人类 Gate：Keyframe Approval / Final Approval。

但 2026-10-04 二次复核后，立即执行路线已收窄：

> **P1A 只验证：单 ComfyUI 进程 + Wan2.2-TI2V-5B + 官方原生 workflow + native offload。**

暂不把以下内容放进 P1A：
- Wan2.2 14B；
- GGUF 14B；
- WanVideoWrapper 14B/block-swap；
- LTX-2.x 原生 ComfyUI；
- PuLID / FaceID；
- GPT-SoVITS / MuseTalk；
- 两个同时常驻的 ComfyUI 服务。

原因不是这些路线“永远不能用”，而是当前机器为 12GB VRAM + ~32GB RAM，且本地尚未安装 Wan 权重/完成 API workflow 基线。先把变量收窄，拿到本机证据，再扩展。

## 第一阶段目标

把一张已人工确认的关键帧，用 Wan2.2-TI2V-5B 在本机生成第一条可复现的短视频，并记录：

- 模型文件名与 hash
- ComfyUI commit
- workflow hash
- 实际端口
- 输入 keyframe
- prompt
- seed
- 分辨率
- 帧数
- 实际 fps
- 峰值显存
- 系统 RAM 峰值
- 运行耗时
- 输出路径
- 成功/失败原因

**P1 Gate 不再预设“576×1024 一定稳定”。** 分辨率和帧数必须通过阶梯实测得到。

## 当前生产架构

```text
故事/剧本
  ↓
视觉设定 + 连续性锁
  ↓
正式分镜
  ↓
冻结关键帧
  ├─ Hero Lane：ChatGPT/人工精修
  └─ Local Lane：ComfyUI（P2 以后）
  ↓
Approved Keyframe
  ↓
P1A 视频基线
  └─ 单 ComfyUI + Native Wan2.2-TI2V-5B
  ↓
P1B 可选对照（仅 P1A 通过后）
  ├─ FramePack
  └─ WanGP / 其他低显存 runner
  ↓
P2 双身份同框 keyframe
  ↓
P3 EP001 First Cut
  ↓
P4 完整控制平面
  ↓
P5 TTS / Lip Sync / 后期
  ↓
P6 一键单集
  ↓
P7 系列化
```

## 重要事实边界

- Wan2.2 官方仓库的 5B 720P 独立推理示例写的是至少 24GB VRAM；但 ComfyUI 官方 Wan2.2 页面明确写“5B version should fit well on 8GB vram with the ComfyUI native offloading”。因此本项目不拿任何一边的数字直接当 4070S 实测结果，而是以本机 benchmark 为准。
- Wan2.2 I2V-A14B 官方独立推理示例要求至少 80GB VRAM。12GB 上的 14B 必须依赖量化/强 offload/第三方实现，故退出 P1A。
- LTX-2.x 官方 ComfyUI-LTXVideo 当前 README 推荐 32GB+ VRAM，因此不作为本机 P1A/P1B 原生 ComfyUI 首选。
- MuseTalk 官方 Gradio 默认端口是 7860；GPT-SoVITS API v2 默认 9880；ComfyUI 上游默认 8188，但本项目必须发现实际本机端口，不允许硬编码。

## 文档阅读顺序

新接手 AI/Codex：
1. AGENTS.md
2. PROJECT_STATE.md
3. docs/17_TECH_ROUTE_REVALIDATION.md
4. docs/00_PROJECT_CHARTER.md
5. docs/01_PRD.md
6. docs/02_FEASIBILITY.md
7. docs/03_TECHNICAL_ARCHITECTURE.md
8. docs/04_SOP.md
9. docs/05_DIRECTORY_STANDARD.md
10. docs/06_CHARACTER_SYSTEM.md
11. docs/08_MODEL_AND_WORKFLOW_MATRIX.md
12. docs/10_QA_ACCEPTANCE.md
13. docs/11_ROADMAP.md
14. docs/13_CODEX_RUNBOOK.md
15. docs/14_DECISION_LOG.md
16. docs/15_EP001_PILOT_PLAN.md
17. docs/stages/ 下对应阶段执行报告

## 本地数据原则

Git 只保存：
- 代码
- 配置
- workflow
- 剧本/分镜/提示词
- model manifest
- benchmark
- QA

不提交：
- 大模型
- LoRA 权重
- cache
- 批量帧
- 大视频
- API key

## 当前下一步

本地 Agent 只执行：
**docs/stages/P0R_REBASE_EXECUTION.md → docs/stages/P1A_WAN22_5B_BASELINE.md**

在 P1A prerequisites 未通过前，**不提交任何图生视频任务**。
