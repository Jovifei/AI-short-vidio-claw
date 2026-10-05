# AGENTS.md — AI/Codex 最高执行规则

## 1. 当前项目状态

人物方向已获得“可继续前期工作”的用户认可。

状态：
PREPROD_MODEL_DIRECTION_APPROVED

不是：
FINAL_GOLDEN_MODEL_APPROVED

不要混淆。

## 2. 必须先读

1. README.md
2. PROJECT_STATE.md
3. docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. docs/19_ACTIVE_VISUAL_SPEC.md
5. docs/30_VISUAL_DIRECTION_BIBLE.md
6. docs/31_CINEMATOGRAPHY_GRAMMAR.md
7. docs/32_CHARACTER_PERFORMANCE_BIBLE.md
8. docs/45_STAGE_ACCEPTANCE_CRITERIA.md
9. docs/49_AGENT_OPERATING_RULES.md
10. 当前 stage 文件

## 3. Production 硬规则

- 主角镜头必须 Image First → Video Second。
- Approved Keyframe 前禁止 Product I2V。
- Visual Reference 高于文字 Prompt。
- 场景可现代，人物服装保持批准古装。
- GPU heavy jobs 串行。
- Lab output 不能满足 Product Gate。
- Agent 不能自行设置 USER_APPROVED/GOLDEN_MODEL_APPROVED。

## 4. 人物

DAIYU：
canonical visual + approved refs。

WUKONG：
canonical visual + Douzhanshengfo stages + approved refs。

人物脸不对：
回模型/关键帧层。
不要在视频层硬救。

## 5. Motion

M0：静态
M1：微动作
M2：慢中动作
M3：高风险

自动队列默认只允许 M1/M2。
M0 用静态。
M3 需显式人工决定。

## 6. 失败上限

Keyframe：
3 轮仍不对 → Hero/manual。

I2V：
2 次系统性身份失败 → static fallback。

M2：
3 次失败 → M1。

不要无限抽卡。

## 7. 本地前置

先运行：
python scripts/project_preflight.py --stage <STAGE>

Production 视频前：
python scripts/production_guard.py ...

Guard fail：
绝不 POST /prompt。

## 8. 记录

所有可进入 Production 的资产必须有：
- asset ID
- path
- sha256
- source
- refs
- stage
- status
- approval

## 9. 技术栈

不要因为新模型热门自动更换 Production。

任何新模型：
Lab
→ fixed regression
→ compare
→ approval
→ production promotion。

## 10. 任务结束报告

必须写：
- 完成 WBS ID
- Gate
- Files
- Benchmark/QA
- Blocker
- Commit
- Next WBS

不能只写“继续优化”。
