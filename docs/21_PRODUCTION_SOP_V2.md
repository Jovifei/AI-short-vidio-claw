# 21 Production SOP V2 — 从想法到成片

## 总原则

技术成功不等于产品成功。
每一步必须有输入、输出、Gate。

## Stage 0：Idea

输入：
- 一句话事件
- 情绪
- 结尾

输出：
- episode brief

Gate：
一集只讲一个核心事件，45–90 秒能讲完。

## Stage 1：Visual Lock

输入：
- approved face refs
- approved costume refs

输出：
- Golden Face Set
- Golden Costume Set
- reference manifests

Gate：
VISUAL_TARGET_LOCKED

## Stage 2：Storyboard

每镜必须写：
- shot_id
- story purpose
- composition
- identity refs
- costume stage
- props
- start state
- main action
- end state
- motion tier
- duration
- continuity

## Stage 3：Keyframe

优先 Hero Lane。
每镜 1–3 candidates。

QA 顺序：
1. face
2. costume
3. anatomy
4. relation
5. composition
6. lighting

只有 USER_APPROVED 才能进入视频。

## Stage 4：Motion Selection

M0：静态
M1：微动作
M2：中动作
M3：高风险

默认只把 M1/M2 放入 I2V。

## Stage 5：I2V

输入必须是 approved keyframe。

视频 prompt 只描述运动，不重新定义人物。

一次先 1 take。
如果身份漂：
- 减 motion
- 减 frames
- 改静态
- 不通过换人物模型硬救

## Stage 6：First Cut

先把：
- approved still
- accepted motion clips
按时间线拼起来。

先看故事，再补动态。

## Stage 7：Audio

顺序：
1. ambience
2. dialogue/voice-over
3. SFX
4. BGM
5. lip sync（后置）

## Stage 8：QA

视觉：
identity / costume / continuity / anatomy / motion

声音：
对白可懂 / 环境合理 / 无爆音

剪辑：
节奏 / 缺镜 / 黑帧 / 字幕安全区

## Stage 9：Final Approval

用户确认：
- 人物对
- 故事对
- 节奏对

才输出 final。

## 状态机

DRAFT
→ VISUAL_TARGET_LOCKED
→ STORYBOARD_READY
→ KEYFRAME_CANDIDATE
→ KEYFRAME_APPROVED
→ MOTION_PENDING
→ VIDEO_ACCEPTED / STATIC_ACCEPTED
→ FIRST_CUT
→ AUDIO_READY
→ FINAL_QC
→ USER_APPROVED
→ DONE
