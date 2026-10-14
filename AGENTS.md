# AGENTS — V5执行与真实图片交接

## Git 提交与版本（Jovi 2026-10-14 指令）

以后所有 Commit 使用中文；需要双语时中文在前、英文在后。维护 VERSION.json 和 CHANGELOG.md，用不可变版本标签关联固定实现提交，计划 SHA 与实现 SHA 分开记录。复审后的补修发布下一补丁版，不移动已有标签。工程版本不授予真实审片接受或正式生产批准。

## 最新入口及有界授权

FID2并行计划以固定计划`b37edc51236cf0b340401c0141a2e7687f5b394b`的`docs/preproduction/FID1_FID2_PLAN_COLLISION_RECONCILIATION_20261015.md`为唯一新合同。V006/schema4/v2已运行take10，V007/schema5/v3只保留时间候选工程；V008/schema6/v4为独立逐ROI强度工程，不能混用身份。真实源图叠层发现V008预注册背景ROI穿过长翎，当前`GEOMETRY_BLOCKED`，不改框、不准备真实take14、不部署或GPU。旧两份计划原样保留，只读历史。take09保持Jovi真实CHANGES_REQUIRED，take10人审PENDING，下游SH901/902关闭。

v0.2.1将schema6几何停止点落入prepare/submit代码：必须有`config/source_fidelity_trials/geometry_manifest.json`绑定profile原始字节、源图、ROI、几何JSON与叠层哈希；缺失/未知/阻塞/漂移失败关闭。`LOCAL_GEOMETRY_PASS`只表示输入几何检查，不是Jovi视频接受；`SYNTHETIC_FIXTURE`不能用于真实执行。新候选必须使用独立版本身份并真实复核，不通过改写V008记录解除本次阻塞。

最新纠正合同为`71ba6cb939c1e8fd5e468398f375008209ac0a51`的`docs/preproduction/FID1_V008_GEOMETRY_INDEPENDENT_REVIEW_AND_V009_CORRECTION_20261015.md`。它接受v0.2.0工程、拒收V008几何，允许找不到安全背景区时失败停止。本轮原图/49帧检查返回`NO_SAFE_BACKGROUND_ROI`，记录在`docs/reviews/20261015-fid1-v009-geometry/`；不创建V009、take15，不擅自删第三ROI或猜框。任何新GPU仍需另行明确授权和现场全部门禁。

用户明确要求把缺失图片直接提交Git。本次`assets/media/source_library/`32项既有生成原件/裁片入库，这是旧“媒体不进Git”的有界例外。不要再要求用户寻找旧ZIP、OpenArt账号或CDN链接。大模型、密钥、第三方原始截图、批量成片仍不提交。

先读START_HERE_LOCAL → docs/preproduction/GIT_MEDIA_HANDOFF → 当前PROJECT_STATE。正式生产流程仍读51号整合、30_PREPRODUCTION_V5_EXECUTION和LOCAL_SHOOTING_RUNBOOK；V3创作30–50号文件继续有效，不把source小样改成新剧本。

## 当前事实

- `assets/media/git_media_manifest.json`：实际32PNG、Git/local路径/hash。
- 原registry：`assets/registry/generated_assets_v5.json`；原30镜各集production_plan_v5和approval_manifest_v5是正式事实源。
- `episodes/T1_SOURCE_PILOT/`仅是3张现有源图的同源保真诊断，不是EP001或LOOKREEL替代，不直接授予原产品T1通过。
- 未完成精确剧情关键帧及独立服装状态仍由远端承担，不转嫁本地猜图。

## 不可越过

1. 原17项hash保持。sync_repo_media离线预检、复制、幂等，不覆盖冲突，不改批准。
2. Source≠keyframe，图片存在≠用户批准，runtime成功≠visual接受。
3. 不把“感觉可以”的方向认可扩展成所有图批准；不虚构quote，不用单元测试fixture当用户意见。
4. 二维设定板/ROI不能称为三维模型、已训LoRA或独立服装定妆。源图服装stage不互换成EP001 HOME/RAIN。
5. 主角正式镜头Image First→Video Second，不允许随机SDXL或无图T2V冒充角色生产。
6. 原LOOKREEL/EP001计划和批准不因source小样修改。source结果不可冒名SH001/COMP09进入成片。
7. source_pilot review默认不勾；用户主动导出具体反馈后才apply。批准只写独立local快照；三卡均获批后prepare。
8. prepare不提交；submit默认dry-run，明确--execute才运行。GPU并发1；状态未知先查history，不重复POST。
9. M0/M3不自动I2V；保真小样固定M1、49帧/24fps，不夸大为3–5秒正式素材。
10. 只检查实际出场角色；ref必须正确角色/用途/stage、hash有效。既有V5 guard不得绕过。
11. 已有job目录不覆盖；源图、计划、workflow或审批变更重新prepare。旧任务hash漂移必须停止。
12. 视频仍是单ComfyUI Wan2.2-TI2V-5B，不自动装14B、新runner或训练LoRA；新图默认ChatGPT Images，不自动消费第三方积分。

## 本地目录

Git原图`assets/media/source_library/`；运行副本`local/references/`；各项目`local/production/<ID>/`包含candidates、approved、video/<SHOT>/jobs/takeNN、audio、edit/review与final。

T1_SOURCE_PILOT的review.html、current_review.json、reviews/<hash>/与trial视频均与原剧集分开。

## 报告与Git

分别报告：contract_ok、media_received、reference_approved、keyframe_approved、runtime_success、visual_accepted、final_approved。不得相互替代，不把CPU测试当用户GPU测试。

保留本地未提交修改和Obsidian笔记，不reset/clean。新代码先测试；具体批准如实记录。回传文件、SHA、QA、实际WBS/Gate与缺口，禁止“全完成”的泛化表述。
