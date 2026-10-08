# PROJECT_STATE

**本轮：真实源图已直接进入Git；已有素材交接故障已修复；原30镜精确剧情图片制作仍未完成。**

## 实际交付

`assets/media/source_library/`32个PNG，54,044,452字节：原V5 17原件、9张旧构图来源、6张确定性服装ROI。原件hash与原registry一致。不是新生成32张，不是30镜已获批。用户明确要求直接提交仓库，本次有界图片库不再依赖聊天ZIP或第三方CDN登录。

本地入口`START_HERE_LOCAL.md` → `docs/preproduction/GIT_MEDIA_HANDOFF.md`。`sync_repo_media.py`离线复制、预检全包hash、不覆盖冲突、可重复运行，不改任何用户审批。

## 具体可审片的小样

`episodes/T1_SOURCE_PILOT/`已准备3张完整源图的明确绑定、当前衣料ROI和独立审批模板：SH901草坡、SH902石阶、SH903山水。每条49帧/24fps/480×832，固定姿势微动，使用已有5B。

这是可选同源保真诊断，不是更改故事/新视频引擎；不直接满足原LOOKREEL/EP001内容Gate。用户需具体批准每卡显示的原图及参考。代码只写独立local快照，任务标T1_SOURCE_ONLY和不可进入成片。

## 仍未完成及责任

EP00120张精确剧情关键帧、LOOKREEL来源差异修订、独立HOME/RAIN/受伤等状态图仍由REMOTE_IMAGE_PRODUCTION负责。没有以“等待用户批准”掩盖尚未产出，也不交给本地假装只剩GPU。原两集计划和批准表保持不变。

## 验证分层

真实32文件首次导入、重复跳过、hash核验已在助手CPU环境执行。旧V5和launch回归加新媒体/小样测试通过；数量见tasks/git_media_delivery_status.json和CI。

没有运行用户Windows显卡、没有训练LoRA、没有新图像积分消费、没有授予原30镜批准。测试fixture只在临时目录使用并丢弃。小样runtime/画质仍待实际运行。

## 不变路线

Identity First / Image First → Video Second；单ComfyUI、Wan2.2-TI2V-5B、GPU串行、明确prepare/dry-run/execute。ChatGPT Images仍是新静帧默认通道；本轮仅恢复已有生成图片并做确定性裁切，没有触发新付费生成。
