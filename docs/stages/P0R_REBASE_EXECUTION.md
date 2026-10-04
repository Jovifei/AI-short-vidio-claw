# P0R 本机重新基线执行报告

## 目标

在**不下载新模型、不改技术路线、不启动视频生产**的前提下，把本机事实写成可复现记录。

## 输入

- 当前仓库
- Windows 主机
- RTX 4070 Super
- 现有 ComfyUI Desktop
- 现有模型目录

## 禁止事项

- 不下载 Wan/LTX/FramePack/WanGP 模型
- 不修 FaceID/PuLID
- 不安装第二套 ComfyUI
- 不创建大规模源码框架
- 不提交 I2V job

## Step 1：硬件/系统盘点

记录：
- Windows 版本
- GPU 名称
- dedicated VRAM
- system RAM
- NVIDIA driver
- CUDA runtime
- pagefile
- 每个相关磁盘总容量/空闲容量

命令输出保存到：
`local/p0r/system_inventory.json`

## Step 2：Python/AI Runtime

记录：
- Python 路径和版本
- Conda/venv
- PyTorch 版本
- torch CUDA version
- CUDA available
- ffmpeg/ffprobe 路径和版本

不要求现在“统一环境”。

## Step 3：ComfyUI

定位：
- Desktop 安装位置
- backend 路径
- models 路径
- custom_nodes
- version/commit（可取得则记录）
- 启动参数

启动现有 ComfyUI 后探测实际监听：
- 8000
- 8188
- 以及系统实际 LISTENING 端口

最终写：
`COMFYUI_URL=http://127.0.0.1:<actual>`

**不能因官方默认 8188 就修改 Desktop 实际配置。**

## Step 4：已有节点/模型

输出清单：
`local/p0r/models_inventory.csv`
`local/p0r/custom_nodes_inventory.csv`

字段：
- name
- path
- size
- modified
- category

只盘点，不搬迁。

## Step 5：磁盘预算

报告至少列：
- 当前 ComfyUI 模型总占用
- 项目盘剩余空间
- 下载 5B baseline 前保留安全余量
- 临时视频/缓存预留

此阶段不猜“100GB 一定够”，只给实际数据与建议。

## Step 6：输出文档

提交 Git：
`docs/benchmarks/P1_ENVIRONMENT.md`

不能提交：
`local/*`

报告模板：
- Machine
- GPU/VRAM
- RAM/pagefile
- Disk
- Python
- PyTorch/CUDA
- FFmpeg
- ComfyUI actual URL
- ComfyUI version
- Existing models
- Existing nodes
- Missing for P1A
- Risks

## Gate

P0R PASS 需满足：
- 实际 ComfyUI URL 已知
- 磁盘空闲已知
- Python/FFmpeg 可定位
- 现有模型/节点清单已知
- 能明确列出 P1A 需要下载什么

PASS 后停止，提交报告，进入 P1A 下载前审批。
