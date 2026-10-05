# PROJECT_STATE

更新时间：2026-10-05
状态：**REMOTE_PREP_COMPLETE / LAB_RUNTIME_VERIFIED / PRODUCT_WAITING_V0_REFERENCE_LOCK**

## 1. 当前判断

Wan2.2-TI2V-5B 在本机的 Runtime 已有有效 Lab 数据。
但现有短剧人物成果不合格，原因不是简单的“模型不能跑”，而是过去没有先锁人物 reference，并混用了 Lab 与 Product。

V2 已完成路线纠偏。

## 2. 远端已经完成

- 项目架构/PRD/SOP
- V2 Lab/Production 分离
- Active Visual Spec
- 角色 Character Cards
- Costume Stages
- Location/Prop Registry
- 第一季创作圣经
- LOOKREEL01 10 构图完整创作包
- EP001 完整剧本与 20 镜
- Image/Video Prompt Packs
- Continuity / Edit / QA
- Production I2V workflow candidate
- Wan2.2 5B local model manifest
- reference_index
- production_guard
- package validator
- local handoff 文档

详细：
docs/23_REMOTE_PREP_COMPLETION.md

## 3. 当前唯一真正前置

V0 Visual Target Lock。

需要本地落地：
- DAIYU face refs
- DAIYU costume refs
- WUKONG face refs
- WUKONG costume refs
- 10 composition refs

并由用户明确批准。

## 4. Lab 已知事实

- ComfyUI: http://127.0.0.1:8188（以本机当前运行复核为准）
- RTX 4070 SUPER 12282 MiB
- RAM ~31.82 GB
- Wan2.2-TI2V-5B 三份核心模型已安装
- 480×832×49 T2V 10/10 success
- p50 187.7095 s
- p95 264.101 s
- 一次 I2V wiring success
- approved identity I2V 尚未验证

## 5. Product 当前 Gate

V0 未 PASS：
禁止 Product I2V。

K1 未 PASS：
禁止 T1。

T1 未 PASS：
Wan2.2 5B 只能叫 Lab Runtime / Production Candidate，不能叫正式生产引擎。

E0 未获用户批准：
禁止完整 EP001 生产。

## 6. 下一步

本地 Codex 执行：
docs/24_LOCAL_CODEX_START_PROMPT.md

远端无需继续编造人物素材。
等待真实 reference → V0 → K1。
