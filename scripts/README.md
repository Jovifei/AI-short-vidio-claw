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

FID1 is isolated to `T1_SOURCE_ONLY`. Legacy schema-v2/v3 profiles use `LoadImage -> Wan22ImageToVideoLatent -> FID1WanSourceROIAnchor -> KSampler`; schema-v4 uses `ModelSamplingSD3 -> FID1WanTimestepAwareROIAnchor -> KSampler.model` and `Wan22ImageToVideoLatent -> FID1WanTimestepAwareROIAnchor -> KSampler.latent_image`. The validator checks these exact live ports, frozen ROI JSON, shot profile, sampler budget, source approval/hash and dependency hashes. Ordinary V5 graphs still require their original 12-node path and cannot contain an unprofiled FID1 node.

ComfyUI's `noise_mask` is a **denoise mask**: `1` allows denoising, `0` preserves the latent. Legacy schema-v2/v3 profiles write `base_mask * (1 - anchor_alpha)` into `LATENT.noise_mask`; the resulting spatial mean changes Wan22's timestep for the entire time slot, and take05/take07 both failed visually. Schema-v4 leaves Wan's original `noise_mask` untouched so condition encoding retains slot0=0/future=1, applies ROI preservation only through the cloned MODEL's KSampler `denoise_mask_function`, and uses the instance-patched `scale_latent_inpaint` to place the source ROI on the current flow-noise trajectory at each sigma. For each future cell with alpha>0, LATENT carries the complete source value; KSampler applies feather alpha once. It keeps the source first slot clean, preserves latent metadata, and leaves non-ROI future cells denoisable. V005 keeps V004's ROI boxes and four-cell feather exactly, changing only the anchor strategy. The graph validator freezes ModelSamplingSD3 to shift 8, flow sampling and multiplier 1000. All versions remain diagnostic and do not claim identity locking or visual acceptance.

The shot-specific profiles freeze their approved source hash, size, frame count, fps, seed, ROI rectangles, prompts, and anchor strategy:

- `config/source_fidelity_trials/SH903_FID1_V002.json`: SH903, seed `2026100803`.
- `config/source_fidelity_trials/SH903_FID1_V003.json`: controlled SH903 take05 profile matching take03 prompts and sampling values.
- `config/source_fidelity_trials/SH903_FID1_V004.json`: soft-edge ROI profile used by take07; differs from V003 only by `feather_latent=4` per approved face ROI.
- `config/source_fidelity_trials/SH903_FID1_V005.json`: corrected timestep-aware candidate used by take09; identical to V004 for source, prompts, seed, sampler values, ROI bounds and feather, changing only the anchor strategy. Take08 is preserved as one failed attempt caused by Comfy's 1→48 mask-channel expansion.
- `config/source_fidelity_trials/SH901_FID1_V001.json`: SH901, seed `2026100801`.
- `config/source_fidelity_trials/SH902_FID1_V001.json`: SH902, seed `2026100802`.
- `config/source_fidelity_trials/SH901_FID1_V002.json` and `SH902_FID1_V002.json`: independent schema-4 candidates preserving each shot's own source, seed, prompt and V001 ROI bounds with feather=4.

