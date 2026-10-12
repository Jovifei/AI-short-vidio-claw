# 脚本入口（V5）

主文档：`docs/30_PREPRODUCTION_V5_EXECUTION.md`；具体PowerShell命令见`docs/preproduction/LOCAL_COMMANDS_V5.md`。

| 脚本 | 用途 | 是否提交GPU |
|---|---|---|
| `import_reference_bundle.py` | 全包hash预检后复制已有图，不覆盖、不批准 | 否 |
| `preproduction.py plan` | 精确帧级数据合同 | 否 |
| `approve_asset.py reference/keyframe` | 记录真实的具体批准，先验证后写入 | 否 |
| `production_guard.py` | V5 guard入口，校验实际出场角色和I2V链路 | 否 |
| `build_render_queue.py` | V5 queue入口，静帧与blocked分别列出 | 否 |
| `preproduction.py prepare` | 冻结image/workflow/job及源文件hash | 否 |
| `submit_prepared.py` | 默认dry-run；明确--execute才调用原probe | 可选 |
| `render_reference_review.py` | 带标识的静态审片序列，CPU+FFmpeg | 否 |
| `validate_production_package.py` | 区分contract_ok和production_ready | 否 |

保留`reference_index.py`与`create_contact_sheet.py`作为一般素材浏览工具，不把它们产生的索引自动当批准登记。

保留`p1_comfy_probe.py`作为底层工具。正式流程不能用它绕过失败的guard；新入口通过任务包调用它。V5批准表不兼容旧空字段格式，必须显式按真实资产迁移，不自动赋予批准。

## FID1 Wan2.2 source-only trial

FID1 is isolated to `T1_SOURCE_ONLY`. The API graph is `LoadImage -> Wan22ImageToVideoLatent -> FID1WanSourceROIAnchor -> KSampler -> VAEDecode -> Video`; the FID1 validator checks those live ports, frozen ROI JSON, shot profile, sampler budget, source approval/hash and dependency hashes. Ordinary V5 graphs still require their original 12-node path and cannot contain an unprofiled FID1 node.

ComfyUI's `noise_mask` is a **denoise mask**: `1` allows denoising, `0` preserves the latent. The FID1 node blends the encoded first latent into only the profile's future face/head ROIs and sets `denoise_mask = base_mask * (1 - anchor_alpha)`. It preserves Wan's first-slot mask and leaves pixels outside the selected ROIs denoisable. Legacy schema-v2 profiles use a hard 0/1 anchor; schema-v3 may set per-ROI `feather_latent` (1–4 latent cells). With `feather_latent=4`, alpha is 0 at the ROI boundary, then 0.25/0.5/0.75 inward, and 1 in the core. The pinned KSampler performs continuous mask blending. Both modes are diagnostics and can create patches/seams; neither claims identity locking or visual acceptance.

The shot-specific profiles freeze their approved source hash, size, frame count, fps, seed, ROI rectangles, prompts, and anchor strategy:

- `config/source_fidelity_trials/SH903_FID1_V002.json`: SH903, seed `2026100803`.
- `config/source_fidelity_trials/SH903_FID1_V003.json`: controlled SH903 take05 profile matching take03 prompts and sampling values.
- `config/source_fidelity_trials/SH903_FID1_V004.json`: soft-edge ROI take06 profile; differs from V003 only by `feather_latent=4` per approved face ROI.
- `config/source_fidelity_trials/SH901_FID1_V001.json`: SH901, seed `2026100801`.
- `config/source_fidelity_trials/SH902_FID1_V001.json`: SH902, seed `2026100802`.

Local commands for the first trial:

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/fid1_deploy.py deploy --root . --comfy-root local/comfyui/image/ComfyUI
python scripts/fid1_deploy.py verify --root . --comfy-root local/comfyui/image/ComfyUI
python scripts/source_pilot.py prepare --root . --shot SH903 --seed 2026100803 --out local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04 --trial-profile config/source_fidelity_trials/SH903_FID1_V002.json
python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04 --url http://127.0.0.1:8188
python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04 --url http://127.0.0.1:8188 --comfy-root local/comfyui/image/ComfyUI --execute
python scripts/fid1_qa_report.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04
```

The submit command without `--execute` is a dry-run. Execute also verifies the deployed node hash, local ComfyUI `/object_info` socket schema, and an empty queue; the existing probe rechecks the queue before POST. Unknown submissions are reconciled through ComfyUI history and never automatically retried. Each take path is immutable.

`fid1_qa_report.py` runs ffprobe, decodes the full MP4, extracts all 49 frames, makes first/middle/last and all-frame contact sheets, verifies the output hash, and records probe resources. Its `visual_review_template.json` leaves every criterion `PENDING`, the reviewer blank, and the quote blank. After Jovi actually watches the whole clip, copy/fill that template under `local/review_evidence/` with the exact review and preview/apply it with:

```powershell
python scripts/fid1_qa_report.py record-review --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04 --feedback local/review_evidence/FID1_SH903_TAKE04_VISUAL_REVIEW.json
python scripts/fid1_qa_report.py record-review --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04 --feedback local/review_evidence/FID1_SH903_TAKE04_VISUAL_REVIEW.json --apply
```

SH901 requires a hash-bound Jovi acceptance of SH903 take04; SH902 requires the same for SH901's new take. Source-pilot input approval remains separate from output visual acceptance. All three results remain ineligible for the original LOOKREEL01/EP001 cut.

Rollback only removes the exact FID1 package installed by this tool, and refuses if its bytes or ownership changed:

```powershell
python scripts/fid1_deploy.py rollback --root . --comfy-root local/comfyui/image/ComfyUI
```

测试：`python -m unittest discover -s tests -p "test_preproduction_v5.py" -v`，不需要GPU/Pillow。审片序列另需Pillow及FFmpeg。

## 保留的V3管理工具

`project_preflight.py`、`register_asset.py`、`validate_schema.py`及`schemas/`均保留；它们提供V3知识/台账检查。V5使用独立版本标记的计划/批准表，旧schema通过不能替代新的hash/live-chain guard。具体整合见docs/51_PREPRODUCTION_INTEGRATION_V5.md。
