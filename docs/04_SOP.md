# 04 AI 短剧标准生产 SOP

## SOP 总原则

**每一步都有输入、输出、质量门。未通过上一质量门，不进入下一步。**

## S0 立项

输入：一句话 idea。

输出：
- episode brief；
- 时长；
- 核心情绪；
- 一句话冲突；
- 结尾钩子；
- 角色 stage。

质量门：
- 一集只讲一个核心事件；
- 能在 10–20 镜完成；
- 不依赖大量复杂动作。

## S1 剧本

输出 script.md。

要求：
- 场景数量尽量 2–5；
- 每场有因果；
- 对白短；
- 无对白动作承担至少一半情绪表达；
- 每 3–8 秒有可见变化。

## S2 视觉设定

输出 visual_design.md。

必须写：
- 角色固定特征；
- 当前 stage 服装；
- 场景固定布局；
- 核心道具；
- continuity lock；
- 本集可以变化的状态。

禁止：
- 用“好看、唯美”代替可见事实；
- 把演员名字当人物描述；
- 直接复制某影视造型。

## S3 正式分镜

输出 storyboard.md。

每镜只有一个主动作，格式至少包含：
- SHOT-ID；
- purpose；
- duration；
- shot size；
- camera；
- start state；
- main action；
- end state；
- characters；
- props；
- continuity refs；
- frozen keyframe description。

## S4 关键帧

先生成 keyframe，视频不能跳过这一步。

### Hero Lane
适用于：
- 双人接触；
- 手部交互；
- 人物脸必须极准；
- 关键海报镜头。

可以人工用 ChatGPT 网页生成/修图，然后保存至本项目 local 目录并记录来源。

### Local Lane
适用于：
- 单人；
- 日常动作；
- 中远景；
- 批量过场；
- 已稳定的角色 LoRA。

### Keyframe Gate
至少检查：
- 身份；
- 脸型；
- 身高差；
- 手指；
- 服装；
- 道具；
- 场景；
- 构图；
- 与前后镜连续性。

通过后标记 APPROVED，不再让视频模型“重新设计人物”。

## S5 图生视频

默认 native ComfyUI + Wan2.2。

一个镜头只要求：
- 一个主要动作；
- 一个次级微动作；
- 简洁运镜。

例：
主要动作：黛玉给悟空缠绷带。
次级动作：悟空看她一眼。
运镜：极慢推近。

不要同一 4 秒要求“起身→走路→拥抱→转头→拿东西”。

每个 shot 最多先抽 2–3 take，进入 QC 后再决定是否继续。

## S6 视频 QC

检查：
- start frame 是否守住；
- 人物是否换脸；
- 新增/消失肢体；
- 道具是否穿帮；
- 背景是否融化；
- 动作是否完整；
- 结束姿态是否能接下一镜。

通过放 accepted/。
失败写 reason code，不只写“效果不好”。

## S7 语音

角色 voice map 跨集复用。

台词进入 GPT-SoVITS。
每句保存：
- character_id；
- voice_id；
- text；
- emotion；
- speed；
- output。

严禁克隆无授权真实演员声音作为正式资产。

## S8 口型

只有 eligibility=true 的镜头进入 MuseTalk：
- 标准人脸；
- 嘴部清晰；
- 遮挡少；
- 镜头稳定。

孙悟空默认不强制 MuseTalk。先做专项 benchmark。

## S9 声音设计

四类轨道：
1. dialogue
2. ambience
3. sfx
4. bgm

生活短剧环境声很重要：
- 雨声；
- 冰箱压缩机；
- 菜市场；
- 碗筷；
- 水龙头；
- 公交报站；
- 风；
- 衣物摩擦。

## S10 剪辑

edit_plan.md 写：
- shot order；
- in/out；
- 台词位置；
- 转场；
- 音效；
- 字幕；
- 音量目标。

用 FFmpeg/ffprobe 实现可重复渲染。

## S11 最终 QC

自动检查：
- 分辨率；
- fps；
- 时长；
- 音轨；
- 黑帧；
- 静音；
- 字幕越界；
- shot 缺失；
- manifest 完整。

视觉检查：
- 角色；
- 连续性；
- 画面异常；
- 口型。

人工最后确认故事节奏和情绪。

## S12 发布归档

最终包包含：
- final.mp4；
- cover；
- caption；
- qa_report；
- manifest；
- model/workflow versions。

只将文本事实和小型配置提交 Git；大媒体留 local/outputs。
