# 真实图片入库与本地交接

本轮解决“方案在Git、PNG在聊天附件，本地一直收不到”的故障。用户明确要求直接提交仓库，本次为这批已生成素材建立有界的Git图片库；不继续要求下载旧ZIP或登录OpenArt。

## 实物与边界

`assets/media/source_library/`包含32个真实PNG，共54,044,452字节：原V5登记的17项原件、9张旧情侣构图来源、6张新的确定性服装细节裁片。原17项保持字节、SHA256及旧registry目标路径。没有新出图计费，没有把裁片叫作独立定妆。

`assets/media/git_media_manifest.json`逐文件记录Git位置、local位置、大小和hash。图片是Git blob，不是LFS指针、URL占位、过期Action附件或仅登记文件名。父图/裁框在bootstrap配置和试拍reference registry中保留。

**EP001精确20张剧情关键帧仍未制作完成，LOOKREEL来源与计划仍有差异。** 本轮没有改变那30镜的计划与批准，也没有把待制作转成“只等用户签字”。这些图仍由远端负责。

## 1. 代码和图片一起接收（现在执行）

在`E:/project/AI-short-vidio-claw`使用本机已有Python。先检查本地改动；保留/提交到本地分支或使用独立worktree，不reset/clean，不丢弃Obsidian笔记。

```powershell
Set-Location E:/project/AI-short-vidio-claw
git status --short
git fetch origin
git pull --ff-only
git rev-parse HEAD
python scripts/sync_repo_media.py
python scripts/sync_repo_media.py --apply
python scripts/sync_repo_media.py --check
```

首次32项复制；相同文件跳过；重复copied=0、already_present=32。第一条是dry-run。没有网络下载、生成任务或GPU使用。全体源/目标hash预检后才写入，冲突停下不覆盖。使用同卷硬链接原子发布，NTFS支持时可用，不支持则报告错误，不能靠覆盖写绕开。

Git原件：`assets/media/source_library/`。
本地副本：`local/references/generated/20261005_v5/`、`local/references/received_sources_20261007/`、`local/references/pilot_source_crops/`。
收据：`local/reports/git_media_receipt.json`。

**32项到位只表示接收修复，不表示30镜获批。** 导入不改原registry审批和两集批准表。

## 2. 三张具体可审核的源图保真小样

为避免继续用地铁Lab，也不伪造尚未完成的EP001镜头，增加独立诊断包`T1_SOURCE_PILOT`：

| 编号 | 完整源图 | 检验 | 限制 |
|---|---|---|---|
| SH901 | REFB02_02草坡相伴 | 双人微动时脸及黄灰、淡紫衣服 | 不起身、不转头 |
| SH902 | REFB02_06石阶休憩 | 前后层次、饰品及衣料 | 不移动托脸的手 |
| SH903 | REFB02_01山水牵手 | 红金装、淡紫衣裙及固定牵手轮廓 | 不松手、不迈步 |

三张均为941×1672的现有完整单场景源图；不是新生成图。每卡展示原图、两张脸参考及两张该源图服装ROI，用户需确认该试验是否接受这些具体外观。脸部裁片较小，不用于宣称高分辨率训练集完成。

本小样只验证“批准源图在49帧里是否保持住”。**不是新剧本，不替代LOOKREEL/EP001，不直接授予原生产T1通过，也不能让全镜0/30变成完成。** 结果单独记录。

```powershell
python scripts/source_pilot.py review
Start-Process local/production/T1_SOURCE_PILOT/review.html
```

默认没有勾选。用户满意才勾选并导出`T1_SOURCE_REVIEW.json`；不满意卡不能由Agent代勾。“感觉可以”的总体方向认可不自动扩展成这次具体审批。

## 3. 记录实际选择

将主动导出的文件放到`local/review_evidence/T1_SOURCE_REVIEW.json`：

```powershell
python scripts/source_pilot.py apply --feedback local/review_evidence/T1_SOURCE_REVIEW.json
python scripts/source_pilot.py apply --feedback local/review_evidence/T1_SOURCE_REVIEW.json --apply
```

第一条预览；第二条写入。仅修改`local/production/T1_SOURCE_PILOT/`内的独立审批快照和批准图，不影响原30镜。

`current_review.json`指向不可覆盖的review快照，绑定原图、参考、计划和真实选择。这不是防伪签名；必须真实展示且用户主动选择，不能把单元测试fixture当用户意见。

三卡没全部获批，仍可接收/审片，但prepare阻止这组三图试验。若用户要换图，回远端改候选，不改原剧本凑数。

## 4. 获批后离线准备，再本机串行试拍

先检查本机ComfyUI真实URL、队列、模型、空闲显存/RAM和磁盘。不升级14B，不开启第二个GPU服务。

每条49帧、24fps≈2.04秒，480×832、M1、固定镜头。不是3秒或5秒成片素材。沿用现有Wan2.2-TI2V-5B和probe。

```powershell
python scripts/source_pilot.py prepare --shot SH901 --seed 2026100801 --out local/production/T1_SOURCE_PILOT/video/SH901/jobs/take01
python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH901/jobs/take01 --url http://127.0.0.1:8188
```

第二条仍为dry-run。用户确认执行试验、队列为空、输入审批有效后，才在第二条加`--execute`。

SH901完成并实际看片后，再按相同命令处理SH902/SH903，各用独立目录与seed2026100802/2026100803。不能并发，也不能覆盖take01。要重做用take02；已提交但状态未知先查history，不自动重复POST。

任务`purpose=T1_SOURCE_ONLY`、`eligible_for_final_cut=false`；输出前缀`video/T1_SOURCE_ONLY/`。源图/计划/审批变化必须重新prepare，旧任务hash会阻止漂移。

## 5. 回传

每条保存真实输出路径、输入hash、workflow/model/seed、frames/fps、耗时、显存/RAM采样、首中尾截图及完整观看意见。换脸/多肢体要记录失败，不能以运行成功替代画质。固定姿势两次仍崩坏则暂停动态，保留同源静态。

回传检查摘要及run_record，不提交密钥、权重或TEST FIXTURE审批。不把源图小样冒名成SH001/COMP09。

## 6. 验证

助手CPU环境Python3.13.5/Pillow12.3.0：原V5 53项、已有launch31项及新增媒体/试拍回归。精确数量与CI见`tasks/git_media_delivery_status.json`及PR checks。

实际32项首次导入、重复跳过、hash核查通过。隔离临时目录用明确TEST FIXTURE审批验证三条prepare，未提交ComfyUI，fixture丢弃，原registry和30镜批准文件hash未改。这些不是用户Windows/GPU验收。

## 7. 仍缺的远端制作

- LOOKREEL：服装/身份、古典乐器、相机遮脸、镜像与四格等来源修订。
- EP001：对应左手背伤口/包扎、服装和雨天连续性的20张独立剧情关键帧。
- 独立无水印HOME/RAIN/受伤状态参考；当前6个ROI不替代这些。

不把上述缺口推给本地重新编剧、猜脸、补画，却宣称只剩显卡。
