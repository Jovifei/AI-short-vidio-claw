# 24 给本地 Codex 的启动指令

请接管 E:\project\AI-short-vidio-claw 最新 main。

不要继续跑历史 P1A 泛化 T2V benchmark。

严格阅读：
1. AGENTS.md
2. PROJECT_STATE.md
3. docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. docs/19_ACTIVE_VISUAL_SPEC.md
5. docs/25_CHARACTER_MODELING_REVIEW_SPEC.md
6. docs/05_DIRECTORY_STANDARD.md
7. docs/22_LOCAL_HANDOFF.md
8. docs/27_GPU_EXECUTION_CHECKLIST.md
9. docs/stages/V0_REFERENCE_AND_LOOK_LOCK.md
10. docs/stages/K1_TEN_COMPOSITION_KEYFRAMES.md

## Task 0：人物模型审核优先

用户需要先审核：
- DAIYU Model Sheet
- WUKONG Model Sheet
- Couple Scale Sheet

将最终图片放：
local/production/MODEL_REVIEW/

根据用户反馈更新：
assets/characters/daiyu/modeling_review.yaml
assets/characters/wukong/modeling_review.yaml

没有 GOLDEN_MODEL_APPROVED，不进入 K1 视频生产。

## Task 1：Reference Inbox

创建并检查：
local/references/inbox/
local/references/active_visual_target/

如果 reference 还没在本机，列出缺失项并停止，不用 SDXL 临时猜人物。

## Task 2：Index

reference 到位后运行：
python scripts/reference_index.py --root local/references/active_visual_target --out local/references/reference_index.json

检查 hash，不自动批准。

## Task 3：Contact Sheet

安装轻量工具依赖：
pip install -r requirements-tools.txt

生成角色联系表：
python scripts/create_contact_sheet.py --input local/references/active_visual_target/daiyu --out local/production/MODEL_REVIEW/daiyu_contact.jpg
python scripts/create_contact_sheet.py --input local/references/active_visual_target/wukong --out local/production/MODEL_REVIEW/wukong_contact.jpg

给用户看。
未确认前停止。

## Task 4：V0 Manifest

根据用户明确批准结果更新：
assets/characters/daiyu/reference_manifest.yaml
assets/characters/wukong/reference_manifest.yaml

只有明确批准 ref_id 才进入 golden_face_refs / golden_costume_refs。

## Task 5：K1

V0 PASS 后，按照：
episodes/LOOKREEL01/plan.yaml
episodes/LOOKREEL01/shot_cards.yaml
episodes/LOOKREEL01/image_prompts.md

制作 10 张关键帧。

candidate：
local/production/LOOKREEL01/candidates/<SHOT>/

approved：
local/production/LOOKREEL01/approved/

用户批准后运行 approve_asset.py 写真实 hash。

## Task 6：Package Validation

python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01

## Task 7：Build Queue

python scripts/build_render_queue.py --manifest episodes/LOOKREEL01/approval_manifest.json --project-root local/production/LOOKREEL01 --out local/production/LOOKREEL01/render_queue.json

## Task 8：T1 前 Guard

对每个 READY shot：
python scripts/production_guard.py --approval-manifest episodes/LOOKREEL01/approval_manifest.json --shot COMP01 --image <approved-image-path> --workflow workflows/video/production/VID_wan22_5b_i2v_prod_v001.json

只有 ok=true 才允许调用 ComfyUI。

## Stop Rules

- Golden Model 未批准：停止。
- K1 未全部 USER_APPROVED：不开始 EP001。
- Production Guard fail：不提交视频。
- M0/M3：不自动做完整 I2V。
