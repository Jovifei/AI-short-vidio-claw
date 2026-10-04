# 13 Codex 执行手册（P0R/P1A 优先）

## 1. 当前命令

本地 Codex 第一轮不要“继续实现所有规划”。

只执行：
1. P0R
2. P1A

详细步骤见 docs/stages。

## 2. P0R

必须重新探测：
- GPU/VRAM
- RAM
- driver
- CUDA runtime
- Python
- PyTorch
- FFmpeg
- ComfyUI 路径
- ComfyUI commit/version
- 实际监听端口
- custom_nodes
- models
- disk free
- pagefile（能读则记录）

禁止：
- 下载 Wan
- 下载 LTX
- 安装 Wrapper
- 装 PuLID
- 修 FaceID
- 建第二 ComfyUI

产出：
docs/benchmarks/P1_ENVIRONMENT.md

然后停下，确认 P1A 下载清单。

## 3. P1A 下载前清单

Codex 必须先报告：
- 需要哪些 5B 文件
- 每个文件来源
- 每个文件大小
- 预计总下载
- 目标存储路径
- 磁盘剩余
- ComfyUI 版本是否包含 Wan2.2 官方 template

只下载官方 5B baseline 所需文件。

## 4. P1A workflow

优先从 ComfyUI 官方 Template Library 获取 Wan2.2 5B。
不得手写复杂 workflow。

操作：
1. GUI 手工成功加载一次；
2. 导出 API workflow JSON；
3. 固定副本进入 workflows/video/lab；
4. 记录 hash；
5. 再写自动提交脚本。

## 5. P1 最小脚本

文件：
scripts/p1_comfy_probe.py

功能：
- --url
- --workflow
- --image
- --prompt
- --seed
- --width
- --height
- --frames
- --output-record

执行：
health
→ validate input
→ submit
→ wait
→ collect output
→ record time
→ record NVML peak VRAM（如可）
→ record process/system RAM（如可）
→ write JSON

脚本不做 episode 业务。

## 6. 参数测试规则

固定：
- input
- prompt
- seed（稳定性测试可另用 seed set）
- workflow version

每次只改变：
- frames 或
- resolution

推荐 ladder：
480×832 / 49
→ 480×832 / 81
→ 576×1024 / 49
→ optional 576×1024 / 81

如果 480×832 本身不符合官方 node constraint：
记录事实，选择最近合法 9:16 尺寸。

## 7. 10 次稳定性

选出首个成功配置后：
- clean start
- 10 次串行
- 不并发
- 每次记录峰值/时间/错误

不能只跑一次就写“稳定”。

## 8. P1A-Q

基础运行稳定后才换成真实 keyframe。

三类：
A. 单人微动作
B. 双人同框无接触
C. 双人低接触但避开复杂手

每类 3 takes。

如果 C 很差：
不推翻视频引擎；
先把高风险镜头转静态。

## 9. P1B 决策

P1A 后向用户汇报：
- 5B quality
- speed
- VRAM/RAM
- storage
- EP001 预计时间

只有明确问题需要解决才进 P1B。

## 10. P2

先不要安装所有 identity tools。
按“双身份同框”实验设计一个最小矩阵。

林黛玉 FaceID 如果要用：
- 先补 InsightFace
- 仅静帧
- 验证五官不被现代化

悟空：
- 禁止 FaceID 作为唯一锁定。

## 11. P3

20 keyframes first。
6 low-risk motion first。
voice-over only。
No lip sync。

## 12. 文档更新

每个阶段结束：
- PROJECT_STATE
- ROADMAP
- DECISION_LOG
- benchmark
- manifests

只有本机实测可以写“verified on 4070S”。
