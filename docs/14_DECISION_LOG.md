# 14 架构决策记录 ADR（V2）

## ADR-001 Image First → Video Second
Accepted。Production 主角镜头禁止纯 T2V。

## ADR-002 Wan2.2 5B
Accepted as measured Lab runtime and conditional LOW-risk Production candidate。
只有 approved keyframe 的 T1 通过后，才能升级为 Production Candidate。

## ADR-003 Lab / Production 分离
Accepted 2026-10-05。
现有多数视频是 benchmark，不是产品素材。
LAB_ONLY 不进入 final timeline。

## ADR-004 Visual Target Before Motion
Accepted 2026-10-05。
V0/K1 必须在 Production I2V 之前。
这解决旧路线中“P1A 需要 approved input，但 approved input 放到后续阶段才创建”的循环。

## ADR-005 Visual Reference Is Identity Source
Accepted 2026-10-05。
用户批准 reference/golden keyframe 高于文字 prompt。

## ADR-006 Active Costume Policy
Accepted 2026-10-05。
当前 Pilot 人物只用批准古装；现代生活场景允许，但人物现代服装禁止。

## ADR-007 Hero Lane
Accepted。
MVP 可以用 ChatGPT Web 生成全部关键帧。
本地身份自动化不是首条成片的前置条件。

## ADR-008 Motion Risk Tier
Accepted。
采用 M0/M1/M2/M3。
高风险镜头第一版可以高质量静态 + 轻镜头运动。

## ADR-009 Human Gates
Accepted。
- Visual Target Lock
- Keyframe Approval
- Final Approval

## ADR-010 Local Identity Automation Deferred
Accepted 2026-10-05。
PuLID/IPAdapter/LoRA 在 E0/E1 视觉路线证明后再做，用于降低人工成本和提高自动化。

## ADR-011 Existing P0R/P1A Data
Accepted as historical Lab evidence。
不删除 5B 模型、T2V benchmark 和 I2V wiring 记录，但不把它们写成人物质量证明。

## ADR-012 EP001 Starts After Look Reel
Accepted 2026-10-05。
先做 10 keyframes + 20–30 秒 E0，用户确认人物后再做完整故事。

## ADR-013 Release Review
Accepted。
公开发布前单独检查 reference、模型、声音、音乐和相关素材的使用条件。
