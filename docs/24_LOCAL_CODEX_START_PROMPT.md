# 24 给本地 Codex 的启动指令（V3）

请接管：
E:\project\AI-short-vidio-claw
最新 main。

## Step 0：更新

git status
git pull --ff-only
记录 HEAD。

安装轻量工具依赖：

pip install -r requirements-tools.txt

## Step 1：Preflight

运行：

python scripts/project_preflight.py --stage MODEL_REVIEW

如果报错：
修文件/路径事实。
不要直接开始 GPU。

## Step 2：读当前事实

顺序：

1. AGENTS.md
2. PROJECT_STATE.md
3. docs/49_AGENT_OPERATING_RULES.md
4. docs/45_STAGE_ACCEPTANCE_CRITERIA.md
5. docs/30_VISUAL_DIRECTION_BIBLE.md
6. docs/31_CINEMATOGRAPHY_GRAMMAR.md
7. docs/32_CHARACTER_PERFORMANCE_BIBLE.md
8. docs/25_CHARACTER_MODELING_REVIEW_SPEC.md
9. docs/41_PRELOCAL_READINESS_CHECKLIST.md

## Step 3：人物建模图落盘

用户已经允许当前方向继续前期工作。

把最终候选建模图放：

local/production/MODEL_REVIEW/
- daiyu/
- wukong/
- couple/

以及用于身份锁定的 reference：

local/references/active_visual_target/
- daiyu/face/
- daiyu/costume/
- wukong/face/
- wukong/costume/
- composition/lookreel01/

不要把截图 UI 边框当人物 reference，如果有原图优先原图。

## Step 4：Index

python scripts/reference_index.py ^
  --root local/references/active_visual_target ^
  --out local/references/reference_index.json

## Step 5：Contact Sheet

python scripts/create_contact_sheet.py ^
  --input local/references/active_visual_target/daiyu ^
  --out local/production/MODEL_REVIEW/daiyu_contact.jpg

python scripts/create_contact_sheet.py ^
  --input local/references/active_visual_target/wukong ^
  --out local/production/MODEL_REVIEW/wukong_contact.jpg

生成 couple contact sheet 同理。

## Step 6：等待 Final Golden Approval

当前用户只是允许继续前期，不自动写 FINAL GOLDEN。

把 Contact Sheet 给用户。

用户明确锁定后：
- modeling_review.yaml → golden_model_status: APPROVED
- reference_manifest.yaml → USER_APPROVED
- 填 golden_face_refs / golden_costume_refs
- 写 approved_at

Agent 不得擅自执行。

## Step 7：Schema / Preflight

JSON manifest：

python scripts/validate_schema.py ...

然后：

python scripts/project_preflight.py --stage V0

V0 PASS 后再 K1。

## Step 8：K1

读：
episodes/LOOKREEL01/
docs/46_BATCH_PRODUCTION_PLAN.md
docs/47_PROMPT_COMPOSITION_SYSTEM.md
docs/48_REFERENCE_BUNDLE_SPEC.md

每次做 3–5 张后停下审核。

不要 10 张全自动出完才看。

## Step 9：Approval

用户批准图后：

python scripts/approve_asset.py ...

然后：

python scripts/build_render_queue.py ...

## Step 10：T1

每条先：

python scripts/production_guard.py ...

ok=true 才调用 ComfyUI。

优先：
COMP09
COMP04
COMP01/05

禁止先做 COMP07/08 高风险动态。

## Step 11：E0

10 still + 约4 motion
→ 20–30s Look Reel
→ 用户批准

## Step 12：EP001

Look Reel approved 后：

20 still 全部先完成
→ silent story cut
→ 4–6 motion
→ audio
→ first cut

## GPU Stop Rules

- Guard fail：STOP
- identity 2次系统性失败：STATIC
- M2 3次失败：降 M1
- M3：默认不自动
- OOM：先减 workload，不自动安装14B runner

## 每日/每批提交

必须更新：
- PROJECT_STATE
- approval manifest
- asset ledger
- QA
- WBS/Gate

不要只提交 mp4。
