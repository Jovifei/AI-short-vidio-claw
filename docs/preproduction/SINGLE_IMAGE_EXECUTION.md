# 独立单图执行层｜S0阶段交付

日期：2026-10-07。该层不改变V2/V3/V5路线，不替换Wan，不是另一套媒体导入工具。

## 本轮实际问题

本轮请求了单人楼道关键帧与单图背景编辑，图像工具仍返回1536×1024等横向设定拼贴。此结果不能作为独立关键帧。备用HeyGen单图创建返回403（需要付费计划），没有升级账户，没有生成付费视频。不能用反复发送同一大上下文来掩盖这个阻塞。

本轮**合格新独立关键帧=0**。以下交付是完成的执行层与真实输入准备，不是宣称完成出图。

## S0现在已经做完

新增 `scripts/remote_image_packets.py` 和 `config/remote_image_jobs.json`，从现有两份V5计划生成42个互相隔离的单图请求：

|类型|数量|说明|
|---|---:|---|
|服装与状态|9|悟空DAILY/HOME/FORMAL，黛玉OUTDOOR/HOME/RAIN，左手浅伤/包扎，悟空雨湿状态|
|EP001关键帧|20|逐镜保留production_plan_v5原字段，不改1440帧时间线|
|LOOKREEL独立镜头|9|保持648帧计划，不把REFBATCH02序号误当COMP序号|
|COMP10子画面|4|四个独立画面分别生成，之后CPU排成一张四格；四格不送I2V|

42是**请求数**，产品镜头仍30，不是42张已完成图片。

四张真实V5裁片（两个人脸、两套已有服装）进入inputs，核对现有registry的SHA256。它们只保留已有方向认可，不补写用户批准；低分辨率裁片不冒充新高清定妆。整张项目板不作为出图输入。悟空FORMAL裁片只给FORMAL任务，不充当DAILY/HOME。

## 依赖关系

最先可发的三个请求：`WARD_W_DAILY`、`WARD_W_FORMAL`、`WARD_D_OUTDOOR`。

完成日常装后才能做居家装；有居家装后制作左手浅伤；再制作相同手位的包扎状态。剧情镜头按实际出现的服装和伤手状态引用这些真实结果。没有结果，request返回missing_outputs，并且prompt=null、reference_images=[]，不发送占位路径。

角色先做定妆、再做镜头候选，不再出现“先要获批镜头才能生成定妆”的循环。远端视觉QA通过仅允许它作为下游候选参考，**不会**令V5用户批准或生产视频Gate通过。

## 工具用法

已有原17项素材并核实hash后，可重建任务包：

```powershell
python scripts/remote_image_packets.py build --out local/remote_packets/BATCH01
python scripts/remote_image_packets.py request --packet local/remote_packets/BATCH01 --task WARD_W_DAILY
```

这些命令只生成单图请求，不联网、不用GPU、不下载模型。当前执行负责人仍为远端，不要求本地Codex补画这些图。

请求交给出图服务时，仅发送本张prompt与reference_images对应的真实图，不发送INDEX、完整项目文档、script.md或整集shot cards。具体服务参数必须通过该服务实际接口映射，不能把此JSON当任何提供商API的现成契约。

## 成图验收

实际图保存为 `outputs/<TASK_ID>.png`。技术检查要求单帧、短边至少720、竖幅比接近9:16、能解码。自动检测仅判断尺寸/比例等，不声称能自动判定人脸一致或检测所有拼贴。

远端必须实际看图，再写绑定图hash的QA：single_scene、identity_matches_direction、costume_matches_task、anatomy_and_continuity、no_text_or_watermark。需要reviewer和method；测试里的合成图片/测试QA不能当真实通过。

```powershell
python scripts/remote_image_packets.py inspect --packet local/remote_packets/BATCH01 --task WARD_W_DAILY --image outputs/WARD_W_DAILY.png --qa qa/WARD_W_DAILY.json
```

inspect不会写原registry、两份approval_manifest或任何USER_APPROVED；只记录REMOTE_QA_CANDIDATE。依赖结果、输入hash、任务定义变化会使旧结果失效。

COMP10四张子画面齐全后：

```powershell
python scripts/remote_image_packets.py assemble-comp10 --packet local/remote_packets/BATCH01
```

它是明确的CPU四格排版，拒绝四格重复同一张图，输出依然是候选、不可送I2V。

## 测试与交付

助手容器Python 3.13.5/Pillow 12.3.0：新增28项测试通过，原V5 53项回归通过。测试涵盖完整42任务DAG、三张起始任务、缺父图拦截、伤手阶段、FORMAL不代替DAILY、单人不索取第二角色、横板/低清拒收、源文件篡改、谱系变化、四格确定性合成和不写用户批准。

本轮实际构建包含42个task.json、42个独立prompt、4张真实裁片、索引和测试记录。该包是远端出图执行包，不取代此前26项实体来源包，不新增用户本机接收器。

## 尚未完成与下一阶段

S0_EXECUTION_ISOLATION：完成并测试。
S1_WARDROBE_AND_STATE_IMAGES：0/9合格新图，仍远端负责。
S2_LOOKREEL_AND_EP001_IMAGES：0/30新计划精确关键帧，仍远端负责。
S3_MEDIA_ACCEPTANCE_AND_HANDOFF：未满足，不交给本地冒充只剩GPU。

当前需要的是一个能真正按单张参考编辑请求工作的出图通道；这不是用户原图重新上传问题，也不是4070S问题。找到可接入的参考图编辑服务后先做三个起始任务，验证实物再扩展，不能仅依据该文档把production_ready改为true。
