# V5｜事实来源、外部复核与未完成事项

检查日期：2026-10-06。这里不把上游宣传、历史本机数据和本轮验证混在一起。

## 仓库事实

基线commit：`f3d9d3b59525efff372f3d60d3982ff2b09a545b`。

- 原guard：`scripts/production_guard.py`，blob `46d13982b6a50ef809a5836a796ee68183c52dd2`。
- 原队列：`scripts/build_render_queue.py`，blob `b10db2c5f89d044632cb97e37c03412b38642848`。
- 原批准工具：`scripts/approve_asset.py`，blob `b8f919565ab29edfb134b795dfd0aa25aecff55f`。
- 原工作流：`workflows/video/production/VID_wan22_5b_i2v_prod_v001.json`，blob `c860ed4463238989a3e29f41f09c8004a6775b42`。保留未改。
- 历史T2V/I2V和32GB机器数据：`docs/reviews/2026-10-05-远端审核.md`、`docs/benchmarks/P1_4070S_BASELINE.md`。本轮没有复测用户机器。

## 外部官方资料

### ComfyUI Wan2.2原生说明

https://docs.comfy.org/tutorials/video/wan/wan2_2

使用点：区分5B与14B；5B图生路径必须启用LoadImage；三份权重分别放diffusion_models、vae、text_encoders。教程的低显存说明不是本轮实际分辨率/帧数的测量。

### ComfyUI Server Routes

https://docs.comfy.org/development/comfyui-server/comms_routes

使用点：POST `/prompt` 返回prompt_id/队列信息；GET `/history/{prompt_id}`核对任务；`/upload/image`上传本地输入；`/queue`只用于状态读取与已有probe校验。本轮新工具不请求清空队列、不自动中断别人的任务。

### FFmpeg Filters

https://ffmpeg.org/ffmpeg-filters.html

使用点：fps、静帧/视频尺度与后期拼接。CPU审片使用FFmpeg concat demuxer、fps过滤器和libx264；它不创造角色动作，不属于I2V。

### FFmpeg命令与版本边界

https://ffmpeg.org/ffmpeg.html
https://ffmpeg.org/documentation.html

官方在线文档对应较新的版本；是否具有指定编码器/滤镜以本机`ffmpeg -version`和实际执行为准。本轮容器CPU审片成功，不表示Windows上所有后期命令都已验过。

## 不是本轮已经验证的内容

- 图中原著文字、具体影视版本、人物眼皮类型的文学考证。
- 已训练LoRA、三维mesh、rig、UV、可复用衣料仿真。
- 用户显卡上的新I2V质量或帧数上限。
- 用户本机此刻RAM/VRAM空闲量、端口是否仍为8188。
- 具体影视改编、演员形象、音乐/声音素材的发布授权。
- 新生成的30个剧情关键帧、口型或正式成片。

这些状态保持未验证/待制作。前期数据齐全与生产完成是不同里程碑。
