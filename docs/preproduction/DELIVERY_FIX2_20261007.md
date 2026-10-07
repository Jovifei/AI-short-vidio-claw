# 实体素材交付 FIX2｜2026-10-07

## 本轮边界

本轮继续解决“清单在Git、真实图没到本机”的交付故障。不是换路线，不是宣布30镜已完成。

**使用本次实际提供的 `AI_short_drama_MEDIA_HANDOFF_FIX2.zip`，不要使用上一条空答复中没有实际交到用户的旧包名/旧hash。** 本说明取代旧MEDIA_RECOVERY的接收入口；旧脚本和测试保留为历史，不拿旧脚本接收本ZIP。

## 实物

ZIP：65,965,628 bytes。

SHA256：`e7c90d0d5885445eb650cfefdeb1512cfc316a706b896dbf0cdad3ffe5189f6a`

包内 `MEDIA_MANIFEST.json` SHA256：`b39e2546ba2af81cefa9a1c751271b322c7294db4857b406a5ace6ce1bb193ed`

32个PNG文件，32个不同的内容hash：

- 原V5 17项，逐字节保持registry中的hash，包括3张设定板、10张REFBATCH02样图、4张原裁片。
- 10张旧古装构图来源，以LOOK_SOURCE_COMP01–COMP10编号。不是把最近REFBATCH02按序号错绑定到LOOKREEL。
- 1张手部接触上下文，整图是现代服装，禁止进入正式剧情。
- 4张确定性裁片选项，保留父图、裁框和限制。没有用放大或补造角度冒充定妆。

这些是已有原件恢复与裁切，不是32张新生成图片，不是获批关键帧。

## 审核入口

ZIP内 `REVIEW.html` 内嵌32项预览，展示每项限制、尺寸和来源；可以逐项选择。默认未审核，不联网。

`LOOKREEL_sources_review_FIX2.mp4` 为10张来源的27秒静态审片，720×1280/24fps/648帧；画面标注SOURCE REVIEW - NOT PRODUCTION。不是Wan输出，不是正式Look Reel。

`SHOT_GAPS.json` 有LOOKREEL01十镜和EP001二十镜的逐项缺口，携带现有V5计划字段。来源与正式镜头不是同一资产状态。

## 本地接收

保存ZIP，例如 `E:/incoming/AI_short_drama_MEDIA_HANDOFF_FIX2.zip`。保留本地未提交修改，不运行reset/clean。

```powershell
python scripts/receive_delivery_fix2.py --root . --bundle E:/incoming/AI_short_drama_MEDIA_HANDOFF_FIX2.zip
python scripts/receive_delivery_fix2.py --root . --bundle E:/incoming/AI_short_drama_MEDIA_HANDOFF_FIX2.zip --apply
python scripts/receive_delivery_fix2.py --root . --check
```

第一条dry-run，第二条写local，第三条复核。标准库脚本；不安装模型、不启动服务、不动GPU。

包内也有同一脚本 `RECEIVE_MEDIA.py`，尚未拉到新代码时可在解压目录用它，并把 `--root` 指向已有V5项目。

原17项去 `local/references/generated/20261005_v5/`；其余去 `local/references/media_handoff_fix2_20261007/`。

收据为 `local/delivery/fix2/RECEIPT.json`。首次32项导入；重复运行应0项新增、32项already_present。

写入前先验证全部源文件和本地冲突；不覆盖不同内容；拒绝路径穿越、链接、Windows保留名称和重复ZIP项。同卷硬链接原子发布适用于NTFS/POSIX；不支持时停止，不悄悄降低为覆盖写入。

**Git提交只有代码/说明，PNG在对话ZIP中。git pull不等于媒体传输。** 本轮未上传到GitHub Release或公开仓库，不能让本地Agent假设远端有一个可下载的Release URL。

## 参考反馈

用户导出 `MEDIA_REVIEW_FIX2.json` 后：

```powershell
python scripts/apply_delivery_feedback_fix2.py --root . --feedback E:/incoming/MEDIA_REVIEW_FIX2.json
```

预览后，只有确实发生用户逐项选择，才可加 `--apply`。仅原4张符合V5角色/face或costume角色的裁片能授予参考批准；其他来源仅记录意见。不会批准任何关键帧、LoRA、三维模型或完整定妆，不改30镜批准表。

反馈JSON是审计记录，不是防伪数字签名。对曾批准资产又选择不采用会要求先显式撤销/解决冲突，不静默忽略。

## 本轮验证

在助手容器Python 3.13.5运行：既有V5 53项 + 新接收16项 + 新反馈9项 = **78项离线测试通过**。这是本轮运行的子集，不宣称重跑了上一PR全部80项。

另在独立测试目录实际导入本ZIP32项，重复导入32项跳过，check32项通过；所有PNG打开、尺寸与hash一致；原registry和两份批准JSON前后hash不变。

两个V5计划仍 `contract_ok=true`、`ready=[]`、`production_ready=false`。这是如实保留，不是导入故障。

Chromium测试32卡片、默认未审核、4个参考批准选项及只导出参考选择通过；容器file URL导航受限，测试用内嵌HTML加载，未宣称测试Windows浏览器策略。

27秒来源审片通过ffprobe核验。以上没有测试用户电脑ComfyUI/GPU、81帧I2V质量或正式成片。

## 仍由远端承担的未完成项

- EP001 SH001–SH020：精确对应当前60秒计划的独立关键帧仍未完成。
- LOOKREEL01：来源图仍需处理服装阶段、乐器、镜像、遮挡、人物一致性差异。
- 独立HOME/雨天/受伤等定妆与状态图仍未完整。

本轮独立出图尝试未达到格式要求，未计入完成。不会拿设定大板缩略图裁成20张凑数，也不把“还没产出图”转写为“用户没批准”。这些事项保持REMOTE_PREPARATION，不交给本地假装只剩GPU。

当前安全可执行动作是媒体接收、参考审核、合同检查，不是正式开拍。
