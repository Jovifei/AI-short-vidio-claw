# 本地开拍执行书｜唯一操作入口补充（2026-10-07）

适用：Windows / RTX 4070 Super 12GB / 约32GB RAM；沿用现有ComfyUI、Wan2.2-TI2V-5B、V5计划。本文补齐操作，不另起V6/V7路线，不改已批准作品定义。

## 0. 先回答“现在能不能开拍”

**能接收、盘点和准备本地环境；不能把当前仓库状态当作可以批量开拍。**

三个问题必须分开：

| 问题 | 判据 | 当前已知 |
|---|---|---|
| 有方案吗？ | V5两集计划和离线测试 | 有；LOOKREEL01=27秒/648帧，EP001=60秒/1440帧 |
| 有三张可试拍输入吗？ | 三张具体获批、文件hash有效、相应服装引用有效的I2V关键帧 | 尚无已验证通过的三张 |
| 整集素材齐吗？ | **每一镜，包括静态镜头**，都有真实获批关键帧 | 尚未齐 |

`OpenArt COMPLETED`只表示一条出图任务结束，不表示原图收到、人物像、无水印或获批。OA001实际返回中心有大水印的预览，不能替代30镜，详见`OA001_REVIEW.md`。

制作缺口仍由远端负责：9套/状态独立图片任务及两集逐镜图，详见`remote_image_packets.py`的42个独立任务与`tasks/remote_image_phase_status.json`。42是请求数，不是出图数。不要把未完成图片交给本地说成“只剩GPU”；本地阶段可以提前接收，但渲染必须等输入。

## 1. 图像通道：ChatGPT Images默认，Nano Banana可选

ChatGPT Images能新建和编辑上传图片，因此满足本项目“参考图→静帧候选”的通道要求。使用单镜请求和少量真实参考，不把整个项目说明、角色大板、文件目录或进度表发给出图模型。每次输出一张连续画面；先查人脸、古装和肢体，再查氛围。

之前Nano Banana只是为排查反复输出拼贴板而做的单图试验；没有同输入A/B证据证明它比ChatGPT更适合本项目。现改为`config/image_channel_policy.json`：ChatGPT原生优先；OpenArt不自动继续收费、不自动换模型、失败不自动重试。

区分三个产品：ChatGPT网页图片、OpenAI图像API、OpenArt上的图像模型。前者不是后两者的通用API凭证；OpenAI API与ChatGPT订阅分开计费。当地Codex能否直接调某个图片工具，以它实际工具列表和登录状态为准，不能从“装了Codex”推导出已获得图像API。

官方资料（2026-10-07核对）：
- https://help.openai.com/en/articles/11084440-images-in-chatgpt
- https://developers.openai.com/api/docs/guides/image-generation
- https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform

以上支持功能与计费区别；“单镜隔离、先脸后动作”是本项目制作决策，不是官方对相似度的保证。

## 2. 远端交接应当提供的实物，不让本地补设计

一个批次必须有：真实PNG/JPEG/WebP原图、源参考ID及SHA256、逐镜文件清单、对应计划版本、人物/服装/左手伤口等可见状态审核、使用限制和未通过项。不能交缩略图链接当原图，不能把16宫格裁成16张新完成镜头。

远端自己的构图/服装/解剖QA可以标为REMOTE_QA_PASS；用户是否接受人物是另一条明确反馈。只缺用户判断时才写WAITING_USER_REVIEW；图尚未生成、未收到原字节或服装不对时，仍记REMOTE_ARTWORK_PENDING。

既有实体来源包仍是`AI_short_drama_MEDIA_READY.zip`，不是重新打包一个新版本：54,937,113 bytes，SHA256 `6259e103d41af94a3c984d6d47a62b65b70579ba7694bede2c338ad3ba3e6906`。它包含26项既有来源，不是30镜成品。Git保存索引，ZIP在对话附件，**git pull不传PNG**。

## 3. L0：安全接收代码与素材（不消耗GPU）

