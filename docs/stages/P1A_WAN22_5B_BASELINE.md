# P1A Wan2.2-TI2V-5B 最小视频闭环

## 唯一目标

证明 RTX 4070 Super 12GB + ~32GB RAM 上，**单 ComfyUI 原生 Wan2.2 5B** 能以某一组本机参数稳定执行 I2V。

不是做 EP001，不是比较所有模型。

## 官方依据

ComfyUI 官方 Wan2.2 教程提供：
- Wan2.2-TI2V-5B
- 原生 workflow
- native offloading
- 5B “should fit well on 8GB vram”说明

官方 template 所需核心文件：
- `wan2.2_ti2v_5B_fp16.safetensors`
- `wan2.2_vae.safetensors`
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`

下载前必须以当前官方模板再次确认文件名/大小。

## Step 0：下载前审批

Codex 先输出表：
- file
- source URL
- size
- target path
- existing? yes/no
- free disk before
- free disk after estimate

只下载 P1A 所需文件。

## Step 1：GUI 首次运行

1. 更新/确认 ComfyUI 版本支持 Wan2.2 5B template。
2. Template Library 打开 “Wan2.2 5B”。
3. 加载 P1A approved test image。
4. 使用官方默认参数先跑一次最小合法 I2V。

失败时记录完整 console，不连续盲重试。

## Step 2：导出 API Workflow

GUI 成功一次后：
- 导出 API JSON
- 保存到 `workflows/video/lab/VID_wan22_5b_p1a_v001.json`
- 记录 SHA256
- 不手工重建同等 graph

## Step 3：最小自动化脚本

实现：
`scripts/p1_comfy_probe.py`

参数：
- --url
- --workflow
- --image
- --positive
- --negative
- --seed
- --width
- --height
- --frames
- --record

功能：
探活 → 读取 workflow → 参数注入 → 提交 → 等待 → 获取输出 → 记录 metadata。

不实现完整 framework。

## Step 4：参数阶梯

任何一级如果不是 workflow 合法尺寸，记录并取最近合法尺寸。

建议顺序：

L1：480×832 / 49 frames
L2：480×832 / 81 frames
L3：576×1024 / 49 frames
L4：576×1024 / 81 frames（optional）

规则：
- 每次只改一项
- 不改采样器/steps/CFG 来掩盖 OOM
- 不并发

## Step 5：稳定性测试

从最优“能跑”参数中选择候选 baseline：
连续 10 次串行。

记录每次：
- seed
- start/end
- elapsed
- peak VRAM
- peak system RAM
- output
- errors
- GPU reset/restart 是否发生

## Step 6：性能预算

计算：
- p50 elapsed
- p95 elapsed
- 6 镜 × 2 takes
- 12 镜 × 2 takes
- 20 镜 × 2 takes
的粗略纯 GPU 时间。

同时记录模型总磁盘占用。

## PASS

- 10 次至少 9 次成功
- 无持续 OOM
- metadata 完整
- 可由脚本拿到输出路径
- 得出本机 recommended baseline
- 得出 p50/p95 和磁盘预算

## FAIL 分类

A. 模型无法加载
B. workflow/API 不兼容
C. VRAM OOM
D. RAM/pagefile 失败
E. 输出损坏
F. 速度不可接受

任何 FAIL 必须先定位原因；不得自动跳 14B。
