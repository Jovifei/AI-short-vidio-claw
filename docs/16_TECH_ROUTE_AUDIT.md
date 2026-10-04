# 16 技术路线审核报告（2026-10-04）

状态：审核完成，结论 **GO（可行，附 5 项修正）**。本报告不推翻任何既有 ADR，
只修正事实边界、扩充 benchmark 候选集，并登记新的已知缺口。

审核方法：

1. 内部一致性：通读全部 00–15 号文档并交叉核对。
2. 外部事实核验：对技术路线中的每一条模型/显存/许可证声称，逐一对照官方 README、
   ComfyUI 官方文档与社区实测数据（核验日期 2026-10-04）。

---

## 1. 外部事实核验结果

| # | 文档声称 | 出处 | 核验结论 |
|---|---|---|---|
| 1 | Wan2.2 已进入 ComfyUI 原生生态（T2V/I2V/TI2V） | docs/02, docs/08 | ✅ 属实。ComfyUI 官方提供 Wan2.2 原生教程 |
| 2 | Wan2.2 5B TI2V 面向消费级 GPU | docs/02 | ✅ 属实且偏保守。官方文档称 5B 配合 ComfyUI 原生 offload 可在 8GB 显存运行；本项目"不把 720P 原生满配当 12GB 基线"的谨慎是正确的 |
| 3 | Wan2.2 A14B 12GB 可运行 | docs/02/03 隐含 | ⚠️ 有条件属实。FP16 约需 45–65GB，FP8 约需 18–26GB（12GB 装不下）；只有 GGUF Q4/Q5 + CPU offload（实测约 5–10GB）可在 4070 级 12GB 卡上运行，且量化版本加载需要 ComfyUI-GGUF 自定义节点。**"纯原生节点 + 14B + 12GB" 不成立** |
| 4 | WanVideoWrapper 作者建议原生可用时优先原生；Wrapper 永久 WIP；支持 FP8/GGUF/block swap | docs/02/03/08/ADR-003 | ✅ 属实。README 原文："Unless it's a model/feature not available yet on native, you shouldn't." |
| 5 | FramePack 最低 6GB，RTX 30/40/50 可运行 | docs/02/ADR-004 | ✅ 属实。社区有 RTX 4060 8GB 成功实测。注意其底座是 Wan 系 14B，长视频中段漂移需专项评估 |
| 6 | PuLID 官方称 FLUX 本地 demo 支持 12GB | docs/02/08 | ⚠️ 基本属实但有歧义。官方 README 同时写明 "PuLID-FLUX can run on a 16GB graphic card" 与 "Local gradio demo supports 12GB graphic card now"。12GB 说法对应 gradio demo（依赖 CPU offload，速度明显下降），不等同于生产用 ComfyUI 节点路径。**P2 必须在 ComfyUI 内实测 PuLID-FLUX 12GB 工作流后才可作为路线依据** |
| 7 | ComfyUI_IPAdapter_plus 自 2025-04-14 起 maintenance-only；GPL-3.0 | docs/08/09/12 | ✅ 属实。"保留能力、不押注更新、不 vendor 源码"的处理正确 |
| 8 | MuseTalk 1.5 支持中文等多语言口型 | docs/02/08 | ✅ 属实。且显存需求低（约 4GB 级），对 12GB 目标无压力 |
| 9 | GPT-SoVITS few-shot/zero-shot TTS，消费级显卡可用 | docs/02/08 | ✅ 属实（1 分钟样本可训练/推理，官方给出消费级 GPU 数据） |
| 10 | Wan2.2 Animate/S2V 为 14B，先验证再决定，不作 MVP 依赖 | docs/08/PROJECT_STATE | ✅ 判断正确。社区反馈 16GB 卡跑 Animate 也需 offload 才勉强可行，12GB 不应押注 |

## 2. 时效性核验（2026-10 视角）

- **Wan 2.5 / 2.6：未开放权重**（API/商业版）。主线押注 Wan2.2 开源族没有踩空。
  Wan 2.7 仅部分模型开放，状态需持续跟踪。
- **LTX-2.x（如 LTX-2.3）已成为开源视频主力竞争者**，以速度低显存著称，
  原矩阵（docs/08）未覆盖。
- **Wan2GP（deepbeepmeep/Wan2GP）** 是面向低显存 GPU 的 Wan 运行器，
  12GB 场景值得纳入对照。

结论：路线不算错误，但 docs/08 的"当前推荐"落后约半个世代。若不在 P1 引入
新候选，可能在次优基线上冻结 production workflow。

## 3. 内部一致性问题

