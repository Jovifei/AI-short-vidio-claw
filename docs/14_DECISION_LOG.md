# 14 架构决策记录 ADR

## ADR-001：采用 Image First → Video Second

状态：Accepted

原因：
- 双人连续性比文生视频更难；
- 角色脸是本项目核心资产；
- 冻结 keyframe 能把“人物设计”和“动作生成”解耦；
- 失败镜头可局部返工。

替代：
纯 T2V。

不选原因：
人物和构图不够可控，不适合作为系列主线。

---

## ADR-002：原生 ComfyUI + Wan2.2 为主视频路线

状态：Accepted for Benchmark

原因：
- Wan2.2 官方已进入 ComfyUI 生态；
- 降低自定义插件耦合；
- 更适合长期 workflow 维护。

备注：
必须经过 P1 12GB 实测才升级为 Production Frozen。

---

## ADR-003：WanVideoWrapper 为 Lab/Low-VRAM 层

状态：Accepted

原因：
- 支持 FP8/GGUF/block swap/offload 与大量新模型；
- 适合 12GB；
- 更新快。

为什么不做唯一主线：
其作者 README 明确建议 native 可用时优先 native，且项目长期 WIP。

---

## ADR-004：FramePack 做长镜/低动作回退

状态：Accepted for Benchmark

依据：
官方声明 RTX 30/40/50、最低 6GB 显存可运行，长视频上下文设计对消费卡友好。

不作为默认：
生活短剧仍需要镜头级导演和角色连续性，长生成不是核心 KPI。

---

## ADR-005：人类和非人角色使用不同 identity 策略

状态：Accepted

林黛玉：
PuLID/IPAdapter → 稳定后 LoRA。

孙悟空：
角色 LoRA + reference conditioning 优先。

原因：
FaceID/InsightFace 对标准人脸更可靠，不应假设同样适用于猿猴角色。

---

## ADR-006：不把影视版林黛玉演员作为目标 identity

状态：Accepted

只提取非独占的抽象视觉方向：
圆润鹅蛋脸、非尖下巴、古典眼眉、灵秀气质。

实际资产需要独立原创，避免系列永远依赖某现代演员 likeness。

---

## ADR-007：两道永久人工 Gate

状态：Accepted

1. Keyframe Approval
2. Final Approval

即使未来一键化，也不删除。

原因：
创作质量、版权风险和 AI 异常不能完全由自动评分替代。

---

## ADR-008：Git 只存创作事实，不存大媒体/大模型

状态：Accepted

原因：
- clone 可控；
- 模型可替换；
- 媒体由 manifest 关联；
- GitHub 不适合大模型与批量视频。

---

## ADR-009：先 CLI 后 UI

状态：Accepted

原因：
当前价值在生产闭环、benchmark 和可复现，不在界面。

UI 只有在 P6 后 pipeline 稳定才值得做。

---

## ADR-010：借鉴 Story Claw 与 Drama Skills 的理念，不 fork 为核心

状态：Accepted

借鉴：
- stage-aware assets
- voice map
- VLM QC
- continuity lock
- frozen keyframe
- text-first production facts

不直接 fork：
本项目硬件、ChatGPT Hero Lane、视频引擎和角色问题不同，需要更轻、更可替换的控制平面。
