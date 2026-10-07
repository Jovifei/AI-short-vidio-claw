# 2026-10-07｜实体素材补交与交付状态纠正

审核依据：用户粘贴的两份本地 Codex 审计、远端 `92793fa`、对话中实际挂载的 V5 ZIP 和图片文件。未访问用户 E/F 盘或 Obsidian，不改变本地 GPU 环境。

## 结论

此前“远端能做的已经全部完成”的表述不准确。计划、脚本、参考图登记，不等于已经交付可开拍的30张关键帧。图没有到本机、服装参考不完整、逐镜图未完成，是不同的问题，不能全部写成“等待用户审批”。

本次补交是 **MEDIA_RECOVERY**，不是完整开拍包。`remote_complete=false`、`production_ready=false` 保持明确。

## 实物清单

包名：`AI_short_drama_media_recovery_20261007.zip`。

- 原V5 17项原件：3张设定板、10张样图、4张原裁片；逐字节hash与Git中的registry一致。
- 找回旧古装构图来源10张：对应LOOKREEL的十类构图，均标为SOURCE，不冒充精确符合计划的关键帧。有吉他/古典乐器、服装、亲密动作、遮脸等差异，已在每图说明中记录。
- 包扎道具来源1张：整体有现代服装，只能参考手部/道具，禁止整图进入正式剧情。
- 新的确定性裁片4张：日常古装选项、悟空居家装选项、黛玉居家装选项、手背包扎道具。记录父图hash和裁切框，没有伪造新角度或新定妆照。

共32个真实图片文件，约59 MB原始文件量。所有原件在ZIP的 `payload/local/...` 下。目录、大小、分辨率、SHA256、来源和限制在 `MEDIA_MANIFEST.json`。

**这些图片没有提交到公开Git仓库。Git只保存工具和说明。必须接收这一个ZIP；单独git pull仍然拿不到图片。** 对话附件路径也不是用户 E 盘路径。

## 本地一条命令导入

先保存ZIP，例如：`E:/incoming/AI_short_drama_media_recovery_20261007.zip`。保留现有未提交代码和Obsidian笔记，不执行reset/clean。

在已拉取本补丁的仓库根目录运行：

```powershell
python scripts/receive_media_v5.py --root . --bundle E:/incoming/AI_short_drama_media_recovery_20261007.zip --apply
python scripts/receive_media_v5.py --root . --check
```

纯Python标准库，不装模型、不启动服务、不使用GPU。工具校验固定交付manifest hash、32项源hash、仓库原17项registry，再写 `local/`。发现本地冲突即停止，不覆盖。可重复运行；第二次应报告 `already_present=32`。写入采用同卷硬链接原子发布，适合NTFS；文件系统不支持时停止，不静默采用不安全覆盖。

原17项恢复到：

`local/references/generated/20261005_v5/`

其他来源/选项进入：

`local/references/recovery_20261007/`

创建两集的 candidates/approved/video/audio/edit **目录**，但不会制造任何假关键帧。

收据：`local/delivery/RECEIPT_20261007.json`。它会同时显示 `materials_received=true` 和 `production_ready=false`，不能只摘前者汇报“可以开拍”。

## 审核不再要求手填JSON

包内 `REVIEW.html` 是可独立打开的本地审核页，内嵌压缩预览。默认全部未审核。只有原4张face/costume裁片提供明确“批准为参考”选项；其他图只记录保留/不用/修改意见，不越过逐镜批准。

用户导出 `MEDIA_FEEDBACK_20261007.json` 后：

```powershell
python scripts/apply_media_feedback_v5.py --root . --feedback E:/incoming/MEDIA_FEEDBACK_20261007.json
python scripts/apply_media_feedback_v5.py --root . --feedback E:/incoming/MEDIA_FEEDBACK_20261007.json --apply
```

第一条dry-run；第二条只记录真实选择的参考批准。不会批准关键帧，不会把HOME选项或雨天/受伤状态当成已完成。审核意见是审计记录，不是防伪数字签名。

## 仍未完成，负责人不是本地GPU

1. EP001 SH001–SH020，按当前60秒计划、古装、左手背绷带、雨伞和衣服连续性制作的20张精确剧情关键帧。
2. LOOKREEL01来源图与实际计划的差异修复、最终人物脸一致性审核；10张来源不等于10张完成图。
3. 独立的可用HOME等服装定妆，以及必要雨湿/包扎状态图。裁片只是选项。

本轮出图尝试没有得到合格独立镜头。未将不符合布局要求的设定大板裁成小格凑数，也未计入上述完成量。未完成项继续属于 **REMOTE_PREPARATION**，见 `tasks/remote_delivery_status_20261007.json`。

用户对具体图片的真实判断不能由Agent伪造，但“没有准备出图”也不能改写为“用户没签”。

## 保留原路线

V2产品路线、V3创作规则、V5执行合同均不变。Wan2.2-TI2V-5B、单ComfyUI、GPU串行、获批静帧先于I2V、三张合适获批图可局部T1，全部保留。不引入14B、另一视频平台、LoRA或三维模型前置。

## 本轮验证

容器Python 3.13.5：原V5 53项回归 + 接收工具18项 + 审核意见9项，共80项离线测试通过。另实际用真实ZIP做32项导入、重复导入和hash核查；原两份批准表保持DRAFT。Chromium通过32卡片DOM、默认未审核和只导出参考批准的逻辑测试；容器禁止file URL导航，因此未宣称验证用户Windows的文件打开策略。

以上不代表用户电脑I2V画质/显存/上传/输出已验证，更不代表30镜已完成。

## 工程包校验

ZIP字节数：64223971。

SHA256：`c558b4c3e209cd5711a4216b098a445433ae0c0c6a4218c37a6ff4a83b5b6428`。

包内MEDIA_MANIFEST原始文件SHA256：`18c4e0ca528254b052cfdc92763450e895aa7a74c598353be3b5241df0aa4fff`。接收脚本将该manifest hash固定校验，不接受同名的另一套素材。
