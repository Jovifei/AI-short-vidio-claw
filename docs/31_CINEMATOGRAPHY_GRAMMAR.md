# 31 摄影机语法与剪辑覆盖规则

状态：ACTIVE

## 1. 核心摄影原则

第一季摄影机不是炫技角色。
摄影机像一个熟悉他们生活的人：
**近、静、克制、偶尔带一点偷看的感觉。**

## 2. 9:16 构图安全区

### Face Safe
重要眼睛/嘴部不要贴近：
- 顶部 8%
- 左右 6%
- 底部 14%

因为平台 UI、字幕、裁切会占空间。

### Two-shot
两人头部尽量在画面上半部 20–55% 区域。
不要让一个人贴边到后续裁切就消失。

## 3. 推荐景别比例

每 60 秒：
- Establishing / Full：15%
- Medium Two-shot：35%
- Medium Close：30%
- Close-up：15%
- Detail：5%

手部 Detail 不超过 5%，因为它是生成高风险区。

## 4. 镜头焦段“感觉”

不是要求真实镜头型号，而是 Prompt 视觉语言：

### 28–35mm
适合：
- 市场
- 阳台
- 楼道
- 冰箱
- 全身双人
- 环境关系

### 50mm
适合：
- 双人日常
- 同桌
- 照顾
- 室内

### 65–85mm
适合：
- 偷看
- 情绪 close-up
- 安静脸部
- 不适合复杂双人全身

避免超广角近脸导致悟空猴脸/黛玉脸型变形。

## 5. Camera Height

默认：
- 胸口到眼平

情侣平等镜头：
- 眼平

儿童化/弱化人物的高机位慎用。

低机位：
只用于 COMP09、英雄感或开阔户外，不连续滥用。

## 6. Camera Motion

优先级：
1. Static
2. Slow push
3. Slow lateral slide
4. Slow follow
5. Very slow handheld-like drift

第一季禁用为默认：
- whip pan
- fast orbit
- crash zoom
- drone-like impossible motion
- rapid handheld shake

原因：
这些运动同时提高背景和身份漂移风险。

## 7. Coverage

一个小场景建议最多三种覆盖：

A. Establishing Two-shot
B. Emotional Medium/Close
C. Insert（仅必要）

不要同一件小事拆十几个机位。

## 8. Eye-line

关系建立靠 eye-line：
- 悟空看黛玉时，不一定黛玉也看他
- 黛玉先看伤口，再看悟空
- 雨伞镜头可以两人都看前方

避免所有镜头都“看镜头”。

## 9. Relationship Blocking

### 亲密但自然
肩距：
- 普通日常：10–40cm
- 亲密：0–15cm

### 不用接触也能有 CP
- 同方向坐
- 一个人看另一个
- 一个人做事另一个等待
- 共享一个道具
- 同一视线目标

## 10. Cut Logic

动作切：
- 开门 → 药箱落桌
- 冰箱 → 小桌
- 雨棚 → 雨路

视线切：
- 黛玉看伤 → 悟空装没事
- 悟空偷看 → 黛玉低头

声音先行：
- 雨声提前进入 SH018
- 市场声可提前进入 SH016

## 11. Shot Duration

静态 Hero：
2.0–3.5s

M1：
2.0–4.0s

M2：
2.5–4.0s

M3：
MVP 不作为必须。

## 12. 连续性剪辑

必须锁：
- 屏幕方向
- 手伤位置
- 伞在哪只手
- 谁坐左/右
- 冰箱/桌子的相对位置

生成模型会随机翻转，必要时剪辑前水平翻转，但涉及文字/伤口方向时禁止盲翻。
