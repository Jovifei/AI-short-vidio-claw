# scripts

## Active V2 Tools

### reference_index.py
扫描 local/references，计算 hash。
它绝不会自动批准 reference。

示例：
python scripts/reference_index.py --root local/references/active_visual_target --out local/references/reference_index.json

### validate_production_package.py
检查 LOOKREEL/EP 包是否具备文档与 approval manifest。

示例：
python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01

### production_guard.py
Production I2V 的 fail-closed 门禁。
验证：
- shot 已用户批准
- keyframe hash 一致
- identity refs
- costume refs
- LoadImage
- start_image connection

通过 Guard 后才允许调用 p1_comfy_probe.py 或后续 Comfy client。

### p1_comfy_probe.py
已有的 Lab/低层 ComfyUI 提交工具。
V2 中它不是 approval system，必须放在 Production Guard 后面使用。

## Future
完整 episode CLI 仍属于后续 A3/P4，等 E0/E1 成功后再抽象。
