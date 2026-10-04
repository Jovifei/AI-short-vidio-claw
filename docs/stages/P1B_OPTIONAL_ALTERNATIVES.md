# P1B 可选低显存替代路线

## 触发条件

只有以下任一成立：
- P1A 运行不稳定；
- 5B 质量明显不足；
- 速度预算不可接受；
- 需要比 5B 更适合某类镜头的 executor。

## 核心规则

**一次只引入一个替代。**

优先顺序建议：
1. FramePack
2. WanGP（选择一个具体模型/配置）

不允许：
FramePack + WanGP + GGUF 14B + LTX 同时安装比较。

## Option A：FramePack

先验证：
- 安装体积
- RAM
- 5 秒 I2V
- 人物漂移
- 长镜延续
- p50 time

官方 6GB 声明只作为候选理由，不作为本机结果；社区也有 8GB + 大量 shared memory 失败报告。

## Option B：WanGP

先选一个明确目标：
例如解决低 VRAM、质量或某一特定模型能力。

必须记录：
- WanGP release
- model/profile
- VRAM
- RAM
- disk
- time
- output quality

32GB RAM 是硬 Gate。

## 替换 Production 的条件

替代路线需要同时满足：
- 成功率不低于 5B baseline
- 质量明显提升，或速度明显更好
- RAM/磁盘成本可接受
- 自动化接口可实现
- 许可证可接受

否则保留为 Lab。
