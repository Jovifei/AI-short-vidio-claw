# 11 路线图（V2 Active）

## 已完成 Lab

- P0R 本机环境基线：完成
- Wan2.2 5B 权重/ComfyUI：完成
- T2V 480×832×49 十次运行：完成
- 一次 I2V 接线成功：完成

注意：这些只证明 Runtime，不证明人物 Production。

## 当前 Product Roadmap

### V0 Visual Target Lock
- [ ] 收集用户批准人物脸 reference
- [ ] 收集用户批准古装 reference
- [ ] 建立 manifest/hash
- [ ] Golden Face Set
- [ ] Golden Costume Set
- [ ] 10 composition refs 编号
Gate：VISUAL_TARGET_LOCKED

### K1 Ten Composition Keyframes
- [ ] 10 张 candidate
- [ ] face QA
- [ ] costume QA
- [ ] anatomy QA
- [ ] 用户逐张批准
Gate：10/10 approved

### T1 Approved I2V
- [ ] production workflow
- [ ] production guard
- [ ] 3 张 approved keyframe 各 1 take
- [ ] 一张 LOW-risk 重复 3–5 次
Gate：Production Candidate for LOW-RISK I2V

### M1 Motion Ladder
- [ ] 10 张分 M0/M1/M2/M3
- [ ] 禁止 Agent 自行升级高风险镜头

### E0 CP Look Reel
- [ ] 20–30 秒
- [ ] 约 4 个 motion shot
- [ ] 其余静态/轻推拉
Gate：用户批准整体人物视觉

### E1 EP001
- [ ] 20 shot cards
- [ ] 20 approved keyframes
- [ ] 4–6 低风险 motion
- [ ] First Cut
Gate：人物正确 + 故事成立

### A1 本地身份自动化
只有 E1 成功后才评估：
- PuLID
- IPAdapter
- Character LoRA
目标是降低 Hero Lane 成本，不是重新定义人物。

### A2 音频/口型
- GPT-SoVITS
- MuseTalk
- SFX/BGM
- FPS/upscale

### A3 控制平面
把已验证手工流程自动化。

### Series
连续 3 集后再考虑 UI/规模化。

## 冻结原则
在 K1 未 PASS 前：
- 不再跑无 reference 的故事 T2V
- 不训练角色 LoRA
- 不开始 EP001
- 不接 lip sync
