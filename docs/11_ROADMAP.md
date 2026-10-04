# 11 阶段路线图与任务拆解

## 总体路线

P0 规格与骨架
→ P1 4070S 基准
→ P2 角色锁定
→ P3 EP001 人工辅助闭环
→ P4 自动化控制平面
→ P5 语音/口型/声音
→ P6 一键单集
→ P7 系列化与泛化

---

## P0 产品与工程基线

状态：进行中，本轮主要完成。

任务：
- [x] 项目章程
- [x] PRD
- [x] 可行性报告
- [x] 技术架构
- [x] SOP
- [x] 目录规范
- [x] 人物系统
- [x] episode 标准
- [x] 模型矩阵
- [x] 参考来源
- [x] QA
- [x] Roadmap
- [x] 风险/合规
- [x] Codex runbook
- [x] EP001 试播计划
- [ ] 本地 Codex 拉取并确认环境路径

Gate：
文档能让一个没有聊天历史的 Codex 说清项目目标、限制、下一步。

---

## P1 RTX 4070S 基准验证

目标：
不是“装最多节点”，而是找出可稳定生产的最小技术组合。

任务：
1. 实现 scripts/env_probe.py。
2. 记录：
   - GPU driver
   - CUDA
   - VRAM
   - RAM
   - Python
   - PyTorch
   - ComfyUI commit
   - custom node commits
3. 准备固定 3 张 keyframe：
   - 单人轻动作
   - 双人低接触
   - 双人手部交互
4. Native Wan2.2 I2V benchmark。
5. WanVideoWrapper FP8/GGUF/offload benchmark。
6. FramePack benchmark。
7. 每条记录显存峰值、耗时、失败率、identity/motion。
8. 形成 P1_4070S_BASELINE.md。
9. 冻结第一个 production video workflow。

Gate：
至少一个 3–5 秒 9:16 I2V 工作流在 12GB 上稳定；连续 10 次 OOM ≤2。

---

## P2 角色一致性系统

目标：
先解决角色，再做短剧。

### 林黛玉
- [ ] 完成原创原著型 face brief
- [ ] 20–30 张一致 reference
- [ ] 正/3/4/侧/全身
- [ ] 至少 5 种表情
- [ ] 3 个生活 stage
- [ ] PuLID/IPAdapter benchmark
- [ ] 判断 LoRA 是否必要

### 孙悟空
- [ ] 固定毛色、耳型、眉骨、口鼻结构
- [ ] 20–30 张 reference
- [ ] 参考 conditioning benchmark
- [ ] LoRA 训练 benchmark
- [ ] 3 个生活 stage

### 双人
- [ ] 10 个生活动作 keyframe test
- [ ] 身高差锁定
- [ ] 手部接触成功率统计
- [ ] 确立 Hero Lane 规则

Gate：
固定 10 场景测试中，主观身份评分 ≥4/5 的关键帧 ≥80%。

---

## P3 EP001 人工辅助完整闭环

目标：
先做出一条真正能看的片，不急着自动化所有环节。

使用：
- Codex 生成/维护文档
- ChatGPT 手工 Hero keyframe
- ComfyUI I2V
- GPT-SoVITS
- MuseTalk（仅合适镜头）
- FFmpeg

任务：
- [ ] 冻结剧本
- [ ] 20 镜分镜
- [ ] 20 张 approved keyframe
- [ ] 选 10–15 镜动画化
- [ ] TTS
- [ ] 环境声
- [ ] 剪辑
- [ ] QA
- [ ] EP001 v1 成片

Gate：
45–90 秒完整成片，角色连续，无严重穿帮。

---

## P4 Codex 自动化控制平面

目标：
让“手工操作 ComfyUI”转为“Codex/CLI 提交任务”。

任务：
- [ ] Python project skeleton
- [ ] config loader
- [ ] ComfyUI health check
- [ ] workflow parameter injection
- [ ] queue submit
- [ ] status poll/websocket
- [ ] result retrieval
- [ ] manifest writer
- [ ] shot state machine
- [ ] reroll command
- [ ] resume command
- [ ] benchmark command

建议 CLI：
- claw doctor
- claw episode validate EP001
- claw shot render EP001 SH006
- claw shot reroll EP001 SH006
- claw episode status EP001
- claw episode render EP001

Gate：
任意单镜可以从 manifest 一键重跑，任务中断后可恢复。

---

## P5 音频、口型、后期自动化

任务：
- [ ] voice_map
- [ ] GPT-SoVITS adapter
- [ ] MuseTalk adapter
- [ ] 孙悟空对白专项策略
- [ ] ambience library
- [ ] sfx library
- [ ] FFmpeg timeline
- [ ] subtitle
- [ ] loudness
- [ ] final technical QC

Gate：
同一集从 accepted clips 自动输出 final.mp4。

---

## P6 一键单集

输入：
episode brief + 角色 stage。

系统自动：
文本 → keyframe task → video task → audio → edit → QA。

仍保留两个强制人工 gate：
1. keyframe approval
2. final approval

不追求“完全无人值守发布”。

---

## P7 系列化

- 跨集状态
- 角色长期 stage
- voice map
- 场景复用
- 道具生命周期
- 自动 recap
- 封面/标题/文案
- 多系列模板
- 新模型 benchmark bot

## 优先级规则

任何时候出现新模型，不因“新”而打断主线。

只有满足：
- 可在目标硬件运行；
- 相同 benchmark 明显提升；
- 许可证可接受；
- 能回退；
才升级 Production。
