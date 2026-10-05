# 40 ChatGPT / Codex / ComfyUI / GPU 分工矩阵

状态：ACTIVE

## 1. 原则

不要让同一个工具做它不擅长的事情。

### ChatGPT Web / 远端
擅长：
- 产品规划
- 剧本
- 分镜
- 美术方向
- Prompt
- 参考图生成/编辑
- QA 标准
- 文档
- 方案复核

### Local Codex
擅长：
- 文件管理
- Hash/Manifest
- 调用本地 API
- 批量任务
- 自动 QA 记录
- FFmpeg
- 训练脚本
- 环境与模型版本管理

### ComfyUI
擅长：
- 可视化/可版本化生成 Workflow
- 图像/视频模型执行
- 批量渲染
- 本地模型复用

### GPU
只负责：
- 真正推理/训练
- 不负责“决定人物长什么样”

## 2. 任务矩阵

| 工作 | ChatGPT | Codex | ComfyUI/GPU |
|---|---|---|---|
| PRD | 主 | 读 | 否 |
| 剧本 | 主 | 管理 | 否 |
| 分镜 | 主 | 验证 schema | 否 |
| 人物视觉方向 | 主 + 用户 | 记录 | 可辅助 |
| Hero Keyframe | 主 | 收集/Hash | 可选 |
| Reference Manifest | 设计 | 主 | 否 |
| I2V Prompt | 主 | 注入 | 执行 |
| Render Queue | 设计 | 主 | 执行 |
| VRAM Benchmark | 复核 | 主 | 主 |
| LoRA 训练计划 | 主 | 实施 | 主 |
| Asset QA | 主+用户 | 自动记录 | 否 |
| Video QA | 主+用户 | 自动初检 | 输出 |
| Edit Plan | 主 | 执行 | 否 |
| FFmpeg | 设计 | 主 | CPU/GPU encode |
| Final Approval | 用户 | 记录 | 否 |

## 3. 必须用户决定

- Golden Face
- Golden Costume
- Golden Model
- 关键帧是否批准
- Look Reel 是否批准
- First Cut 是否批准
- 最终成片是否批准

AI 不能替用户写这些“已批准”。

## 4. 远端可以先做完的工作

- 世界观
- 第一季规划
- 每集结构
- 视觉圣经
- 摄影语法
- 表演语法
- 服装 stage
- 场景 stage
- 道具 continuity
- Shot Card
- Image Prompt
- Video Prompt
- Sound Bible
- Edit Spec
- QA
- Failure Recovery
- Training Plan
- Schema
- 自动化脚本骨架

## 5. 必须等本地的工作

- 实际 reference 文件落盘
- 本地 hash
- ComfyUI 实际 workflow 验证
- GPU 推理
- GPU 训练
- 本地音频模型
- FFmpeg 真正媒体处理
- 大媒体文件落盘

## 6. 顺序约束

ChatGPT 准备完成
→ Local Codex 导入资产
→ 用户批准
→ GPU
→ QA
→ 用户批准
→ 下一阶段

不能：
GPU 先跑一堆 → 再问人物是不是对。
