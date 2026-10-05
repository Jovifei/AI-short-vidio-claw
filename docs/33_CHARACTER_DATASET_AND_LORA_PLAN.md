# 33 角色数据集与 LoRA 训练计划（只做规划，后续本地执行）

状态：DESIGN COMPLETE / EXECUTION DEFERRED

## 1. 为什么 LoRA 后置

LoRA 的目的不是“寻找人物长什么样”，而是：
**复制已经由用户批准的 Golden Model。**

因此训练前必须满足：
- Golden Model Approved
- 至少 20–30 张 approved 角色图
- 脸型/发式/服装方向稳定
- 已有 LOOKREEL/E0 证明人物方向可用

没有这些，训练只会把错误人物固化。

## 2. 数据集结构

local/training/
├─ daiyu_v1/
│  ├─ images/
│  ├─ captions/
│  ├─ rejected/
│  ├─ audit/
│  └─ dataset_manifest.json
├─ wukong_v1/
│  ├─ images/
│  ├─ captions/
│  ├─ rejected/
│  ├─ audit/
│  └─ dataset_manifest.json
└─ couple_v1/
   ├─ validation/
   └─ benchmark/

Git 仅提交：
- dataset_manifest.example.json
- training_config.example.yaml
- benchmark rubric
不提交训练图和权重。

## 3. 数据量目标

### DAIYU
最低 24 张，推荐 36–60 张：
- front 15%
- 3/4 35%
- profile 10%
- half/full 25%
- expressions 15%

### WUKONG
最低 30 张，推荐 45–70 张：
因为非标准人脸与毛发结构更复杂。

必须覆盖：
- front
- left/right 3/4
- profile
- neutral/smile/serious
- full body
- hand/fur visibility
- headwear/crown stage

## 4. 数据来源优先级

1. 用户批准的自生成 Golden Images
2. 从 Golden Model 出发的受控扩展图
3. 明确可用的授权素材

不把未经审核的网络图直接混入训练集。

## 5. 去重

同一构图只保留 1–2 张。

避免：
- 十几张几乎相同的正脸
- 同一光线/表情过度占比
- 单一服装绑死身份

## 6. Caption 原则

Caption 分成：

Identity token：
- daiyu_cp_v1
- wukong_cp_v1

Visible traits：
- classical hair ornaments
- lavender robe
- golden-brown simian fur
- buddhist crown

Pose/shot：
- three-quarter portrait
- full body
- seated
- side profile

Emotion：
- restrained smile
- serious
- caring glance

不要 Caption 不可见的文学性格。

## 7. 角色与服装解耦

长期目标：
Identity LoRA 不应死绑一种衣服。

建议：
- 角色 identity 数据占 60–70%
- 多 costume stage 占 30–40%

如果训练后只会固定一套衣服，判为过拟合。

## 8. 悟空特殊项

必须在 audit 中标注：
- brow shape
- muzzle shape
- ear shape
- cheek fur
- forehead fur
- headwear
- fur color

验证集需要故意测试：
- 不戴重冠
- 轻量 HOME stage
看猴脸是否仍稳定。

## 9. 黛玉特殊项

验证集必须测试：
- 无明显花朵遮脸
- 中性表情
- 微笑
- 侧脸
- HOME stage

如果模型一笑就变成现代 AI 女生脸，训练失败。

## 10. 训练实验矩阵

一次只改一个主变量：

Experiment A：
低 rank baseline

Experiment B：
rank 增加

Experiment C：
学习率变化

Experiment D：
caption/数据重新平衡

不要同时变：
rank + lr + optimizer + crop。

## 11. Validation Set

固定 8–12 个 prompt：
- portrait front
- 3/4
- profile
- full body
- HOME
- OUTDOOR
- neutral
- smile
- two-shot

任何新 LoRA 都跑同一套。

## 12. 评分

Identity /5
Geometry /5
Costume flexibility /5
Expression flexibility /5
Anatomy /5
Overfit /5（5=无明显过拟合）

Golden LoRA Gate：
- identity ≥4
- geometry ≥4
- two-shot 可用
- 不锁死单一 costume
- 无严重过拟合

## 13. 权重版本

建议：
DAIYU_ID_V001.safetensors
WUKONG_ID_V001.safetensors

不要命名 final_final2。

manifest 记录：
- dataset hash
- config hash
- base model
- trainer
- steps
- rank
- date
- benchmark

## 14. Couple LoRA

第一阶段**不建议**直接训练“情侣 LoRA”。

原因：
会把：
- 位置
- 身高差
- 固定构图
- 服装
绑定在一起。

先训练各自 Identity，双人构图由 workflow/reference 解决。

## 15. 训练结束后的生产接入

LoRA 只能作为：
Hero Lane 的自动化替代方案。

生产 Gate 不变：
候选图仍需 Keyframe QA。
