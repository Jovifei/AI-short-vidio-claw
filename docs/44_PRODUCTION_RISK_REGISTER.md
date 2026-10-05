# 44 产品风险登记表

状态：ACTIVE

| ID | 风险 | 概率 | 影响 | 早期信号 | 缓解 | Owner |
|---|---|---|---|---|---|---|
| R01 | 黛玉脸现代化 | 高 | 致命 | 尖下巴/大眼/网红妆 | Golden Face + Hero Lane + hard reject | Art |
| R02 | 悟空人脸化 | 高 | 致命 | 鼻口变人类、耳形变 | Monkey face landmarks + static fallback | Art |
| R03 | 双人串脸 | 中高 | 高 | 两人特征互换 | reference bundle + two-pass/manual edit | Art |
| R04 | 古装变现代衣服 | 中 | 高 | hoodie/T恤 | costume stage lock | Art |
| R05 | I2V 身份漂移 | 中高 | 高 | 中段换脸 | M1、短帧、2次上限、static | Video |
| R06 | 手部崩坏 | 高 | 中高 | 多指/融合 | 不做手部特写、静态修图 | Art |
| R07 | 复杂接触崩坏 | 高 | 中高 | 抱起/镜子异常 | M0 static | Director |
| R08 | 32GB RAM 不足 | 中 | 高 | pagefile 激增 | 5B、单进程、避免14B offload | Tech |
| R09 | GPU 时间浪费 | 高 | 中 | 大量 rejected clips | keyframe approval before video | PM |
| R10 | 文档与实际脱节 | 中 | 高 | Agent继续旧路线 | active docs + gate matrix + PROJECT_STATE | PM |
| R11 | Reference 权利不清 | 中 | 高 | 商业发布前无记录 | release rights review | PM |
| R12 | 声音模仿风险 | 中 | 高 | 未授权 voice clone | authorized voice only | Audio |
| R13 | 模型升级破坏质量 | 中 | 中高 | 单镜变好、回归变差 | regression set + frozen prod | Tech |
| R14 | LoRA 过拟合服装 | 中 | 中 | 只会一套衣服 | multi-stage dataset | ML |
| R15 | 画面太像海报 | 高 | 中 | 全都正面摆拍 | life layer / unposed blocking | Director |
| R16 | 故事不成立 | 中 | 高 | 静音看不懂 | 先20 still story cut | Director |
| R17 | 剪辑过慢 | 中 | 中 | 每镜>4s且无信息 | shot duration rules | Edit |
| R18 | 音乐压过生活感 | 中 | 中 | BGM太满 | ambience first | Audio |

## 风险级别

致命：
一旦发生直接 Reject，不进入下一阶段。

高：
必须在当前阶段修。

中：
可以记录，进入剪辑再决定。

低：
不影响叙事即可接受。

## 当前 Top 5

1. R01 黛玉脸现代化
2. R02 悟空人脸化
3. R05 I2V 漂移
4. R09 GPU 浪费
5. R10 路线脱节

这五项已经分别通过：
Visual Spec / Golden Model / Motion Tier / Guard / Active Docs 缓解。
