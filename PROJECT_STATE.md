# PROJECT_STATE

更新时间：2026-10-05
状态：**REMOTE_PREP_COMPLETE / MODEL_REVIEW_PREPARED / PRODUCT_WAITING_USER_APPROVAL**

## 1. 当前判断

现有 Wan2.2-TI2V-5B Runtime 已有有效 Lab 数据。
过去人物效果不合格的根因不是简单的“模型不能跑”，而是没有先锁人物 reference，并混用了 Lab 与 Product。

V2 路线已经修正为：
Visual Lock → Keyframe → Approved I2V → Look Reel → EP001。

## 2. 远端已经完成

### 规划与创作
- 产品章程 / PRD / SOP
- 第一季 Creative Bible
- 10 集方向
- LOOKREEL01 10 构图完整方案
- EP001 完整剧本
- EP001 20 镜 storyboard
- EP001 20 镜 detailed shot cards
- image/video prompt packs
- continuity / edit / QA

### 人物建模
- DAIYU character card
- WUKONG character card
- costume stages
- modeling review spec
- modeling review manifests
- model sheet generation brief
- couple scale review requirements

### 场景/道具
- locations registry
- props registry

### 技术
- Production I2V workflow candidate
- Wan2.2 5B local model manifest
- Quality gates
- Production Guard
- Reference indexer
- Contact sheet generator
- Explicit approval tool
- Render queue builder
- Package validator

## 3. 当前唯一核心 Gate

先让用户审核人物建模板：

1. DAIYU Model Sheet
2. WUKONG Model Sheet
3. Couple Scale Sheet

然后把最终批准内容写入：
- assets/characters/daiyu/modeling_review.yaml
- assets/characters/wukong/modeling_review.yaml
- reference manifests

只有 Golden Model Approved 后才进入 K1。

## 4. Lab 已知事实

- RTX 4070 SUPER 12282 MiB
- RAM ~31.82 GB
- Wan2.2-TI2V-5B 三份核心模型已安装
- 480×832×49 T2V 10/10 success
- p50 187.7095 s
- p95 264.101 s
- 一次 I2V wiring success
- approved identity I2V 尚未验证

## 5. 当前禁止

在人物 Golden Model 未批准前：
- 不开始 Product I2V
- 不训练 LoRA
- 不开始完整 EP001 GPU 渲染
- 不把临时 candidate 当 reference
- 不用 T2V 创建主角

## 6. 下一步

用户审核人物模型图。

通过后：
V0 → K1 → T1 → E0 → E1。

本地 Codex 执行细节：
docs/24_LOCAL_CODEX_START_PROMPT.md
docs/27_GPU_EXECUTION_CHECKLIST.md
