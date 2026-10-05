# 06 角色一致性与双身份系统（V2）

## 1. Source of Truth

人物身份优先级：
1. 用户批准的视觉 reference
2. 用户批准的 golden keyframe
3. 文字 Character Bible
4. prompt 风格词

文字描述只能帮助生成，不能单独决定人物是谁。

## 2. 当前视觉模式

ACTIVE：REFERENCE_LOCKED_CLASSIC

目标：
- 林黛玉保持用户认可的古典荧幕参考脸感；
- 孙悟空保持用户认可的经典齐天大圣猴脸结构；
- 两人只穿已批准古装；
- 现代生活场景可以存在，但人物不自动现代化。

## 3. 林黛玉

重点：
- 偏圆润鹅蛋脸
- 自然下颌，非尖 V 下巴
- 眼眉含蓄古典
- 鼻口小巧
- 古典发式
- 表情丰富，不固定歪头/低头

Hard Reject：
- 网红尖下巴
- 通用 AI 少女脸
- 强现代妆感
- 现代人物服装

## 4. 孙悟空

重点：
- 猴脸结构优先
- 眉骨、眼窝、吻部、耳形稳定
- 毛色与批准 reference 一致
- 表情可以温和，但不能普通人脸化

Hard Reject：
- 男性人脸加毛
- 耳/吻部随机
- 物种漂移
- 现代人物服装

## 5. Golden Reference Pack

V0 建立。

每人至少：
- front
- 3/4 left
- 3/4 right
- neutral
- expressive
- full/half body costume

真实 reference 放 local/，Git 存 manifest/hash。

## 6. Costume Stage

DAIYU：
- CLASSIC_OUTDOOR
- CLASSIC_HOME
- CLASSIC_RAIN

WUKONG：
- CLASSIC_OUTDOOR
- CLASSIC_HOME
- CLASSIC_INJURED

HOME 只减轻古装层数，不改为现代睡衣/运动服。

## 7. 双身份

MVP 不要求先本地自动生成。

第一条产品路线：
Hero Lane 生成双人 approved keyframe
→ 用户批准
→ Wan I2V

本地 PuLID/IPAdapter/LoRA 属后续自动化优化。

## 8. QA

每张双人关键帧：
- DAIYU identity ≥4/5
- WUKONG identity ≥4/5
- costume correct
- anatomy pass
- interaction readable

人物不对时，必须回 keyframe，不得通过视频重抽补救。
