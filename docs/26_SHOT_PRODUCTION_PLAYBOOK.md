# 26 镜头生产详细执行手册（Shot Production Playbook）

日期：2026-10-05
状态：ACTIVE

## 1. 一个镜头不是一个 Prompt

每个镜头必须拆成以下生产对象：

1. Shot Card
2. Composition Reference
3. Identity Reference
4. Costume Stage
5. Prop/Continuity State
6. Keyframe Candidate
7. Keyframe QA
8. User Approval
9. Motion Tier
10. I2V Prompt
11. Video Take
12. Video QA
13. Accepted/Static Decision
14. Edit Placement
15. Manifest Record

缺任何中间状态，后续 Agent 不能靠猜。

## 2. Shot Card 必填字段

每个 Shot 至少有：

- shot_id
- title
- story_purpose
- location
- time_of_day
- weather
- characters
- identity_refs
- costume_stage
- body_position
- eye_line
- hand_state
- props
- continuity_in
- continuity_out
- composition
- camera_height
- camera_angle
- framing
- lens_feel
- depth_of_field
- light_direction
- color_temperature
- keyframe_frozen_moment
- motion_tier
- primary_motion
- secondary_motion
- camera_motion
- environment_motion
- target_duration
- risk_notes
- fallback
- approval_status

## 3. Keyframe 制作 SOP

### 3.1 读取输入

必须先读：
- active visual target
- 两位 character card
- stage yaml
- shot card
- composition ref
- continuity state

### 3.2 生成 Candidate

每轮建议 1–3 张，不要一次几十张。

每张 candidate 要写：
- candidate_id
- source channel
- generation date
- prompt revision
- input refs
- file hash

### 3.3 Face Gate

先裁脸查看。

DAIYU：
- 脸型
- 眼眉
- 下巴
- 古典气质

WUKONG：
- 猴脸结构
- 眉骨
- 吻部
- 耳形
- 毛发分区

Face Gate 失败：
直接退回，不继续看光线。

### 3.4 Costume Gate

检查：
- stage 是否匹配
- 花色/配色
- 发饰/头箍
- 护腕/腰带
- 是否混入现代衣服

失败：
局部 edit 或重新生成。

### 3.5 Anatomy Gate

重点检查：
- 手指
- 手腕
- 双人接触
- 脚
- 镜像
- 道具握持

### 3.6 Story Gate

问：
- 这张图一眼能看懂此镜头在讲什么吗？
- 两人关系是否自然？
- 是否像海报摆拍而不是生活抓拍？

### 3.7 User Approval

只有用户明确确认：
才写 USER_APPROVED。

Agent 自己最多写 CANDIDATE_RECOMMENDED。

## 4. I2V SOP

### 4.1 Guard

先运行 production_guard。

如果 Guard fail：
不提交。

### 4.2 Motion Prompt

只写运动。

每镜：
- 一个主动作
- 一个次动作
- 一个简单运镜
- 一个环境微动

禁止：
“起身 → 走路 → 回头 → 拿东西 → 拥抱”。

### 4.3 第一 Take

先跑一条。

看：
- 脸是否漂
- 衣服是否漂
- 肢体是否增加
- 背景是否融化
- 动作是否读得懂

### 4.4 第二 Take 条件

只有第一条的问题属于随机性，才抽第二条。

如果第一条系统性换脸：
不继续抽。

### 4.5 静态降级

出现以下任一情况：
- 连续 2 条 identity drift
- 复杂手部崩坏
- 接触关系崩坏
- 镜像异常
- 背景破坏人物

直接：
STATIC_ACCEPTED + subtle camera move。

## 5. M0/M1/M2/M3 详细定义

### M0
只用：
- camera crop
- zoom
- parallax
- environment overlay

不让主体真正改变姿态。

### M1
主体最大位移非常小：
- 眨眼
- 呼吸
- 小眼神
- 小笑
- 头轻微转
- 袖摆/毛发

### M2
身体有明确但慢的位移：
- 1–2 步
- 轻靠
- 递物
- 举伞
- 举花

### M3
复杂：
- 抱起
- 快速打闹
- 接吻过程
- 双人手部交叉
- 大幅旋转

MVP 默认禁止自动生成 M3。

## 6. 视频 QA 原因码

- VID_IDENTITY_DAIYU
- VID_IDENTITY_WUKONG
- VID_SPECIES_DRIFT
- VID_COSTUME_DRIFT
- VID_EXTRA_LIMB
- VID_HAND_FAIL
- VID_PROP_DRIFT
- VID_BG_MELT
- VID_CAMERA_FAIL
- VID_MOTION_TOO_LARGE
- VID_MOTION_TOO_STATIC
- VID_END_FRAME_BAD

## 7. Accepted 决策

Accepted 不代表完美。

只要：
- 人物身份正确
- 故事可读
- 无硬错误
- 动作不分散注意力

即可进入剪辑。

## 8. 剪辑 SOP

先做 Story Cut：
- 不加复杂音效
- 不加调色炫技
- 不加口型

先确认故事节奏。

然后：
Sound Cut
→ Subtitle Cut
→ Color/Grain
→ Final QA

## 9. 每镜本地目录

local/production/<PROJECT>/<SHOT>/
- candidates/
- approved/
- takes/
- accepted/
- qa/
- records/

## 10. 每镜 Git 记录

Git 不存大媒体，只存：
- shot card
- approval
- hashes
- prompt
- workflow
- QA
- accepted decision

这样以后换模型仍然能重做。
