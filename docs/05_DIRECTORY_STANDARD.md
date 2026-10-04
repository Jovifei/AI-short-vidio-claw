# 05 目录与文件规范

## 1. 设计目标

目录必须同时满足：
- 人能一眼看懂；
- Codex 能按约定自动定位；
- 大文件不进 Git；
- 每一集可单独重跑；
- 模型、工作流、人物、集数彼此解耦。

## 2. 标准目录

~~~text
AI-short-vidio-claw/
├─ README.md
├─ AGENTS.md
├─ PROJECT_STATE.md
├─ .env.example
├─ .gitignore
│
├─ config/
│  ├─ project.example.yaml
│  ├─ models.example.yaml
│  └─ runtime.example.yaml
│
├─ docs/
│  ├─ 00_PROJECT_CHARTER.md
│  ├─ 01_PRD.md
│  ├─ 02_FEASIBILITY.md
│  ├─ 03_TECHNICAL_ARCHITECTURE.md
│  ├─ 04_SOP.md
│  ├─ 05_DIRECTORY_STANDARD.md
│  ├─ 06_CHARACTER_SYSTEM.md
│  ├─ 07_EPISODE_STANDARD.md
│  ├─ 08_MODEL_AND_WORKFLOW_MATRIX.md
│  ├─ 09_REFERENCE_SOURCES.md
│  ├─ 10_QA_ACCEPTANCE.md
│  ├─ 11_ROADMAP.md
│  ├─ 12_RISK_AND_COMPLIANCE.md
│  ├─ 13_CODEX_RUNBOOK.md
│  ├─ 14_DECISION_LOG.md
│  ├─ 15_EP001_PILOT_PLAN.md
│  └─ benchmarks/
│
├─ assets/
│  ├─ README.md
│  ├─ characters/
│  │  ├─ daiyu/
│  │  │  ├─ character.yaml
│  │  │  ├─ reference/
│  │  │  ├─ approved/
│  │  │  └─ stages/
│  │  └─ wukong/
│  ├─ locations/
│  ├─ props/
│  ├─ style/
│  └─ audio/
│
├─ models/
│  ├─ README.md
│  └─ manifests/
│
├─ workflows/
│  ├─ README.md
│  ├─ image/
│  ├─ video/
│  ├─ lipsync/
│  └─ post/
│
├─ prompts/
│  ├─ README.md
│  ├─ system/
│  ├─ image/
│  ├─ video/
│  └─ qa/
│
├─ episodes/
│  ├─ README.md
│  ├─ _template/
│  └─ EP001/
│
├─ src/
│  └─ ai_short_video_claw/
│     ├─ adapters/
│     ├─ pipeline/
│     ├─ manifests/
│     ├─ qa/
│     └─ cli/
│
├─ scripts/
│  └─ README.md
│
├─ tests/
│
├─ outputs/
│  └─ README.md
│
├─ build/
├─ dist/
└─ local/                 # 整个目录 Git ignored
   ├─ models/
   │  ├─ checkpoints/
   │  ├─ diffusion_models/
   │  ├─ loras/
   │  ├─ vae/
   │  ├─ text_encoders/
   │  ├─ clip_vision/
   │  ├─ ipadapter/
   │  ├─ insightface/
   │  ├─ tts/
   │  └─ lipsync/
   ├─ comfyui/
   │  ├─ image/
   │  └─ video/
   ├─ cache/
   ├─ temp/
   └─ external/
~~~

## 3. 关键目录解释

### assets/
保存“创作身份资产”与小型配置，不保存未经授权的影视素材库。

人物资产按 character_id 管理。每个角色应该有 character.yaml，记录：
- canonical_name
- visual_traits
- forbidden_drift
- baseline_stage
- approved_reference IDs
- lora model id
- voice id

approved/ 只放最终确认的人物参考图。数量控制，避免仓库膨胀；大图可放 local 并在 yaml 记录路径/hash。

### models/
Git 中只放 manifest，不放权重。

local/models/ 才是真正模型文件夹。

建议不要在多个 ComfyUI 安装里重复下载同一权重；优先用：
- Windows junction/symlink；
- ComfyUI extra_model_paths；
指向统一 local/models。

### workflows/
只保存可复用、已验收的 ComfyUI API workflow JSON。

命名：
- IMG_identity_pulid_v001.json
- IMG_keyframe_dual_v001.json
- VID_wan22_i2v_576x1024_v001.json
- VID_wan22_lowvram_v001.json
- LIP_musetalk_v001.json

不能把临时实验 workflow 直接覆盖 production 版本。

### episodes/
每集一个独立工作单元。

EP001/
- episode.yaml
- script.md
- visual_design.md
- storyboard.md
- image_prompts.md
- video_prompts.md
- edit_plan.md
- qa_report.md
- manifest.json
- frames/
- video/
- audio/

其中 generated 大文件可在 local 或 ignored 子目录。

### outputs/
只用于成片及交付包，本地生成，不进入 Git。
建议：
- outputs/previews/
- outputs/final/
- outputs/archive/

### build/
代码编译、打包的临时目录，可删除重建。

### dist/
未来 CLI/桌面工具的发行包，不作为素材目录。

## 4. 文件命名

镜头：
SHOT-EP001-001

关键帧：
EP001_SH001_KF_v003.png

视频 take：
EP001_SH001_TAKE02.mp4

接受视频：
EP001_SH001_ACCEPTED.mp4

对白：
EP001_SH001_DAIYU_LINE01.wav

人物 reference：
CHAR_DAIYU_BASE_FRONT_v002.png

人物 stage：
CHAR_DAIYU_STAGE_HOME_v001.yaml

## 5. 版本原则

- prompt 修改必须增加 revision；
- workflow 结构变更必须增加版本；
- approved 资产不可静默覆盖；
- accepted clip 不覆盖旧 take；
- final.mp4 每次交付写 build number 或日期到 manifest。

## 6. 模型目录与 ComfyUI 的关系

本项目不要求复制模型到 ComfyUI 默认路径。
推荐 local/models 为单一真实来源，然后映射至 ComfyUI。

映射示意：
- local/models/diffusion_models → ComfyUI/models/diffusion_models
- local/models/loras → ComfyUI/models/loras
- local/models/vae → ComfyUI/models/vae
- local/models/text_encoders → ComfyUI/models/text_encoders
- local/models/clip_vision → ComfyUI/models/clip_vision
- local/models/ipadapter → ComfyUI/models/ipadapter

模型 manifest 必须记录：来源 URL、文件名、hash、许可证、用途、最后验证日期。