Historical take09 commands (already executed; existing jobs and QA must not be recreated):

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/fid1_deploy.py deploy --root . --comfy-root local/comfyui/image/ComfyUI
python scripts/fid1_deploy.py verify --root . --comfy-root local/comfyui/image/ComfyUI
python scripts/source_pilot.py prepare --root . --shot SH903 --seed 2026100803 --out local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --trial-profile config/source_fidelity_trials/SH903_FID1_V005.json
python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --url http://127.0.0.1:8188
python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --url http://127.0.0.1:8188 --comfy-root local/comfyui/image/ComfyUI --execute
python scripts/fid1_qa_report.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09
```

The submit command without `--execute` is a dry-run. Execute also verifies the deployed node hash, local ComfyUI `/object_info` socket schema, and an empty queue; the existing probe rechecks the queue before POST. Unknown submissions are reconciled through ComfyUI history and never automatically retried. Each take path is immutable.

`fid1_qa_report.py` runs ffprobe, decodes the full MP4, extracts all 49 frames, makes first/middle/last and all-frame contact sheets, verifies the output hash, and records probe resources. Its `visual_review_template.json` leaves every criterion `PENDING`, the reviewer blank, and the quote blank. After Jovi actually watches the whole clip, copy/fill that template under `local/review_evidence/` with the exact review and preview/apply it with:

```powershell
python scripts/fid1_qa_report.py review-page --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --out local/production/T1_SOURCE_PILOT/review_sessions/SH903_take09_NEW
python scripts/fid1_qa_report.py record-review --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --feedback local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json
python scripts/fid1_qa_report.py record-review --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --feedback local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json --apply
```

The standalone review page embeds the actual approved input, output video, frozen face/costume references and QA sheets. All selections and the reviewer/quote start blank. Export records only the user's actual selections; playback events never select PASS. Copy Jovi's actual export into the feedback path before preview/apply. Creating the page does not change the old job, QA or approvals. Use a new unused review session directory.

SH901 requires an explicitly selected accepted SH903 job; SH902 requires an explicitly selected accepted SH901 job. No latest scan or hardcoded take fallback is used. After real acceptance, prepare a new unused downstream take with its independent profile and `--previous-job`:

```powershell
python scripts/source_pilot.py prepare --root . --shot SH901 --seed 2026100801 --out local/production/T1_SOURCE_PILOT/video/SH901/jobs/take02 --trial-profile config/source_fidelity_trials/SH901_FID1_V002.json --previous-job local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09
```

New FID1 contract schema 2 freezes the selected predecessor's job/integrity/workflow/input/run/QA/output/review evidence and identities. Prepare rechecks before publication; submit rechecks during dry-run, under the submission lock, and after runtime checks before writing an attempt marker. Completed historical jobs remain reviewable using their frozen bytes; they are not required to match current implementation files. Legacy downstream schema-1 jobs cannot execute and must use a new take with a frozen predecessor receipt. The receipt covers the direct predecessor; SH902 embeds SH901's frozen ancestor receipt through SH901 job bytes rather than rehashing every completed historical ancestor. Source-pilot input approval remains separate from output visual acceptance. All results remain ineligible for the original LOOKREEL01/EP001 cut.

Rollback only removes the exact FID1 package installed by this tool, and refuses if its bytes or ownership changed:

```powershell
python scripts/fid1_deploy.py rollback --root . --comfy-root local/comfyui/image/ComfyUI
```

测试：`python -m unittest discover -s tests -p "test_preproduction_v5.py" -v`，不需要GPU/Pillow。审片序列另需Pillow及FFmpeg。

## 保留的V3管理工具

`project_preflight.py`、`register_asset.py`、`validate_schema.py`及`schemas/`均保留；它们提供V3知识/台账检查。V5使用独立版本标记的计划/批准表，旧schema通过不能替代新的hash/live-chain guard。具体整合见docs/51_PREPRODUCTION_INTEGRATION_V5.md。

### FID1 feedback transactions (R1–R4)
`fid1_qa_report.py record-review` now reads one feedback/QA byte snapshot and reports `feedback_sha256` / `qa_sha256` in dry-run. Bind the reviewed preview when applying actual Jovi feedback:
```powershell
python scripts/fid1_qa_report.py record-review --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --feedback local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json
python scripts/fid1_qa_report.py record-review --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09 --feedback local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json --expected-feedback-sha256 <preview-feedback-sha> --expected-qa-sha256 <preview-qa-sha> --apply
```
The job review lock is exclusive and ownership checked. Interrupted publication preserves evidence and `qa/.fid1-review-recovery.json`; lock/recovery markers close predecessor admission. Inspect saved bytes and actual writer status before any manual recovery; never delete markers or replay approval automatically. Hash pins are byte bindings, not reviewer authentication.
New schema-2 FID1 jobs require `local/production/T1_SOURCE_PILOT/video/<shot>/jobs/takeNN`. Original non-FID1 preparation and completed historical jobs remain separate. New review sessions generate derived sheets labeled actual source frame numbers and times (49/24: 1/25/49 = 0/1/2 seconds). Historical QA/media are not rewritten. Review choices remain empty after playback.
