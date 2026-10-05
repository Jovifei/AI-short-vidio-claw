# scripts — V3 工具索引

## 环境

pip install -r requirements-tools.txt

## 1. project_preflight.py

检查 Product Stage 前置。

示例：

python scripts/project_preflight.py --stage MODEL_REVIEW
python scripts/project_preflight.py --stage V0
python scripts/project_preflight.py --stage K1
python scripts/project_preflight.py --stage T1

Fail-closed。

## 2. reference_index.py

扫描 reference，生成 SHA256/ref_id。
不会自动批准。

## 3. create_contact_sheet.py

将本地 Reference 排成 Contact Sheet。
只用于审核。

## 4. approve_asset.py

只有用户明确批准后调用。

必须：
--user-confirmed YES

它不应该被 Agent 在无人确认时自动调用。

## 5. register_asset.py

向 local/asset_ledger.jsonl 登记资产。

不能授予 USER_APPROVED。

## 6. validate_schema.py

使用 schemas/ 校验 JSON。

## 7. validate_production_package.py

检查 LOOKREEL/EP 包结构与 approval manifest。

## 8. build_render_queue.py

只从 USER_APPROVED/PRODUCTION_READY shot 生成队列。

## 9. production_guard.py

视频前最终门禁：
- approval
- hash
- identity refs
- costume refs
- LoadImage
- start_image

Guard 不通过禁止 POST /prompt。

## 10. p1_comfy_probe.py

底层 ComfyUI API 提交/监控/记录工具。

V3 中：
必须位于 Production Guard 之后。

它不是 approval system。

## 推荐调用链

reference_index
→ contact_sheet
→ user approval
→ approve_asset
→ validate package
→ build queue
→ production_guard
→ p1_comfy_probe

## Future

完整 CLI：
等 E0/EP001 手工流程证明有效以后再抽象。
