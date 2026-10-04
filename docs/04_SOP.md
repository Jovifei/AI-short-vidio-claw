# 04 AI 短剧标准生产 SOP（阶段门控版）

## 总原则

**每一步都有输入、输出、质量门。未通过上一质量门，不进入下一步。**
本 SOP 描述最终完整生产方式，但当前执行阶段必须服从 PROJECT_STATE 和 docs/stages。

当前特殊约束：
- P1：只验证视频 baseline，不做身份/TTS/LipSync。
- P2：先解决双身份关键帧。
- P3 v0.1：20 张关键帧 + 6 个低风险动态镜头 + 画外音，不做 LipSync。
- P5 才正式接入 GPT-SoVITS/MuseTalk。

## S0 立项

输入：一句话 idea。

输出：
- episode brief
- 时长
- 核心情绪
- 一句话冲突
- 结尾钩子
- 角色 stage

Gate：
- 一集只讲一个核心事件
- 10–20 镜可表达
- 复杂动作不是主体

## S1 剧本

输出 script.md。

要求：
- 场景尽量 2–5 个
- 每场有因果
- 对白短
- 动作承担主要情绪表达
- 每 3–8 秒有可见变化

## S2 视觉设定

输出 visual_design.md。

必须写：
- 角色固定特征
- 当前 stage
- 场景布局
- 核心道具
- continuity lock
- 本集允许变化的状态

禁止：
- “唯美、好看”替代可见事实
- 用演员名字代替人物设计
- 直接复制具体影视造型

## S3 分镜

输出 storyboard.md。

每镜包含：
- SHOT-ID
- purpose
- duration
- shot size
- camera
- start state
- main action
- secondary action
- end state
- characters
- props
- continuity refs
- frozen keyframe

原则：
**一镜一个主要动作。**

## S4 关键帧

视频不能跳过 keyframe approval。

### Hero Lane
适用：
- 双人接触
- 手部高风险
- 关键情绪
- identity 必须精确

可以使用 ChatGPT/人工精修。

### Local Lane
P2 之后再根据本机 identity benchmark 选择。

### Gate
至少检查：
- identity
- face design
- anatomy
- costume
- prop
- spatial continuity
- composition

Approved 后视频模型不得重新设计人物。

## S5 图生视频

### P1A
只用一张测试关键帧验证 Wan2.2-TI2V-5B runtime。

### 正式生产
每镜只要求：
- 一个主要动作
- 一个次级微动作
- 简洁运镜

高风险动作允许直接保留静态。

## S6 视频 QC

检查：
- start frame
- identity
- limb
- props
- background
- motion completion
- end state

失败写 reason code。

## S7 语音

**P5 才进入正式主线。**

角色 voice map 跨集复用。
只使用有权利的声音。

P3 First Cut 可使用授权临时声音/人工录音作为画外音。

## S8 口型

**P3 v0.1 禁用。P5 才测试。**

MuseTalk eligibility：
- 标准人脸
- 嘴部可见
- 遮挡少
- 镜头稳定

孙悟空单独 benchmark。

失败时允许：
- 画外音
- 侧脸
- 反打
而不是强行修嘴。

## S9 声音设计

轨道：
1. dialogue
2. ambience
3. sfx
4. bgm

生活感环境声优先：
雨、冰箱、菜市场、碗筷、水、公交、风、衣料。

## S10 剪辑

edit_plan.md：
- shot order
- in/out
- dialogue
- transition
- sfx
- subtitle
- audio level

FFmpeg/ffprobe 为可复现后端。

## S11 最终 QC

技术：
- resolution
- fps
- duration
- tracks
- black frame
- silence
- subtitle bounds
- missing shot
- manifest

视觉：
- identity
- continuity
- abnormal frames
- lip sync（如启用）

人工：
- 节奏
- 情绪
- CP 感
- 是否像“生活中的人”而非摆拍海报

## S12 归档

交付：
- final.mp4
- cover
- caption
- qa_report
- manifest
- model/workflow versions

Git 只保存文本、小配置和必要的小型参考资产。
