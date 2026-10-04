# 07 单集工程与镜头数据标准

## 1. Episode 必备文件

每集至少有：

1. episode.yaml
2. script.md
3. visual_design.md
4. storyboard.md
5. image_prompts.md
6. video_prompts.md
7. edit_plan.md
8. qa_report.md
9. manifest.json

这些是“创作事实”。生成媒体只是事实的执行结果。

## 2. episode.yaml

推荐字段：

~~~yaml
episode_id: EP001
title: 大圣今天受伤了
target_duration_sec: 60
aspect_ratio: "9:16"
status: storyboard
characters:
  - DAIYU
  - WUKONG
stages:
  DAIYU: HOME
  WUKONG: INJURED
theme: "照顾不是说出口的"
hook: "不怕天不怕地的大圣，最怕她不说话"
~~~

## 3. storyboard Shot Schema

每一镜必须回答：

- shot_id
- story_purpose
- duration_sec
- location_id
- characters
- character_stages
- props
- shot_size
- lens_feel
- camera_position
- camera_motion
- start_state
- main_action
- secondary_action
- end_state
- dialogue
- ambience
- continuity_from
- continuity_to
- frozen_keyframe
- reference_plan
- risk_level

## 4. 风险等级

LOW：
- 单人
- 无遮挡
- 小动作
- 固定机位

MEDIUM：
- 双人
- 简单手部
- 轻微走动
- 道具交互

HIGH：
- 双人身体接触
- 明显手部遮挡
- 复杂步态
- 吃东西特写
- 拥抱/背人
- 大幅运镜

Hero Lane 优先处理 HIGH。

## 5. Frozen Keyframe

冻结帧描述的是“镜头起点最重要的一格”。

必须能看出：
- 谁在哪里；
- 正在做什么之前；
- 双手位置；
- 道具；
- 视线；
- 身体朝向；
- 服装；
- 场景空间。

视频提示词只写“从这格怎么动到终点”，不要再次重写人物设计。

## 6. Reference 状态

沿用三个明确层级：

IMG：
只有提示词，还没有图。

PLAN：
明确准备挂哪张图，但尚未验证文件。

REF：
真实存在、已检查、允许进入生产的参考图。

视频生产只能把 REF 当正式 reference。

## 7. Manifest

manifest 机器字段示例：

~~~json
{
  "episode_id": "EP001",
  "shot_id": "SHOT-EP001-006",
  "status": "VIDEO_ACCEPTED",
  "inputs": {
    "keyframe": "EP001_SH006_KF_v002.png",
    "refs": ["CHAR_DAIYU_HOME_FRONT", "CHAR_WUKONG_INJURED_3Q"]
  },
  "workflow": {
    "id": "VID_wan22_i2v_576x1024_v001",
    "hash": "..."
  },
  "model": {
    "name": "Wan2.2",
    "variant": "...",
    "precision": "..."
  },
  "seed": 123456,
  "render": {
    "width": 576,
    "height": 1024,
    "frames": 65,
    "fps": 16
  },
  "takes": 2,
  "accepted_take": 2,
  "qc": {
    "identity": 4,
    "motion": 4,
    "continuity": 5
  }
}
~~~

## 8. 状态与可恢复性

episode 和 shot 都必须有显式状态。

Codex 启动时读取状态，不通过“看见某文件就猜已完成”。

任何一步中断，都从最近一个已接受资产恢复。
