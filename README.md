# AI-short-vidio-claw

> 本地优先、角色一致、可复现的 AI 竖屏短剧生产线。目标硬件：Windows + RTX 4070 Super 12GB + 约 32GB RAM + ComfyUI + Codex。

## 当前状态

**技术 Lab：Wan2.2-TI2V-5B 已证明能在本机运行。**
**产品 Production：尚未通过人物视觉锁定，当前禁止继续用未批准角色图制作故事视频。**

2026-10-05 审核发现：
- 大部分已生成 mp4 是官方模板地铁乐手；
- 一条 SH001 是无参考图 T2V；
- 唯一一次 I2V 使用未审核 SDXL 静帧；
- 因此“成果不像要求”不是 5B 已经被证明不行，而是 Production 根本还没按产品要求开始。

完整纠偏：
- docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
- docs/19_ACTIVE_VISUAL_SPEC.md

## V2 当前有效路线

```text
V0 视觉 reference 锁定
  ↓
K1 用户 10 个构图 → 10 张 approved keyframe
  ↓
T1 用 approved keyframe 验证 Wan2.2 5B I2V
  ↓
M1 动态风险分级
  ↓
E0 20–30 秒 CP Look Reel
  ↓
用户批准人物方向
  ↓
E1 EP001 20 张 story keyframe
  ↓
EP001 First Cut：静态 + 低风险 I2V
  ↓
本地身份自动化 / TTS / LipSync / 控制平面
```

## 关键产品规则

1. Production 不允许纯 T2V 创建主角。
2. 没有 approved identity refs，不生成产品关键帧。
3. 没有 approved keyframe，不提交产品视频。
4. 用户判断人物“像不像”时，视觉 reference 高于文字 prompt。
5. 当前人物服装只使用已批准古装，不穿现代服装；场景可以现代生活化。
6. 人物脸优先于动作复杂度和原生清晰度。
7. 高风险动作允许保留为静态照片/轻推拉，不强迫 I2V。

## Lab 与 Production

### Lab
用于显存、速度、API、OOM、workflow 测试。
输出必须标记 LAB_ONLY。

### Production
用于真正短剧。
必须携带：
- identity refs
- costume refs
- composition ref
- approved keyframe
- approval manifest
- motion tier

## 当前下一步

**停止继续做泛化 T2V benchmark。**

本地 Agent 只执行：
1. docs/stages/V0_REFERENCE_AND_LOOK_LOCK.md
2. docs/stages/K1_TEN_COMPOSITION_KEYFRAMES.md

10 张人物静帧通过用户批准后，再执行 T1。

## 文档阅读顺序

1. AGENTS.md
2. PROJECT_STATE.md
3. docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. docs/19_ACTIVE_VISUAL_SPEC.md
5. docs/stages/README.md
6. docs/06_CHARACTER_SYSTEM.md
7. docs/15_EP001_PILOT_PLAN.md
8. 对应 active stage 文件
9. docs/reviews/2026-10-05-远端审核.md（历史执行审计）

已有 P0R/P1A benchmark 继续保留，作为 Lab 事实，不删除。
