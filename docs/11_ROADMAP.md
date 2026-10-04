# 11 阶段路线图与任务拆解（执行版）

## 新总路线

P0R 本机重新基线
→ P1A Wan2.2 5B 最小视频闭环
→ P1A-Q 视觉质量
→ P1B 可选替代比较
→ P2 双身份同框
→ P3 EP001 First Cut
→ P4 控制平面
→ P5 音频/口型/后期
→ P6 一键单集
→ P7 系列化

任何 Gate 未通过，不把后续阶段“预安装”到本机。

---

## P0R 本机重新基线

状态：**PASS（2026-10-04）** — 产出 `docs/benchmarks/P1_ENVIRONMENT.md`；实际 URL `http://127.0.0.1:8188`；Wan2.2 5B 三文件均缺失，已进入下载。

执行文档：
docs/stages/P0R_REBASE_EXECUTION.md

产出：
- P1_ENVIRONMENT.md
- local/inventory.json
- 实际 ComfyUI URL
- 磁盘容量
- 已有模型/节点清单
- 依赖缺口

Gate：
没有未知关键环境项。

---

## P1A Wan2.2-TI2V-5B 最小闭环

执行文档：
docs/stages/P1A_WAN22_5B_BASELINE.md

目标：
不是做短剧，只做第一条可复现 I2V。

最小安装：
- Wan2.2 5B 所需官方模型
- 官方 ComfyUI workflow

最小代码：
- scripts/p1_comfy_probe.py

Gate：
- 10 次串行稳定
- metadata 完整
- 无不可解释 OOM
- 得出推荐起始参数

---

## P1A-Q 视觉质量

固定 3 张 approved keyframe × 3 takes。

Gate：
至少低风险/微动作镜头可达到可剪标准。

如果 5B “能跑但质量不够”，不等于项目失败，进入 P1B。

---

## P1B 可选替代

执行文档：
docs/stages/P1B_OPTIONAL_ALTERNATIVES.md

最多一次只加入一个：
1. FramePack
2. WanGP 某一个明确模型/配置

不把 LTX native/14B GGUF 全部一起拉进来。

Gate：
只有明显优于 P1A 才替换 production candidate。

---

## P2 角色与双身份

执行：
docs/stages/P2_CHARACTER_DUAL_IDENTITY.md

最高优先：
双身份同框关键帧。

Gate：
10 个固定生活场景中 ≥8 张同时满足两个角色 identity。

---

## P3 EP001 First Cut

执行：
docs/stages/P3_EP001_FIRST_CUT.md

v0.1：
- 20 张 approved keyframe
- 6 个低风险 I2V
- 其余静态运动
- voice-over
- no lip sync

Gate：
45–90 秒可观看、无重大连续性错误。

---

## P4 控制平面

执行：
docs/stages/P4_CONTROL_PLANE.md

只有 P3 证明人工流程有效后才抽象完整 CLI。

Gate：
任意 shot 一键重跑/恢复。

---

## P5 音频/口型/后期

执行：
docs/stages/P5_AUDIO_LIPSYNC_POST.md

Gate：
accepted clips 可自动合成 final。

---

## P6 一键单集

执行：
docs/stages/P6_AUTOMATED_EPISODE.md

保留：
- Keyframe Approval
- Final Approval

---

## P7 系列化

执行：
docs/stages/P7_SERIES_SCALE.md

加入：
- 跨集状态
- voice map
- 场景复用
- 自动 recap
- benchmark regression
- 新模型 Lab lane

## 速度/存储 Gate

P1A/P1B 必须额外给出：
- 单 shot p50 / p95 时间
- 预计 6/12/20 animated shots 总 GPU 时间
- 模型总磁盘占用
- 临时文件占用
- 推荐最低空闲空间

没有这四项，不冻结 production workflow。
