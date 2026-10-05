# AI-short-vidio-claw

> RTX 4070 Super 12GB + ComfyUI + Codex 的角色一致 AI 竖屏短剧生产线。

## 当前状态

**模型人物方向：用户已表示“感觉可以，可以继续使用建模人物做前期工作”。**
因此当前状态记为：

`PREPROD_MODEL_DIRECTION_APPROVED`

但最终 `GOLDEN_MODEL_APPROVED` 仍需要：
- 本地保存最终建模图/reference
- SHA256
- Reference Manifest
- 用户明确最终锁定

**远端/非本地 Preproduction 已继续扩展到 V3 详细层。**

## 当前 Active Route

```text
Model Direction PREPROD APPROVED
  ↓
Local Reference Hash + Final Golden Lock
  ↓
V0 Visual Lock
  ↓
K1 10 Approved Couple Keyframes
  ↓
T1 Approved-Keyframe I2V
  ↓
E0 20–30s CP Look Reel
  ↓
User Approval
  ↓
EP001 20 Story Keyframes
  ↓
4–6 Low-risk Motion Shots
  ↓
First Cut
  ↓
Audio / Local Identity Automation / Full CLI
```

## 最重要规则

1. 用户批准的 Reference 才是人物事实源。
2. Production 禁止主角纯 T2V。
3. 没有 Approved Keyframe 不进 I2V。
4. 人物脸 > 服装 > 解剖 > CP 感 > 构图 > 动作 > 清晰度。
5. 场景可以现代，人物保持批准古装。
6. 高风险动作允许 Static + 微镜头运动。
7. Lab 与 Production 永远分开。

## 已准备的主要内容

### 人物
`assets/characters/`
- Canonical Visual
- Expression Library
- Costume Stages
- Model Review
- Reference Manifest

孙悟空增加：
- WUKONG_DZS_FORMAL
- WUKONG_DZS_DAILY
- WUKONG_DZS_HOME

林黛玉增加：
- DAIYU_CANONICAL_LAVENDER
- DAIYU_CANONICAL_HOME

### 美术/摄影
`docs/30_VISUAL_DIRECTION_BIBLE.md`
`docs/31_CINEMATOGRAPHY_GRAMMAR.md`
`docs/32_CHARACTER_PERFORMANCE_BIBLE.md`

结构化配置：
`assets/style/`
`assets/relationship/`

### LOOKREEL01
`episodes/LOOKREEL01/`
- 10 shot plan
- detailed shot cards
- image/video prompts
- edit plan
- QA
- approval manifest

### EP001
`episodes/EP001/`
《大圣今天受伤了》
- script
- storyboard
- detailed shot cards
- continuity
- image/video prompts
- edit plan
- QA
- approval manifest

### 第一季
`episodes/SEASON01/`
- 10 集结构
- episode briefs
- asset reuse matrix

### 训练/声音/后期
- 33 LoRA Plan
- 34 Audio Bible
- 35 Post-production
- 36 QA Regression
- 37 Asset Versioning
- 38 Season Blueprint
- 39 Failure Recovery

### 执行管理
- 40 Work Split
- 41 Readiness
- 42 Capacity
- 43 WBS
- 44 Risk Register
- 45 Stage Acceptance
- 46 Batch Plan
- 47 Prompt System
- 48 Reference Bundle
- 49 Agent Rules
- 50 Preproduction Completion

## 自动化工具

`scripts/`
- reference_index.py
- create_contact_sheet.py
- approve_asset.py
- register_asset.py
- validate_schema.py
- project_preflight.py
- validate_production_package.py
- build_render_queue.py
- production_guard.py
- p1_comfy_probe.py

## Schema

`schemas/`
- reference manifest
- approval manifest
- render record
- asset ledger

## 本机下一步

本地 Codex 先：

```bash
git pull --ff-only
pip install -r requirements-tools.txt
python scripts/project_preflight.py --stage MODEL_REVIEW
```

然后把当前认可的建模图/reference 落到：
`local/references/active_visual_target/`

做 Hash、Contact Sheet、最终 Golden Lock。

在 Final Golden Lock 前，不批量消耗 GPU。
