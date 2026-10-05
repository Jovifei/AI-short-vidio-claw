# 05 目录与文件规范（V2 Active）

## 1. 目标

目录必须让人和 Agent 都能回答：
- 角色 reference 在哪里；
- 哪些是 Lab；
- 哪些是 Production；
- 哪些是 approved；
- 哪些可以提交 Git；
- 哪些必须只留本地。

## 2. 标准目录

~~~text
AI-short-vidio-claw/
├─ README.md
├─ AGENTS.md
├─ PROJECT_STATE.md
│
├─ config/
│  ├─ project.example.yaml
│  ├─ models.example.yaml
│  └─ runtime.example.yaml
│
├─ docs/
│  ├─ 00_PROJECT_CHARTER.md
│  ├─ 01_PRD.md
│  ├─ 05_DIRECTORY_STANDARD.md
│  ├─ 18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
│  ├─ 19_ACTIVE_VISUAL_SPEC.md
│  ├─ 20_CREATIVE_AND_SERIES_BIBLE.md
│  ├─ 21_PRODUCTION_SOP_V2.md
│  ├─ 22_LOCAL_HANDOFF.md
│  ├─ stages/
│  ├─ benchmarks/
│  └─ reviews/
│
├─ assets/
│  ├─ characters/
│  │  ├─ daiyu/
│  │  │  ├─ character.yaml
│  │  │  ├─ reference_manifest.example.yaml
│  │  │  └─ stages/
│  │  └─ wukong/
│  │     ├─ character.yaml
│  │     ├─ reference_manifest.example.yaml
│  │     └─ stages/
│  ├─ style/
│  │  └─ ACTIVE_VISUAL_TARGET.yaml
│  ├─ locations/
│  ├─ props/
│  └─ audio/
│
├─ prompts/
│  ├─ image/
│  ├─ video/
│  └─ qa/
│
├─ workflows/
│  ├─ image/
│  ├─ video/
│  │  ├─ lab/
│  │  └─ production/
│  ├─ lipsync/
│  └─ post/
│
├─ episodes/
│  ├─ LOOKREEL01/
│  ├─ EP001/
│  └─ _template/
│
├─ scripts/
│  ├─ p1_comfy_probe.py
│  ├─ reference_index.py
│  ├─ production_guard.py
│  └─ validate_production_package.py
│
├─ models/
│  └─ manifests/
│
├─ outputs/
│  └─ README.md
│
└─ local/                     # Git ignored
   ├─ references/
   │  ├─ inbox/
   │  └─ active_visual_target/
   │     ├─ daiyu/
   │     │  ├─ face/
   │     │  └─ costume/
   │     ├─ wukong/
   │     │  ├─ face/
   │     │  └─ costume/
   │     └─ composition/
   │        └─ lookreel01/
   │
   ├─ production/
   │  ├─ LOOKREEL01/
   │  │  ├─ candidates/
   │  │  ├─ approved/
   │  │  ├─ video/
   │  │  ├─ audio/
   │  │  └─ edit/
   │  └─ EP001/
   │     ├─ candidates/
   │     ├─ approved/
   │     ├─ video/
   │     ├─ audio/
   │     └─ edit/
   │
   ├─ models/
   ├─ cache/
   └─ temp/
~~~

## 3. Lab 与 Production 物理分开

Lab workflow：
workflows/video/lab/

Production workflow：
workflows/video/production/

Lab media：
local/lab/ 或 docs/reviews/（仅审核副本）

Production media：
local/production/<PROJECT_ID>/

禁止把 lab output 直接复制为 approved production asset。

## 4. Reference

第三方/用户 reference 原图：
local/references/

Git 中只保存：
- ref_id
- hash
- relative path
- approval status
- notes

真实大图不提交。

## 5. Approved Keyframe

路径：
local/production/<PROJECT_ID>/approved/

命名：
<PROJECT>_<SHOT>_KF_vNNN.png

例：
LOOKREEL01_COMP01_KF_v001.png

每张必须在 approval_manifest 中有：
- sha256
- approved_by_user
- approved_at
- identity refs
- costume refs

## 6. Candidate

路径：
local/production/<PROJECT_ID>/candidates/<SHOT_ID>/

candidate 永远不能被 Production Guard 当作 approved input。

## 7. 视频

原始 take：
local/production/<PROJECT_ID>/video/<SHOT_ID>/takes/

accepted：
local/production/<PROJECT_ID>/video/<SHOT_ID>/accepted/

命名：
<PROJECT>_<SHOT>_TAKE01.mp4
<PROJECT>_<SHOT>_ACCEPTED_v001.mp4

## 8. Episode 文档

Git 中 episodes/<ID>/ 必须包含：
- episode.yaml / plan.yaml
- script.md（剧情项目）
- storyboard.md
- image_prompts.md
- video_prompts.md
- edit_plan.md
- approval_manifest.json
- qa.md / qa_report.md

## 9. 模型

Git：
models/manifests/

真实权重：
local/models/ 或 F:/ComfyUI/models（当前机器）

不要复制大模型进仓库。

## 10. build / dist / outputs

build：
软件构建临时产物。

dist：
未来 CLI/桌面程序发行包。

outputs：
最终交付索引/小型说明；真实大视频默认留 local/production/.../edit/。

## 11. 状态

DRAFT
CANDIDATE
USER_APPROVED
PRODUCTION_READY
VIDEO_ACCEPTED
FIRST_CUT
FINAL_QC
DONE

只有用户明确批准才能进入 USER_APPROVED。
