# 27 本地 GPU / ComfyUI 详细执行清单

日期：2026-10-05
目标硬件：RTX 4070 SUPER 12GB / ~32GB RAM
状态：ACTIVE LOCAL RUNBOOK

## 1. 本文件解决什么

本地 Agent 不需要重新设计路线，只需要按阶段执行：
- Reference
- Keyframe
- Guard
- I2V
- QA
- Edit

## 2. 启动前检查

### Git
- git status
- git pull --ff-only
- 记录 HEAD

### ComfyUI
确认：
- 实际 URL
- 当前 PID
- queue empty
- models 可见
- output 可写

### GPU/RAM
记录：
- nvidia-smi
- VRAM 空闲
- RAM 空闲
- pagefile

若有其他大模型进程占用 GPU：
先停止。

## 3. Reference Stage

### 目录
local/references/active_visual_target/

### 索引
运行 reference_index.py。

### Contact Sheet
生成 contact sheet 后给用户审核。

注意：
contact sheet 只是展示，不代表批准。

## 4. LOOKREEL01 Keyframe Stage

每个 COMP：
1. 读取 shot card
2. 准备 reference bundle
3. 生成 candidate
4. QA
5. 给用户看
6. 用户批准
7. 复制 approved
8. 计算 hash
9. 写 approval manifest

未批准的 candidate 禁止进入 video。

## 5. T1 I2V Stage

### 选择
优先：
COMP09
COMP04
COMP01 或 COMP05

避免：
COMP07/08 等高风险。

### Guard
运行 production_guard。

### Comfy
workflow：
workflows/video/production/VID_wan22_5b_i2v_prod_v001.json

推荐先：
480×832
49 frames
24fps container
20 steps
CFG 5
uni_pc/simple

这些是当前 Lab 已验证的运行参数，不代表视觉最优。

## 6. 单条运行

每一条必须记录：
- shot
- keyframe sha
- prompt
- seed
- workflow sha
- width/height/frames
- start/end
- elapsed
- sampled VRAM
- sampled RAM
- output sha

## 7. 运行策略

GPU jobs：
严格串行。

一条失败后：
先读日志，不立刻连抽。

OOM：
1. clean state
2. frames 降低
3. 分辨率降低
4. 仅在必要时研究 alternative runner

Identity drift：
不是显存问题。
先：
- motion 更小
- frames 更短
- prompt 更克制
- static fallback

## 8. 质量优先级

GPU 渲染完成后按以下顺序看片：
1. 第一帧是否与 approved keyframe 一致
2. 中间帧是否换脸
3. 最后一帧是否可用
4. 衣服
5. 肢体
6. 背景
7. 动作
8. 清晰度

如果 1–5 有硬错误，高清也不接受。

## 9. LOOKREEL01 First Cut

输入：
- 10 approved stills
- 约 4 accepted motion clips

FFmpeg 可以先只做：
- 静态图转 24fps clip
- motion clips
- concat
- 简单音频

先不要过度调色。

## 10. EP001

只有 E0 用户批准后：
开始 EP001。

流程：
20 keyframes 全部先批准
→ 4–6 motion clips
→ first cut
→ audio
→ final

## 11. 模型训练

不要现在立刻训练 LoRA。

训练触发条件：
- Golden Face 已稳定
- 至少 20–30 张 approved 数据
- 手工/ChatGPT Hero Lane 已证明人物目标
- 确认本地生成效率确实值得优化

训练前做：
- 数据去重
- 角度平衡
- 表情平衡
- costume tag
- face crop check

## 12. 输出结构

local/production/LOOKREEL01/
local/production/EP001/

每个 shot：
- approved still
- takes
- accepted
- QA

## 13. 每日结束

Codex 必须更新：
- PROJECT_STATE
- stage progress
- approval manifest
- QA summary

不能只说“今天跑了很多图”。

必须说：
- 哪些通过
- 哪些失败
- 原因
- 下一步
