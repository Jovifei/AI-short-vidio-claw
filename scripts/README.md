# scripts

## Active V2 Tools

### reference_index.py
扫描 local/references，计算 SHA256 和 ref_id。
不会自动批准。

示例：
python scripts/reference_index.py --root local/references/active_visual_target --out local/references/reference_index.json

### create_contact_sheet.py
把人物 reference 排成联系表，方便用户审核。

依赖：
pip install -r requirements-tools.txt

示例：
python scripts/create_contact_sheet.py --input local/references/active_visual_target/daiyu --out local/production/MODEL_REVIEW/daiyu_contact.jpg

### approve_asset.py
把“用户已经明确批准”的某张 keyframe 写入 approval manifest。

它要求：
--user-confirmed YES

示例：
python scripts/approve_asset.py --manifest episodes/LOOKREEL01/approval_manifest.json --shot COMP01 --image local/production/LOOKREEL01/approved/LOOKREEL01_COMP01_KF_v001.png --user-confirmed YES --daiyu-ref DAIYU_FACE_FRONT_001 --wukong-ref WUKONG_FACE_FRONT_001 --daiyu-costume DAIYU_CLASSIC_OUTDOOR --wukong-costume WUKONG_CLASSIC_OUTDOOR

注意：
此工具不应由 Agent 在没有用户明确批准时自行调用。

### validate_production_package.py
检查 LOOKREEL/EP 包文档与 approval manifest。

### production_guard.py
Production I2V 的 fail-closed 门禁。
验证：
- shot 已用户批准
- keyframe hash 一致
- identity refs
- costume refs
- LoadImage
- start_image connection

通过后才允许调用 ComfyUI。

### build_render_queue.py
只从 USER_APPROVED / PRODUCTION_READY shot 构建渲染队列。
未批准镜头自动 skipped。

### p1_comfy_probe.py
已有底层 ComfyUI 提交工具。
V2 中必须位于 Production Guard 后面。

## Future
完整 episode CLI 等 E0/E1 证明流程后再抽象。