1. **fps 链路未闭合**：`config/project.example.yaml` 交付 24fps，
   `runtime.example.yaml` 源 fps 为 16/24，docs/07 manifest 示例 fps=16，
   而 Wan2.2 A14B 原生输出 16fps。插帧模型在 PROJECT_STATE 中为"尚未决定"，
   16→24 的策略悬空。
2. **放大链路未决策**：576×1024 → 1080×1920 需约 1.9× 放大，放大模型未选
   （已诚实标注待定，但为 P1 后必答题）。
3. **速度预算缺失**：量化 14B 在 12GB 上单镜（3–5 秒）预计分钟级到十几分钟级；
   20 镜 × 2–3 takes ≈ 单集纯生成小时级。P1 已要求记录耗时，但未定义
   "可接受的单集总工时"这一 Gate。
4. **存储预算缺失**：Wan 权重族 + FLUX/SDXL 基座 + 文本编码器 + LoRA 训练数据，
   `local/models` 预计 100GB+，无容量规划条目。

## 4. 最大技术缺口：双身份同框关键帧

docs/06 分别给出林黛玉（PuLID/LoRA）与孙悟空（LoRA+reference）的身份方案，
但**没有任何文档给出"两个身份在同一关键帧中同时锁定"的工作流方案**
（双条件叠加、分区 PuLID/IPAdapter、In-Context LoRA、regional mask 等均未评估）。
EP001 的 20 镜中双人镜头占比过半，此项是 P2 的第一优先课题。

## 5. 修正建议（按优先级）

| 序号 | 建议 | 落点 |
|---|---|---|
| R1 | P1 benchmark 候选集扩充：native 5B TI2V / native+ComfyUI-GGUF 14B / WanVideoWrapper FP8 / FramePack / **LTX-2.x / Wan2GP** | docs/08、PROJECT_STATE、ADR-011 |
| R2 | 修正"原生优先"边界：12GB 上 14B 的"原生"必须搭配 GGUF 量化节点；纯原生 tier 是 5B TI2V 与低分辨率 | ADR-002 补注 |
| R3 | 立项"双身份同框 keyframe"专项（P2 前置） | docs/06 后续专项文档 |
| R4 | P1 结束时确定 fps/插帧/放大链路 | PROJECT_STATE 待定项 |
| R5 | P1 增加单集总工时推算与 `local/models` 存储预算 | P1 通过条件 |

## 6. 总体判定

**GO。** Image First → Video Second、原生优先 + Wrapper 作 Lab 层、FramePack 回退、
人类/非人角色分策略、adapter 化、GPU 串行、两道人工 Gate 等核心决策与外部事实全部
吻合；P1 Gate（12GB 稳定 3–5 秒 I2V、10 次运行 OOM ≤2）在 5B TI2V 或 GGUF 量化 14B
路线下属可达成。项目不存在需要中止的单点依赖，但必须先按 R1–R5 修正执行细节。

## 7. 核验来源（2026-10-04 访问）

- ComfyUI 官方 Wan2.2 教程：https://docs.comfy.org/tutorials/video/wan/wan2_2
- Wan2.2 VRAM 实测汇总：https://willitrunai.com/blog/wan-2-2-vram-requirements
- Wan 2.2 14B Low-VRAM 工作流：https://github.com/Cordux/ComfyUI-Wan2.2-workflow
- kijai/ComfyUI-WanVideoWrapper README：https://github.com/kijai/ComfyUI-WanVideoWrapper
- Wan-Video/Wan2.2 官方仓库：https://github.com/Wan-Video/Wan2.2
- FramePack 8GB 实测：https://github.com/lllyasviel/FramePack/issues/43
- ToTheBeginning/PuLID README：https://github.com/ToTheBeginning/PuLID
- cubiq/ComfyUI_IPAdapter_plus README：https://github.com/cubiq/ComfyUI_IPAdapter_plus
- TMElyralab/MuseTalk：https://github.com/TMElyralab/MuseTalk
- RVC-Boss/GPT-SoVITS：https://github.com/RVC-Boss/GPT-SoVITS
- Wan 2.5/2.6/2.7 权重开放状态：https://wan27.org/blog/latest-wan-model
- LTX-2.3 vs Wan2.2 对比：https://www.nemovideo.com/blog/ltx-2-3-vs-wan-2-2
- 开源视频模型 2026 格局：https://ltx.io/blog/open-source-video-generation-models-guide
- Wan2GP：https://github.com/deepbeepmeep/Wan2GP
- Wan2.2-Animate-14B 16GB 显卡讨论：https://huggingface.co/Wan-AI/Wan2.2-Animate-14B/discussions/4

注意：以上第三方网页与社区数据仅作路线参考，任何模型在本项目的最终定位仍以
`docs/benchmarks/` 下 4070S 本机实测为准（AGENTS.md 固定 benchmark 原则）。
