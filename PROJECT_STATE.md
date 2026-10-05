# PROJECT_STATE

更新时间：2026-10-05 23:45 +08:00

状态：
**REMOTE_PREPRODUCTION_V3_COMPLETE / MODEL_DIRECTION_PREPROD_APPROVED / FINAL_GOLDEN_HASH_PENDING**

## 1. 用户最新反馈

用户对当前建模人物方向表示：
“感觉可以，继续用建模的人物制作短剧所需的所有不在本地执行的工作。”

项目解释：
- 允许继续所有非本地 Preproduction；
- 允许围绕当前人物方向写剧本、Prompt、Stage、视觉圣经；
- 不自动等同 FINAL_GOLDEN_MODEL；
- Final Golden 仍需要本地 Reference + Hash + 最终批准。

## 2. 已完成的非本地工作

### 产品/架构
- PRD / Route V2
- Lab / Production Split
- Gate Matrix
- Work Split
- WBS
- Risk Register
- Stage Acceptance

### 人物
- DAIYU / WUKONG Canonical Visual
- Expression Library
- Modeling Review
- Costume Stages
- Douzhanshengfo Formal/Daily/Home
- Relationship Interaction Library

### 视觉
- Visual Direction Bible
- Cinematography Grammar
- Lighting/Color
- Performance Bible
- Reference Bundle Spec
- Prompt Composition System

### 创作
- Season 01 10 episodes
- LOOKREEL01 full package
- EP001 full package
- Asset reuse matrix

### 后期/声音
- Audio Voice/Sound Bible
- Post-production Spec
- QA Regression
- Failure Recovery

### ML/Automation
- LoRA Dataset/Training Plan
- Schemas
- Reference Index
- Contact Sheet
- Explicit Approval Tool
- Asset Ledger Tool
- Project Preflight
- Package Validator
- Render Queue
- Production Guard
- Production Wan2.2 5B I2V candidate workflow

## 3. 已知本地 Lab

- RTX 4070 SUPER 12282 MiB
- RAM ~31.82 GB
- Wan2.2-TI2V-5B models installed
- 480×832×49 T2V 10/10
- p50 187.7095s
- p95 264.101s
- one I2V wiring success
- approved-keyframe I2V not yet verified

## 4. 当前唯一正确 Local Gate

MODEL_REVIEW_FINAL：

1. 保存最终人物建模/reference
2. SHA256
3. Contact Sheet
4. 用户最终锁定
5. modeling_review.yaml → APPROVED
6. reference_manifest → USER_APPROVED

然后才进入 V0/K1/T1。

## 5. 当前禁止

- 未批准人物批量 I2V
- 无 start_image 的 Product T2V
- 自动训练 LoRA
- 自动把 PREPROD_APPROVED 改 GOLDEN
- M3 高风险镜头自动批量
- 为了“继续推进”自行改人物脸

## 6. 详细索引

docs/30–50 为当前扩展 Preproduction 知识层。

当前执行优先阅读：
- AGENTS.md
- docs/49_AGENT_OPERATING_RULES.md
- docs/45_STAGE_ACCEPTANCE_CRITERIA.md
- docs/41_PRELOCAL_READINESS_CHECKLIST.md