先在PowerShell打开仓库；所有示例为单行，避免把Bash续行复制到PowerShell。

```powershell
Set-Location E:/project/AI-short-vidio-claw
git status --short
git fetch origin
git pull --ff-only
git rev-parse HEAD
python --version
```

有未提交修改先保存；有冲突停止处理，不reset/clean、不覆盖Obsidian笔记。只在修改已保存、快进可行时pull。

把来源包解压，使README位于例如`E:/incoming/AI_short_drama_MEDIA_READY/README_RECEIVE.md`，然后：

```powershell
python scripts/import_reference_bundle.py --source-root E:/incoming/AI_short_drama_MEDIA_READY --repo-root . --registry assets/registry/received_sources_20261007.json
```

完整首收26项（已有项跳过）；第二次`imported=0, already_present=26, approvals_changed=0`。复用现有导入器，不同时跑旧FIX2/RECOVERY入口。接收registry不得替换生产批准registry。

输出位置：`local/references/generated/20261005_v5/`与`local/references/received_sources_20261007/`。新增合格图进入其真实登记路径，不移动后忘记更新hash。

## 4. L1：离线检查与缺口报告

工具只需Python和Pillow；ComfyUI保持原环境，不自动升级PyTorch/CUDA/驱动。Pillow已存在就不重复安装。

```powershell
python -m unittest discover -s tests -p "test_preproduction_v5.py" -v
python -m unittest discover -s tests -p "test_launch_readiness.py" -v
python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01
python scripts/validate_production_package.py --project-dir episodes/EP001
python scripts/launch_readiness.py --project all --out local/reports/launch_check_001.json
```

报告输出已存在就换新编号。`launch_readiness`默认只报告，缺图不阻止其它独立准备；加`--require t1-inputs`或`--require whole-project-inputs`才以退出码2拦截后续流程。

主要字段：
- `approved_files_not_received`：引用的获批文件还没到本机；不是用户没有审美意见。
- `shot_approvals_not_recorded`：此镜没有具体批准证据。
- `reference_files_missing_or_changed`：来源文件缺失/hash变化。
- `valid_i2v_input_shots`、`valid_still_input_shots`：分别检查。
- `t1_input_threshold_met`：至少三张I2V输入有效，**不是T1运行通过**。
- `whole_project_inputs_ready`：全部静/动态镜头输入有效，**不是成片验收通过**。

本轮修正旧validator的缺口：不能只因四个I2V镜头输入齐就报告十镜整集ready；静态镜头也要实际图和批准。

## 5. L2：参考与关键帧批准入账（不代签）

只对实际呈现且用户明确选择的图片操作。批准证据模板在`config/examples/approval_evidence_v5.template.json`，`subject_id/sha256/scope/user_quote/source/recorded_at`都需真实值。证据不是防伪数字签名，不能凭YES伪造意见。

```powershell
python scripts/approve_asset.py reference --root . --registry assets/registry/generated_assets_v5.json --id DAIYU_FACE_CROP --evidence local/review_evidence/DAIYU_FACE_CROP.json --user-confirmed YES
```

同理分别确认悟空脸、适用于该镜的真实服装。FORMAL不自动覆盖DAILY/HOME；雨湿和包扎状态不得凭空生成引用。新增来源先登记真实文件和角色用途，再批准。

关键帧路径：`local/production/LOOKREEL01/candidates/COMP09/`保存候选；用户具体确认的**原字节**复制到`local/production/LOOKREEL01/approved/LOOKREEL01_COMP09_KF_v001.png`。修改、裁切、转格式后hash变化，需重新按实际最终文件确认。

```powershell
python scripts/approve_asset.py keyframe --root . --plan episodes/LOOKREEL01/production_plan_v5.json --manifest episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --id COMP09 --image local/production/LOOKREEL01/approved/LOOKREEL01_COMP09_KF_v001.png --bindings config/examples/bindings_COMP09_v5.json --evidence local/review_evidence/COMP09.json --user-confirmed YES
```

