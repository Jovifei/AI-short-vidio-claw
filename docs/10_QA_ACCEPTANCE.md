# 10 质量验收标准

## 1. 质量哲学

AI 短剧不是“没有瑕疵才通过”，而是“瑕疵不破坏叙事与人物可信度”。

优先级：
1. 身份
2. 连续性
3. 动作可读
4. 情绪
5. 构图
6. 清晰度
7. 原生分辨率

## 2. Keyframe QA

每项 1–5 分：

### Identity
5：与 approved reference 明显同一人/同一悟空。
3：有轻微漂移但观众仍自然识别。
1：换脸/换物种。

### Face Design
特别检查林黛玉：
- 下巴不尖；
- 眼型不突然变现代大双；
- 眉形不粗重；
- 不长期歪头；
- 不出现明显现代网红脸。

### Anatomy
- 手指数量；
- 手腕；
- 接触关系；
- 肢体穿插；
- 悟空毛发与皮肤边界。

### Continuity
- stage；
- 伤口；
- 绷带；
- 伞；
- 食物；
- 衣服湿度；
- 时间/天气。

Keyframe gate：
Identity ≥4，Continuity ≥4，Anatomy ≥3，且无致命错误。

## 3. Video QA

### 硬失败
- 主角换脸；
- 多脸；
- 肢体突然增减；
- 人物突然消失；
- 关键道具消失；
- 严重背景融化；
- 镜头无法完成叙事动作；
- OOM / corrupt output。

### 软失败
- 小手指异常但不是焦点；
- 衣褶轻微变化；
- 背景路人略异常；
- 运动幅度不足但可剪。

评分：
- identity 1–5
- motion 1–5
- continuity 1–5
- composition 1–5
- emotion 1–5

accepted：
- identity ≥4；
- continuity ≥4；
- motion ≥3；
- 无硬失败。

## 4. Audio QA

TTS：
- 无错字；
- 情绪合理；
- 不爆音；
- 同角色跨集声线一致；
- 人名读音固定。

Dialogue：
- 音量可懂；
- 不被 BGM 压住；
- 环境声不喧宾夺主。

## 5. Lip Sync QA

MuseTalk 镜头：
- 唇形节奏与语音基本同步；
- 人脸身份不因 lip sync 明显改变；
- 嘴周无明显 patch 边缘；
- 头部大运动时不撕裂。

不通过时允许保留原视频，改用画外音/侧脸/反打，不强行修口型。

## 6. Edit QA

- 9:16；
- 无黑帧；
- 无缺镜；
- 时长在目标范围；
- 台词不截断；
- 字幕安全区；
- 音轨无突变；
- 开头 2 秒有信息；
- 结尾有情绪落点或钩子。

## 7. 系列一致性 QA

每集额外检查：
- 人物五官基线；
- 身高差；
- 声线；
- 家中固定布局；
- 常用道具；
- CP 相处方式；
- 上一集留下的状态。

## 8. 失败原因码

KF_IDENTITY
KF_ANATOMY
KF_COMPOSITION
KF_CONTINUITY
VID_IDENTITY_DRIFT
VID_EXTRA_LIMB
VID_PROP_DRIFT
VID_BG_MELT
VID_MOTION_FAIL
VID_CAMERA_FAIL
AUDIO_TTS_ERROR
AUDIO_LEVEL
LIP_IDENTITY
LIP_SYNC
EDIT_MISSING_SHOT
EDIT_TIMING

Codex 必须记录原因码，以便后续统计“最费时间的问题”。
