# 24 给本地 Codex 的启动指令

请接管 E:\project\AI-short-vidio-claw 最新 main。

不要继续跑历史 P1A T2V benchmark。

严格阅读：
1. AGENTS.md
2. PROJECT_STATE.md
3. docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. docs/19_ACTIVE_VISUAL_SPEC.md
5. docs/05_DIRECTORY_STANDARD.md
6. docs/22_LOCAL_HANDOFF.md
7. docs/stages/V0_REFERENCE_AND_LOOK_LOCK.md
8. docs/stages/K1_TEN_COMPOSITION_KEYFRAMES.md

然后只执行以下任务：

## Task 1：Reference Inbox
创建并检查：
local/references/inbox/
local/references/active_visual_target/

如果用户 reference 还没在本机，列出缺失项并停止，不要用 SDXL 临时猜人物。

## Task 2：Index
reference 到位后运行：

python scripts/reference_index.py ^
  --root local/references/active_visual_target ^
  --out local/references/reference_index.json

检查 hash，不自动批准。

## Task 3：V0 Manifest
根据用户明确批准结果更新：
assets/characters/daiyu/reference_manifest.yaml
assets/characters/wukong/reference_manifest.yaml

只有明确批准的 ref_id 才进入 golden_face_refs / golden_costume_refs。

## Task 4：V0 Contact Sheet
生成联系表，供用户确认。
未确认前停止。

## Task 5：K1
V0 PASS 后，按照 episodes/LOOKREEL01/plan.yaml 和 image_prompts.md 制作 10 张关键帧。

如果关键帧通过 ChatGPT Web 产生：
把成品放到：
local/production/LOOKREEL01/candidates/<SHOT>/

用户批准后复制到：
local/production/LOOKREEL01/approved/

然后写真实 sha256 到：
episodes/LOOKREEL01/approval_manifest.json

状态改 USER_APPROVED。

## Task 6：Package Validation
运行：

python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01

## Task 7：T1 前 Guard
选 approved keyframe 后先运行：

python scripts/production_guard.py ^
  --approval-manifest episodes/LOOKREEL01/approval_manifest.json ^
  --shot COMP01 ^
  --image <approved-image-path> ^
  --workflow workflows/video/production/VID_wan22_5b_i2v_prod_v001.json

只有返回 ok=true 才允许调用 ComfyUI。

## Stop
K1 十张还未全部 USER_APPROVED 前，不开始 EP001。
