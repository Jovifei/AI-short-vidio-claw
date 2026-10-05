# 36 QA 与回归测试矩阵

状态：ACTIVE
目的：防止“模型升级/Prompt 修改后，一张变好、其他九张变坏”。

## 1. QA 分四层

L1 Character
L2 Keyframe
L3 Motion
L4 Episode

每层有独立 Gate。

## 2. Character Regression Set

DAIYU 固定测试：
1. front neutral
2. left 3/4
3. right 3/4
4. profile
5. smile
6. mild displeasure
7. HOME full
8. OUTDOOR full

WUKONG 固定测试：
1. front neutral
2. left 3/4
3. right 3/4
4. profile
5. smile
6. serious
7. HOME full
8. FORMAL/OUTDOOR full

任何 identity 模型/LoRA/workflow 改动后都重新跑。

## 3. Couple Regression Set

固定 6 张：
- side by side
- sitting
- looking at same direction
- light shoulder contact
- shared prop
- low-angle full body

评分：
- DAIYU ID
- WUKONG ID
- height ratio
- costume
- anatomy
- chemistry

## 4. Keyframe QA

每张：
- Identity /5
- Costume /5
- Anatomy /5
- Continuity /5
- Chemistry /5
- Composition /5
- Lighting /5

Hard fail:
- identity <4
- modern clothing
- species drift
- extra major limb
- wrong continuity state

## 5. Motion QA

首帧：
must match approved start.

中段：
- identity stable
- no duplicate face
- no extra limb
- costume stable

尾帧：
- usable or at least non-breaking
- no severe drift

评分：
- Identity /5
- Motion /5
- Background /5
- Camera /5
- End frame /5

## 6. Failure Rate

每种 motion tier 单独统计：

M1:
- first-take acceptance
- two-take acceptance

M2:
同上。

不要把 M0/M3 与 M1 混在同一成功率。

## 7. Episode QA

### Identity continuity
抽检每个 shot 的关键帧。
两角色必须像同一个人。

### Costume continuity
stage 变化必须来自脚本。

### Prop continuity
药箱、绷带、伞。

### Story
静音看一遍是否能理解主要动作。

### Audio
闭眼听一遍是否有明显音量跳变。

## 8. Regression Trigger

以下改动必须跑 regression：
- Base image model
- Identity LoRA
- IPAdapter/PuLID configuration
- Wan workflow
- prompt template
- upscale
- face restoration
- lip sync
- color pipeline

## 9. Baseline Freeze

每次 Production Freeze 记录：
- git SHA
- model hashes
- workflow hashes
- prompt template hash
- reference set hash
- QA result

## 10. Stop Conditions

连续三次改动导致：
- identity 分数下降
或
- 关键帧通过率下降 > 20%

停止继续“调参”，回退最后通过版本。

## 11. 用户主观评分

用户反馈分类：
A. 一眼就对
B. 基本对，有细节要修
C. 不是这个人

A/B 才能进入下一阶段。
C 直接回人物建模，不在视频阶段修。