此命令是条件式示例；当前示例bindings不是现成批准，不应复制执行后期待自动过关。远端交接对应批次时应提供真实bindings，不由本地猜。

## 6. L3：本地环境探活（只读），与图片工作可并行

```powershell
Get-Command ffmpeg
ffmpeg -version
nvidia-smi
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory
Get-Volume | Select-Object DriveLetter,SizeRemaining,Size
$ComfyUrl = 'http://127.0.0.1:8188'
Invoke-RestMethod "$ComfyUrl/system_stats"
Invoke-RestMethod "$ComfyUrl/queue"
Invoke-RestMethod "$ComfyUrl/object_info/UNETLoader"
Invoke-RestMethod "$ComfyUrl/object_info/CLIPLoader"
Invoke-RestMethod "$ComfyUrl/object_info/VAELoader"
```

8188必须与当前运行相符；无法探活时检查实际端口，不另起8189。只保留一套生成进程；停止其它GPU任务前先确认进程归属，不杀无关程序。

核对现有三文件名与ComfyUI菜单：`wan2.2_ti2v_5B_fp16.safetensors`、`wan2.2_vae.safetensors`、`umt5_xxl_fp8_e4m3fn_scaled.safetensors`。实际库可能为`F:/ComfyUI/models`，必须本地确认；不复制18GB模型到Git，不因文件不见就自动全量下载。

记录驱动、Comfy版本、GPU空闲、RAM空闲、磁盘、队列；本轮助手CPU/云端检查不能代替这些数值。

## 7. L4：T1试拍，不改27秒/60秒生产时间线

先得到三张合适的获批I2V输入。按本项目先考虑COMP09、COMP04、COMP05/COMP01，由实际合格图决定；不要以抱起/镜像/打闹作为首条。

```powershell
python scripts/launch_readiness.py --project LOOKREEL01 --require t1-inputs
```

退出码非0则不能继续。新增`prepare_t1_trial.py`复用V5原图/引用/连线检查，制作**T1_ONLY**副本，默认480×832和原计划参数，仅允许长度33/49/81；不更改生产计划、不变相批准图。

```powershell
python scripts/prepare_t1_trial.py --root . --project LOOKREEL01 --shot COMP09 --frames 49 --seed 2026100701 --out local/production/LOOKREEL01/video/COMP09/jobs/t1_49_s001
python scripts/submit_prepared.py --root . --job-dir local/production/LOOKREEL01/video/COMP09/jobs/t1_49_s001 --url http://127.0.0.1:8188
```

第二条仍是dry-run。确认队列空、输入正确、该次GPU试拍获得执行许可后：

```powershell
python scripts/submit_prepared.py --root . --job-dir local/production/LOOKREEL01/video/COMP09/jobs/t1_49_s001 --url http://127.0.0.1:8188 --execute
```

首条49帧稳定后，再用同一图81帧；OOM时先看日志和空闲资源，必要时33帧独立试验，不改主计划凑通过。每个新试验新目录，禁止覆盖或自动重投。

**49/24=2.0417秒，81/24=3.375秒。** 49帧试验不能直接占用计划里3秒的镜头，更不能冒充5秒。`T1_ONLY`默认`eligible_for_final_cut=false`；正式片使用原计划prepare出的足长任务和实际验收输出。

每条保存输入/工作流hash、seed、耗时、采样VRAM/RAM、prompt_id、真实输出位置；完整播放并检查首中尾：脸、古装、冠帽、左手、背景。三张至少两张可剪后，对最好低风险镜头串行3–5次；这才是本机生产候选验证。

有`submission_intent.json`但结果未知时先查ComfyUI history，禁止自动再次POST。内存失败不能推出“人物模型错”；身份连续漂移不能靠增加显存解决。

## 8. L5：正式LOOKREEL01，一条任务一份记录

完整Look Reel需要10/10关键帧，不只4个I2V。先检查：

