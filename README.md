# AI-short-vidio-claw

> 面向 RTX 4070 Super 12GB 的角色一致 AI 竖屏短剧生产线。

## 当前状态

**远端能完成的产品规划、剧本、资产模型、SOP、Prompt、Workflow 候选与门禁代码已经准备完成。**

当前状态：

- Lab Runtime：Wan2.2-TI2V-5B 已在本机证明可运行。
- Product：等待 V0 人物/服装 Reference 落地与用户批准。
- 禁止继续用未批准人物做故事视频。

## 核心原则

1. Identity First。
2. Image First → Video Second。
3. Lab 与 Production 分离。
4. 用户批准的视觉 reference 是人物事实源。
5. 人物古装先锁定，再做生活场景。
6. Approved Keyframe 才能进 I2V。
7. 高风险动作允许静态表达。
8. 本地自动化服务于已经确定的美术目标，而不是替代美术决策。

## Active Route

```text
V0 Reference / Look Lock
  ↓
K1 10 Approved Couple Keyframes
  ↓
T1 Approved-Keyframe I2V
  ↓
M1 Motion Risk Selection
  ↓
E0 20–30s CP Look Reel
  ↓
User Visual Approval
  ↓
E1 EP001 Story Production
  ↓
Local Identity Automation
  ↓
Audio / LipSync / Full Control Plane
  ↓
Series
```

## 已准备好的创作包

### LOOKREEL01
`episodes/LOOKREEL01/`

包含：
- 10 个构图计划
- 图片生成说明
- 视频动作提示
- 剪辑计划
- QA
- approval manifest

### EP001
`episodes/EP001/`

《大圣今天受伤了》

包含：
- episode config
- 完整剧本
- 20 镜 storyboard
- shot manifest
- continuity
- image prompts
- video prompts
- edit plan
- QA
- approval manifest

## 人物/资产

`assets/characters/`
- DAIYU character card
- WUKONG character card
- HOME / OUTDOOR / RAIN / INJURED stages

`assets/locations/locations.yaml`
`assets/props/props.yaml`

当前视觉规格：
`docs/19_ACTIVE_VISUAL_SPEC.md`

## Production Video

候选：
`workflows/video/production/VID_wan22_5b_i2v_prod_v001.json`

它还不是正式 Production Frozen。
必须先通过：
`docs/stages/T1_APPROVED_I2V_BASELINE.md`

## 自动化门禁

`scripts/reference_index.py`
- 计算本地 reference hash
- 不会自动批准

`scripts/validate_production_package.py`
- 检查 episode/lookreel 包

`scripts/production_guard.py`
- 检查用户批准状态
- 校验 keyframe hash
- 检查 identity/costume refs
- 检查 LoadImage/start_image
- 不通过时禁止提交 ComfyUI

## 本地目录

真实 reference、大模型、candidate、approved 图片、视频都放 local/。

详见：
`docs/05_DIRECTORY_STANDARD.md`

## 新 Agent 阅读顺序

1. AGENTS.md
2. PROJECT_STATE.md
3. docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. docs/19_ACTIVE_VISUAL_SPEC.md
5. docs/20_CREATIVE_AND_SERIES_BIBLE.md
6. docs/21_PRODUCTION_SOP_V2.md
7. docs/22_LOCAL_HANDOFF.md
8. docs/23_REMOTE_PREP_COMPLETION.md
9. docs/24_LOCAL_CODEX_START_PROMPT.md
10. 当前 stage 文件

## 现在唯一正确的下一步

本地 Codex 执行：

`docs/24_LOCAL_CODEX_START_PROMPT.md`

即：
**导入真实人物/服装 references → V0 → 用户批准 → K1。**

在人物视觉没有锁定前，不再消耗 GPU 生成故事视频。
