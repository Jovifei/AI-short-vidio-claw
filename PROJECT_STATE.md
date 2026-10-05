# PROJECT_STATE

更新时间：2026-10-05
状态：**LAB 5B runtime verified / PRODUCT visual target NOT LOCKED / Active next = V0 → K1**

## 1. 审核结论

当前成果“不像要求”的根因已经定位。

不是简单的“Wan2.2 5B 路线错了”，而是：
- 已生成的大多数视频属于 Lab benchmark；
- Lab 中大量使用官方地铁乐手 prompt；
- 故事向 SH001 是无参考图 T2V；
- 唯一 I2V 来自未批准 SDXL 静帧；
- 没有 approved 孙悟空/林黛玉视觉 reference；
- 旧文档把 approved keyframe 放在 P2，却让 P1A 先要求它，存在阶段依赖循环；
- 旧 Character Bible 与用户当前视觉要求不一致。

因此 V2 将“视觉锁定”放到视频 Production 之前。

## 2. 保留的 Lab 事实

已有事实继续有效：
- ComfyUI URL http://127.0.0.1:8188
- RTX 4070 SUPER 12282 MiB
- RAM 约 31.82 GB
- Wan2.2-TI2V-5B 官方三份模型已安装
- 480×832×49 T2V 串行 10/10 成功
- p50 187.7095 s
- p95 264.101 s
- 曾有一次 480×832×49 I2V 成功
- 未测试 approved identity keyframe 的 Production I2V

这些只证明 runtime，不证明人物效果。

## 3. 当前冻结动作

现在停止：
- 泛化 T2V benchmark
- 临时人物图继续 I2V
- 直接开始 EP001
- 本地 LoRA/PuLID 扩张
- TTS/LipSync

## 4. 当前立即阶段

### V0
收集并冻结：
- 林黛玉 Golden Face Set
- 孙悟空 Golden Face Set
- 双方 Golden Costume Set
- 10 张 composition refs

状态目标：
VISUAL_TARGET_LOCKED

### K1
按用户的 10 个构图生成 10 张 approved keyframe。

第一优先是：
人物脸 → 古装 → CP 感 → anatomy → 构图。

## 5. V0/K1 完成后

再执行 T1：
用 approved keyframe 验证 Wan2.2 5B Production I2V。

只有 T1 通过，才能把 5B 写成：
Production Candidate for LOW-RISK I2V。

## 6. EP001

EP001 现在排在 E0 CP Look Reel 之后。

先让用户批准 20–30 秒人物视觉样片，再做《大圣今天受伤了》。

## 7. 旧 P1A 状态

旧 P1A benchmark 文档不删除，但归档为 Lab 路线。
十次 T2V 不再作为下一步任务。

详细审计：
docs/reviews/2026-10-05-远端审核.md