```powershell
python scripts/launch_readiness.py --project LOOKREEL01 --require whole-project-inputs
python scripts/build_render_queue.py --root . --plan episodes/LOOKREEL01/production_plan_v5.json --approval episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --out local/production/LOOKREEL01/queue_001.json
```

V5正式I2V仍是COMP09、COMP04、COMP05、COMP01；其余六镜静态。每一镜都用对应实际`shot_id`和新任务目录，不把模板路径照抄为所有镜头：

```powershell
python scripts/preproduction.py prepare --root . --plan episodes/LOOKREEL01/production_plan_v5.json --approval episodes/LOOKREEL01/approval_manifest_v5.json --registry assets/registry/generated_assets_v5.json --workflow workflows/video/production/VID_wan22_5b_i2v_prod_v001.json --shot COMP09 --seed 2026100702 --out local/production/LOOKREEL01/video/COMP09/jobs/take01
python scripts/submit_prepared.py --root . --job-dir local/production/LOOKREEL01/video/COMP09/jobs/take01 --url http://127.0.0.1:8188
```

dry-run检查后再明确加`--execute`。一镜失败两次且属于系统性身份/接触错误，回同一获批静帧，不换脸，不重新套现代衣服，不购买14B云推理。

按计划648帧/24fps剪辑，参考声音/剪辑文件。静帧小幅推拉，不用花哨转场。输出`edit/review/LOOKREEL01_candidate_v001.mp4`；用户整体验收后才继续EP001，不把“来源审片27秒”当正式片。

## 9. L6：EP001正式制作

先齐20/20逐镜关键帧，静音顺序审查故事；`launch_readiness --project EP001 --require whole-project-inputs`通过后，沿用T1已经实测的生产参数。

当前V5正式I2V六镜：**SH002、SH006、SH007、SH009、SH013、SH017**。SH001、SH019等虽在旧创作稿里建议可动，当前执行计划仍为STILL；不能同时照旧稿和V5跑。当前1440帧/24fps=60秒。

左手背伤口→绷带贯穿；拿篮/拿伞用未伤右手；进屋与雨后换衣有连续性；片尾床边避开尖肩甲。三句台词先画外音，对口型不是首片条件。

声音资产实际存在后才合成；本轮没有授权声样就不声称已配音，不克隆演员声音。记录真实时长、字幕安全区、编码、音量、黑帧/缺镜、全片看图和听声结果。

## 10. 目录、批次报告与提交

```text
local/references/...                                  # 真实参考；Git存hash和用途
local/production/<PROJECT>/candidates/<SHOT>/         # 候选
local/production/<PROJECT>/approved/                  # 最终送入视频的获批字节
local/production/<PROJECT>/video/<SHOT>/jobs/<TAKE>/   # job/workflow/input/运行记录
local/production/<PROJECT>/video/<SHOT>/accepted/      # 实际验收后视频
local/production/<PROJECT>/audio/                     # dialogue/ambience/sfx/music/mix
local/production/<PROJECT>/edit/review/                # 候选成片
local/production/<PROJECT>/edit/final/                 # 用户最终验收版本
local/reports/                                       # 本机可追溯检查，不假装远端测试
```

每批提交文字台账、具体批准记录、prompt/workflow版本和小型审片索引；不提交权重/密钥/授权受限原图。报告分别给出：完成镜头ID、有效输入数、真实I2V成功数、视觉通过数、静态回退数、阻塞责任和下一项。不得用“跑了十次”替代“交付十镜”。

## 11. 开拍前完成定义与本次边界

我能提前完成的剧本、计划、依赖、命令、门禁、测试并不能代替仍缺的图。远端交接完成至少需要该批实物图、hash、bindings和可呈现审片；用户具体反馈不能伪造；本机T1/GPU测量只能在本机完成。

**截至本说明，完整远端素材尚未齐，不能写“所有开拍前工作完成”。本地先接收与检查，图片制作缺口继续由远端承担。** 不再要求本地重复写路线或自行寻找错配人物来填空。
