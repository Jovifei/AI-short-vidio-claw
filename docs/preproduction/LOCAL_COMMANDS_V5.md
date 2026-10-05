# V5｜本地接收命令与交付路径

以下在仓库根目录 `E:\project\AI-short-vidio-claw` 执行。使用现有已能运行ComfyUI/probe的Python环境，不要另装大模型。PowerShell中不要使用Bash的反斜线续行；下列均为单行。

## 0. 接收与检查，不覆盖个人修改

```powershell
git status --short
git pull --ff-only
python -m unittest discover -s tests -p "test_preproduction_v5.py" -v
python scripts/validate_production_package.py --project-dir episodes/EP001
python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01
```

有未提交修改时先保存，不执行reset/clean。`contract_ok=true`只说明计划结构可用；素材没有批准时`production_ready=false`是正确结果。

## 1. 导入本次真实素材包

把 `AI_short_drama_preproduction_v5.zip` 解压到例如 `E:\incoming\short_drama_v5`。其中有同名顶层目录 `preproduction_v5`。不要把里面的`local/`覆盖式复制到整个仓库。

```powershell
python scripts/import_reference_bundle.py --source-root E:/incoming/short_drama_v5/preproduction_v5 --repo-root .
```

源包和仓库registry各文件hash必须一致。工具先验全包再写文件；17项已存在且同hash时会全部跳过。原图实际进入 `local/references/generated/20261005_v5/`，仍被Git忽略。仓库保留的只是索引、hash和规则。

## 2. 确认参考，不再猜角色

阅读 `CHARACTER_ASSET_SPEC_V5.md`；使用实际资产ID。用户只认可整体方向时继续做编剧/静帧候选，不把所有refs改成APPROVED。

把真实的具体批准写到一个JSON，结构参考 `config/examples/approval_evidence_v5.template.json`。模板的null必须填成真实值；`user_quote`不能编造。

```powershell
python scripts/approve_asset.py reference --root . --registry assets/registry/generated_assets_v5.json --id DAIYU_FACE_CROP --evidence local/review_evidence/DAIYU_FACE_CROP.json --user-confirmed YES
```

同样分别处理悟空脸、对应服装图。设定大板/整张场景不能直接声明face role。要新增清晰参考，先复制到local、写registry角色/用途/hash，实际批准后再引用。

## 3. 关键帧生产与批准

每张按`director_cards_v5.md`准备输入；生成渠道可继续使用对话出图/人工编辑，不强制改为本地SDXL。

候选：`local/production/LOOKREEL01/candidates/COMP09/`。

批准输入：`local/production/LOOKREEL01/approved/LOOKREEL01_COMP09_KF_v001.png`。

格式改变、裁切、加字或重新压缩都会改变hash；最终批准的是实际送I2V的文件。绑定示例在`config/examples/bindings_COMP09_v5.json`；其中引用仍是候选ID，并不预先通过门禁。

```powershell
python scripts/approve_asset.py keyframe --root . --plan episodes/LOOKREEL01/production_plan_v5.json --manifest episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --id COMP09 --image local/production/LOOKREEL01/approved/LOOKREEL01_COMP09_KF_v001.png --bindings config/examples/bindings_COMP09_v5.json --evidence local/review_evidence/COMP09.json --user-confirmed YES
```

此命令没有任何参考时必须失败，而不是先写一个空的批准记录。

## 4. 建队列、guard与离线任务包

```powershell
python scripts/build_render_queue.py --root . --plan episodes/LOOKREEL01/production_plan_v5.json --approval episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --out local/production/LOOKREEL01/queue_v5.json
python scripts/production_guard.py --root . --plan episodes/LOOKREEL01/production_plan_v5.json --approval episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --workflow workflows/video/production/VID_wan22_5b_i2v_prod_v001.json --shot COMP09
python scripts/preproduction.py prepare --root . --plan episodes/LOOKREEL01/production_plan_v5.json --approval episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --workflow workflows/video/production/VID_wan22_5b_i2v_prod_v001.json --shot COMP09 --seed 2026100601 --out local/production/LOOKREEL01/video/COMP09/jobs/take01
```

这些都是离线步骤。队列报告将STILL与blocked分开；不会扫描同名文件碰运气。任务输出目录已存在时拒绝覆盖，下一次改为take02。

## 5. 本机提交，默认dry-run

先核对实际ComfyUI端口。历史8188不是这次自动保证。

```powershell
python scripts/submit_prepared.py --root . --job-dir local/production/LOOKREEL01/video/COMP09/jobs/take01 --url http://127.0.0.1:8188
```

这条只显示命令，不提交。准备好本机资源、允许运行该任务时，在同一命令末尾加`--execute`。它将调用已有`p1_comfy_probe.py`，保留该脚本原有资源采样与history记录。

不要手工用低层probe去绕过失败的guard。任务有submission_intent但结果未知时先查history；不会自动重投。

## 6. 输出、审核与静态回退

实际输出用run_record记录的路径，不用猜SaveVideo编号。保存首/中/尾抽帧与人工完整播放意见；记录左手绷带、服装、冠帽、脸漂移。不合格两次回到同一批准图静态处理，不换脸、不拉大模型。

各项目目录统一为：

```text
local/production/<PROJECT>/
  candidates/<SHOT>/
  approved/<PROJECT>_<SHOT>_KF_v001.png
  video/<SHOT>/jobs/take01/
  video/<SHOT>/accepted/
  audio/{dialogue,ambience,sfx,music,mix}/
  edit/{review,final}/
```

## 7. 本轮审片序列的再生成（不需要GPU）

```powershell
python scripts/render_reference_review.py --root . --group REFBATCH02 --out local/production/MODEL_REVIEW/REFBATCH02_review_v5.mp4
```

需要已有FFmpeg与Pillow。它永远带REFERENCE REVIEW标签，不进入正式EP001。现有视频是本轮已经生成的CPU审片结果；本机不必为了重现而重复跑。

## 8. 提交回仓库的材料

提交更新后的计划/审批索引、运行记录和审核说明。不要提交模型权重、密钥、未授权原图或几GB中间视频。需要远端看片时单独提供小型审片副本，明确LAB/REFERENCE_REVIEW/EPISODE_CANDIDATE类别。
